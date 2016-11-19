import logging
import rpy2.robjects as robjects
from logging.handlers import TimedRotatingFileHandler

import ast
import collections
import os
import common.constant as c

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

	def get_str_obj(self, str_obj):
		if isinstance(str_obj, str):
			return ast.literal_eval(str_obj)
		return str_obj

	def convert_selected_attrs(self, attrs_ls):
		attrs_ls = ast.literal_eval(str(attrs_ls))
		return collections.OrderedDict(zip(attrs_ls['names'], attrs_ls['types']))
	
	def combine_cliques_for_query(self, jtree_cliques, merged_cliques):
		jtree_cliques = [sorted(clique) for clique in jtree_cliques]
		merged_cliques = [sorted(clique) for clique in merged_cliques]
		comb = []
		for e in jtree_cliques + merged_cliques:
			if e not in comb:
				comb += [e]
		return comb

	def save_merged_jtree(self, task_id, eps1_level, jtree):
		parent = c.MEDIATE_DATA_DIR % {'task_id': task_id}
		if not os.path.exists(parent):
			os.makedirs(parent)

		file_name = 'jtree_eps1_%d.display' % eps1_level
		file_path = os.path.join(parent, file_name)
		with open(file_path, 'w+') as jtree_file:
			jtree_file.write(str(jtree))
		return file_path

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

class ProcessStatus():

	@staticmethod
	def get_code(str_name):
		mappings = dict({
			'WAITTING':0,
			'PENDING':1,
			'PROGRESS':2,
			'SUCCESS':3,
			'REVOKED':4,
			'FAILURE':5
		})
		return mappings[str_name]

	@staticmethod
	def get_name(code):
		mappings = dict({
			'WAITTING':0,
			'PENDING':1,
			'PROGRESS':2,
			'SUCCESS':3,
			'REVOKED':4,
			'FAILURE':5
		})
		reverse = dict(zip(mappings.values(), mappings.keys()))
		return reverse[code]