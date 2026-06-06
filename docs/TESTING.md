# 🧪 Testing & Evaluation

Quality assurance in RAG systems requires both code tests and behavioral evaluation.

## ⚙️ Running Tests

### Unit Tests
Test individual components like the retriever, chunker, and LLM wrappers.
```bash
$env:PYTHONPATH="."
pytest tests/unit/core
```

### Integration Tests
Test the full flow from API request to Agent response.
```bash
pytest tests/integration
```

---

## 📈 RAG Evaluation (RAGas)

We use **RAGas** (Retrieval Augmented Generation Assessment) to quantify performance.

### Metrics Tracked:
1.  **Faithfulness**: Does the answer only contain facts found in the context?
2.  **Answer Relevance**: Does the answer directly address the user's query?
3.  **Context Precision**: Are the most relevant chunks ranked at the top?
4.  **Context Recall**: Were all necessary facts retrieved?

### Running Evaluation
Check the `scripts/evaluation` directory for RAGas scripts.
```bash
python scripts/evaluation/run_ragas.py --dataset test_set.json
```
