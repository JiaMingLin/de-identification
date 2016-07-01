from rest_framework import serializers
from .models import Task, Job

from common.data_utilities import DataUtils
from common.base import Base
from prob_models.dep_graph import DependencyGraph
from prob_models.jtree import JunctionTree
from dptable.variance_reduce import VarianceReduce
from dptable.inference import Inference

import common.constant as c
import numpy as np
import os
import ast
import collections

# TODO: All the operations/methods should NOT gather in this file, it is too long to read.
class TaskSerializer(serializers.ModelSerializer, Base):

	class Meta:
		model = Task
		field = ('task_id', 'task_name', 'data_path','selected_attrs' ,'jtree_strct', 'dep_graph', 'start_time', 'end_time', 'status')

	def create(self, validated_data):
		selected_attrs = self.convert_selected_attrs(validated_data['selected_attrs'])
		data = DataUtils(
			file_path = validated_data['data_path'], 
			selected_attrs = selected_attrs
		)
		# coarsilize
		# TODO: Should add the sample rate.
		data.data_coarsilize()
		
		# dependency graph
		dep_graph = DependencyGraph(data)
		edges = dep_graph.get_dep_edges()

		# junction tree
		nodes = data.get_nodes_name()
		jtree = JunctionTree(edges, nodes)

		# optimize marginal
		domain = data.get_domain()
		var_reduce = VarianceReduce(domain, jtree.get_jtree(display=True), 0.2)
		optimized_jtree = var_reduce.main()

		task_obj = Task.objects.create(
			selected_attrs = validated_data['selected_attrs'],
			task_name = validated_data['task_name'],
			data_path = validated_data['data_path'],
			jtree_strct = str(optimized_jtree),
			dep_graph = str(dep_graph.get_dep_edges(display = True)),
			valbin_map = str(data.get_valbin_maps()),
			domain = dict(domain) # this is the domain of coarsed data
		)
		self.save_coarse_data(task_obj, data)
		return task_obj

	
	def convert_selected_attrs(self, attrs_ls):
		attrs_ls = ast.literal_eval(attrs_ls)
		return collections.OrderedDict([(attr['attr_name'], attr['dtype']) for attr in attrs_ls])


	def save_coarse_data(self, task, data):
		# TODO: to deal with failure
		folder = c.MEDIATE_DATA_DIR % {'task_id': task.task_id}
		if not os.path.exists(folder):
			os.makedirs(folder)	
		file_path = os.path.join(folder,c.COARSE_DATA_NAME)
		data.save(file_path)

class JobSerializer(serializers.ModelSerializer):
	class Meta:
		model = Job
		field = ('dp_id', 'task_id', 'privacy_level', 'epsilon', 'status', 'synthetic_path', 'statistics_err', 'log_path', 'start_time', 'end_time')

	# The Job is not going to be modified.
	def create(self, validated_data):

		privacy_level = validated_data['privacy_level']
		epsilon = float(validated_data['epsilon'])

		# retrieve task information fram DB.
		task = validated_data['task_id']
		task_id = task.task_id
		data_path = task.data_path
		jtree_strct = ast.literal_eval(task.jtree_strct)
		edges = ast.literal_eval(task.dep_graph)
		domain = ast.literal_eval(task.domain) # This is the corsed domain
		valbin_map = ast.literal_eval(task.valbin_map)
		selected_attrs = self.convert_selected_attrs(task.selected_attrs)
		nodes = domain.keys()

		# TODO: Should not read data again.
		inference = Inference(self.get_coarse_data(task_id), edges, nodes, domain, jtree_strct , epsilon)
		sim_df = inference.execute()
		stats_err = self.get_statistical_error(task_id, sim_df)

		sim_df = self.data_generalize(sim_df, valbin_map, selected_attrs)

		# Save the synthetic data to file system.
		synthetic_path = self.save_sim_data(sim_df, task_id, privacy_level)
		job_obj = Job.objects.create(
			task_id = task,
			privacy_level = privacy_level,
			epsilon = epsilon,
			synthetic_path = synthetic_path,
			statistics_err = stats_err
		)
		return job_obj

	def get_coarse_data(self, task_id):
		# TODO: Read coarse data from memory cach.
		# TODO: To deal with failure.
		folder = c.MEDIATE_DATA_DIR % {'task_id': task_id}
		file_path = os.path.join(folder,c.COARSE_DATA_NAME)
		return file_path

	def data_generalize(self, dataframe, valbin_map, selected_attrs):
		data = DataUtils(pandas_df=dataframe, valbin_maps = valbin_map, selected_attrs = selected_attrs)
		data.data_generalize()
		return data.get_pandas_df()

	def save_sim_data(self, dataframe, task_id, privacy_level):
		# TODO: to deal with failure
		folder = c.MEDIATE_DATA_DIR % {'task_id': task_id}
		if not os.path.exists(folder):
			os.makedirs(folder)
		file_name = c.SIM_DATA_NAME_PATTERN % {'privacy_level':privacy_level}
		file_path = os.path.join(folder,file_name)
		dataframe.to_csv(file_path, index = False)
		return file_path

	def get_statistical_error(self, task_id, sim_coarsed_df):
		# read the original coarse data first.
		coarsed_data = DataUtils(self.get_coarse_data(task_id))
		coarsed_df = coarsed_data.get_pandas_df()
		nodes = coarsed_data.get_nodes_name()

		# make sure the order
		sim_coarsed_df = sim_coarsed_df[nodes]

		coarsed_df_mean = np.array(coarsed_df.mean(), dtype = float)
		coarsed_df_std = np.array(coarsed_df.std(), dtype = float)

		sim_df_mean = np.array(sim_coarsed_df.mean(), dtype = float)
		sim_df_std = np.array(sim_coarsed_df.std(), dtype = float)

		mean_error = (sim_df_mean - coarsed_df_mean) / coarsed_df_mean
		std_error = (sim_df_std - coarsed_df_std) / coarsed_df_std

		return mean_error, std_error

	def convert_selected_attrs(self, attrs_ls):
		attrs_ls = ast.literal_eval(attrs_ls)
		return collections.OrderedDict([(attr['attr_name'], attr['dtype']) for attr in attrs_ls])