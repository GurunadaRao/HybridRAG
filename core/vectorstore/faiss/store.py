import faiss
import numpy as np
from typing import List, Dict, Any

class FAISSStore:
    def __init__(self, embedding_dimension: int):
        self.index = faiss.IndexFlatL2(embedding_dimension)
        self.metadata: List[Dict[str, Any]] = []

    def add_embeddings(self, embeddings: List[List[float]], metadatas: List[Dict[str, Any]]):
        if len(embeddings) != len(metadatas):
            raise ValueError("Number of embeddings must match number of metadata entries")
        
        vectors = np.array(embeddings).astype('float32')
        self.index.add(vectors)
        self.metadata.extend(metadatas)

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        if self.index.ntotal == 0:
            return []
            
        vector = np.array([query_embedding]).astype('float32')
        distances, indices = self.index.search(vector, top_k)
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx != -1 and idx < len(self.metadata):
                res = self.metadata[idx].copy()
                res["vector_score"] = float(dist) # Lower is better for L2
                results.append(res)
        return results
