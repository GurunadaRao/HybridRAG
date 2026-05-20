from typing import List, Dict, Any

class Reranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        try:
            from sentence_transformers import CrossEncoder
            self.model = CrossEncoder(model_name)
        except ImportError:
            self.model = None
            print("Warning: sentence-transformers not installed. Reranker is a pass-through.")

    def rerank(self, query: str, documents: List[Dict[str, Any]], text_key: str = "text") -> List[Dict[str, Any]]:
        if not documents:
            return []
            
        if self.model is None:
            # Fallback if sentence-transformers is not available
            return documents
            
        pairs = [[query, doc.get(text_key, "")] for doc in documents]
        scores = self.model.predict(pairs)
        
        for doc, score in zip(documents, scores):
            doc["rerank_score"] = float(score)
            
        # Sort descending by rerank score
        return sorted(documents, key=lambda x: x["rerank_score"], reverse=True)
