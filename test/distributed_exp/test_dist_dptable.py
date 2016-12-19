import os
import common.constant as c
from django.test import TestCase
from spark_exp.data_dist import DataDist
from spark_exp.dptable_dist import DPTableDist

class TestDistDPTable(TestCase):
	def setUp(self):
		path = '/data/data_10dim_100M-coarse.csv'
		domain_path = os.path.join(c.ROOT_PATH, 'static/test/data_10dim_100M-coarse.domain')
		self.data = DataDist(domain_path, data_path = path)

	def test_dptable(self):
		dptable = DPTableDist(self.data, eps1 = 10, eps2 = 0.5)
		dptable.run()		
