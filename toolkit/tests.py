from django.test import TestCase

from data_utilities import DataUtils
from dep_graph import DependencyGraph

TESTING_FILE = 'desktop/static/testing_row_data.csv'

class DataUtilitiesTests(TestCase):
    def test_data_preview(self):
        data = DataUtils(TESTING_FILE)
        preview = data.data_preview()
        self.assertEqual(len(preview.values[0]) > 0, True)

class DependencyGraphTests(TestCase):

    def setUp(self):
        self.data = DataUtils(TESTING_FILE)

    def test_dep_graph_edges_length_is_6(self):
        dep_graph = DependencyGraph(self.data)
        edges = dep_graph.get_dep_edges(display = True)
        self.assertEqual(len(edges) == 6, True)
