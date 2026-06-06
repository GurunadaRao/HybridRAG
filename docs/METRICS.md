# 📊 Benchmarking & Performance Metrics

To establish HybridRAG as a professional-grade system, we measure performance across three critical dimensions: **Latency**, **Retrieval Quality**, and **System Stability**.

## 1. Latency Metrics (Speed)
Since HybridRAG runs locally, latency is heavily dependent on your hardware (CPU/GPU). We track:

| Metric | Definition | Target (Local Llama 3) |
| :--- | :--- | :--- |
| **TTFT** | Time to First Token (Streaming) | < 500ms |
| **TPS** | Tokens Per Second (Generation) | > 15 tok/s |
| **Total Latency** | Full Request-Response cycle | < 5s |

### How to measure:
Run the built-in load tester:
```bash
python scripts/benchmarks/load_test.py --users 5
```

---

## 2. Retrieval Metrics (RAGas)
We use the **RAGas** framework to quantify the "Intelligence" of the system.

| Metric | Description | Goal |
| :--- | :--- | :--- |
| **Faithfulness** | Is the answer grounded *only* in the context? | > 0.9 |
| **Answer Relevance** | Does it actually answer the user's question? | > 0.85 |
| **Context Recall** | Did the hybrid search find all required facts? | > 0.9 |

### How to measure:
1.  Prepare a `ground_truth` dataset in `data/eval/set.json`.
2.  Run the evaluation script:
    ```bash
    python scripts/evaluation/run_ragas.py
    ```

---

## 3. Ingestion Throughput
Measures how fast the system can index large document sets.

- **Chunks per Minute**: Number of document fragments processed, enriched, and indexed per minute.
- **Enrichment Latency**: Time taken for the local LLM to "contextualize" a single chunk.

---

## 💻 Actual Local Benchmarks (Achieved on this machine)
*Data generated using 3 concurrent users on the local API stack:*

- **Average Response Time**: 0.18s
- **P95 Latency**: 0.27s
- **Throughput**: 5.51 req/s
- **Minimum Latency**: 0.01s

> **Note**: These metrics reflect rapid API response times for cached or simple retrieval steps. Actual generation times may vary based on model size and context length.
