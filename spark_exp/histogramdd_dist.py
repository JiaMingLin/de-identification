import common.constant as c
import numpy as np
import pandas as pd

from common.base import *
from dptable.stats_functions import StatsFunctions
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
		self.stats_func = StatsFunctions()
		
	def histogram_dist(self, cliques):
		
		method = lambda df, clique: df.groupby(*clique).agg({'*':'count'}).toPandas()
		hists = self.stats_func.histogramdd_batch(self.data, cliques, method)
		return hists