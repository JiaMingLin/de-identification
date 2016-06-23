import json
import pandas as pd
from .base import Base

class DataUtils(Base):

    def __init__(self, file_path, selection = None):
        self.file_path = file_path
        self.dataframe = pd.read_csv(file_path)

        if(selection != None):
            self.dataframe = self.dataframe[selection]

        self.preview_count = 5

    def data_preview(self, format = None):
        if(format=='json'):
            return json.dumps(dict(((col,val.tolist()) for (col,val) in dict(self.dataframe[:self.preview_count]).items())))
        return self.dataframe[:self.preview_count]

    def get_pandas_df(self):
        return self.dataframe

    def get_domain(self):
        domain = dict((pair[0], list(set(pair[1]))) for pair in dict(self.dataframe).items())
        return domain
