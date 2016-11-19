from .models import Task, Job
from celery import shared_task,current_task
from common.data_utilities import DataUtils
from common.base import *
from prob_models.dep_graph import DependencyGraph
from prob_models.jtree import JunctionTree
from datetime import datetime
from dptable.variance_reduce import VarianceReduce
from dptable.inference import Inference
from dptable.stats_functions import StatsFunctions
from dptable.simulate import Simulate
from django.shortcuts import get_object_or_404, get_list_or_404

import common.constant as c
import numpy as np
import os
import ast
import json
import collections

@shared_task
def create_process(request):

	is_celery = False if 'unitest' in request.keys() else True

	process = Preprocess(request)
	process_update(c.CELERY_PROGRESS, 0, 'Initialize', is_celery)
	process.update_instance('PROGRESS', is_celery)
	
	# read data
	process_update(c.CELERY_PROGRESS, 5, 'Reading Data', is_celery)
	process.read_data()
	
	# coarser data
	process_update(c.CELERY_PROGRESS, 15, 'Encoding Data', is_celery)
	process.coarse()

	# dep-graph
	process_update(c.CELERY_PROGRESS, 40, 'Building Dependency Graph', is_celery)
	process.build_dep_graph()

	# junction tree and merge
	process_update(c.CELERY_PROGRESS, 75, 'Building Junction Tree and Optimizing Marginals', is_celery)
	process.build_jtree()

	# save coarse data
	process_update(c.CELERY_PROGRESS, 85, 'Save Mediate Data', is_celery)
	process.save_coarse_data()
	
	process_update(c.CELERY_PROGRESS, 100, 'Preprocess Done', is_celery)
	process.update_instance('SUCCESS', is_celery)

	if is_celery:
		return process.task_id
	return process

@shared_task
def update_process(request):

	is_celery = False if 'unitest' in request.keys() else True

	process_update(c.CELERY_PROGRESS, 0, 'Initialize', is_celery)
	process = Preprocess(request)
	# re-compute jtree

	# merge clique
	pass

@shared_task
def create_anonymity(request):

	is_celery = False if 'unitest' in request.keys() else True
	anonymit = Anonymization(request, is_celery)
	process_update(c.CELERY_PROGRESS, 0, 'Initialize', is_celery)
	anonymit.update_instance('PROGRESS', is_celery)

	# read coarse data
	process_update(c.CELERY_PROGRESS, 5, 'Reading Coarse data', is_celery)
	anonymit.get_coarse_data()

	# get histogram
	process_update(c.CELERY_PROGRESS, 17, 'Computing Contingency Tables', is_celery)
	anonymit.get_histograms()

	# do inference
	process_update(c.CELERY_PROGRESS, 48, 'Doing DP Inferences', is_celery)
	anonymit.do_inference()

	# simulate
	process_update(c.CELERY_PROGRESS, 72, 'Simulating Data', is_celery)
	anonymit.simulate()

	# statistical error rate
	process_update(c.CELERY_PROGRESS, 89, 'Evaluating Statistical Errors', is_celery)
	anonymit.get_statistical_error()

	# generalize data
	process_update(c.CELERY_PROGRESS, 95, 'Generalizing Data', is_celery)
	anonymit.data_generalize()

	# save synthetic data
	process_update(c.CELERY_PROGRESS, 95, 'Writing Data', is_celery)
	anonymit.save_data()
	anonymit.update_instance('SUCCESS', is_celery)

	return anonymit.dp_id

def process_update(progress, percent, name, is_celery = False):
	if is_celery is True:
		current_task.update_state(
				state = progress, 
				meta = {
						c.CELERY_PRO_PERCENT: percent, 
						c.PRO_NAME: name
				}
		)

