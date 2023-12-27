from py2neo import Graph
from py2neo.bulk import merge_nodes, merge_relationships
import pandas as pd
import json

im_data = pd.read_csv("sf_dataset.csv")

df_business = im_data.filter(
    [
        "business_id",
        "business_name",
        "business_address",
        "latitude",
        "longitude"
    ]
)
df_business = df_business.drop_duplicates('business_id', keep='last')
json_business = df_business.to_json(orient="records")
dict_business = json.loads(json_business)
print('business: ', len(dict_business))

df_zip = im_data.filter(["zip"])
df_zip = df_zip.drop_duplicates('zip', keep='last')
json_zip = df_zip.to_json(orient="records")
dict_zip = json.loads(json_zip)
print('zip: ', len( dict_zip ))

df_person = im_data.filter(["user_name", "deviceID"])
df_person = df_person.drop_duplicates('deviceID', keep='last')
json_person = df_person.to_json(orient="records")
dict_person = json.loads(json_person)
print('person: ', len( dict_person ))

df_relationship = im_data.filter(["business_id", "deviceID", "scan_timestamp"])
json_relationship = df_relationship.to_json(orient="records")
dict_relationship = json.loads(json_relationship)

df_relationship_zip = im_data.filter(["business_id", "zip"])
df_relationship_zip = df_relationship_zip.drop_duplicates(
    'business_id',
    keep='last'
)
json_relationship_zip = df_relationship_zip.to_json(orient="records")
dict_relationship_zip = json.loads(json_relationship_zip)
# dict_relationship_zip = []


graph = Graph(
    "neo4j+s://1b4e9707.databases.neo4j.io",
    auth=(
        "neo4j",
        "VZWCC6OoZP44vsGxkkzchHLUhfbG4yEdn0D5ZNrCnOI"
    )
)
# graph.merge(dict_business, "Business", "business_id")
ss = merge_nodes(
    graph,
    dict_business,
    ("Business", "business_id"),
    labels={"Business"}
)

merge_nodes(graph, dict_zip, ("Zip", "zip"), labels={"Zip"})

merge_nodes(
    graph.auto(),
    dict_person,
    merge_key="deviceID",
    labels={"Person"}
)


ex_people = []

for p in dict_relationship:

    device = p["deviceID"]
    business = p["business_id"]

    ex_people.append((device, p, business))

merge_relationships(
    graph.auto(),
    ex_people,
    "VISITED",
    start_node_key=("Person", "deviceID"),
    end_node_key=("Business", "business_id")
)
ex_zip = []

for p in dict_relationship_zip:

    rzip = p["zip"]
    business = p["business_id"]
    ex_zip.append((business, p, rzip))

merge_relationships(
    graph.auto(),
    ex_zip,
    "ISLOCATED",
    start_node_key=("Business", "business_id"),
    end_node_key=("Zip", "zip")
)
