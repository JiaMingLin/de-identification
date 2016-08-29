import os
import common.constant as c

from django.test import TestCase
from api.serializers import TaskSerializer, JobSerializer

class TestFull(TestCase):

	def setUp(self):

		self.data_dir = os.path.join(c.TEST_FILE_PATH, 'exp')
		# noises
		self.privacy_levels = [1,2]

		# number of runs
		self.nrun = 2

		# test cases
		self.cases = [
			(
				"data2",
				[["Age", "Income", "TRV"]]
			)
		]

	def get_eps(self, level):
		corr = {
			1: 0.01,
			2: 0.1,
			3: 1,
			4: 10,
			5: 100
		}
		return corr[level]

	def test_full(self):
		for data_name, white_list in self.cases:
			domain = self.read_domain_file(data_name)
			self.diff_privacy(data_name, domain, self.privacy_levels, white_list = white_list)

	def diff_privacy(self, data_name, domain, eps_ls, white_list = []):
		data_input = {
			"task_name": "%s.dat" % data_name,
			"data_path": "%s/%s.dat" % (self.data_dir, data_name),
			"selected_attrs": domain,
			"white_list": white_list,
			"names": domain['names']
		}
		task_obj = None
		for i in range(self.nrun):
			task = TaskSerializer()
			if i == 0:
				task_obj = task.create(data_input)
			else:
				task_obj = task.update(task_obj, data_input)

			self.save_merged_jtree(task_obj)
			for lv in self.privacy_levels:
				privacy_input = {
					"privacy_level":lv,
					"epsilon":self.get_eps(lv),
					"task_id": task_obj.task_id,
					"exp_round":i
				}
				serializer = JobSerializer(data = privacy_input)
				if(serializer.is_valid()): serializer.save()


	def save_merged_jtree(self, task):
		task_id = task.task_id
		jtree = task.jtree_strct

		parent = c.MEDIATE_DATA_DIR % {'task_id': task_id}
		if not os.path.exists(parent):
			os.makedirs(parent)

		file_name = 'jtree.display'
		file_path = os.path.join(parent, file_name)
		with open(file_path, 'w+') as jtree_file:
			jtree_file.write(jtree)

	def read_domain_file(self, data_name):
		import re
		file_pattern = '%s.domain' % data_name
		domain_path = os.path.join(self.data_dir, file_pattern)
		names = []
		dtypes = []
		with open(domain_path, 'r') as domain:
			content = domain.readline()
			while len(content) > 0:
				splited_line = re.split('\s+', content)

				if splited_line[1] not in ['C', 'D']:
					content = domain.readline()
					continue
				names.append(splited_line[0])
				dtypes.append(splited_line[1])
				content = domain.readline()

		return {'names': names, 'types': dtypes }




		