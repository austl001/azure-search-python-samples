
import json
import requests

with open("api/local.settings.json") as read_file:
    config = json.load(read_file)

service_name = config["Values"]["SearchServiceName"]
api_version = config["Values"]["ApiVersion"]

headers = {
    'Content-Type': 'application/json',
    'api-key': config["Values"]["SearchApiKey"]
}

index_name = "mosl-demo-index"

# Querying the Azure Cognitive Search Index

search_string = "error correction"

url = "https://{}.search.windows.net/indexes/{}/docs".format(service_name, index_name)
url += "?api-version={}".format(api_version)
url += "&search={}".format(search_string)
url += "&$count=true"
#url += '&$top=5'
url += '&highlight=merged_text'
print(url)

resp = requests.get(url, headers = headers)
print(resp.status_code)

search_results = resp.json()

search_results.keys()
search_results["@odata.context"]
search_results["@odata.count"]
len(search_results['value'])
search_results['value'][0].keys()

for result in search_results["value"]:
    print("PDF Name: {}, Search Score {}".format(result["metadata_storage_name"], result["@search.score"])
    )

print(search_results["value"][0]["merged_text"][:350])

print("Results Found: {}, Results Returned: {}".format(search_results['@odata.count'], len(search_results['value'])))
print("Highest Search Score: {}".format(search_results['value'][0]['@search.score']))

search_results['value'][0]['@search.highlights']['merged_text']