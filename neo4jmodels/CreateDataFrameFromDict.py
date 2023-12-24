import pandas as pd

from neo4jmodels.dfmodels import DataFrameCreator
# from neo4jmodels.DataFrameActor import DataFrameActor


class CreateDataFrame(DataFrameCreator):

    def create_data_frame(self, data):
        self._df = pd.DataFrame.from_dict(data)
        return self._df
        # self._df = DataFrameActor(df)

    @property
    def df(self):
        return self._df
