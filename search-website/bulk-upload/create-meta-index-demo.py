# Create Azure Cognitive Search Index

import requests
import json

with open("api/local.settings.json") as read_file:
    config = json.load(read_file)

service_name = config["Values"]["SearchServiceName"]
api_version = config["Values"]["ApiVersion"]

headers = {
    'Content-Type': 'application/json',
    'api-key': config["Values"]["SearchApiKey"]
}

index = {
  "fields": [
    {
      "name": "id",
      "type": "Edm.String",
      "key": True,
      "searchable": False,
      "filterable": False,
      "facetable": False,
      "sortable": True
    },
    {
      "name": "metadata_storage_name",
      "type": "Edm.String",
      "searchable": True,
      "filterable": True,
      "facetable": True,
      "sortable": True
    },
    {
      "name": "content",
      "type": "Edm.String",
      "searchable": True,
      "filterable": False,
      "facetable": False,
      "sortable": False
    },
    {
      "name": "keyPhrases",
      "type": "Collection(Edm.String)",
      "searchable": True,
      "filterable": False,
      "facetable": False,
      "sortable": False
    },
    {
      "name": "merged_text",
      "type": "Edm.String",
      "searchable": True,
      "filterable": False,
      "facetable": False,
      "sortable": False
    },
    {
      "name": "Test1",
      "type": "Edm.String",
      "searchable": True,
      "filterable": True,
      "facetable": True,
      "sortable": True
    },
    {
      "name": "Test2",
      "type": "Edm.String",
      "searchable": True,
      "filterable": True,
      "facetable": True,
      "sortable": True
    },
    {
      "name": "Test3",
      "type": "Edm.String",
      "searchable": True,
      "filterable": True,
      "facetable": True,
      "sortable": True
    }
  ],
  "suggesters": [
    {
      "name" : "sg",
      "searchMode": "analyzingInfixMatching",
      "sourceFields": ["metadata_storage_name"]
    }
  ]
}


index_name = "mosl-demo-index-meta2"
uri = f"https://{service_name}.search.windows.net/indexes/{index_name}?api-version={api_version}"

resp = requests.put(uri, headers = headers, data = json.dumps(index))
print(resp.status_code)
print(resp.ok)

# Create Azure Cognitive Search Indexer

indexer_name = "mosl-demo-indexer-meta"
datasource_name = "blob-datasource"
skillset_name = "mosl-demo-skillset"

indexer = {
  "name": indexer_name,
  "dataSourceName" : datasource_name,
  "targetIndexName" : index_name,
  "skillsetName" : skillset_name,
  "fieldMappings" : [
    {
      "sourceFieldName" : "metadata_storage_path",
      "targetFieldName" : "id",
      "mappingFunction" : {"name": "base64Encode"}
    },
    {
      "sourceFieldName" : "metadata_storage_name",
      "targetFieldName" : "metadata_storage_name",
    },
    {
      "sourceFieldName" : "content",
      "targetFieldName" : "content"
    },
    {
      "sourceFieldName" : "Test1",
      "targetFieldName" : "Test1"
    },
    {
      "sourceFieldName" : "Test2",
      "targetFieldName" : "Test2"
    },
    {
      "sourceFieldName" : "Test3",
      "targetFieldName" : "Test3"
    }
  ],
  "outputFieldMappings" :
  [
    {
      "sourceFieldName" : "/document/merged_text",
      "targetFieldName" : "merged_text"
    },
    {
      "sourceFieldName" : "/document/pages/*/keyPhrases/*",
      "targetFieldName" : "keyPhrases"
    },
  ],
  "parameters":
  {
    "maxFailedItems": 1,
    "maxFailedItemsPerBatch": 1,
    "configuration":
    {
      "dataToExtract": "contentAndMetadata",
      "parsingMode": "default",
      "firstLineContainsHeaders": False,
      "delimitedTextDelimiter": ",",
      "imageAction": "generateNormalizedImages"
    }
  }
}

uri = f"https://{service_name}.search.windows.net/indexers/{indexer_name}?api-version={api_version}"

resp = requests.put(uri, headers = headers, data = json.dumps(indexer))
print(resp.status_code)
print(resp.ok)


uri = f"https://{service_name}.search.windows.net/indexers/{indexer_name}/status?api-version={api_version}"

resp = requests.get(uri, headers=headers)
print(resp.status_code)
print(resp.json().get('lastResult').get('status'))
print(resp.ok)


# sample query in search explorer:
# search=*&$select=metadata_storage_name,Test1,Test2,Test3,merged_text&$filter=Test1 eq 'TRUE' and search.ismatch('Annex*', 'content')&$count=true&highlight=merged_text