class Preprocess(Base):
	def __init__(self, request):

		self.chunk_size = request['chunk_size'] if 'chunk_size' in request.keys() else -1
		self.coarse_data_path = None
		self.data = None
		self.data_path = request['data_path']
		self.date_format = request['selected_attrs']['date_format'] if 'date_format' in request['selected_attrs'].keys() else None
		self.dep_graph = None # original edges

		self.domain = None
		self.edges = None
		self.eps1_val = request['eps1_val'] if 'eps1_val' in request.keys() else c.EPSILON_1
		self.eps1_level = request['eps1_level'] if 'eps1_level' in request.keys() else 1
		self.jtree_strct = None
		self.jtree_file_path = None
		
		self.names = request['names'] if 'names' in request.keys() else None
		self.nodes = None
		self.opted_cluster = None
		self.selected_attrs = self.convert_selected_attrs(request['selected_attrs'])
		self.specified_c_domain = request['selected_attrs']['specified_c_domain'] if 'specified_c_domain' in request['selected_attrs'].keys() else None
		self.task_id = request['task_id']
		self.task_folder = self.create_task_folder(self.task_id)
		self.valbin_map = None

		self.white_list = self.get_white_list(request)

	def read_data(self):
		self.data = DataUtils(
			file_path = self.data_path, 
			selected_attrs = self.selected_attrs,
			names = self.names,
			specified_c_domain = self.specified_c_domain,
			chunk_size = self.chunk_size,
			date_format = self.date_format
		)

	def coarse(self):
		self.data.data_coarsilize()
		self.domain = self.data.get_domain()
		self.nodes = self.data.get_nodes_name()
		self.valbin_map = str(self.data.get_valbin_maps())

	def build_dep_graph(self):
		# dependency graph
		dep_graph_obj = DependencyGraph(self.data, eps1_val = self.eps1_val)
		self.edges = dep_graph_obj.get_dep_edges(display = True)
		self.cust_edges = dep_graph_obj.set_white_list(self.white_list) \
							.get_dep_edges(display = True)
		self.dep_graph = str(self.edges)

	def get_white_list(self, request):
		white_list = request['white_list'] if 'white_list' in request.keys() else "[]"
		if not isinstance(white_list, list):
			white_list = ast.literal_eval(white_list)
		return white_list

	def build_jtree(self):
		# junction tree
		jtree = JunctionTree(
			self.cust_edges, 
			self.nodes, 
			self.get_jtree_file_path(self.task_id, self.eps1_level), # the path to save junction tree file
		)

		# optimize marginal
		var_reduce = VarianceReduce(self.domain, jtree.get_jtree()['cliques'], 0.2)
		self.opted_cluster = var_reduce.main()
		self.jtree_strct = jtree.get_jtree()['cliques']
		self.jtree_file_path = self.save_merged_jtree(self.task_id, self.eps1_level, self.jtree_strct)

	def save_coarse_data(self):
		# TODO: to deal with failure
		file_path = os.path.join(self.task_folder,c.COARSE_DATA_NAME)
		if self.data is not None:
			self.data.save(file_path)
			self.coarse_data_path = file_path

	def update_instance(self, status, is_celery):
		if not is_celery:
			return

		instance = get_object_or_404(Task, pk = self.task_id)
		instance.eps1_val = self.eps1_val
		instance.eps1_level = self.eps1_level
		instance.dep_graph = str(self.edges)
		instance.valbin_map = str(self.valbin_map)
		instance.domain = str(self.domain.items()) if self.domain is not None else None
		instance.white_list = self.white_list
		instance.jtree_strct = str(self.jtree_strct)
		instance.opted_cluster = str(self.opted_cluster)
		instance.status = ProcessStatus.get_code(status)
		instance.end_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
		instance.save()

