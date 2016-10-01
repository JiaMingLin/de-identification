import re
import numpy as np

from common.base import *
from time import time


class DataDist(Base):
	"""
	read data to spark dataframe, now we only support parquet file.

	Parameters:

		domains: string
			The path to domains file on local disk.
	 
	 	data_path: string
			The path to the data. data_path and dataframe can not be specified or None at the same time.

		dataframe: spark dataframe
			The spark dataframe. data_path and dataframe can not be specified or None at the same time.
	"""
	def __init__(self, domains_path, data_path = None, dataframe = None):
		
		if (data_path is None and dataframe is None) or (data_path is not None and dataframe is not None):
			raise Exception('The data_path and dataframe can not be specified or None at the same time')

		self.LOG = Base.get_logger("DataDist")
		self.domains = self.read_domain(domains_path)

		t1 = time()
		self.LOG.info("Starting to loading data...")
		if dataframe is None:
			self.data_path = data_path
			self.dataframe = sqlContext.read.format('com.databricks.spark.csv').options(header='true', inferschema='true').load(data_path)
		else:
			self.dataframe = dataframe

		self.LOG.info("Data has been loaded in %d sec.!!!" % (time() - t1))

		"""
		t1 = time()
		self.LOG.info("Coalesce data starting...")
		self.dataframe = self.dataframe.coalesce(partitions)
		self.dataframe.persist()
		self.nrow = self.dataframe.count()
		self.LOG.info("Coalesce data complete in %d sec." % (time() - t1))
		"""

	def get_df(self):
		return self.dataframe
	"""
	def get_nrow(self):
		return self.nrow
	"""
	
	def get_domain(self):
		return self.domains

	def read_domain(self, domains_path):
		def readlinesplit(line):
			return re.split('\s+', line.strip())

		def readdomain(line):
			splited_line = readlinesplit(line)
			#return (splited_line[0], splited_line[1], splited_line[2], list(np.asarray(splited_line[3:], dtype=int)))
			return (splited_line[0], list(np.asarray(splited_line[3:], dtype=int)))

		domains = []

		with open(domains_path, 'r') as f:
			first = readlinesplit(f.readline())
			ncol = first[0]; nrow = first[1]
			for line in f:
				domains.append(readdomain(line))

		return dict(domains)
