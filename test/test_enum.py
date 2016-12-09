from django.test import TestCase
from common.enums import *

class TestEnum(TestCase):
	def test_eval_method_enum_names(self):
		self.assertEqual(isinstance(EvalMethodEnums.get_names(), dict), True)

	def test_ml_algorithm_enum_names(self):
		self.assertEqual(isinstance(MLAlgorithmEnums.get_names(), dict), True)

	def test_measure_enum_names(self):
		self.assertEqual(isinstance(MeasureEnums.get_names(), dict), True)