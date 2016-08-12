import time
import collections
import pandas as pd
import numpy as np
import random as rand
import common.constant as c
from common.base import Base
from numpy import linspace, searchsorted, diff


class DataUtils(Base):

	
	def __init__(self, file_path = None , pandas_df = None, selected_attrs = None, valbin_maps = None):
		"""
		Parameter
			file_path:
				the path of original data
			selected_attrs:
				{
					"A":"C",
					"B":"D",...
				}			
		"""
		self.LOG = Base.get_logger("DataUtils")
		self.valbin_maps = dict() if valbin_maps is None else valbin_maps
		self.dataframe = self._loading(file_path, pandas_df)

		if(selected_attrs != None):
			self.selected_attrs = selected_attrs
			self.dataframe = self.dataframe[selected_attrs.keys()]

		self.preview_count = 5
		

	def _loading(self, file_path, pandas_df):
		if pandas_df is None:			
			self.LOG.info("Reading dataframe from file...")

			start = time.time()
			pandas_df = pd.read_csv(file_path)
			end = time.time()
			self.LOG.info("Reading dataframe from file complete in %d seconds." % (end-start))

		self.LOG.info("Reading dataframe from cache...")
		return pandas_df

	def data_preview(self, format = None):
		self.LOG.info("Preview data")
		sub_df = self.dataframe[:self.preview_count]
		return sub_df

	def get_pandas_df(self):
		return self.dataframe

	def get_domain(self):
		self.LOG.info("Get data domain")
		domain = collections.OrderedDict((pair[0], list(set(pair[1]))) for pair in collections.OrderedDict(self.dataframe).items())
		return domain

	def get_nodes_name(self):
		return list(self.dataframe.columns.values)

	def get_valbin_maps(self):
		return self.valbin_maps

	def save(self, path):
		self.dataframe.to_csv(path, index=False)

	def data_coarsilize(self):
		df = self.dataframe
		
		self.LOG.info("Data coarsilizing...")
		for (attr_name, attr_type) in self.selected_attrs.items():
			self.LOG.debug("Coarsilizing for (%s, %s)" % (attr_name, attr_type))
			col = df[attr_name]
			unique_vals = list(col.unique())
			if attr_type == 'D':
				sorted_uniques = sorted(unique_vals)
				df[attr_name] = self._discrete_parser(col, sorted_uniques)
			elif attr_type == 'C':
				df[attr_name] = self._continue_parser(col)
		self.dataframe = df

	def data_generalize(self):

		self.LOG.info("Data generalizing...")
		df = self.dataframe
		for (attr_name, attr_type) in self.selected_attrs.items():
			col = df[attr_name]
			unique_vals = list(col.unique())
			if attr_type == 'D':
				df[attr_name] = self._discrete_generalizer(col)
			elif attr_type == 'C':
				df[attr_name] = self._continue_generalizer(col)
		self.dataframe = df


	def _discrete_generalizer(self, coarsed_col):

		self.LOG.debug("Data generalizing for discrete column: %s" % (coarsed_col.name))
		mapping = self.valbin_maps[coarsed_col.name]
		reversed_map = dict(zip(mapping.values(), mapping.keys()))
		return coarsed_col.map(reversed_map)


	def _continue_generalizer(self, coarsed_col):
		self.LOG.debug("Data generalizing for continuous column: %s" % (coarsed_col.name))
		edges = self.valbin_maps[coarsed_col.name]
		dedges = diff(edges)
		dedges = np.append(dedges, [dedges[-1]])
		generalizer = lambda coarse_val: int(np.round((edges[coarse_val-1] + edges[coarse_val]) / 2.0, 2) * 100) / 100.0
		#generalizer = lambda coarse_val: rand.uniform(edges[coarse_val-1], edges[coarse_val-1]+dedges[coarse_val])
		return coarsed_col.apply(generalizer)

	def _discrete_parser(self, col, unique_vals):
		self.LOG.debug("Parse discrete data (%s, %d)" % (col.name, len(unique_vals)))

		reverse_mapping = dict([(item[1], item[0]) for item in enumerate(unique_vals)])
		self.valbin_maps[col.name] = reverse_mapping
		return col.map(reverse_mapping)

	def _continue_parser(self, col):
		D = c.MAX_BIN_NUMBER
		smax = max(col)+.5; smin = min(col)-.5
		edges = []
		uniques = col.unique()
		if len(uniques) > D:
			edges = linspace(smin, smax, D+1)
		else:
			edges = col.unique()

		self.LOG.debug("Parse continous data (column name, max, min, bins) (%s, %0.1f, %0.1f, %d)" % (col.name, smax, smin, len(edges)))

		self.valbin_maps[col.name] = list(edges)
		Ncount = searchsorted(edges, list(col), 'right')
		return pd.Series(Ncount)