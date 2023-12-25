import os
import importlib
from sqlalchemy import create_engine, or_, and_
from sqlalchemy.orm import Session
from urllib.parse import quote_plus


class SQLUtils(object):

    def __init__(self, dbaccount, dbpasswd, db, host='127.0.0.1'):

        dbpasswd = quote_plus(dbpasswd)
        self.engine = create_engine(
            os.getenv("dbengine").format(
                dbaccount=dbaccount,
                dbpasswd=dbpasswd,
                host=host,
                db=db
            ),
            echo=False
        )
        self._set_session()
        self.query_model = None
        self.query = None
        self.total = 0

    def _set_session(self):
        self.sess = Session(self.engine)

    def _get_query_model(self, base_model, model_name, model_attr=None):
        query_model = None
        f_model = importlib.import_module(base_model)
        query_model = getattr(
            f_model, model_name
        ) if hasattr(
            f_model, model_name
        ) else None

        if query_model and model_attr:
            query_model = getattr(
                query_model, model_attr
            ) if hasattr(
                query_model, model_attr
            ) else None

        return query_model

    def _set_query(self):
        self.query = self.sess.query(self.query_model)

    def set_query_model(self, base_model, model_name):
        self.query_model = self._get_query_model(base_model, model_name)
        self._set_query()

    def get_all(self, conds=None):
        self.total = self.query.filter(conds).count()
        return self.query.filter(conds).all()

    def get_query_conditions(self, base_model, model_name, mode, *conds):
        rsp = None
        query_parameters = list()
        for cond in conds:
            q_model = self._get_query_model(
                base_model, model_name, cond.get('attr')
            )
            if q_model:
                query_parameters.append(q_model == cond.get("value"))
        if mode == "or":
            rsp = or_(*query_parameters)
        if mode == "and":
            rsp = and_(*query_parameters)

        return rsp
