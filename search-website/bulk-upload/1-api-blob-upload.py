
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

# container_client = blob_service_client.create_container(container_name)

container_client = blob_service_client.get_container_client(container_name)

# DELETE BLOBS AS REQUIRED:

'''content = container_client.list_blobs()

for blob in content:
    container_client.delete_blob(blob.name) '''


## FIRST UPLOAD
# Check what files there are:

file_location = os.getcwd() + "/bulk-upload/upload-documents-1"

for file in os.listdir(file_location):
    print(file)

# Iterate through files and upload to blob storage account

for file in os.listdir(file_location): 
    blob_client = blob_service_client.get_blob_client(
        container = container_name,
        blob = file
    )
    with open(os.path.join(file_location, file), "rb") as data:
        blob_client.upload_blob(data)

## SECOND UPLOAD
# Check what files there are:

file_location = os.getcwd() + "/bulk-upload/upload-documents-2"

for file in os.listdir(file_location):
    print(file)

# Iterate through files and upload to blob storage account

for file in os.listdir(file_location):
    blob_client = blob_service_client.get_blob_client(
        container = container_name,
        blob = file
    )
    with open(os.path.join(file_location, file), "rb") as data:
        blob_client.upload_blob(data)

# check files have been uploaded

blob_list = container_client.list_blobs()

blob_counter = 0

for blob in blob_list:
    blob_counter += 1
    print(blob.name)

print(blob_counter)
