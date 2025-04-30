import os
from config import BUCKET_NAME, SOURCE_BLOB_NAME, LOCAL_PATH

# Load documents from a PDF (downloaded from GCS)
def load_documents():
    all_documents = []
    loaded_files = 0
    skipped_files = 0

    for blob_path in SOURCE_BLOB_NAME:
        local_path = os.path.join(LOCAL_PATH, os.path.basename(blob_path))
        download_pdf_from_gcs(BUCKET_NAME, blob_path, local_path)

        # Determine file loader by extension
        try:
            if local_path.endswith(".pdf"):
                loader = PyPDFLoader(local_path)
            elif local_path.endswith(".docx"):
                loader = Docx2txtLoader(local_path)
            else:
                print(f"⚠️ Skipping unsupported file type: {local_path}")
                skipped_files += 1
                continue

            documents = loader.load()
            all_documents.extend(documents)
            loaded_files += 1
            print(f"✅ Loaded: {local_path}")

        except Exception as e:
            print(f"❌ Error loading {local_path}: {e}")
            skipped_files += 1

    print(f"\n📊 Summary:")
    print(f"   ✅ Loaded files: {loaded_files}")
    print(f"   ⚠️ Skipped files: {skipped_files}")
    print(f"   📄 Total documents loaded: {len(all_documents)}")
    return all_documents

from dotenv import load_dotenv
load_dotenv()

from google.cloud import storage

def download_pdf_from_gcs(bucket_name, source_blob_name, destination_file_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    # ✅ Make sure the local directory exists
    os.makedirs(os.path.dirname(destination_file_name), exist_ok=True)

    blob.download_to_filename(destination_file_name)
    print(f"Downloaded {source_blob_name} to {destination_file_name}.")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./google-key.json"

client = storage.Client()
buckets = list(client.list_buckets())
print("✅ GCS authentication successful. Buckets found:", [b.name for b in buckets])

from langchain_community.document_loaders import Docx2txtLoader
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS

# Load environment variables
load_dotenv()

# Generate embeddings using Gemini and create a FAISS index
def create_index(documents):
    print("🔍 Generating embeddings with Gemini...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_documents(documents, embeddings)
    print("📦 Index created!")
    return vector_store

# Create the QA chain using Gemini
def create_qa_chain(index):
    retriever = index.as_retriever()
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    return RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

# Run the agent with user input
def run_agent():
    documents = load_documents()
    index = create_index(documents)
    qa_chain = create_qa_chain(index)

    while True:
        query = input("\n🔎 Enter your query (or type 'exit' to quit): ")
        if query.lower() == 'exit':
            print("👋 Exiting...")
            break
        response = qa_chain.run(query)
        print("🧠 Model's answer:", response)

# Execute the script
if __name__ == "__main__":
    run_agent()
