import collections
import numpy as np
from django.test import TestCase
from dptable.variance_reduce import VarianceReduce


class TestDPTable(TestCase):

	def setUp(self):
		self.domain = collections.OrderedDict([
			('A', [1,2,3,4,5,6,7,8]),
			('B', [2,3,4,5,6,7,8,9]),
			('C', [3,4,5,6,7,8,9,0]),
			('D', [4,5,6,7,8,9,0,1]),
			('E', [5,6,7,8,9,0,1,2]),
			('F', [6,7,8,9,0,1,2,3]),
			('G', [7,8,9,0,1,2,3,4])
			])
		self.jtree = [
			['A','B','C'],
			['B','C','D'],
			['C','D','E'],
			['D','E','F'],
			['E','F','G']
		]
		self.cnum = [2,3,4,5]
		self._lambda = 0.2
		self.var_reduce = VarianceReduce(self.domain, self.jtree, self.cnum, self._lambda)

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
		self.assertEqual(log_sum_by_clique[0] == 6.2383246250395068, True)

	def test_main_func(self):
		print self.var_reduce.main()
