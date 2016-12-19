from common.base import *
from rpy2.robjects import pandas2ri

import common.constant as c
import pandas.rpy.common as com
import rpy2.robjects as ro
import rpy2.rlike.container as rlc
from time import time

class SimulateDist(Base):
	from pyspark.sql import Row
	def __init__(self, model, nrows):
		self.LOG = Base.get_logger("SimulateDist")
		self.model = model
		self.nrows = nrows

	def run(self):
		
		# broadcast the simulate R function obj
		simulate = self.get_r_method(c.SIMULATE_R_FILE, 'simulate')
		
		t1 = time()
		self.LOG.info("SimulateDist starting...")
		br_sim = sc.broadcast(simulate)

		# broadcast the size
		br_size = sc.broadcast(self.nrows / partition_num)

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
		self.LOG.info("Data simulation complete in %d sec." % (time() - t1))
		
		return sim_data