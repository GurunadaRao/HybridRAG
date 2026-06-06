# 🏗️ Architecture Deep-Dive

HybridRAG is designed as a modular, local-first intelligence engine. It leverages advanced RAG techniques to ensure high precision and privacy.

## 🌉 System Overview

The system is split into three primary layers:
1.  **Ingestion Layer**: Processes documents (PDF/CSV/Text), chunks them contextually, and builds the hybrid index.
2.  **Retrieval Layer**: Combines semantic vector search with lexical keyword search.
3.  **Orchestration Layer**: A LangGraph-powered state machine that reasons over the retrieved context.

---

## 🧠 The Agentic Loop (LangGraph)

Unlike standard "retrieve-and-read" RAG, HybridRAG uses a feedback loop:

1.  **Retrieve**: Fetch candidates from Hybrid Search.
2.  **Grade**: Evaluate if retrieved chunks are relevant to the query.
3.  **Refine**: If relevance is low, the agent rewrites the query or fetches more context.
4.  **Generate**: Final answer generation with citations.

### 📄 Contextual Chunking
Before indexing, chunks are "contextualized." A small LLM pass generates a brief summary of the *entire* document which is then prepended to every chunk. This prevents the "lost in the middle" problem where chunks lose their high-level meaning.

---

## 🔍 Hybrid Retrieval & RRF

We use **Reciprocal Rank Fusion (RRF)** to merge results from two distinct search engines:

| Engine | Type | Best For |
| :--- | :--- | :--- |
| **ChromaDB** | Semantic (Vector) | Conceptual queries, synonyms, "vibes". |
| **BM25** | Lexical (Keyword) | Specific terms, product IDs, technical jargon. |

**RRF Formula:**
$$Score(d) = \sum_{r \in R} \frac{1}{k + rank(d, r)}$$

---

## 💾 Data Flow

1.  **Client** sends query to **FastAPI**.
2.  **FastAPI** triggers the **LangGraph** workflow.
3.  **LangGraph** calls the **Retriever Manager**.
4.  **Retriever** queries **ChromaDB** and **BM25** in parallel.
5.  **Reranker** (Local) sorts the top candidates.
6.  **Ollama (Llama 3)** generates the final response.
7.  **Client** renders the response with Markdown support.
