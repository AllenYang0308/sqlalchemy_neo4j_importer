import sys
import yaml
import logging
import datetime
from neo4jmodels.env import get_env
from neo4jmodels.node_map_factory import MapGenerator, NeoMapCreator


def run_neo4j_importer(conf, logger):
    retry_times = 0
    offset = conf.get('offset', 0)
    limit = conf.get('limit', 10000)
    while True:
        if retry_times > 5:
            break

        try:
            nds, rds = [], []
            datalength = 0
            for node in conf['nodes']:
                node.update({'offset': offset, 'limit': limit})
                nds.append(
                    MapGenerator.generat_node_data(**node)
                )
            for nlen in nds:
                datalength = datalength + len(nlen['data'])
            for rel in conf['relations']:
                rel.update({'offset': offset, 'limit': limit})
                rds.append(
                    MapGenerator.generate_relation_data(**rel)
                )
            for rlen in rds:
                datalength = datalength + len(rlen['data'])
            if datalength > 0:
                nc = NeoMapCreator(
                    **get_env("ETLNeo4j"),
                    build_metadata={'nodes': nds, 'relations': rds}
                )
                nc.build_neo_map()

                offset = offset + limit
                retry_times = 0
            else:
                break
            retry_times = 0
            msg = {
                "file": settings_file,
                "offset": offset,
                "limit": limit,
                "log_time": datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "status": "successful."
            }
            logger.info(msg)
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


if __name__ == '__main__':

    settings_file = sys.argv[1]
    log_file = settings_file.split('/')[1].split('.')[0]
    logging.basicConfig(filename=f"logs/{log_file}.log",
                        format='%(levelname)s:%(message)s',
                        level=logging.INFO)
    logger = logging.getLogger("Neo4jImporterLogger")

    with open(settings_file) as f:
        conf = yaml.safe_load(f)
        run_neo4j_importer(conf, logger)

    # retry_times = 0

    # with open(settings_file) as f:
    #     conf = yaml.safe_load(f)
    #     offset = int(conf.get("offset", 0))
    #     limit = int(conf.get("limit", 10000))

    #     while True:
    #         if retry_times > 5:
    #             break

    #         try:
    #             # print("offset: ", offset)
    #             # print("limit: ", limit)
    #             nds, rds = [], []
    #             datalength = 0
    #             stime = time.time()
    #             for node in conf['nodes']:
    #                 node.update({'offset': offset, 'limit': limit})
    #                 nds.append(
    #                     MapGenerator.generat_node_data(**node)
    #                 )
    #             etime = time.time()
    #             # print("generate node time: ", etime - stime)
    #             for nlen in nds:
    #                 datalength = datalength + len(nlen['data'])
    #             stime = time.time()
    #             for rel in conf['relations']:
    #                 rel.update({'offset': offset, 'limit': limit})
    #                 rds.append(
    #                     MapGenerator.generate_relation_data(**rel)
    #                 )
    #             etime = time.time()
    #             # print('generate relation time: ', etime - stime)
    #             for rlen in rds:
    #                 datalength = datalength + len(rlen['data'])
    #             stime = time.time()
    #             if datalength > 0:
    #                 nc = NeoMapCreator(
    #                     **get_env("ETLNeo4j"),
    #                     build_metadata={'nodes': nds, 'relations': rds}
    #                 )
    #                 nc.build_neo_map()

    #                 offset = offset + limit
    #                 retry_times = 0
    #             else:
    #                 break
    #             retry_times = 0
    #             etime = time.time()

    #         except Exception as e:
    #             retry_times = retry_times + 1
    #             msg = {
    #                 "file": settings_file,
    #                 "offset": offset,
    #                 "limit": limit,
    #                 "error": e,
    #                 "log_time": datetime.datetime.now().strftime(
    #                     "%Y-%m-%d %H:%M:%S"
    #                 )
    #             }
    #             logger.error(msg)
    # if retry_times > 5:
    #     msg = {
    #         "file": settings_file,
    #         "status": "successful.",
    #         "log_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #     }
    #     logger.info(msg)
    # else:
    #     msg = {
    #         "file": settings_file,
    #         "offset": offset,
    #         "limit": limit,
    #         "status": "import failed.",
    #         "log_time": datetime.datetime.now().strftime(
    #             "%Y-%m-%d %H:%M:%S"
    #         )
    #     }
    #     logger.error(msg)
