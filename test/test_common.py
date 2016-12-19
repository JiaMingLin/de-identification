import common.constant as c
from common.data_utilities import DataUtils
from common.base import Base

from django.test import TestCase


TESTING_FILE = c.TEST_ORIGIN_DATA_PATH
class DataUtilitiesTests(TestCase):
# TODO: The Data Coarse and Generalize step should seperate, to simulate a more real case.

	def setUp(self):
		self.selected_attrs = dict({
			'Age':'C', 
			'workclass':'D',
			'fnlwgt':'C',
			'education':'D',
			'education_num':'D',
			'marital_status':'D',
			'occupation':'D',
			'relationship':'D',
			'race':'D',
			'sex':'D',
			'capital_gain':'C',
			'capital_loss':'C',
			'hours_per_week':'C',
			'native_country':'D',
			'salary_class':'D'
		})		
		self.data = DataUtils(file_path = TESTING_FILE, selected_attrs = self.selected_attrs)
		self.data.data_coarsilize()

		
		self.base = Base()

	def test_data_preview(self):
		data = DataUtils(file_path = TESTING_FILE)
		preview = data.data_preview()
		self.assertEqual(len(preview.values[0]) > 0, True)

	def test_read_data_by_three_selected_column(self):
		"""
		Test the read data by user specified columns
		"""
		self.assertEqual(len(self.data.get_nodes_name()) == len(self.selected_attrs), True)

	def test_data_domain_keep_original_order(self):
		"""
		Test the order in domain object is in same order with 
		original raw data.
		"""
		df = self.data.get_pandas_df()
		domain = self.data.get_domain()
		cols = domain.keys()
		self.assertEqual(cols == list(df.columns.values), True)

	def test_data_coarsilization(self):
		print self.data.get_pandas_df()[:5]

	def test_data_generalization(self):
		self.data.data_generalize()
		print self.data.get_pandas_df()[:5]

	def test_is_skip_pre_processing_with_create(self):
		create_flag = True
		request = {
			'data_path':'/path/to/dummy/file.csv',
			'selected_attrs':{
				'names':['A', 'D', 'C', 'B'],
				'types':['C', 'C', 'C', 'D']
			}
		}
		instance = {
			'data_path':'/path/to/dummy/file.csv',
			'selected_attrs':{
				'names':['A', 'D', 'C', 'B'],
				'types':['C', 'C', 'C', 'D']
			}
		}
		skip_pre_process = self.base.is_pre_process_skip(request, request, create_flag)
		self.assertEqual(skip_pre_process == False, True)

	def test_is_skip_pre_processing_with_data_path_change(self):

		create_flag = False
		request = {
			'data_path':'/path/to/dummy/file.csv',
			'selected_attrs':{
				'names':['A', 'D', 'C', 'B'],
				'types':['C', 'C', 'C', 'D']
			}
		}
		instance = {
			'data_path':'/path/to/dummy/file22222222.csv',
			'selected_attrs':{
				'names':['A', 'D', 'C', 'B'],
				'types':['C', 'C', 'C', 'D']
			}
		}
		
		skip_pre_process = self.base.is_pre_process_skip(request, instance, create_flag)
		print skip_pre_process
		self.assertEqual(skip_pre_process == False, True)

	def test_is_skip_pre_processing_with_selected_attr_change(self):

		create_flag = False
		request = {
			'data_path':'/path/to/dummy/file.csv',
			'selected_attrs':{
				'names':['A', 'D', 'C', 'B'],
				'types':['C', 'C', 'C', 'D']
			}
		}
		instance = {
			'data_path':'/path/to/dummy/file.csv',
			'selected_attrs':{
				'names':['A', 'D', 'C', 'B'],
				'types':['D', 'D', 'D', 'D']
			}
		}
		skip_pre_process = self.base.is_pre_process_skip(request, instance, create_flag)
		print skip_pre_process
		self.assertEqual(skip_pre_process == False, True)

	def test_is_skip_pre_processing_without_change(self):
		
		create_flag = False
		request = {
			'data_path':'/path/to/dummy/file.csv',
			'selected_attrs':{
				'names':['A', 'D', 'C', 'B'],
				'types':['C', 'C', 'C', 'D']
			}
		}
		instance = {
			'data_path':'/path/to/dummy/file.csv',
			'selected_attrs':{
				'names':['A', 'D', 'C', 'B'],
				'types':['C', 'C', 'C', 'D']
			}
		}
		skip_pre_process = self.base.is_pre_process_skip(request, instance, create_flag)
		self.assertEqual(skip_pre_process == True, True)