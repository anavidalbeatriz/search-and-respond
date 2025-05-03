import os
import io
import tempfile
from dotenv import load_dotenv
from config import BUCKET_NAME, PGVECTOR_CONNECTION_STRING
from google.cloud import storage

from langchain_core.documents import Document
from langchain_community.document_loaders import UnstructuredWordDocumentLoader, PyPDFLoader
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores.pgvector import PGVector

from agent_instructions import get_agent_instructions

load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./google-key.json"

# ✅ GCS authentication check
client = storage.Client()
buckets = list(client.list_buckets())
print("✅ GCS authentication successful. Buckets found:", [b.name for b in buckets])

def load_documents_from_gcs():
    """Load all documents from GCS bucket."""
    bucket = client.bucket(BUCKET_NAME)
    all_documents = []
    loaded_files = 0
    skipped_files = 0

    # List all blobs (files) in the bucket
    all_blobs = [blob.name for blob in bucket.list_blobs()]
    print("All blobs in bucket:", all_blobs)

    for blob_path in all_blobs:
        try:
            blob = bucket.blob(blob_path)
            filename = os.path.basename(blob_path)
            file_bytes = blob.download_as_bytes()

            if filename.endswith(".pdf"):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                    tmp_pdf.write(file_bytes)
                    tmp_pdf.flush()
                    loader = PyPDFLoader(tmp_pdf.name)
            elif filename.endswith(".docx"):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_docx:
                    tmp_docx.write(file_bytes)
                    tmp_docx.flush()
                    loader = UnstructuredWordDocumentLoader(file_path=tmp_docx.name, mode="elements")
            else:
                print(f"⚠️ Skipping unsupported file type: {filename}")
                skipped_files += 1
                continue

            documents = loader.load()
            for doc in documents:
                document = Document(
                    page_content=doc.page_content,
                    metadata={"source": blob_path, "file_name": filename}
                )
                all_documents.append(document)

            print(f"✅ Loaded: {filename}")
            print(f"   📄 Metadata: {document.metadata}")
            loaded_files += 1

        except Exception as e:
            print(f"❌ Error loading {blob_path} from GCS: {e}")
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

def run_agent(query: str):
    documents = load_documents_from_gcs()
    index = create_index(documents)
    qa_chain = create_qa_chain(index)

    instructed_query = get_agent_instructions(query)
    response = qa_chain.run(instructed_query)

    if "Sorry, I cannot answer that" in response:
        return "Sorry, I don't have information about that topic."
    return response

if __name__ == "__main__":
    while True:
        query = input("\n🔎 Enter your query (or type 'exit' to quit): ")
        if query.lower() == 'exit':
            print("👋 Exiting...")
            break

        answer = run_agent(query)
        print("🧠 Model's answer:", answer)
