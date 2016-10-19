from common.base import *
from rpy2.robjects import pandas2ri

class Simulate(Base):
	def __init__(self, model, nrows):
		self.model = model
		self.nrows = nrows
	
	def run(self):
		simulate = self.get_r_method(c.SIMULATE_R_FILE, 'simulate')
		sim_data = simulate(self.model, self.nrows)
		pandas_df = pandas2ri.ri2py_dataframe(sim_data)
		return pandas_df.astype(int, copy=False)
