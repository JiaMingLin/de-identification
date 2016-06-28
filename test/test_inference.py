from django.test import TestCase
from dptable.inference import Inference
from dptable.variance_reduce import VarianceReduce
from prob_models.dep_graph import DependencyGraph
from prob_models.jtree import JunctionTree
from common.data_utilities import DataUtils


import common.constant as c

class TestInerence(TestCase):
	def setUp(self):

		# import data
		data = DataUtils(c.TEST_DATA_PATH)
		domain = data.get_domain()
		nodes = data.get_nodes_name()
		
		# compute dependency graph
		dep_graph = DependencyGraph(data)
		edges = dep_graph.get_dep_edges()
		
		# compute junction tree
		jtree = JunctionTree(edges, nodes)
		cliques = jtree.get_jtree()
		# optimize marginals

		self.inference = Inference(c.TEST_DATA_PATH, edges, nodes, domain, cliques , 0.2)

	def test_execute_inference(self):
		self.inference.execute()
