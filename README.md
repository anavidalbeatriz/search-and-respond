# 🧠 Search-and-Respond Agent (LangChain + Gemini + pgvector)

This project is an intelligent document-based Q&A system using **LangChain**, **Gemini**, and **pgvector**, integrated with **Google Cloud Storage**. It allows users to ask questions via a web interface, and the backend retrieves relevant answers from `.docx` and `.pdf` documents stored in GCS.

---

## 📁 Project Structure

. ├── agent-query-app/ # React frontend ├── app.py # Flask API server ├── main.py # Core logic: loads documents, runs agent ├── config.py # Config settings (e.g., GCS paths, DB string) ├── agent_instructions.py # Prompt customization for the agent ├── requirements.txt ├── .env ├── .gitignore └── google-key.json # GCP service account key (excluded from git)


---

## 🧰 Prerequisites

- Python 3.9+
- Node.js (for frontend)
- PostgreSQL with [pgvector extension](https://github.com/pgvector/pgvector)
- Google Cloud Project with access to a bucket
- Service account JSON key

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/search-and-respond.git
cd search-and-respond

### 2. Creat the .env file

GOOGLE_APPLICATION_CREDENTIALS=./google-key.json
PGVECTOR_CONNECTION_STRING=postgresql+psycopg2://<username>:<password>@localhost:<port>/<database>
BUCKET_NAME=your-gcs-bucket-name
LOCAL_PATH=./downloads
SOURCE_BLOB_NAME=["path/in/gcs/file1.pdf", "path/in/gcs/file2.docx"]

Replace <username>, <password>, <port>, and <database> with your actual PostgreSQL credentials.

### 3. Set Up Python Environment

python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

pip install -r requirements.txt

### 4. Enable PostgreSQL pgvector

🧠 pgvector PostgreSQL with Docker
This project provides a simple Docker setup to run a PostgreSQL database with the pgvector extension enabled, which is used for storing and querying vector embeddings (e.g., for AI/ML apps).

🐳 Quickstart
1. Clone the Repository
git clone https://github.com/yourusername/your-repo.git
cd your-repo

2. Start the Database
Make sure Docker is installed and running on your machine. Then run:
docker-compose up -d
This will:
Build the image using the provided Dockerfile
Start a PostgreSQL instance on port 5433
Create a database called vectordb with the pgvector extension

3. Connect to the Database
You can connect to the database using any PostgreSQL client. For example:
psql -h localhost -p 5433 -U postgres -d vectordb
Password: mysecretpassword

🧠 Tip: Use tools like pgAdmin or DBeaver for GUI-based access.

🚀 Running the Backend
Start the Flask API

python app.py

💻 Running the Frontend (React)
1. Go to the frontend folder:
cd agent-query-app

2. Install dependencies and start the app
npm install
npm start

✍️ How to Ask Questions
Just type your question into the UI. The agent will:

Load documents from GCS (in memory, not downloaded)

Use Gemini to embed and query them

Return relevant answers based on vector search

📚 Custom Agent Instructions
Modify agent_instructions.py to guide how the agent should respond (e.g., tone, fallback behavior, forbidden topics).


