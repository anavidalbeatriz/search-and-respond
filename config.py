# config.py
import os
from dotenv import load_dotenv
load_dotenv()

BUCKET_NAME = "shared-resources-sample"
SOURCE_BLOB_NAME = [
    "project-planning/[Guidelines] Project Change.docx",
    "project-planning/[Guidelines] Project Planning - work in progress.docx",
    "project-planning/[Guidelines] Project Planning.docx"
]
LOCAL_PATH = "C:/Users/AnaBeatrizVidal/Downloads/search-and-respond-main/search-and-respond-main/docs"
PGVECTOR_CONNECTION_STRING = os.getenv("PGVECTOR_CONNECTION_STRING")
