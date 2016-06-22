import json
import pandas as pd


class DataUtils():

    def __init__(self, file_path):
        self.file_path = file_path
        self.dataframe = pd.read_csv(file_path)
        self.preview_count = 5

    def data_preview(self, format = None):

        if(format=='json'):
            return json.dumps(dict(((col,val.tolist()) for (col,val) in dict(self.dataframe[:self.preview_count]).items())))
        return self.dataframe[:self.preview_count]
    
