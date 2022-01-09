
# az group create --name test-rg --location westeurope
# az storage account create --name moslcogsearchdemo --resource-group test-rg --location westeurope
# az storage account show-connection-string --name moslcogsearchdemo

# Import required python modules

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
