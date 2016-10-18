import os
import common.constant as c
from django.test import TestCase
from spark_exp.data_dist import DataDist
from spark_exp.dep_graph_dist import DepGraphDist

class TestDistGraph(TestCase):
	def setUp(self):
		self.data = DataDist(c.DOMAIN_FILE, data_path = c.HDFS_MEDIAN_DATA)

	def test_dep_graph(self):
		graph = DepGraphDist(self.data)
		edges = graph.fit()
		print edges