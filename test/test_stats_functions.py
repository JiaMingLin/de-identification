from django.test import TestCase
from common.data_utilities import DataUtils
from dptable.stats_functions import StatsFunctions

import common.constant as c

class TestStatsFunctions(TestCase):

	def setUp(self):
		selected_attributes = {
			"Age":"C",
			"workclass":"D",
			"fnlwgt":"C",
			"education":"D",
			"education_num":"D",
			"marital_status":"D",
			"occupation":"D",
			"relationship":"D",
			"race":"D",
			"sex":"D",
			"capital_gain":"C",
			"capital_loss":"C",
			"hours_per_week":"C",
			"native_country":"D",
			"salary_class":"D"

		}
		self.data = DataUtils(c.TEST_ORIGIN_DATA_PATH, selected_attrs = selected_attributes)
		self.data.data_coarsilize()
		self.stats_funcs = StatsFunctions()


	def test_histogram(self):
		cliques = [['capital_loss', 'salary_class'], ['fnlwgt'], ['workclass', 'occupation'], ['education', 'education_num', 'salary_class'], ['sex', 'hours_per_week', 'salary_class'], ['occupation', 'sex', 'capital_gain', 'salary_class'], ['marital_status', 'relationship', 'sex', 'salary_class'], ['race', 'native_country']]
		self.stats_funcs.histogramdd_batch(self.data, cliques)

