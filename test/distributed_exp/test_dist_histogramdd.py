import os
import common.constant as c
from django.test import TestCase
from spark_exp.data_dist import DataDist
from spark_exp.histogramdd_dict import HistogramddDist

class TestHistogramddDist(TestCase):
	def setUp(self):
		self.data = DataDist(c.DOMAIN_FILE, data_path = c.HDFS_MEDIAN_DATA)
		self.cliques = [['capital_loss', 'salary_class'], ['fnlwgt'], ['workclass', 'occupation'], ['education', 'education_num', 'salary_class'], ['sex', 'hours_per_week', 'salary_class'], ['age', 'marital_status', 'relationship', 'salary_class'], ['occupation', 'sex', 'capital_gain', 'salary_class'], ['marital_status', 'relationship', 'sex', 'salary_class'], ['race', 'native_country']]
	
	def test_histogramdd_dist(self):
		hist_dist = HistogramddDist(self.data)
		filled_cts = hist_dist.histogram_dist(self.cliques)
		print filled_cts