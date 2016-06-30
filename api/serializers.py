from rest_framework import serializers
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from .models import Task, Job

from common.data_utilities import DataUtils
from common.base import Base
from prob_models.dep_graph import DependencyGraph
from prob_models.jtree import JunctionTree
from dptable.variance_reduce import VarianceReduce

import common.constant as c
import os
import json
import collections

class TaskSerializer(serializers.ModelSerializer, Base):

	selected_attrs = serializers.ListField(
		child=serializers.DictField()
	)
	class Meta:
		model = Task
		field = ('task_id', 'task_name', 'data_path', 'jtree_strct', 'dep_graph', 'start_time', 'end_time', 'status')

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
		var_reduce = VarianceReduce(data.get_domain(), jtree.get_jtree(display=True), 0.2)
		optimized_jtree = var_reduce.main()

		task_obj = Task.objects.create(
			selected_attrs = validated_data['selected_attrs'],
			task_name = validated_data['task_name'],
			data_path = validated_data['data_path'],
			jtree_strct = str(optimized_jtree),
			dep_graph = str(dep_graph.get_dep_edges(display = True))
		)
		self.save_coarse_data(task_obj, data)
		return task_obj

	
	def convert_selected_attrs(self, attrs_ls):
		return collections.OrderedDict([(attr['attr_name'], attr['dtype']) for attr in attrs_ls])

	def save_coarse_data(self, task, data):
		folder = c.MEDIATE_DATA_DIR % {'task_id': task.task_id}
		if not os.path.exists(folder):
			os.makedirs(folder)		
		file_path = os.path.join(folder,c.COARSE_DATA_NAME)
		data.save(file_path)

class JobSerializer(serializers.ModelSerializer):
	class Meta:
		model = Job
		field = ('dp_id', 'task_id', 'privacy_level', 'epsilon', 'status', 'synthetic_path', 'statistics_err', 'log_path', 'start_time', 'end_time')
