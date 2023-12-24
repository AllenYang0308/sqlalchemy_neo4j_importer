from abc import ABC, abstractmethod
import importlib
from neo4jmodels.utils import SQLUtils
from neo4jmodels.DataFrameActor import DataFrameActor
from neo4jmodels.base.models import Model
from neo4jmodels.base.fields import Field


class NodeDataSet(ABC):

    @abstractmethod
    def get_data_frame_actor(self) -> DataFrameActor:
        return DataFrameActor([])


class NodeFormatter(object):

    def __init__(self, base_model="", formatter="", formatter_conf={}):
        self._formatter = None
        if formatter_conf:
            self._set_formatter_by_config(formatter_conf)
        else:

            self._set_formatter_by_name(base_model, formatter)

    @property
    def formatter(self):
        return self._formatter

    def _set_formatter_by_config(self, formatter_conf={}):
        conf = dict()
        for k,v in formatter_conf['attrs'].items():
            conf[k] = Field(v)
        self._formatter = type(formatter_conf['model_name'], (Model, ), conf)

    def _set_formatter_by_name(self, base_model="", formatter=""):

        try:
            fbs_model = importlib.import_module(base_model)
            self._formatter = getattr(
                fbs_model, formatter
            ) if hasattr(
                fbs_model, formatter
            ) else None
        except Exception:
            self._formatter = None

    def get_formatter_data(self, data=[]):
        return [
            self.formatter(**row).convert() for row in data
        ] if self._formatter else data


class SQLDataSet(NodeDataSet):

    def __init__(self, host="", dbaccount="", dbpasswd="", db="",
                 data_base_model="", model_name="", formatter_base_model="",
                 formatter_model="", formatter_conf={}, mode="and",
                 model_conditions=[]):
        self.sqldb = SQLUtils(dbaccount, dbpasswd, db, host)
        self.data_base_model = f"{data_base_model}.{model_name}"
        self.sqldb.set_query_model(data_base_model, model_name)
        self.query_conditions = self._get_conditions(
            data_base_model, model_name, mode, *model_conditions
        )
        self.formatter = NodeFormatter(
            formatter_base_model, formatter_model, formatter_conf
        )
        self._dataframe = None

    def _get_conditions(self, base_model, model_name,
                        mode="and", *model_conditions):
        return self.sqldb.get_query_conditions(base_model, model_name, mode,
                                               *model_conditions)

    def set_formatter(self, formatter_base_model, formatter_model_name):
        try:
            m = importlib.import_module(formatter_base_model)
            self.formatter = getattr(m, formatter_model_name)
        except Exception:
            self.formatter = None

    def _result_to_dict(self, result):
        return [row.__dict__ for row in result]

    @property
    def dataframe(self):
        return self._dataframe

    def get_data_frame_actor(self):
        rsp = None
        if not self.formatter:
            rsp = self._result_to_dict(
                self.sqldb.get_all(
                    self.query_conditions
                )
            )
        else:
            rsp = self.formatter.get_formatter_data(
                self._result_to_dict(
                    self.sqldb.get_all(
                        self.query_conditions
                    )
                )
            )
        self._dataframe = DataFrameActor(rsp)
