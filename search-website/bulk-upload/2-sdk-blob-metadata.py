
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

# Get list of blobs

blob_list = container_client.list_blobs()

blobs_list = []

for blob in blob_list:
    blobs_list.append(blob.name)

for blob in blobs_list:
    print(blob)

# Retrieving metadata as dataframe

df = pd.DataFrame(pd.read_pickle("bulk-upload/blob.metadata.pkl"))

df_blobs = pd.DataFrame({"FileName" : blobs_list})

# Check length of metadata file is the same as list of blobs

len(df_blobs) == len(df)

len(set(df_blobs["FileName"]))

len(df["FileName"])

all(item in blobs_list for item in df["FileName"])

df_meta = df_blobs.join(df.set_index("FileName"), on = "FileName")

# Upload metdata

for blob in blobs_list:
    df_blob = df_meta[df_meta["FileName"] == blob]
    metadata = df_blob.to_dict(orient = "records")[0]
    blob_client = BlobClient.from_connection_string(
        container_name = container_name,
        blob_name = blob,
        conn_str = connection_string
    )
    blob_client.set_blob_metadata(metadata = metadata)

