import collections
import pandas as pd
from common.base import Base

class DataUtils(Base):

    def __init__(self, file_path, selection = None):
        self.file_path = file_path
        self.dataframe = pd.read_csv(file_path)

        if(selection != None):
            self.dataframe = self.dataframe[selection]

        self.preview_count = 5

    def data_preview(self, format = None):
        sub_df = self.dataframe[:self.preview_count]
        return sub_df

    def get_pandas_df(self):
        return self.dataframe

    def get_domain(self):
        domain = collections.OrderedDict((pair[0], list(set(pair[1]))) for pair in collections.OrderedDict(self.dataframe).items())
        return domain

    def get_nodes_name(self):
        return list(self.dataframe.columns.values)
