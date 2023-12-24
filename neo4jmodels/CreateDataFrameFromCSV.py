import pandas as pd

from neo4jmodels.dfmodels import DataFrameCreator


class CreateDataFrame(DataFrameCreator):

    def create_data_frame(self, data):
        self._df = pd.read_csv(data)

    @property
    def df(self):
        return self._df
