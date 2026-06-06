# 🏁 Installation & Setup Guide

Follow these steps to get HybridRAG running on your local machine.

## 📋 Prerequisites

Ensure you have the following installed:
- **Python 3.10+**: [Download](https://www.python.org/downloads/)
- **Node.js v18+**: [Download](https://nodejs.org/)
- **Ollama**: [Download](https://ollama.com/)
- **MongoDB**: Either a local instance or a [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) account.

---

## 🛠️ Step-by-Step Setup

### 1. Model Preparation
HybridRAG uses local models for reasoning and embeddings. Pull them using Ollama:
```bash
ollama pull llama3
ollama pull nomic-embed-text
```

### 2. Clone and Install
```bash
# Clone the repository
git clone https://github.com/your-username/HybridRAG.git
cd HybridRAG

# Install Backend dependencies (Python)
pip install -r requirements.txt

# Install Frontend dependencies (Node.js)
cd client
npm install
cd ..
```

### 3. Environment Configuration
Create a `.env` file in `apps/api/` based on the example:

```env
# apps/api/.env
MONGODB_URL=mongodb+srv://<user>:<password>@cluster.mongodb.net/
MONGODB_DATABASE=Hybridrag
MONGODB_DOCUMENTS_COLLECTION=documents
MONGODB_CHUNKS_COLLECTION=chunks

# Provider settings
EMBEDDING_PROVIDER=local
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBEDDING_MODEL=nomic-embed-text:latest
```

---

## 🚀 Running the Stack

You can start the entire stack using the root `package.json` scripts:

```bash
# Run both API and Client concurrently
npm run dev
```

Alternatively, start them separately:

**Backend (FastAPI):**
```bash
python -m uvicorn apps.api.main:app --reload --port 8000
```

**Frontend (Vite/React):**
```bash
cd client && npm run dev
```

**Ingestion Dashboard (Streamlit):**
```bash
python -m streamlit run apps/dashboard/streamlit_app.py
```

---

## 🔍 Verification
Once running, visit:
- **Frontend**: `http://localhost:5173`
- **API Health**: `http://localhost:8000/api/health`
- **API Docs (Swagger)**: `http://localhost:8000/docs`
