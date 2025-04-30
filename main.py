import os
from config import BUCKET_NAME, SOURCE_BLOB_NAME, LOCAL_PATH, PGVECTOR_CONNECTION_STRING
from dotenv import load_dotenv

from google.cloud import storage
from langchain_core.documents import Document
from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores.pgvector import PGVector

# Import the instructions from the separate file
from agent_instructions import get_agent_instructions

load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./google-key.json"

# ✅ GCS authentication check
client = storage.Client()
buckets = list(client.list_buckets())
print("✅ GCS authentication successful. Buckets found:", [b.name for b in buckets])

def download_pdf_from_gcs(bucket_name, source_blob_name, destination_file_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    os.makedirs(os.path.dirname(destination_file_name), exist_ok=True)
    blob.download_to_filename(destination_file_name)
    print(f"Downloaded {source_blob_name} to {destination_file_name}.")

def load_documents():
    all_documents = []
    loaded_files = 0
    skipped_files = 0

    for blob_path in SOURCE_BLOB_NAME:
        local_path = os.path.join(LOCAL_PATH, os.path.basename(blob_path))
        download_pdf_from_gcs(BUCKET_NAME, blob_path, local_path)

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
            for doc in documents:
                document = Document(
                    page_content=doc.page_content,
                    metadata={"source": local_path, "file_name": os.path.basename(local_path)}
                )
                all_documents.append(document)
                print(f"✅ Loaded: {local_path}")
                print(f"   📄 Metadata: {document.metadata}")

            loaded_files += 1

        except Exception as e:
            print(f"❌ Error loading {local_path}: {e}")
            skipped_files += 1

    print(f"\n📊 Summary:")
    print(f"   ✅ Loaded files: {loaded_files}")
    print(f"   ⚠️ Skipped files: {skipped_files}")
    print(f"   📄 Total documents loaded: {len(all_documents)}")
    return all_documents

def create_index(documents):
    print("🔍 Generating embeddings with Gemini...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    print("📦 Creating PGVector index...")
    vector_store = PGVector.from_documents(
        documents=documents,
        embedding=embeddings,
        connection_string=PGVECTOR_CONNECTION_STRING,
        collection_name="document_embeddings"
    )
    print("✅ PGVector index created and stored.")
    return vector_store

def create_qa_chain(index):
    retriever = index.as_retriever()
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    return RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

def run_agent():
    documents = load_documents()
    index = create_index(documents)
    qa_chain = create_qa_chain(index)

    while True:
        query = input("\n🔎 Enter your query (or type 'exit' to quit): ")
        if query.lower() == 'exit':
            print("👋 Exiting...")
            break
        
        # Get the query with agent instructions from the separate file
        instructed_query = get_agent_instructions(query)

        # Get the response from the model
        response = qa_chain.run(instructed_query)
        
        # If the model response is not ideal (e.g., doesn't have an answer), provide a fallback
        if "Sorry, I cannot answer that" in response:
            print("🧠 Model's answer: Sorry, I don't have information about that topic.")
        else:
            print("🧠 Model's answer:", response)

if __name__ == "__main__":
    run_agent()
