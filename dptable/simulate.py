from common.base import *
from rpy2.robjects import pandas2ri

from time import time

class Simulate(Base):
	def __init__(self, model, nrows):
		self.model = model
		self.nrows = nrows
		self.LOG = Base.get_logger("Simulate")
	
	def run(self):
		self.LOG.info("Starting to simulate data...")
		t1 = time()
		simulate = self.get_r_method(c.SIMULATE_R_FILE, 'simulate')
		sim_data = simulate(self.model, self.nrows)
		pandas_df = pandas2ri.ri2py_dataframe(sim_data)
		self.LOG.info("Data simulation complete in %d sec." % (time() - t1))
		return pandas_df.astype(int, copy=False)
