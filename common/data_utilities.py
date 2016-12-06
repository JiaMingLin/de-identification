import time
import collections
import pandas as pd
import numpy as np
import random as rand
import common.constant as c
from common.base import Base
from datetime import datetime
from numpy import linspace, searchsorted, diff, bincount


class DataUtils(Base):

	
	def __init__(
		self, 
		file_path = None, 
		selected_attrs = None, 
		pandas_df = None, 
		valbin_maps = None, 
		names=None, 
		specified_c_domain = None,
		chunk_size = -1,
		date_format = None
		):
		""" Loading data to warpped python object

		Parameters
		----------
			file_path: string
				The path of original data
			selected_attrs: dict
				{
					"A":"C",
					"B":"D",
					...
				}
			pandas_df: Pandas dataframe
				Initialize with a pandas dataframe(TODO: deprecated)
			valbin_maps: dict
				A mapping of original values with coarse value
			names: list, experiment
				A list to specifiy the attributes' names when the input file has no header
			specified_c_domain: dict, experiment
				A mapping of continuous type attributes with the specified edges in coarse
		"""
		self.LOG = Base.get_logger("DataUtils")
		self.valbin_maps = dict() if valbin_maps is None else valbin_maps
		self.chunk_size = chunk_size
		if chunk_size > 0:
			self.dataframe = self._loading_chunk(file_path, pandas_df, names)
		else:
			self.dataframe = self._loading(file_path, pandas_df, names)

		if selected_attrs is not None:
			self.selected_attrs = selected_attrs
			# the 'selected_attrs' is ordered
			self.dataframe = self.dataframe[selected_attrs.keys()]

		self.preview_count = 5
		self.specified_c_domain = specified_c_domain
		self.date_format = date_format
		

	def _loading(self, file_path, pandas_df, names = None):
		if pandas_df is None:			
			self.LOG.info("Reading dataframe from file...")

			start = time.time()

			if names is not None:
				pandas_df = pd.read_csv(file_path, header = None, names = names)
			else:
				pandas_df = pd.read_csv(file_path)

			end = time.time()
			self.LOG.info("Reading dataframe from file complete in %d seconds." % (end-start))

		self.LOG.info("Reading dataframe from cache...")
		return pandas_df

	def _loading_chunk(self, file_path, pandas_df, names = None):
		if pandas_df is not None:
			self.LOG.info("Reading dataframe from cache...")
			return pandas_df

		self.LOG.info("Reading dataframe from file chunk...")
		start = time.time()
		if names is not None:
			chunks = pd.read_csv(file_path, header = None, names = names, chunksize = self.chunk_size)
		else:
			chunks = pd.read_csv(file_path, chunksize = self.chunk_size)

		for chunk in chunks:
			pandas_df = chunk
			break

		end = time.time()
		self.LOG.info("Reading dataframe from file chunk complete in %d seconds." % (end-start))
		return pandas_df


	def data_preview(self, format = None):
		self.LOG.info("Preview data")
		sub_df = self.dataframe[:self.preview_count]
		return sub_df

	def get_df(self):
		return self.dataframe

	def get_pandas_df(self):
		self.LOG.warn("DEPRECATED: To use get_df()")
		return self.get_df()

	def get_domains(self):
		self.LOG.info("Get data domains")
		domains = collections.OrderedDict((pair[0], list(set(pair[1]))) for pair in collections.OrderedDict(self.dataframe).items())
		return domains

	def get_domain(self):
		self.LOG.warn("DEPRECATED: a typo...")
		return self.get_domains()

	def get_nodes_name(self):
		return list(self.dataframe.columns.values)

	def get_valbin_maps(self):
		return self.valbin_maps

	def get_count(self):
		return self.get_nrows()
	
	def get_nrows(self):
		return len(self.dataframe.index)

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
			elif attr_type == 'T':
				df[attr_name] = self._date_parser(col, self.date_format[attr_name])
		self.dataframe = df

	def data_generalize(self):

		self.LOG.info("Data generalizing...")
		df = self.dataframe
		for (attr_name, attr_type) in self.selected_attrs.items():
			col = df[attr_name]
			unique_vals = list(col.unique())
			if attr_type in ['D', 'T']:
				df[attr_name] = self._discrete_generalizer(col)
			elif attr_type == 'C':
				df[attr_name] = self._continue_generalizer(col)
		self.dataframe = df


	def _discrete_generalizer(self, coarsed_col):

		self.LOG.info("Data generalizing for discrete column: %s" % (coarsed_col.name))
		mapping = self.valbin_maps[coarsed_col.name]
		reversed_map = dict(zip(mapping.values(), mapping.keys()))
		return coarsed_col.map(reversed_map)


	def _continue_generalizer(self, coarsed_col):
		self.LOG.info("Data generalizing for continuous column: %s" % (coarsed_col.name))
		edges = self.valbin_maps[coarsed_col.name]
		edges = np.array(edges).astype(float)
		#
		def generalizer(coarse_val):
			if coarse_val >= len(edges) :
				return edges[-1]

			locate_val = edges[coarse_val] + edges[coarse_val-1]
			return np.round(locate_val / 2.0, 2) * 100 / 100.0

		#if len(edges) < c.MAX_BIN_NUMBER:
		#	generalizer  = lambda coarse_val: coarse_val

		#generalizer = lambda coarse_val: rand.uniform(edges[coarse_val-1], edges[coarse_val-1]+dedges[coarse_val])
		return coarsed_col.apply(generalizer)

	def _discrete_parser(self, col, unique_vals):
		self.LOG.info("Parse discrete data (column_name, domain_size) = (%s, %d)" % (col.name, len(unique_vals)))

		reverse_mapping = dict([(item[1], item[0]) for item in enumerate(unique_vals)])
		self.valbin_maps[col.name] = reverse_mapping
		return col.map(reverse_mapping)

	def _continue_parser(self, col):
		D = c.MAX_BIN_NUMBER
		smax = max(col)+.5; smin = min(col)
		edges = []
		if self.specified_c_domain is not None:
			edges = self.specified_c_domain[col.name]
		else:
			uniques = col.unique()
			if len(uniques) > D:
				edges = linspace(smin, smax, D+1)
			else:
				edges = sorted(uniques)

		self.LOG.info("Parse continous data (column name, max, min, bins) (%s, %0.1f, %0.1f, %d)" % (col.name, smax, smin, len(edges)))

		self.valbin_maps[col.name] = list(edges)
		Ncount = searchsorted(edges, list(col), 'right')
		return pd.Series(Ncount)

	def _date_parser(self, col, f):
		self.LOG.info("Parse datetime data (column_name) = (%s)" % (col.name))
		source_format = f[0]
		target_format = f[1]

		target_parser = lambda d: (datetime.strptime(str(d), source_format)).strftime(target_format)
		if target_format == 'weekday':
			target_parser = lambda d: (datetime.strptime(str(d), source_format)).weekday()
		
		col = col.apply(target_parser)
		sorted_uniques = sorted(set(col))
		return self._discrete_parser(col, sorted_uniques)

	def aggregation(self, thresh):
		self.LOG.info('minmal threshold %.2f ' % thresh)
		for (attr, mappings) in self.valbin_maps.items():
			if self.selected_attrs[attr] == 'C':
				values = self.dataframe[attr]

				self.dataframe[attr], self.valbin_maps[attr] = self.agg_on_attribute(
					values,
					thresh,
					mappings
				)


	def agg_on_attribute(self, values, thresh, interval_edges):
		agg_map = self.get_agg_map(values, thresh)
		attr_groups = list(zip(*agg_map)[1])
		value_map = dict([(e, i+1) for i, grp in enumerate(attr_groups) for e in grp ])
		new_edges = [edge for i, edge in enumerate(interval_edges) if value_map.values()[i-1] != value_map.values()[i]]
		if len(new_edges) == 0:
			new_edges = [interval_edges[0], interval_edges[-1]]

		return values.map(dict(value_map)), new_edges

	def get_agg_map(self, values, thresh):
		cnt = bincount(values)
		cnt_bins = zip(bincount(values), range(len(cnt) + 1))
		# cache the outliners' levels and sum of level countings.
		agg = 0; q = []
	
	 	#the aggregated result
		result = []

		for cnt, _bin in cnt_bins:
			if cnt <= thresh:
				# cache those level counting less than threshold
				q += [(cnt, _bin)]; agg += cnt
			else:
				if len(q) > 0:
					# if the level cache is not empty
					# the current level should aggregate with cache
					q += [(cnt, _bin)]
					agg += cnt
				else:
					result += [(cnt, [_bin], np.array([cnt]))]
			# when the sum of cached level countings large than threhold
			# trigger the aggregation and clean cache.
			if agg > thresh:
				result += [self.multi_combine(q)]
				q = []; agg = 0

		tail = self.multi_combine(q)
		if tail is not None:
			# the tail might be less than k
			if tail[0] <= thresh:
				result[-1] = self.combine_two(tail, result[-1])
			else:
				result += [tail]
		return result

	def multi_combine(self, queue):
		if len(queue) == 0: return None
		cnts = np.zeros(len(queue))
		cates = []
		for i, cnt_cate in enumerate(queue):
			cnts[i] = cnt_cate[0]
			cates += [cnt_cate[1]]
		return (sum(cnts), cates, cnts)

	def combine_two(self, tail, e):
		return (tail[0]+e[0], tail[1]+e[1], np.concatenate((tail[2], e[2]), axis = 0))