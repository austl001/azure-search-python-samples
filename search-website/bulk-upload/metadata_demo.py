
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import json
import pandas as pd

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

df = pd.DataFrame(pd.read_pickle("bulk-upload/blob.metadata.pkl"))

for blob in blobs_pdf_list:
    df_blob = df[df["FileName"] == blob]
    metadata = df_blob.to_dict(orient = "records")[0]
    blob_client = BlobClient.from_connection_string(
        container_name = container_name,
        blob_name = blob,
        conn_str = connection_string
    )
    blob_client.set_blob_metadata(metadata = metadata)
