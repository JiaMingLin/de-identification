from django.test import TestCase

from data_utilities import DataUtils

# Create your tests here.
class DataUtilitiesTests(TestCase):
    testing_file = 'desktop/static/testing_row_data.csv'
    def test_data_preview(self):
        data = DataUtils(self.testing_file)
        preview = data.data_preview()
        self.assertEqual(len(preview.values[0]) > 0, True)
