# 🚀 HybridRAG: Agentic Local-First Intelligence

![HybridRAG Banner](hybridrag_banner_1778914834249.png)

HybridRAG is a state-of-the-art, **local-first** Retrieval-Augmented Generation system. It combines the power of **LangGraph** agentic workflows with a hybrid search engine (Vector + Lexical) to provide private, high-performance intelligence on your own hardware.

---

## 📖 Documentation Index

### 1. 🏁 [Getting Started](./docs/INSTALLATION.md)
*   Prerequisites (Ollama, Python, Node.js)
*   Local setup & Environment variables
*   Running the development stack

### 2. 🏗️ [Architecture Deep-Dive](./docs/ARCHITECTURE.md)
*   The Agentic Loop (LangGraph)
*   Hybrid Retrieval (Vector + BM25)
*   Contextual Chunking & Enrichment
*   Data Flow Diagrams

### 3. 🛠️ [API Reference](./docs/API.md)
*   Ingestion endpoints
*   Query & Agentic reasoning endpoints
*   WebSocket/Streaming support

### 4. 🧪 [Testing & Evaluation](./docs/TESTING.md)
*   Unit & Integration tests
*   RAGas evaluation pipeline
*   Benchmarking local LLMs

### 5. 🤝 [Contributing](./CONTRIBUTING.md)
*   Coding standards
*   Pull Request process
*   Community guidelines

---

## ✨ Key Features

- **🧠 Agentic Reasoning**: Powered by LangGraph for multi-turn reasoning and self-grading.
- **🔍 Hybrid Search**: Merges Semantic (ChromaDB) and Lexical (BM25) search using RRF.
- **📄 Contextual Chunking**: Enriches document fragments with high-level summaries.
- **🛡️ Privacy First**: Zero data leakage; runs entirely on local models via Ollama.
- **💎 Premium UI**: Modern glassmorphism React dashboard with real-time streaming.

---

## 🚦 Quick Start (TL;DR)

```bash
# 1. Pull models
ollama pull llama3
ollama pull nomic-embed-text

# 2. Install dependencies
npm install
pip install -r requirements.txt

# 3. Start the stack
npm run dev
```

---

## 🗺️ Roadmap

- [ ] **Streaming Support**: Real-time token streaming in the UI.
- [ ] **Multi-Modal**: Support for image-based RAG.
- [ ] **Graph Visualization**: Interactive nodes showing retrieved chunk relationships.

---

<p align="center">Built with ❤️ for the Privacy-Conscious AI Community</p>
