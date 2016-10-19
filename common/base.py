import logging
import rpy2.robjects as robjects
from logging.handlers import TimedRotatingFileHandler

import ast
import collections
import os
import common.constant as c

spark_home = os.environ['SPARK_HOME']
if len(spark_home) > 0:
	from common.importer import *
r = robjects.r
r.source(c.INIT_LIB_R_FILE)

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

	def get_jtree_file_path(self, task_id, eps1_level):
		folder = c.MEDIATE_DATA_DIR % {'task_id': task_id}
		file_name = 'jtree_eps1_%d.rds' % eps1_level
		return os.path.join(folder, file_name)

	def create_task_folder(self, task_id):
		folder = c.MEDIATE_DATA_DIR % {'task_id': task_id}
		if not os.path.exists(folder):
			os.makedirs(folder)
		return folder

	def is_pre_process_skip(self, request, instance, create_flag):
		# when update, 
		# if attributes spec, data path, change then redo pre-processing
		if create_flag is True:
			return False

		if not isinstance(instance, dict):
			tmp = dict()
			tmp['data_path'] = instance.data_path
			tmp['selected_attrs'] = instance.selected_attrs
			instance = tmp

		# compare data path
		if request['data_path'] != instance['data_path']:
			return False

		# compare selected attributes
		selected_attrs_request = self.convert_selected_attrs(request['selected_attrs'])
		selected_attrs_original = self.convert_selected_attrs(instance['selected_attrs'])

		if sorted(selected_attrs_request.items(), key=lambda x: x[0]) != sorted(selected_attrs_original.items(), key=lambda x: x[0]):
			return False

		return True

	def convert_selected_attrs(self, attrs_ls):
		attrs_ls = ast.literal_eval(str(attrs_ls))
		return collections.OrderedDict(zip(attrs_ls['names'], attrs_ls['types']))

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
