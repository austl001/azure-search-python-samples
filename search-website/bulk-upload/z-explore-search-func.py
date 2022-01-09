import requests
import json
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
import azure.functions as func

with open("api/local.settings.json") as read_file:
    config = json.load(read_file)

service_name = config["Values"]["SearchServiceName"]
api_version = config["Values"]["ApiVersion"]
index_name = "mosl-demo-index-meta2"
api_key = config["Values"]["SearchApiKey"]
endpoint = "https://search-test-123.search.windows.net"

search_client = SearchClient(endpoint = endpoint, index_name = index_name, credential = AzureKeyCredential(api_key))
print(search_client)

results = search_client.search(search_text = "meter", highlight_fields=("merged_text"), highlight_pre_tag = '<span style = "background-color: #f5e8a3">', highlight_post_tag = '</span>')

client_side_expected_shape = []

for item in results:
    
    new_document = {}
    new_document["score"]=item["@search.score"]
    new_document["highlights"]=item["@search.highlights"]

    new_shape = {}
    new_shape["id"]=item["id"]
    new_shape["metadata_storage_name"]=item["metadata_storage_name"]
    new_shape["content"]=item["content"]
    new_shape["keyPhrases"]=item["keyPhrases"]
    new_shape["merged_text"]=item["merged_text"]
    new_shape["Test1"]=item["Test1"]
    new_shape["Test2"]=item["Test2"]
    new_shape["Test3"]=item["Test3"]
        
    new_document["document"]=new_shape
    
    client_side_expected_shape.append(new_document)

# format the React app expects
full_response = {}

full_response["count"]=results.get_count()
full_response["facets"]=results.get_facets()
full_response["results"]=client_side_expected_shape

full_response_json = func.HttpResponse(body=json.dumps(full_response), mimetype="application/json",status_code=200)

for x in full_response["results"]:
    print(x)

