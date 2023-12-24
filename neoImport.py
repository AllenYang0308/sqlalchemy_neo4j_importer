import sys
import yaml
from neo4jmodels.env import get_env
from neo4jmodels.node_map_factory import MapGenerator, NeoMapCreator

if __name__ == '__main__':

    settings_file = sys.argv[1]

    with open(settings_file) as f:
        conf = yaml.safe_load(f)

        nds = [
            MapGenerator.generat_node_data(**node) for node in conf['nodes']
        ]
        rds = [MapGenerator.generate_relation_data(**relation) for
               relation in conf['relations']]

        nc = NeoMapCreator(
            **get_env("ETLNeo4j"),
            build_metadata={'nodes': nds, 'relations': rds}
        )
        nc.build_neo_map()
