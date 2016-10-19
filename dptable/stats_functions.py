import common.constant as c
import itertools
import pandas as pd

from common.base import *
from itertools import product
from operator import itemgetter
from time import time

class StatsFunctions(Base):
	def __init__(self):
		self.LOG = Base.get_logger("StatsFunctions")

		
	
	def histogramdd_batch(self, data, cliques, agg_cnt_method = None):
		df = data.get_df()
		domains = data.get_domains()
		def get_levels(col_names):
			return itemgetter(*col_names)(domains)

		def get_aggregated_count(df, agg_cnt_method, clique):
			#agg_cnt = df.groupby(*clique).agg({'*':'count'}).toPandas()
			if agg_cnt_method is None:
				agg_cnt_method = lambda df, clique: pd.DataFrame({'count(1)' : df.groupby(clique).size()}).reset_index()

			agg_cnt = agg_cnt_method()
			agg_cnt.columns = clique + ["freq"]

			if len(agg_cnt.index) > 1000000:
				raise Exception('There are more than 1M combinations in the clique: %s, please consider to drop some features or make data coarse' % str(clique))
			return agg_cnt

		def fill_empty(agg_cnt):
			col_names = agg_cnt[0]
			agg_cnt_df = agg_cnt[1]
			levels = get_levels(col_names)
			if len(col_names) == 1:
				return agg_cnt_df
			empty_full_df = pd.DataFrame(list(product(*levels)), columns = col_names)
			full_histograms = pd.merge(empty_full_df, agg_cnt_df, on = col_names, how='left').fillna(0)
			return full_histograms

		self.LOG.info("Histogramdd starting...")
		t1 = time()
		agg_cnt_dfs = [(clique, get_aggregated_count(df, agg_cnt_method ,clique)) for clique in cliques]
		filled_ct = [fill_empty(agg_cnt) for agg_cnt in agg_cnt_dfs]
		self.LOG.info("Histogramdd complete in %d sec." % (time() - t1))
		return filled_ct

	def histogramdd(self, data, clique, agg_cnt_method = None):
		return self.histogramdd_batch(data, [clique])

	

	



