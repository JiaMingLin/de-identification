import logging
import rpy2.robjects as robjects

import os
import common.constant as c

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

	def get_jtree_file_path(self, task_id):
		folder = c.MEDIATE_DATA_DIR % {'task_id': task_id}
		return os.path.join(folder, 'jtree.rds')

	def create_task_folder(self, task_id):
		folder = c.MEDIATE_DATA_DIR % {'task_id': task_id}
		if not os.path.exists(folder):
			os.makedirs(folder)
		return folder