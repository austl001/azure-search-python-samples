
import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import json

# Instantiate blob service using connection string from Azure CLI when creating storage account

with open("api/local.settings.json") as read_file:
    config = json.load(read_file)

service_name = config["Values"]["SearchServiceName"]
api_version = config["Values"]["ApiVersion"]
connection_string = config["Values"]["BlobConnectionString"]

blob_service_client = BlobServiceClient.from_connection_string(connection_string)

container_name = "mosl-pdf-container"

container_client = blob_service_client.get_container_client(container_name)

blob_list = container_client.list_blobs()
blobs_pdf_list = []
for blob in blob_list:
    blobs_pdf_list.append(blob.name)
print(blobs_pdf_list)
len(blobs_pdf_list)

# Setting meta data

metadata1 = {"Test1":"TRUE", "Test2":"FALSE", "Test3":"2021-01-01"}
metadata2 = {"Test1":"FALSE", "Test2":"TRUE", "Test3":"2020-06-01"}

for blob in blobs_pdf_list[0:24]: 
    blob_client = BlobClient.from_connection_string(
    container_name = container_name, 
    blob_name = blob, 
    conn_str = connection_string
    )
    blob_client.set_blob_metadata(metadata = metadata1)

for blob in blobs_pdf_list[24:49]:
    blob_client = BlobClient.from_connection_string(
        container_name = container_name,
        blob_name = blob,
        conn_str = connection_string
    )
    blob_client.set_blob_metadata(metadata = metadata2)

