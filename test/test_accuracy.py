from django.test import TestCase
from api.serializers import TaskSerializer, JobSerializer

import common.constant as c

class TestFull(TestCase):

	def setUp(self):

		self.data_dir = c.TEST_FILE_PATH
		# noises
		self.privacy_levels = [1,2,3,4,5]

		# test cases
		self.cases = [
			(
				"data2.dat", 
				{
					"names": ["Age","Height","Weight","Income","TRV","HTN","DGF"],
					"types": ["C", "C", "C", "C", "C", "D", "D"]
				},
				[["Age", "Income"], ['Income', 'TRV']]
			),
			(
				"data2.dat", 
				{
					"names": ["Age","Height","Weight","Income","TRV","HTN","DGF"],
					"types": ["C", "C", "C", "C", "C", "D", "D"]
				},
				[]
			)
		]

	def test_full(self):
		for data_name, domain, white_list in self.cases:
			self.diff_privacy(data_name, domain, self.privacy_levels, white_list = white_list)
		

	def diff_privacy(self, data_name, domain, eps_ls, white_list = []):
		data_input = {
			"task_name": data_name,
			"data_path": "%s/%s" % (self.data_dir, data_name),
			"selected_attrs": domain,
			"white_list": white_list
		}
		task = TaskSerializer()
		task_obj = task.create(data_input)

		for lv in self.privacy_levels:
			print "Injecting noise %s with jtree %s" %(self.get_eps(lv), task_obj.jtree_strct)
			privacy_input = {
				"privacy_level":lv,
				"epsilon":self.get_eps(lv),
				"task_id": task_obj.task_id
			}
			serializer = JobSerializer(data = privacy_input)
			if(serializer.is_valid()): serializer.save()


	def get_eps(self, level):
		corr = {
			1: 0.01,
			2: 0.1,
			3: 1,
			4: 10,
			5: 100
		}
		return corr[level]



		