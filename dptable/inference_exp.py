from common.base import *
from rpy2.robjects import pandas2ri

import common.constant as c
import pandas.rpy.common as com
import rpy2.robjects as ro
import rpy2.rlike.container as rlc
import time

class InferenceExp(Base):
	def __init__(self, data, jtree_path, domain, cluster, epsilon = 0.0):
		
		self.LOG = Base.get_logger("InferenceExp")
		self.data = self.convert2rdataframe(data)
		self.data_size = data.get_count()
		self.epsilon = epsilon
		self.rdomain = self.convert2rdomain(domain)
		self.cluster = self.convert2rlistofvector(cluster)
		self.jtree_path = jtree_path

	def execute(self):
		do_inference = self.get_r_method(c.INFERENCE_R_FILE, 'do_inference')
		
		self.LOG.info("Starting to do inferences...")
		start = time.time()
		model = do_inference(c.R_SCRIPT_PATH, self.cluster, self.jtree_path, self.epsilon, self.data, self.rdomain)
		end = time.time()
		self.LOG.info("Doing inferences complete in %d seconds." % (end-start))

		sim = Simulate(model, self.data_size)
		sim_data = sim.run()

		#pandas_df = pandas2ri.ri2py_dataframe(sim_data)
		#return pandas_df.astype(int, copy=False)

	def execute_without_noise(self):
		do_inference_without_noise = self.get_r_method(c.INFERENCE_R_FILE, 'do_inference_without_noise')

		model = do_inference_without_noise(c.R_SCRIPT_PATH, self.cluster, self.jtree_path, self.data, self.rdomain)

		sim = Simulate(model, self.data_size)
		sim_data = sim.run()
		#pandas_df = pandas2ri.ri2py_dataframe(sim_data)
		return pandas_df.astype(int, copy=False)

	def convert2rdataframe(self, data):
		return com.convert_to_r_dataframe(data.get_pandas_df())

	def convert2rdomain(self, domain):
		
		rname = domain.keys()
		rlevels = ro.ListVector([(item[0], ro.IntVector(item[1])) for item in domain.items()])
		rdsize = ro.ListVector([(item[0], len(item[1])) for item in domain.items()])

		rdomain = ro.ListVector([
			('name', rname),
			('levels', rlevels),
			('dsize', rdsize)
		])
		return rdomain

class Simulate(Base):
	from pyspark.sql import Row
	def __init__(self, model, size):
		self.model = model
		self.size = size

	def run(self):
		
		# broadcast the simulate R function obj
		simulate = self.get_r_method(c.SIMULATE_R_FILE, 'simulate')
		br_sim = sc.broadcast(simulate)

		# broadcast the size
		br_size = sc.broadcast(self.size / partition_num)

		# broadcast model
		br_model = sc.broadcast(self.model)
		
		def parallelize_sim(iterable):
			# get size
			partial_size = br_size.value

			# get model
			model = br_model.value

			# get simulate R function
			sim_func = br_sim.value

			partial_df = sim_func(model, partial_size)
			partial_df = pandas2ri.ri2py_dataframe(partial_df)
			return iter(partial_df.to_dict('record'))

		# make parallelize operation
		sim_data = sc.parallelize(range(partition_num), partition_num).mapPartitions(parallelize_sim).toDF()
		print sim_data.count()