# Quickstart Guide: AI-native Textbook with RAG Chatbot

This guide provides instructions to quickly set up and run the Docusaurus frontend and FastAPI backend for the AI-native Textbook with RAG Chatbot.

## Prerequisites

Ensure you have the following installed:

*   **Node.js** (LTS version) & **npm** (for Docusaurus frontend)
*   **Python 3.9+** & **pip** (for FastAPI backend)
*   **Docker** (for Qdrant vector database and Neon PostgreSQL database, or direct installation/cloud service access)

## 1. Backend Setup (FastAPI, Qdrant, Neon)

Navigate to the `backend/` directory.

```bash
cd backend
```

### 1.1. Database Setup (Qdrant & Neon/PostgreSQL)

It is recommended to use Docker for local development. Create a `docker-compose.yaml` file in the `backend/` directory (or use existing if available) with services for Qdrant and a PostgreSQL database (Neon can be used as a cloud-hosted PostgreSQL solution for production/staging).

**Example `docker-compose.yaml` (simplified):**

```yaml
version: '3.8'
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - ./qdrant_data:/qdrant/data
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: rag_db
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - ./pg_data:/var/lib/postgresql/data
```

Start the database services:

```bash
docker-compose up -d
```

Configure your FastAPI application to connect to these services (e.g., via environment variables in a `.env` file).

### 1.2. FastAPI Application

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Run the FastAPI application:

```bash
uvicorn main:app --reload
```

The backend API will be accessible at `http://localhost:8000` (or as configured).

## 2. Frontend Setup (Docusaurus)

Navigate to the `frontend/` directory.

```bash
cd frontend
```

Install Node.js dependencies:

```bash
npm install
```

Start the Docusaurus development server:

```bash
npm start
```

The Docusaurus site will be accessible at `http://localhost:3000`.

## 3. Running the Complete Application

1.  Ensure your backend services (Qdrant, PostgreSQL, FastAPI) are running as described in Section 1.
2.  Ensure your Docusaurus frontend is running as described in Section 2.
3.  Access the textbook at `http://localhost:3000` and interact with the RAG chatbot.

## Next Steps

*   Populate the Qdrant instance with textbook embeddings via the CMS ingestion API.
*   Implement authentication and personalization features.
*   Write comprehensive tests for both frontend and backend components.