import os
from dotenv import load_dotenv
from neo4jmodels.base.fields import Field
from neo4jmodels.base.models import Model

load_dotenv()


class ETLSqlModel(Model):
    host = Field("host")
    dbaccount = Field("dbaccount")
    dbpasswd = Field("dbpasswd")
    db = Field("db")
    data_base_model = Field("data_base_model")
    formatter_base_model = Field("formatter_base_model")


class ETLNeo4jModel(Model):
    neo_conn = Field("neo_conn")
    neo_account = Field("neo_account")
    neo_token = Field("neo_token")


envs = {
    "ETLSQL": ETLSqlModel(**os.environ).convert(),
    "ETLNeo4j": ETLNeo4jModel(**os.environ).convert()
}


def get_env(env_key=None):
    if env_key and env_key in envs.keys():
        return envs[env_key]
    else:
        return ETLSqlModel().convert()