class Anonymization(Base):

	def __init__(self, request, is_celery):
		self.privacy_level = request['privacy_level']
		self.epsilon = float(request['epsilon'])
		self.min_freq = float(request['min_freq']) if 'min_freq' in request.keys() else 0.
		self.exp_round = request['exp_round'] if 'exp_round' in request.keys() else None

		self.dp_id = request['dp_id']
		task = get_object_or_404(Task, pk = request['task_id']) if is_celery else request['task_id']
		self.task_id = task.task_id
		self.eps1_level = task.eps1_level
		self.data_path = task.data_path

		self.jtree_strct = ast.literal_eval(str(task.jtree_strct))
		self.opted_cluster = ast.literal_eval(str(task.opted_cluster))
		
		self.edges = ast.literal_eval(str(task.dep_graph))
		self.domain = task.domain if isinstance(task.domain, dict) else collections.OrderedDict(ast.literal_eval(task.domain)) # This is the corsed domain
		self.valbin_map = ast.literal_eval(str(task.valbin_map))
		self.selected_attrs = task.selected_attrs if isinstance(task.selected_attrs, dict) else self.convert_selected_attrs(task.selected_attrs)
		self.white_list = ast.literal_eval(str(task.white_list))
		self.nodes = self.domain.keys()

		self.histogramdds = None
		self.data = None
		self.sim_df = None
		self.statistics_err = None
		self.generalized_dataframe = None
		self.synthetic_path = None



	def get_coarse_data(self):
		# TODO: Read coarse data from memory cach.
		# TODO: To deal with failure.
		folder = c.MEDIATE_DATA_DIR % {'task_id': self.task_id}
		file_path = os.path.join(folder,c.COARSE_DATA_NAME)
		self.data = DataUtils(
			file_path = file_path, 
			valbin_maps = self.valbin_map,
			selected_attrs = self.selected_attrs
		)

	def kaggregate(self):
		if self.min_freq > 0:
			# cluster_num = len(self.jtree_strct)
			# thresh = self.get_freq_thresh(epsilon, cluster_num, min_freq)
			thresh = self.min_freq
			self.data.aggregation(thresh)
			self.domain = self.data.get_domain()
			self.valbin_map = self.data.get_valbin_maps()

	def get_histograms(self):
		combined_queries = self.combine_cliques_for_query(self.jtree_strct, self.opted_cluster)
		stats_func = StatsFunctions()
		self.histogramdds = stats_func.histogramdd_batch(self.data, combined_queries)

	def do_inference(self):
		inference = Inference(
			self.data, 
			self.get_jtree_file_path(self.task_id, self.eps1_level), 
			self.domain, 
			self.opted_cluster,
			self.histogramdds,
			self.epsilon)

		self.model = inference.execute()

	def simulate(self):
		simulator = Simulate(self.model, self.data.get_nrows())
		self.sim_df = simulator.run()

	def get_statistical_error(self):
		"""
		Compute the mean and standard varience error rates(Both coarse data).
		Parameters
			task_id:
				The task id to retrieve coarsed data.
			sim_coarsed_df:
				The noised sythetic data.
		Returns
			{
				"A":0.05,
				"B":0.12,
				...
			}
		"""
		eps1 = self.eps1_level
		eps2 = self.epsilon
		white_list = self.white_list
		k = self.min_freq
		nodes = self.nodes
		# read the original coarse data first.
		coarsed_df = self.data.get_pandas_df()

		# make sure the order
		sim_coarsed_df = self.sim_df[self.nodes]
		
		coarsed_df_mean = np.array(coarsed_df.mean(), dtype = float)
		coarsed_df_std = np.array(coarsed_df.std(), dtype = float)

		sim_df_mean = np.array(sim_coarsed_df.mean(), dtype = float)
		sim_df_std = np.array(sim_coarsed_df.std(), dtype = float)

		mean_error = np.abs((sim_df_mean - coarsed_df_mean)*100 / coarsed_df_mean)
		std_error = np.abs((sim_df_std - coarsed_df_std)*100 / coarsed_df_std)

		mean_error = [str(rate)+'%' for rate in np.round(mean_error, decimals = 2)]
		std_error = [str(rate)+'%' for rate in np.round(std_error, decimals = 2)]

		self.print_pretty_summary(nodes, mean_error, std_error, eps1, eps2, white_list, k)
		self.statistics_err = {
			'attrs':nodes,
			'measures':['mean', 'std'],
			'values':{
				'mean':mean_error,
				'std':std_error
			}
		}

	def data_generalize(self):
		data = DataUtils(pandas_df=self.sim_df, valbin_maps = self.valbin_map, selected_attrs = self.selected_attrs)
		data.data_generalize()
		self.generalized_dataframe = data.get_pandas_df()

	def save_data(self):
		if self.exp_round:
			self.synthetic_path = self.save_sim_data_exp()
		else:
			self.synthetic_path = self.save_sim_data()

	def save_sim_data(self, spec_file_name = None):
		# TODO: to deal with failure
		folder = c.MEDIATE_DATA_DIR % {'task_id': self.task_id}
		if not os.path.exists(folder):
			os.makedirs(folder)

		file_name = c.SIM_DATA_NAME_PATTERN % {'privacy_level': self.privacy_level}
		if spec_file_name is not None:
			file_name = spec_file_name
			# TODO: a parameter to specify no header output
			file_path = os.path.join(folder,file_name)
			self.generalized_dataframe.to_csv(file_path, index = False, header = False)
		else:
			file_path = os.path.join(folder,file_name)
			self.generalized_dataframe.to_csv(file_path, index = False)

		return c.SIM_DATA_URI_PATTERN % {'task_id':self.task_id, 'file_name':file_name}

	def save_sim_data_exp(self):
		spec_file_name = "sim_eps1lv_%(eps_lv)s_eps2lv_%(privacy_level)s_k_%(min_freq)s_round_%(exp_round)s.csv" % {
				'exp_round': self.exp_round,
				'privacy_level': self.privacy_level,
				'eps_lv': self.eps1_level,
				'min_freq': int(self.min_freq)
		}
		return self.save_sim_data(spec_file_name = spec_file_name)

	def print_pretty_summary(self, nodes, mean_error, std_error, eps1, eps2, white_list, k):
		LOG = Base.get_logger("Statical Accuracy Summary")
		import pandas as pd
		frame = pd.DataFrame({
			'Attribures': nodes,
			'Mean': mean_error,
			'STD': std_error
			})
		LOG.info("eps1: %.2f, eps2: %.2f" % (eps1, eps2))
		LOG.info("White List: %s" % str(white_list))
		LOG.info("k-aggregate value: %d" % k)
		LOG.info('\n'+str(frame))

	def create_instance(self):
		Job.objects.create(
			task_id = self.task_id,
			privacy_level = self.privacy_level,
			epsilon = self.epsilon,
			synthetic_path = self.synthetic_path,
			statistics_err = self.statistics_err
		)

	def update_instance(self, status, is_celery):
		if not is_celery:
			return

		instance = get_object_or_404(Job, pk = self.dp_id)
		instance.synthetic_path = self.synthetic_path
		instance.statistics_err = self.statistics_err
		instance.status = ProcessStatus.get_code(status)
		instance.end_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
		instance.save()
