from typing import List, Dict, Any

def reciprocal_rank_fusion(
    vector_results: List[Dict[str, Any]], 
    bm25_results: List[Dict[str, Any]], 
    k: int = 60,
    top_n: int = 5
) -> List[Dict[str, Any]]:
    """
    Combines results from multiple search methods using Reciprocal Rank Fusion (RRF).
    Assumes results are already sorted by their respective relevance (best first).
    """
    
    rrf_scores: Dict[str, float] = {}
    combined_docs: Dict[str, Dict[str, Any]] = {}
    
    # Process vector results
    for rank, doc in enumerate(vector_results):
        doc_id = str(doc.get("_id", doc.get("chunk_index", str(rank))))
        if doc_id not in combined_docs:
            combined_docs[doc_id] = doc
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
        
    # Process BM25 results
    for rank, doc in enumerate(bm25_results):
        doc_id = str(doc.get("_id", doc.get("chunk_index", str(rank))))
        if doc_id not in combined_docs:
            combined_docs[doc_id] = doc
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
        
    # Sort by RRF score descending
    sorted_docs = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    
    final_results = []
    for doc_id, score in sorted_docs[:top_n]:
        res = combined_docs[doc_id].copy()
        res["rrf_score"] = score
        final_results.append(res)
        
    return final_results
