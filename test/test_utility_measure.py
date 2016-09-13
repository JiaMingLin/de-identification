import common.constant as c
from django.test import TestCase
from common.utility_measure import UserQuery
from common.data_utilities import DataUtils

TEST_DATA_PATH = c.TEST_ORIGIN_DATA_PATH
class TestUtilityMeasure(TestCase):
	def setUp(self):
		self.queries = [
			"Age > 50 and workclass == 'Self-emp-not-inc'",
			"fnlwgt > 159449 and (native_country == 'United-States' or native_country == 'Cuba')",
			"fnlwgt > 159449 and native_country in ('United-States', 'Cuba')",
			"native_country == 'United-States' or native_country == 'Cuba' and fnlwgt > 159449"
		]

		self.user_query = UserQuery(TEST_DATA_PATH)

	def test_get_query_count_with_same_results_cnt(self):
		data = DataUtils(file_path = TEST_DATA_PATH)
		df = data.get_pandas_df()
		result_cnt = [self.user_query.get_query_count(df, query) for query in self.queries]

		self.assertEqual(result_cnt == [1278, 24339, 24339, 41415], True)

	def test_error_measure_with_same_dataset(self):
		results = self.user_query.get_errors(TEST_DATA_PATH, self.queries)
		self.assertEqual(results == [0,0,0,0], True)