import numpy as np
import common.constant as c

from common.base import *
from itertools import combinations
from time import time

from base_func_dist import FunctionDist

class DepGraphDist(Base):
	def __init__(self, 
			data, 
			eps1 = 1.0, 
			threh = 0.2, 
			batch_size = 500, 
			partitions = 120):
		
		self.LOG = Base.get_logger("DepGraphDist")
		self.data = data
		self.eps1 = eps1
		self.threh = threh
		self.batch_size = batch_size
		self.partitions = partitions
		self.beta = 1
	
	def fit(self):
		self.data.coalesce(self.partitions)		
		df = self.data.get_df()
		domains = self.data.get_domains()
		self.nrow = self.data.get_nrows()
		
		features = sorted(domains.keys())
		ncols = len(features); index = range(len(features))
		
		batch = self.get_attrs_batch(index)

		def g_test(iterable):
			import itertools
			import pandas as pd
			import numpy as np

			pair_cnts = np.asarray(list(iterable))
			if len(pair_cnts) < 1: return iter([])

			pair_attrs = pair_cnts[:, 0][0]
			lv_cnts = pair_cnts[:, 1]

			agg = lambda g: sum(np.asarray(list(g))[:, 2])
			grp_sort_keyfunc = lambda e: [e[0], e[1]]

			_sorted = sorted(lv_cnts, key = lambda e: grp_sort_keyfunc(e))
			agg_lv_cnt = [[k[0], k[1], agg(g)] for k,g in itertools.groupby(_sorted, lambda e: grp_sort_keyfunc(e))]

			attr1_lvs = np.unique((np.asarray(agg_lv_cnt)[:,0]))
			attr2_lvs = np.unique((np.asarray(agg_lv_cnt)[:,1]))

			def get_fill_cnt(attr2_grp):
				from collections import OrderedDict
				grp_lv_cnt = np.asarray(attr2_grp)[:, [1,2]]
				full_cnt = OrderedDict(zip(list(attr2_lvs), np.zeros(len(attr2_lvs), dtype=int)))
				full_cnt.update(dict(grp_lv_cnt))
				return full_cnt.values()

			df = pd.DataFrame(agg_lv_cnt, columns = ['a1', 'a2', 'count'])
			contingency_tab = np.asarray([get_fill_cnt(df[df['a1'] == val]) for val in attr1_lvs])
			# expected sum
			def get_expected_sum(xmat):
				rsums = np.sum(xmat, axis = 0).reshape(-1,1)
				csums = np.sum(xmat, axis = 1).reshape(1,-1)
				expected_sum = rsums * csums / float(np.sum(csums))
				return expected_sum

			# mutual information
			def get_mi(xmat):
				xmat = xmat / float(np.sum(xmat))
				expected_sum = get_expected_sum(xmat)
				summand = xmat/expected_sum.T
				zeros = np.where(summand == 0)
				summand[zeros] = 1
				return np.sum(xmat * np.log(summand))
			
			mi = get_mi(contingency_tab)
			#exp_sum = get_expected_sum(contingency_tab)
			#chi2 = np.sum((contingency_tab.T - exp_sum) ** 2 / exp_sum)
			#CV = np.sqrt(chi2 / (np.sum(contingency_tab) * (min(len(attr1_lvs), len(attr2_lvs)) - 1)))
			min_length = min(len(attr1_lvs), len(attr2_lvs)) - 1
			return iter([(pair_attrs, min_length, mi)])

		def pair_func_cnt(iterable, pairs):
			import itertools
			import pandas as pd
			import numpy as np
			result = []

			pandas_df = pd.DataFrame(list(iterable))
			nrows = len(pandas_df)

			for p1, p2 in pairs:
				sub_val = zip(pandas_df[p1].tolist(), pandas_df[p2].tolist())
				sub_val = sorted(sub_val, key = lambda p: p)
				grped_cnt = [((p1, p2), [k[0], k[1], len(list(g))]) for k, g in itertools.groupby(sub_val, lambda p: p)]
				result += grped_cnt

			return iter(result)
		batch_size = self.batch_size
		
		mi_collections = []
		self.LOG.info("DepGraphDist starting...")
		t1 = time()
		for one_round in batch:
			#
			pair_count = df.mapPartitions(lambda iterable: pair_func_cnt(iterable, one_round)) \
						.repartitionAndSortWithinPartitions(
							batch_size, 
							lambda e: (((2 * ncols -1 -e[0]) * e[0]) / 2 + (e[1] - e[0]) -1 ) % batch_size
						) \
						.mapPartitions(g_test)
			mi_collections += pair_count.collect()
		filtered = self.filter_association(mi_collections, features)
		self.LOG.info("Dependency calculate complete in %d sec." % (time() - t1))
		return filtered
		
	def get_attrs_batch(self, attrs):
		# drop those attributes with empty name
		attrs = [a for a in attrs if len(str(a)) > 0 ]
		# the set of all pair attributes combinations
		comb_attrs = list(combinations(attrs, 2))
		stairs = np.arange(0, len(comb_attrs), step = self.batch_size)
		return [comb_attrs[left:left+self.batch_size] for left in stairs]
	
	def filter_association(self, collect, features):
		mi_scale = self.compute_mi_scale()
		noise_thresh_cv2 = np.random.laplace(0, mi_scale, 1)
		
		filtered_collect = []
		for pair in collect:
			attr_indexes = pair[0]
			min_length = pair[1]
			mi = pair[2]
			
			cv2_lh = mi + np.random.laplace(0, mi_scale, 1)
			cv2_rh = (self.threh ** 2) * min_length/2. + noise_thresh_cv2
			if cv2_lh >= cv2_rh:
				filtered_collect += [(features[attr_indexes[0]], features[attr_indexes[1]])]
		return filtered_collect
		
	def compute_mi_scale(self):
		eps_alpha_1 = self.amplify_epsilon_under_sampling(self.eps1, self.beta)
		sensitivity_scale_mi = self.compute_mi_sensitivity_scale(self.nrow, False)
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