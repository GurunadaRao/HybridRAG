from rank_bm25 import BM25Okapi
from typing import List, Dict, Any

class BM25Index:
    def __init__(self):
        self.bm25 = None
        self.documents: List[Dict[str, Any]] = []
        self.tokenized_corpus: List[List[str]] = []

    def _tokenize(self, text: str) -> List[str]:
        # Simple whitespace tokenizer for now. Can be replaced with better tokenizer.
        return text.lower().split()

    def add_documents(self, texts: List[str], metadatas: List[Dict[str, Any]]):
        if len(texts) != len(metadatas):
            raise ValueError("Number of texts must match number of metadata entries")
            
        tokenized = [self._tokenize(text) for text in texts]
        self.tokenized_corpus.extend(tokenized)
        self.documents.extend(metadatas)
        
        self.bm25 = BM25Okapi(self.tokenized_corpus)

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if not self.bm25 or not self.documents:
            return []
            
        tokenized_query = self._tokenize(query)
        doc_scores = self.bm25.get_scores(tokenized_query)
        
        # Get top_k indices sorted by score descending
        top_indices = sorted(range(len(doc_scores)), key=lambda i: doc_scores[i], reverse=True)[:top_k]
        
        results = []
        for idx in top_indices:
            if doc_scores[idx] > 0: # Only include relevant docs
                res = self.documents[idx].copy()
                res["bm25_score"] = float(doc_scores[idx])
                results.append(res)
        return results
