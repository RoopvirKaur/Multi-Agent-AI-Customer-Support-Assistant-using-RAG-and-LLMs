"""
retriever.py
Agent-scoped semantic retriever for Multi-Agent RAG.
Queries FAISS vectorstore and filters by domain agent scope.
"""

from typing import List, Dict, Optional
import numpy as np
from backend.embeddings.embedder import get_embedder
from backend.vectorstore.faiss_store import get_faiss_store


class Retriever:
    """
    Retriever that takes a customer query, embeds it, and performs vector
    similarity search over FAISS with agent-scope metadata filtering.
    """

    def __init__(self):
        self.embedder = get_embedder()
        self.store = get_faiss_store()

    def ensure_index_loaded(self) -> bool:
        """
        Ensure the FAISS index and metadata are loaded in memory and fit TF-IDF embedder.
        """
        loaded = True
        if self.store.index is None or len(self.store.metadata) == 0:
            loaded = self.store.load()

        if loaded and self.store.metadata and not getattr(self.embedder, "is_fitted", True):
            texts = [m.get("text", "") for m in self.store.metadata if m.get("text")]
            if texts:
                self.embedder.fit_corpus(texts)
        return loaded

    def retrieve(
        self,
        query: str,
        agent_scope: Optional[str] = None,
        top_k: int = 5,
        min_similarity: float = 0.0,
    ) -> List[Dict]:
        """
        Retrieve relevant knowledge base chunks for a query.

        Args:
            query: User or agent inquiry string.
            agent_scope: Optional agent domain filter ('billing', 'technical', 'product', 'complaint', 'faq').
            top_k: Maximum number of chunks to return.
            min_similarity: Minimum cosine similarity score threshold (0.0 to 1.0).

        Returns:
            List of matching chunk dicts with 'score', 'document', 'page', 'text', 'scopes'.
        """
        if not query or not query.strip():
            return []

        if not self.ensure_index_loaded():
            print("Warning: FAISS store could not be loaded; vector index may not exist yet.")
            return []

        # 1. Embed query vector
        query_vec = self.embedder.encode(query.strip(), normalize=True)

        # 2. Search FAISS candidate pool across all index items when filtering by scope
        candidate_k = len(self.store.metadata) if agent_scope and self.store.metadata else top_k
        raw_results = self.store.search(query_vec, top_k=candidate_k)

        # 3. Filter by agent_scope and similarity threshold
        filtered_results = []
        normalized_scope = (
            agent_scope.lower().replace("_agent", "").replace("_support", "").strip()
            if agent_scope
            else None
        )

        for meta, score in raw_results:
            if score < min_similarity:
                continue

            if normalized_scope:
                scopes = [s.lower() for s in meta.get("scopes", [])]
                # Include if agent scope matches or if scope is 'all' / general
                if normalized_scope not in scopes and "all" not in scopes:
                    continue

            result_item = {
                "chunk_id": meta.get("chunk_id"),
                "document": meta.get("document"),
                "document_title": meta.get("document_title"),
                "page": meta.get("page"),
                "scopes": meta.get("scopes", []),
                "text": meta.get("text", ""),
                "score": round(score, 4),
            }
            filtered_results.append(result_item)

            if len(filtered_results) >= top_k:
                break

        return filtered_results


# Global singleton retriever
retriever = Retriever()


def get_retriever() -> Retriever:
    """Dependency accessor function to retrieve global Retriever instance."""
    return retriever
