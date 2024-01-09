from abc import ABC, abstractmethod
from py2neo import Graph
from py2neo.bulk import merge_nodes, merge_relationships
from neo4jmodels.node_data_factory import SQLDataSet
from neo4jmodels.env import get_env


# 傳入neo4j資枓集，kwargs參數集
def df_actions(dataset, **kwargs):
    # 支援動作列表(去管複、取出欄位、移除空值列資枓)
    actions = ("deduplicates", "filter_column", "remove_empty_rows")
    for action, params in kwargs.items():
        if action in actions:
            if action == "deduplicates":
                dataset.dataframe.deduplicates(*params)
            if action == "remove_empty_rows":
                dataset.dataframe.remove_empty_rows(*params)
            if action == "filter_column":
                dataset.dataframe.filter_column(*params)
    return dataset


class NeoMapBuilder(ABC):

    @property
    @abstractmethod
    def NeoMap(self) -> None:
        pass

    @abstractmethod
    def add_nodes(self, data, labels):
        pass

    @abstractmethod
    def add_relationships(self, data, relation_name, start_node_key,
                          end_node_key):
        pass


class MapGenerator(object):

    @staticmethod
    def generat_node_data(env, model_name, offset=0, limit=10000,
                          formatter_model="",
                          formatter_conf={}, merge_label=[], merge_keys=[],
                          node_label={}, df_action_map={}, mode="and",
                          model_conditions=[]):
        merge_labels = tuple(merge_label + merge_keys)
        df = SQLDataSet(
            **get_env(env),
            model_name=model_name,
            formatter_model=formatter_model,
            formatter_conf=formatter_conf,
            mode=mode,
            model_conditions=model_conditions
        )
        df.get_data_frame_actor(offset, limit)
        df = df_actions(df, **df_action_map)

        return {
            'data': df.dataframe.to_dict(),
            'merge_key': merge_labels,
            'label': node_label
        }

    @staticmethod
    def generate_relation_data(env, model_name,
                               relation_name, start_key, end_key, offset=0,
                               limit=10000,
                               formatter_model="", formatter_conf={},
                               start_node_key=[], end_node_key=[],
                               df_action_map={}, mode="and",
                               model_conditions=[]):

        df = SQLDataSet(
            **get_env(env),
            model_name=model_name,
            formatter_model=formatter_model,
            formatter_conf=formatter_conf,
            mode=mode,
            model_conditions=model_conditions
        )
        df.get_data_frame_actor(offset, limit)
        df = df_actions(df, **df_action_map)
        rel_data = [
            (x[start_key], x, x[end_key]) for x in df.dataframe.to_dict()
        ]
        return {
            "data": rel_data,
            "relation_name": relation_name,
            "start_node_key": tuple(start_node_key),
            "end_node_key": tuple(end_node_key)
        }


class NeoMap(object):

    def __init__(self, neo_conn):
        self.conn = neo_conn

    def add_nodes(self, data, merge_key, label={}):
        merge_nodes(
            self.conn.auto(),
            data,
            merge_key,
            labels=label
        )

    def add_relationships(
        self,
        data,
        relation_name,
        start_node_key={},
        end_node_key={}
    ):
        merge_relationships(
            self.conn.auto(),
            data,
            relation_name,
            start_node_key=start_node_key,
            end_node_key=end_node_key
        )


class ConcreteNeoMapbuilder(NeoMapBuilder):

    def __init__(self, neo_conn, neo_account, neo_token) -> None:
        self.graph = Graph(
            neo_conn,
            auth=(
                neo_account,
                neo_token
            )
        )
        self._neo_map = NeoMap(self.graph)

    @property
    def NeoMap(self) -> NeoMap:
        return self._neo_map

    def add_nodes(self, data, merge_key, label={}) -> None:
        index_query = f"CREATE INDEX {merge_key[0]} IF NOT EXISTS \
            FOR (i: {merge_key[0]}) ON (i.{merge_key[1]})"
        self.graph.run(index_query)
        self._neo_map.add_nodes(
            data, merge_key, label=label
        )

    def add_relationships(self, data, relation_name, start_node_key,
                          end_node_key):
        self._neo_map.add_relationships(data, relation_name, start_node_key,
                                        end_node_key)


class NeoMapCreator(object):

    def __init__(self, neo_conn, neo_account, neo_token, build_metadata={}):

        self._builder = ConcreteNeoMapbuilder(neo_conn, neo_account, neo_token)
        self.nodes = build_metadata.get('nodes', [])
        self.relations = build_metadata.get('relations', [])

    @property
    def builder(self):
        return self._builder

    @builder.setter
    def builder(self, builder):
        self._builder = builder

    def build_neo_map(self):
        for node in self.nodes:
            self._builder.add_nodes(**node)
        for relation in self.relations:
            self._builder.add_relationships(**relation)
