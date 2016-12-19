import pandas as pd
import numpy as np
from common.base import Base
from common.data_utilities import DataUtils

class UserQuery(Base):
	def __init__(self, sensitive_data):
		""" Import the original data and initialize the utility measurement object

		Parameters
		----------
		sensitive_data: string
			The path to the original data. 
		"""
		self.LOG = Base.get_logger("UserQuery")
		sensitive = DataUtils(file_path = sensitive_data)
		self.sensitive_df = sensitive.get_pandas_df()

	def get_errors(self, synthetic_data, user_queries):
		""" Find the errors of the given queries between sensitive data and synthetic data

		Parameters
		----------
		synthetic_data: string
			The path to the synthetic data.
		user_queries: list
			the list of user queries.

		Returns
		-------
		results: list
			The list of results corresponding to each query
		"""

		# import synthetic data as dataframe
		def get_one_error(df1, df2, query):
			import time
			t0 = time.time()
			try:
				len_df1_result = self.get_query_count(df1, query)
				len_df2_result = self.get_query_count(df1, query)
			except Exception as e:
				return str(e)

			if len_df1_result == 0:
				return 'inif'
			self.LOG.info("User query error measurement spends: %d seconds" % (time.time() - t0))

			return np.abs(len_df1_result - len_df2_result) / len_df1_result

		synthetic = DataUtils(file_path = synthetic_data)
		synthetic_df = synthetic.get_pandas_df()
		results = [get_one_error(self.sensitive_df, synthetic_df, query) for query in user_queries]
		return results
		

	def get_query_count(self, df, query):
		return len(df.query(query))





