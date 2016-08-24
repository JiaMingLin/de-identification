from django.test import TestCase

from common.data_utilities import DataUtils
from prob_models.dep_graph import DependencyGraph
from prob_models.jtree import JunctionTree

import common.constant as c

TESTING_FILE = c.TEST_DATA_PATH

"""
The test file has for fields, and the dependency graph would be a complete graph.
The junction Tree has only one clique

"""
class DependencyGraphTests(TestCase):

	def setUp(self):
		self.data = DataUtils(TESTING_FILE)

	def test_dep_graph_edges_length_is_6(self):
		"""
		Test the Dependency graph computation
		"""
		dep_graph = DependencyGraph(self.data)
		edges = dep_graph.get_dep_edges()
		#print self.data.get_domain()
		#self.assertEqual(len(edges) == 3, True)

	def test_dep_graph_with_white_list(self):
		dep_graph = DependencyGraph(self.data, white_list = [['Age', 'Income', 'TRV'], ['DGF', 'HTN']])
		edges = dep_graph.get_dep_edges()

	def test_dep_graph_without_noise(self):
		dep_graph = DependencyGraph(self.data, noise_flag = False)
		self.assertEqual(
			dep_graph.get_dep_edges() == [['Height', 'HTN'], ['Weight', 'HTN'], ['Income', 'TRV']],
			True)

	def test_dep_graph_contruct_from_edges(self):
		edges = [['A','B'], ['B','C'], ['C', 'D'], ['D', 'E']]
		dep_graph = DependencyGraph(edges = edges)
		self.assertEqual(dep_graph.get_dep_edges() == edges, True)

	def test_dep_graph_add_white_list(self):
		edges = [['A','B'], ['B','C'], ['C', 'D'], ['D', 'E'], ['F']]
		white_list = [['A','B', 'C'], ['C', 'D', 'F']]
		dep_graph = DependencyGraph(edges = edges)
		self.assertEqual(dep_graph.set_white_list(white_list).get_dep_edges() == [['A', 'B'], ['B', 'C'], ['C', 'D'], ['D', 'E'], ['F'], ('A', 'B'), ('A', 'C'), ('B', 'C'), ('C', 'D'), ('C', 'F'), ('D', 'F')], True)

class JunctionTreeTests(TestCase):

	def setUp(self):
		self.data = DataUtils(TESTING_FILE)
		self.dep_graph = DependencyGraph(self.data)
		self.edges = self.dep_graph.get_dep_edges()
		self.nodes = self.data.get_nodes_name()
		self.jtree_path = c.TEST_JTREE_FILE_PATH

	def test_jtree_without_noise(self):
		dep_graph = DependencyGraph(self.data, noise_flag = False)
		edges = dep_graph.get_dep_edges()
		jtree = JunctionTree(edges, self.nodes, self.jtree_path)
		cliques = jtree.get_jtree()['cliques']
		self.assertEqual(cliques == [['HTN', 'Height'], ['HTN', 'Weight'], ['Income', 'TRV'], ['Age'], ['DGF']], True)

	def test_jtree_with_white_list(self):
		dep_graph = DependencyGraph(self.data, white_list = [['Age', 'Income', 'TRV'], ['DGF', 'HTN']])
		edges = dep_graph.get_dep_edges()
		jtree = JunctionTree(edges, self.nodes, self.jtree_path)
		cliques = jtree.get_jtree()['cliques']
		self.assertEqual(cliques == [['HTN', 'Height'], ['HTN', 'Weight'], ['HTN', 'DGF'], ['Income', 'TRV', 'Age']], True)

	def test_build_jtree_then_check_jtree_file(self):
		self.TestA()
		self.TestB()

	def TestA(self):
		"""
		The dependency graph is a complete graph, 
		so there is only one clique in the junction tree
		"""
		jtree = JunctionTree(self.edges, self.nodes, self.jtree_path)
		jtreepy = jtree.get_jtree()
		#print jtreepy
		self.assertEqual(len(jtreepy) == 3, True)

	def TestB(self):
		import os, time
		from stat import *
		st = os.stat(self.jtree_path)
		now = time.time()
		# TODO: Need to know this file is new modified
		#self.assertEqual((st.st_mtime - now) < 100000, True)