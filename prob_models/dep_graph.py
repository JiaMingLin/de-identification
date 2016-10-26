import common.constant as c
import time
import numpy as np
import pandas as pd

from common.base import Base
from itertools import combinations
from itertools import groupby


class DependencyGraph(Base):
	
	# The dependency graph
	dep_graph = None

	def __init__(
		self, 
		data = None, 
		edges = None, 
		noise_flag = True, 
		white_list = [], 
		eps1_val = c.EPSILON_1, 
		cramer = 0.2):
		"""
		__init__
		Input:
			1. DataUtils.Data
		Procedure
			1. Convert the given data frame to dataframe in R
			2. Convert the given Domain(in python dict) to ListVector
			3. Instantial the attributes dependency.
		"""
		self.LOG = Base.get_logger("DepGraph")
		self.noise_flag = noise_flag
		self.eps1_val = eps1_val
		self.cramer = cramer
		self.data = data
		if data is None:
			self.edges = edges
		else:
			self.edges = self._run()

		self.white_list = white_list



	def get_dep_edges(self, display = True):
		pairwise_white_list = reduce(lambda acc, curr: acc+curr
									,[list(combinations(cluster, 2)) for cluster in self.white_list]
									,[])
		if display is False:
			return _get_edges_in_r(self.edges + pairwise_white_list)
		return self.edges + pairwise_white_list

	def set_white_list(self, white_list):
		self.white_list = white_list
		return self

	def _run(self):
		# get pandas df
		if self.data is None:
			raise Exception("The data is not specified.")
		pandas_df = self.data.get_df()
		# get domain
		domains = self.data.get_domains()

		self.LOG.info("Starting to compute Dep-Graph with eps1: %.2f..." % self.eps1_val)
		start = time.time()

		# attributes' name
		attr_names = domains.keys()

		# combinations of 2
		comb = combinations(attr_names, 2)

		mi_scale = self.compute_mi_scale()
		noise_thresh_cv2 = np.random.laplace(0, mi_scale, 1)

		filtered_pairs = []
		for attrs_pair in comb:
			col1_val = pandas_df[attrs_pair[0]]
			col2_val = pandas_df[attrs_pair[1]]
			if self.g_test(col1_val, col2_val, mi_scale, noise_thresh_cv2):
				filtered_pairs += [attrs_pair]

		end = time.time()
		self.LOG.info("Compute Dep-Graph complete in %d seconds." % (end-start))
		return filtered_pairs

	def g_test(self, col1, col2, mi_scale, noise_thresh_cv2):
		xmat = self.find_crosstab(col1, col2)
		mi = self.get_mi(xmat)
		attr1_lvs = sorted(set(col1))
		attr2_lvs = sorted(set(col2))
		min_length = min(len(attr1_lvs), len(attr2_lvs)) - 1

		cv2_lh = mi + np.random.laplace(0, mi_scale, 1)
		cv2_rh = (self.cramer ** 2) * min_length/2. + noise_thresh_cv2
		return cv2_lh >= cv2_rh

	def find_crosstab(self, col1, col2):
		xtab = pd.crosstab(col1, col2)
		return np.asarray(xtab)

	def get_expected_sum(self, xmat):
		rsums = np.sum(xmat, axis = 0).reshape(-1,1)
		csums = np.sum(xmat, axis = 1).reshape(1,-1)
		expected_sum = rsums * csums / float(np.sum(csums))
		return expected_sum

	def get_mi(self, xmat):
		xmat = xmat / float(np.sum(xmat))
		expected_sum = self.get_expected_sum(xmat)
		summand = xmat/expected_sum.T
		zeros = np.where(summand == 0)
		summand[zeros] = 1
		return np.sum(xmat * np.log(summand))

	def compute_mi_scale(self):
		eps_alpha_1 = self.amplify_epsilon_under_sampling(self.eps1_val)
		sensitivity_scale_mi = self.compute_mi_sensitivity_scale(self.data.get_nrows(), False)
		scale_mi = 2 * sensitivity_scale_mi / eps_alpha_1
		return scale_mi
	
	def amplify_epsilon_under_sampling(self, eps1, beta = 1):
		eps_alpha = np.log(np.exp(1) ** (eps1) -1 + beta) - np.log(beta)
		return eps_alpha
	
	def compute_mi_sensitivity_scale(self, N, all_binary):
		N = float(N)
		if all_binary is True:
			sen_scale = (1/N) * np.log(N) + (( N-1 )/N) * np.log(N/(N-1))
		else:
			sen_scale = (2/N) * np.log((N + 1)/2) + ((N-1)/N) * np.log((N+1)/(N-1))
		return sen_scale