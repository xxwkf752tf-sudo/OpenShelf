"""RAGRetriever - context retrieval for agent queries."""
from src.rag.indexer import RAGIndexer

class RAGRetriever:
    def __init__(self, indexer=None):
        self._indexer = indexer or RAGIndexer()

    def retrieve_context(self, query, n_results=5):
        results = self._indexer.query(query, n_results=n_results)
        context = "\n\n".join([f"// File: {r.get('metadata',{}).get('path','unknown')}\n{r.get('content','')}" for r in results])
        return {"context": context, "sources": [r.get("metadata",{}).get("path","") for r in results], "count": len(results)}
