# config.py

import os
from dotenv import load_dotenv
from google.cloud import storage
from google.oauth2 import service_account

# Load environment variables from .env
load_dotenv()

BUCKET_NAME = "shared-resources-sample"
GOOGLE_KEY_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
PGVECTOR_CONNECTION_STRING = os.getenv("PGVECTOR_CONNECTION_STRING")

# Debug: check if the key path is loaded correctly and exists
print("Key path:", GOOGLE_KEY_PATH)
print("File exists?", os.path.exists(GOOGLE_KEY_PATH))

# Load credentials and set up Google Cloud Storage client
credentials = service_account.Credentials.from_service_account_file(GOOGLE_KEY_PATH)
storage_client = storage.Client(credentials=credentials, project=credentials.project_id)
bucket = storage_client.bucket(BUCKET_NAME)

def list_all_blobs():
    """Lists all blob names in the bucket."""
    return [blob.name for blob in bucket.list_blobs()]

def load_blob_content(blob_name):
    """Returns the content of a blob as bytes."""
    blob = bucket.blob(blob_name)
    return blob.download_as_bytes()

# Dynamically fetch all blobs in the bucket
all_blobs = list_all_blobs()
print("All blobs in bucket:", all_blobs)

# Set SOURCE_BLOB_NAME to the list of all blobs found
SOURCE_BLOB_NAME = all_blobs if all_blobs else None

# Ensure that the source blob list is not empty
if not SOURCE_BLOB_NAME:
    print("No blobs found in the bucket.")
else:
    print("Using the following SOURCE_BLOB_NAMES:", SOURCE_BLOB_NAME)
