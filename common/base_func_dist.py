import itertools
import pandas as pd
import numpy as np

class FunctionDist():
	@staticmethod
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
	
	@staticmethod
	def g_test(iterable):
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
		def get_mi(xtab):
			pass
				
		exp_sum = get_expected_sum(contingency_tab)

		chi2 = np.sum((contingency_tab.T - exp_sum) ** 2 / exp_sum)
		CV = np.sqrt(chi2 / (np.sum(contingency_tab) * (min(len(attr1_lvs), len(attr2_lvs)) - 1)))
		return iter([CV])