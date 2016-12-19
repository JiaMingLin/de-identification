import collections
import numpy as np
from django.test import TestCase
from dptable.variance_reduce import VarianceReduce


class TestDPTable(TestCase):

	def setUp(self):
		self.domain = collections.OrderedDict([
			('A', [22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85]), 
			('B', [137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200]), 
			('C', [45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108]), 
			('D', [20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140]), 
			('E', [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60]), 
			('F', [0, 1]), 
			('G', [0, 1])])

		self.jtree = dict({
			'parents': [0, 1, 0, 0, 0], 
			'separators': [[], ['F'], [], [], []], 
			'cliques': [['F', 'B'], ['F', 'C'], ['D', 'E'], ['A'], ['G']]
		})
		self._lambda = 0.2
		self.var_reduce = VarianceReduce(self.domain, self.jtree['cliques'], self._lambda)

	def test_different_matrix_constructor_with_zero_result(self):
		diff_operator = self.var_reduce.construct_difference(4)
		ones_4 = [1,1,1,1]
		result = np.dot(ones_4, diff_operator)
		self.assertEqual(np.sum(np.square(result)) == 0, True)

	def test_jtree_matrix_rep_with_chain_structure(self):
		print self.var_reduce.jt_rep()

	def test_extract_index_of_subset_of_node(self):
		nodes_subset = ['A', 'D', 'B']
		nodes_index = self.var_reduce.find_subset_index(nodes_subset)
		self.assertEqual(nodes_index == [0,3,1], True)

	def test_log_p_func_with_specific_log_sum(self):
		log_sum_by_clique = self.var_reduce.log_p_func()
		self.assertEqual(log_sum_by_clique[0] - 7.20340552108 < 1e-10, True)

	def test_main_func(self):
		opted_cluster = self.var_reduce.main()
		print opted_cluster
