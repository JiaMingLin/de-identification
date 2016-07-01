from django.test import TestCase

from common.data_utilities import DataUtils
from prob_models.dep_graph import DependencyGraph
from prob_models.jtree import JunctionTree

TESTING_FILE = 'static/test/testing_row_data.csv'

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
        edges = dep_graph.get_dep_edges(display = True)
        self.assertEqual(len(edges) == 6, True)

class JunctionTreeTests(TestCase):

    def setUp(self):
        self.data = DataUtils(TESTING_FILE)
        self.dep_graph = DependencyGraph(self.data)
        self.edges = self.dep_graph.get_dep_edges(display=True)
        self.nodes = self.data.get_nodes_name()

    def test_junction_tree_with_one_clique(self):
        """
        The dependency graph is a complete graph, 
        so there is only one clique in the junction tree
        """
        jtree = JunctionTree(self.edges, self.nodes)
        cliques = jtree.get_jtree(display = True)
        print cliques
        self.assertEqual(len(cliques) == 1, True)
