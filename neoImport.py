import sys
import yaml
import logging
import datetime
from neo4jmodels.env import get_env
from neo4jmodels.base.fields import Field
from neo4jmodels.base.models import Model
from neo4jmodels.node_map_factory import MapGenerator, NeoMapCreator


class ConfModel(Model):
    offset = Field("offset", column_type=int, default_value=0)
    limit = Field("limit", column_type=int, default_value=10000)
    nodes = Field('nodes', column_type=list, default_value=[])
    relations = Field('relations', column_type=list, default_value=[])


class DataSetCreator(object):

    def __init__(self, conf):
        self.offset = conf['offset']
        self.limit = conf['limit']
        self.datalength = 0
        self.nodes = self._node_generator(conf['nodes'])
        self.relations = self._relation_generator(conf['relations'])

    def _node_generator(self, node_conf):
        nds = list()
        for node in node_conf:
            node.update({'offset': self.offset, 'limit': self.limit})
            nds.append(MapGenerator.generat_node_data(**node))
        for nlen in nds:
            self.datalength = self.datalength + len(nlen['data'])
        return nds

    def _relation_generator(self, rel_conf):
        rds = list()
        for rel in rel_conf:
            rel.update({'offset': self.offset, 'limit': self.limit})
            rds.append(MapGenerator.generate_relation_data(**rel))
        for rlen in rds:
            self.datalength = self.datalength + len(rlen['data'])
        return rds

    def get_datalength(self):
        return self.datalength

    def get_nodes(self):
        return self.nodes

    def get_relations(self):
        return self.relations


if __name__ == '__main__':

    settings_file = sys.argv[1]
    log_file = settings_file.split('/')[1].split('.')[0]
    logging.basicConfig(filename=f"logs/{log_file}.log",
                        format='%(levelname)s:%(message)s',
                        level=logging.INFO)
    logger = logging.getLogger("Neo4jImporterLogger")
    retry_times = 0

    with open(settings_file) as f:
        conf = yaml.safe_load(f)
        conf = ConfModel(**conf).convert()
        offset = int(conf.get("offset", 0))
        limit = int(conf.get("limit", 10000))

        while True:

            try:
                conf.update({'offset': offset, 'limit': limit})
                data_set_creator = DataSetCreator(conf)
                if data_set_creator.datalength > 0:
                    nc = NeoMapCreator(
                        **get_env("ETLNeo4j"),
                        build_metadata={
                            'nodes': data_set_creator.get_nodes(),
                            'relations': data_set_creator.get_relations()}
                    )
                    nc.build_neo_map()

                    offset = offset + limit
                    retry_times = 0
                else:
                    break

            except Exception as e:
                retry_times = retry_times + 1
                msg = {
                    "file": settings_file,
                    "offset": offset,
                    "limit": limit,
                    "error": e,
                    "log_time": datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                }
                logger.error(msg)
            if retry_times > 5:
                break

    if retry_times <= 5:
        msg = {
            "file": settings_file,
            "status": "successful.",
            "log_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        logger.info(msg)
    else:
        msg = {
            "file": settings_file,
            "offset": offset,
            "limit": limit,
            "status": "import failed.",
            "log_time": datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        }
        logger.error(msg)
