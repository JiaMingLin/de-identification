from django.test import TestCase

from common.data_utilities import DataUtils
from prob_models.dep_graph import DependencyGraph
from prob_models.jtree import JunctionTree

TESTING_FILE = 'static/test/testing_row_data.csv'

"""
The test file has for fields, and the dependency graph would be a complete graph.
The junction Tree has only one clique

"""
class DataUtilitiesTests(TestCase):

    def setUp(self):
        self.data = DataUtils(TESTING_FILE)

    def test_data_preview(self):
        preview = self.data.data_preview()
        self.assertEqual(len(preview.values[0]) > 0, True)

    def test_read_data_by_three_selected_column(self):
        """
        Test the read data by user specified columns
        """
        selected_data = DataUtils(TESTING_FILE, ['A', 'B', 'C'])
        self.assertEqual(len(selected_data.get_nodes_name()) == 3, True)

    def test_data_domain_keep_original_order(self):
        """
        Test the order in domain object is in same order with 
        original raw data.
        """
        df = self.data.get_pandas_df()
        domain = self.data.get_domain()
        cols = domain.keys()
        self.assertEqual(cols == list(df.columns.values), True)


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
        self.edges = self.dep_graph.get_dep_edges()
        self.nodes = self.data.get_nodes_name()

    def test_junction_tree_with_one_clique(self):
        """
        The dependency graph is a complete graph, 
        so there is only one clique in the junction tree
        """
        jtree = JunctionTree(self.edges, self.nodes)
        cliques = jtree.get_jtree(display = True)
        self.assertEqual(len(cliques) == 1, True)
