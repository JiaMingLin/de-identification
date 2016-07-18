import logging
import rpy2.robjects as robjects
from logging.handlers import TimedRotatingFileHandler

import os
import common.constant as c

class Base(object):

	logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s \t %(levelname)s \t %(message)s')

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

	@staticmethod
	def get_logger(name):
		# TODO: The logger would be returned multiple instances as this method called.
		formatter = logging.Formatter("%(asctime)s - %(name)s \t %(levelname)s \t %(message)s")
		handler = TimedRotatingFileHandler(
			c.LOG_FILE_PATH,
			when="midnight"
		)
		handler.setFormatter(formatter)

		logger = logging.getLogger(name)
		logger.addHandler(handler)
		return logger
