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
import json
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
		domain = data.get_domain()
		nodes = data.get_nodes_name()
		
		# dependency graph
		dep_graph = DependencyGraph(data)
		edges = dep_graph.get_dep_edges()

		# create task to get task_id
		task_obj = Task.objects.create(
			selected_attrs = validated_data['selected_attrs'],
			task_name = validated_data['task_name'],
			data_path = validated_data['data_path'], # the original data path
			dep_graph = str(dep_graph.get_dep_edges(display = True)),
			valbin_map = str(data.get_valbin_maps()),
			domain = str(domain.items()) # this is the domain of coarsed data, and sould keep cols ordering.
		)

		# create folder for task
		task_folder = self.create_task_folder(task_obj.task_id)

		# junction tree
		print self.get_jtree_file_path(task_obj.task_id)
		jtree = JunctionTree(
			edges, 
			nodes, 
			self.get_jtree_file_path(task_obj.task_id) # the path to save junction tree file
		)

		# optimize marginal
		var_reduce = VarianceReduce(domain, jtree.get_jtree()['cliques'], 0.2)
		optimized_jtree = var_reduce.main()

		# update task to save the optimized jtree
		task_obj.jtree_strct = str(optimized_jtree)
		task_obj.save()

		self.save_coarse_data(task_folder, data)
		return task_obj

	
	def convert_selected_attrs(self, attrs_ls):
		attrs_ls = ast.literal_eval(attrs_ls)
		return collections.OrderedDict([(attr['attr_name'], attr['dtype']) for attr in attrs_ls])


	def save_coarse_data(self, task_folder, data):
		# TODO: to deal with failure
		file_path = os.path.join(task_folder,c.COARSE_DATA_NAME)
		data.save(file_path)

class JobSerializer(serializers.ModelSerializer, Base):
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
		domain = collections.OrderedDict(ast.literal_eval(task.domain)) # This is the corsed domain
		valbin_map = ast.literal_eval(task.valbin_map)
		selected_attrs = self.convert_selected_attrs(task.selected_attrs)
		nodes = domain.keys()

		# TODO: read coarse in python, and therefore, 
		# the pandas dataframe can be reused in error rate estimations

		inference = Inference(
			self.get_coarse_data(task_id), 
			self.get_jtree_file_path(task_id), 
			domain, 
			jtree_strct , 
			epsilon)

		sim_df = inference.execute()

		# compute the errors rate
		statistics_err = self.get_statistical_error(task_id, sim_df)

		sim_df = self.data_generalize(sim_df, valbin_map, selected_attrs)

		# Save the synthetic data to file system.
		synthetic_path = self.save_sim_data(sim_df, task_id, privacy_level)

		# Save metadata to database
		
		job_obj = Job.objects.create(
			task_id = task,
			privacy_level = privacy_level,
			epsilon = epsilon,
			synthetic_path = synthetic_path,
			statistics_err = statistics_err
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

		# return the download path
		return c.SIM_DATA_URI_PATTERN % {'task_id':task_id, 'file_name':file_name}

	def get_statistical_error(self, task_id, sim_coarsed_df):
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

		mean_error = np.abs((sim_df_mean - coarsed_df_mean)*100 / coarsed_df_mean)
		std_error = np.abs((sim_df_std - coarsed_df_std)*100 / coarsed_df_std)

		mean_error = [str(rate)+'%' for rate in np.round(mean_error, decimals = 2)]
		std_error = [str(rate)+'%' for rate in np.round(std_error, decimals = 2)]

		result = dict({
			"mean":dict(zip(nodes, mean_error)),
			"std":dict(zip(nodes, std_error))
		})
		return result

	def convert_selected_attrs(self, attrs_ls):
		attrs_ls = ast.literal_eval(attrs_ls)
		return collections.OrderedDict([(attr['attr_name'], attr['dtype']) for attr in attrs_ls])