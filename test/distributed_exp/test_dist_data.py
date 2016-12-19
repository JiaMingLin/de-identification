import os
import common.constant as c

from spark_exp.data_dist import DataDist
from django.test import TestCase

class TestDistData(TestCase):
	def setUp(self):
		pass

	def read_median_data(self):
		median_data = DataDist(c.DOMAIN_FILE, data_path = c.HDFS_MEDIAN_DATA)

	def test_read_large_data(self):
		large_data = DataDist(c.DOMAIN_FILE, data_path = c.HDFS_LARGE_DATA)

	def read_huge_data(self):
		huge_data = DataDist(c.DOMAIN_FILE, data_path = c.HDFS_HUGE_DATA)
