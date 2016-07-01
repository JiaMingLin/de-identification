import logging
import rpy2.robjects as robjects

class Base(object):

	logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
	from rpy2.robjects import pandas2ri
	pandas2ri.activate()

	def get_r_method(self, r_file, method_name):
		r = robjects.r
		r.source(r_file)
		r_method = r[method_name]
		return r_method

	def convert2rlistofvector(self, groups):
		return [robjects.StrVector(grp) for grp in groups]

