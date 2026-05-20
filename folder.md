contextual-rag-system/
│
├── README.md
├── .env
├── .gitignore
├── requirements.txt
├── docker-compose.yml
├── pyproject.toml
├── Makefile
│
├── apps/
│ │
│ ├── api/ # Main FastAPI backend
│ │ ├── main.py
│ │ ├── dependencies.py
│ │ ├── middleware.py
│ │ ├── config.py
│ │ │
│ │ ├── routes/
│ │ │ ├── health.py
│ │ │ ├── chat.py
│ │ │ ├── ingest.py
│ │ │ ├── retrieval.py
│ │ │ ├── rerank.py
│ │ │ └── admin.py
│ │ │
│ │ ├── schemas/
│ │ │ ├── chat.py
│ │ │ ├── ingestion.py
│ │ │ ├── retrieval.py
│ │ │ └── response.py
│ │ │
│ │ ├── controllers/
│ │ │ ├── chat_controller.py
│ │ │ ├── ingest_controller.py
│ │ │ └── retrieval_controller.py
│ │ │
│ │ └── utils/
│ │ ├── logger.py
│ │ ├── validators.py
│ │ └── helpers.py
│ │
│ ├── worker/ # Async workers
│ │ ├── celery_app.py
│ │ ├── ingestion_worker.py
│ │ ├── embedding_worker.py
│ │ ├── rerank_worker.py
│ │ └── cleanup_worker.py
│ │
│ └── dashboard/ # Optional admin dashboard
│ ├── app.py
│ ├── pages/
│ └── components/
│
├── core/
│ │
│ ├── ingestion/
│ │ ├── pdf/
│ │ │ ├── pymupdf_loader.py
│ │ │ ├── pdf_parser.py
│ │ │ ├── image_extractor.py
│ │ │ └── table_extractor.py
│ │ │
│ │ ├── json/
│ │ │ ├── json_loader.py
│ │ │ └── json_cleaner.py
│ │ │
│ │ ├── preprocessing/
│ │ │ ├── cleaner.py
│ │ │ ├── deduplicator.py
│ │ │ ├── metadata_extractor.py
│ │ │ └── language_detector.py
│ │ │
│ │ └── pipeline.py
│ │
│ ├── chunking/
│ │ ├── recursive_splitter.py
│ │ ├── semantic_splitter.py
│ │ ├── contextual_chunker.py
│ │ ├── overlap_manager.py
│ │ └── chunk_validator.py
│ │
│ ├── embeddings/
│ │ ├── **init**.py
│ │ ├── base.py
│ │ ├── factory.py
│ │ ├── local/
│ │ │ └── ollama.py
│ │ ├── cloud/
│ │ │ └── huggingface.py
│ │ ├── embedding_cache.py
│ │ └── vector_normalizer.py
│ │
│ ├── contextualization/
│ │ ├── prompt_templates/
│ │ │ ├── contextual_prompt.txt
│ │ │ ├── summary_prompt.txt
│ │ │ └── metadata_prompt.txt
│ │ │
│ │ ├── context_generator.py
│ │ ├── chunk_summarizer.py
│ │ ├── metadata_enricher.py
│ │ └── compression.py
│ │
│ ├── vectorstore/
│ │ ├── qdrant/
│ │ │ ├── qdrant_client.py
│ │ │ ├── collections.py
│ │ │ └── indexing.py
│ │ │
│ │ ├── faiss/
│ │ │ └── faiss_store.py
│ │ │
│ │ └── hybrid_store.py
│ │
│ ├── bm25/
│ │ ├── bm25_indexer.py
│ │ ├── elasticsearch_client.py
│ │ └── tokenizer.py
│ │
│ ├── retrieval/
│ │ ├── vector_retriever.py
│ │ ├── bm25_retriever.py
│ │ ├── hybrid_retriever.py
│ │ ├── reciprocal_rank_fusion.py
│ │ ├── metadata_filtering.py
│ │ ├── query_expansion.py
│ │ ├── hyde_retrieval.py
│ │ └── retrieval_pipeline.py
│ │
│ ├── reranking/
│ │ ├── bge_reranker.py
│ │ ├── cross_encoder.py
│ │ ├── rerank_pipeline.py
│ │ └── score_normalizer.py
│ │
│ ├── llm/
│ │ ├── providers/
│ │ │ ├── gemini_provider.py
│ │ │ ├── openai_provider.py
│ │ │ ├── anthropic_provider.py
│ │ │ └── openrouter_provider.py
│ │ │
│ │ ├── prompt_manager.py
│ │ ├── response_generator.py
│ │ ├── citation_generator.py
│ │ ├── hallucination_guard.py
│ │ └── token_counter.py
│ │
│ ├── memory/
│ │ ├── conversation_memory.py
│ │ ├── session_store.py
│ │ └── summarization_memory.py
│ │
│ ├── evaluation/
│ │ ├── ragas/
│ │ │ ├── faithfulness.py
│ │ │ ├── relevance.py
│ │ │ └── precision.py
│ │ │
│ │ ├── benchmark_runner.py
│ │ ├── latency_tracker.py
│ │ └── evaluation_pipeline.py
│ │
│ ├── observability/
│ │ ├── tracing.py
│ │ ├── metrics.py
│ │ ├── logging.py
│ │ ├── prompt_logs.py
│ │ └── token_usage.py
│ │
│ └── security/
│ ├── auth.py
│ ├── rate_limiter.py
│ ├── api_keys.py
│ └── permissions.py
│
├── infrastructure/
│ │
│ ├── docker/
│ │ ├── api.Dockerfile
│ │ ├── worker.Dockerfile
│ │ └── nginx.conf
│ │
│ ├── kubernetes/
│ │ ├── deployment.yaml
│ │ ├── service.yaml
│ │ ├── ingress.yaml
│ │ └── secrets.yaml
│ │
│ ├── terraform/
│ │ ├── main.tf
│ │ ├── variables.tf
│ │ └── outputs.tf
│ │
│ └── monitoring/
│ ├── prometheus.yml
│ └── grafana/
│
├── data/
│ │
│ ├── raw/
│ │ ├── pdfs/
│ │ ├── json/
│ │ └── uploads/
│ │
│ ├── processed/
│ │ ├── chunks/
│ │ ├── contextual_chunks/
│ │ └── embeddings/
│ │
│ ├── cache/
│ │ ├── embeddings/
│ │ ├── prompts/
│ │ └── retrieval/
│ │
│ └── exports/
│
├── notebooks/
│ ├── chunking_experiments.ipynb
│ ├── embedding_tests.ipynb
│ ├── reranking_analysis.ipynb
│ └── retrieval_benchmarks.ipynb
│
├── scripts/
│ ├── ingest_documents.py
│ ├── rebuild_indexes.py
│ ├── benchmark.py
│ ├── migrate_embeddings.py
│ └── cleanup.py
│
├── tests/
│ │
│ ├── unit/
│ │ ├── test_chunking.py
│ │ ├── test_embeddings.py
│ │ ├── test_reranker.py
│ │ └── test_retrieval.py
│ │
│ ├── integration/
│ │ ├── test_ingestion_pipeline.py
│ │ ├── test_rag_pipeline.py
│ │ └── test_hybrid_search.py
│ │
│ └── evaluation/
│ ├── retrieval_quality.py
│ └── hallucination_tests.py
│
└── docs/
├── architecture/
│ ├── system_design.md
│ ├── sequence_diagrams.md
│ └── scalability.md
│
├── api/
│ └── openapi.json
│
├── deployment/
│ ├── docker_setup.md
│ └── kubernetes_setup.md
│
└── research/
├── contextual_rag.md
├── reranking.md
└── hybrid_search.md
