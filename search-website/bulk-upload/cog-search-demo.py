
# az group create --name test-rg --location westeurope
# az storage account create --name moslcogsearchdemo --resource-group test-rg --location westeurope
# az storage account show-connection-string --name moslcogsearchdemo

# Import required python modules

import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import json
import requests

# Instantiate blob service using connection string from Azure CLI when creating storage account

with open("api/local.settings.json") as read_file:
    config = json.load(read_file)

connection_string = config["Values"]["BlobConnectionString"]

blob_service_client = BlobServiceClient.from_connection_string(connection_string)

container_name = config["Values"]["BlobContainerName"]

container_client = blob_service_client.create_container(container_name)

container_client = blob_service_client.get_container_client(container_name)

# Check what pdf files there are

os.listdir(os.getcwd() + "/bulk-upload/upload-documents")

# Iterate through files and upload to blob storage accout

for pdf in os.listdir("./pdfs"): 
    blob_client = blob_service_client.get_blob_client(
        container = container_name,
        blob = pdf
    )
    with open(os.path.join(".", "pdfs", pdf), "rb") as data:
        blob_client.upload_blob(data)


# check files have been uploaded

blob_list = container_client.list_blobs()
for blob in blob_list:
    print(blob.name)


# create Azure Cognitive Search Service
# az search service create --name search-test-123 --resource-group test-rg --location westeurope --sku free
# api_key = "FA2AD4CC12667C7382DCDCF816FF82DB"

# connect Azure cognitive search to the blob storage

service_name = config["Values"]["SearchServiceName"]
api_version = config["Values"]["ApiVersion"]

headers = {
    'Content-Type': 'application/json',
    'api-key': config["Values"]["SearchApiKey"]
}

datasource_name = "blob-datasource"

uri = f"https://{service_name}.search.windows.net/datasources?api-version={api_version}"

body = {
    "name": datasource_name,
    "type": "azureblob",
    "credentials": {"connectionString": connection_string},
    "container": {"name": container_name}
}

resp = requests.post(uri, headers = headers, data = json.dumps(body))
print(resp.status_code)
print(resp.ok)


# Connect Azure cog search to cog services

# az cognitiveservices account create --name mosl-demo-cogserv --kind CognitiveServices --sku S0 --resource-group test-rg --location westeurope
# az cognitiveservices account keys list --name mosl-demo-cogserv --resource-group test-rg
# key = "051bdf5fa88c450daa423ba3975fc2cd"

# Create Azure Cognitive Search Skillset

skillset = {
  "description": "Extract text from images and merge with content text to produce merged_text. Also extract key phrases from pages",
  "skills":
  [
    {
      "description": "Extract text (plain and structured) from image.",
      "@odata.type": "#Microsoft.Skills.Vision.OcrSkill",
      "context": "/document/normalized_images/*",
      "defaultLanguageCode": "en",
      "detectOrientation": True,
      "inputs": [
        {
          "name": "image",
          "source": "/document/normalized_images/*"
        }
      ],
      "outputs": [
        {
          "name": "text"
        }
      ]
    },
    {
      "@odata.type": "#Microsoft.Skills.Text.MergeSkill",
      "description": "Create merged_text, which includes all the textual representation of each image inserted at the right location in the content field.",
      "context": "/document",
      "insertPreTag": " ",
      "insertPostTag": " ",
      "inputs": [
        {
          "name":"text", "source": "/document/content"
        },
        {
          "name": "itemsToInsert", "source": "/document/normalized_images/*/text"
        },
        {
          "name":"offsets", "source": "/document/normalized_images/*/contentOffset"
        }
      ],
      "outputs": [
        {
          "name": "mergedText", "targetName" : "merged_text"
        }
      ]
    },
    {
      "@odata.type": "#Microsoft.Skills.Text.SplitSkill",
      "textSplitMode" : "pages",
      "maximumPageLength": 4000,
      "inputs": [
        { "name": "text", "source": "/document/content" }
      ],
      "outputs": [
        { "name": "textItems", "targetName": "pages" }
      ]
    },
    {
      "@odata.type": "#Microsoft.Skills.Text.KeyPhraseExtractionSkill",
      "context": "/document/pages/*",
      "inputs": [
        { "name": "text", "source": "/document/pages/*" }
      ],
      "outputs": [
        { "name": "keyPhrases", "targetName": "keyPhrases" }
      ]
    }
  ],
    "cognitiveServices": {
        "@odata.type": "#Microsoft.Azure.Search.CognitiveServicesByKey",
        "description": "MOSL Demo Cognitive Services",
        "key": "051bdf5fa88c450daa423ba3975fc2cd"
    }
}

#  The below is a template for incorporating custom skills into cognitive search

    # {
    #   "@odata.type": "#Microsoft.Skills.Custom.WebApiSkill",
    #   "description": "This skill extracts genetic codes from text",
    #   "uri": "<amls_skill_uri>",
    #   "context": "/document/pages/*",
    #   "httpHeaders": {
    #     "Authorization": "Bearer <amls_skill_key>"
    #   },
    #   "inputs": [
    #     { "name" : "text", "source": "/document/pages/*"}
    #   ],
    #   "outputs": [
    #     { "name": "genetic_codes", "targetName": "genetic_codes" }
    #   ]
    # }


skillset_name = "mosl-demo-skillset"
uri = f"https://{service_name}.search.windows.net/skillsets/{skillset_name}?api-version={api_version}"

resp = requests.put(uri, headers = headers, data = json.dumps(skillset))
print(resp.status_code)
print(resp.ok)


# Create Azure Cognitive Search Index

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
      "filterable": False,
      "facetable": False,
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
    }
  ]
}


index_name = "mosl-demo-index"
uri = f"https://{service_name}.search.windows.net/indexes/{index_name}?api-version={api_version}"

resp = requests.put(uri, headers = headers, data = json.dumps(index))
print(resp.status_code)
print(resp.ok)

# Create Azure Cognitive Search Indexer

indexer_name = "mosl-demo-indexer"

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

# Check on status

uri = f"https://{service_name}.search.windows.net/indexers/{indexer_name}/status?api-version={api_version}"

resp = requests.get(uri, headers=headers)
print(resp.status_code)
print(resp.json().get('lastResult').get('status'))
print(resp.ok)


# Querying the Azure Cognitive Search Index

url = "https://{}.search.windows.net/indexes/{}/docs".format(service_name, index_name)
url += "?api-version={}".format(api_version)
url += "&search=correction"
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