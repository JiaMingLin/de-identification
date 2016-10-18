import common.constant as c
import numpy as np
import pandas as pd

from common.base import *
from itertools import product
from operator import itemgetter
from time import time

class HistogramddDist(Base):
	def __init__(self, data, partitions_num = 120):
		self.LOG = Base.get_logger("HistogramddDist")
		self.data = data
		self.data.coalesce(partitions_num)
		
		self.df = data.get_df()
		self.domain = data.get_domains()
		
		
	
	def get_levels(self, col_names):
		return itemgetter(*col_names)(self.domain)
	
	def get_aggregated_count(self, df, clique):
		agg_cnt = df.groupby(*clique).agg({'*':'count'}).toPandas()
		if len(agg_cnt.index) > 1000000:
			raise Exception('There are more than 1M combinations in the clique: %s, please consider to drop some features or make data coarse' % str(clique))
		return agg_cnt
	
	def fill_empty(self, agg_cnt):
		col_names = agg_cnt[0]
		agg_cnt_df = agg_cnt[1]
		levels = self.get_levels(col_names)
		if len(col_names) == 1:
			return agg_cnt_df
		empty_full_df = pd.DataFrame(list(product(*levels)), columns = col_names)
		full_histograms = pd.merge(empty_full_df, agg_cnt_df, on = col_names, how='left').fillna(0)
		return full_histograms
	
	def histogram_dist(self, cliques):
		self.LOG.info("HistogramddDist starting...")
		t1 = time()
		agg_cnt_dfs = [(clique, self.get_aggregated_count(self.df,clique)) for clique in cliques]
		filled_ct = [self.fill_empty(agg_cnt) for agg_cnt in agg_cnt_dfs]
		self.LOG.info("HistogramddDist complete in %d sec." % (time() - t1))
		return filled_ct