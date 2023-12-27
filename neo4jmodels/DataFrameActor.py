from neo4jmodels.models_map import model_map
import importlib
import json


class DataFrameActor(object):

    def __init__(self, data):
        model_type = model_map[data.__class__.__name__]
        model = importlib.import_module(f"neo4jmodels.{model_type}")
        df_model = getattr(model, "CreateDataFrame")
        cc = df_model()
        self._df = cc.create_data_frame(data)

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, df):
        self._df = df

    def deduplicates(self, *subsets):
        if not self._df.empty:
            self._df = self._df.drop_duplicates(
                subset=list(subsets), keep="last"
            )

    def get_frame_head(self):
        return tuple(self._df.head())

    def remove_empty_rows(self, *field_names):
        if not self._df.empty:
            for field_name in field_names:
                self._df = self._df[~self._df[field_name].isnull()]

    def filter_column(self, *columns):
        self._df = self._df.filter(columns)

    def to_json(self, orient="records"):
        return self._df.to_json(orient=orient)

    def to_dict(self, orient="records"):
        return json.loads(self._df.to_json(orient=orient))
