import sys
import yaml
from neo4jmodels.env import get_env
from neo4jmodels.node_map_factory import MapGenerator, NeoMapCreator

if __name__ == '__main__':

    settings_file = sys.argv[1]

    with open(settings_file) as f:
        conf = yaml.safe_load(f)
        offset = int(conf['offset'])
        limit = int(conf['limit'])
        while True:
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
            else:
                break
