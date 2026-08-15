"""
faiss_store.py
FAISS Vector Store wrapper for indexing, storing, loading, and searching chunk embeddings.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import numpy as np
import faiss

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
VECTORSTORE_DIR = Path(__file__).resolve().parent


def resolve_store_path(env_var: str, default_filename: str) -> Path:
    """
    Resolve index / metadata path directly to backend/vectorstore/ directory
    or custom configured path.
    """
    raw = os.getenv(env_var)
    if raw:
        p = Path(raw)
        if p.is_absolute():
            return p
        # If relative path like ./vectorstore/faiss_index.bin, map to backend/vectorstore/faiss_index.bin
        filename = p.name
        return VECTORSTORE_DIR / filename

    return VECTORSTORE_DIR / default_filename


class FAISSStore:
    """
    Manages FAISS IndexFlatIP index and associated metadata JSON for RAG retrieval.
    """

    def __init__(
        self,
        dimension: int = 384,
        index_path: Optional[Path] = None,
        metadata_path: Optional[Path] = None,
    ):
        self.dimension = dimension
        self._index_path = Path(index_path) if index_path else None
        self._metadata_path = Path(metadata_path) if metadata_path else None
        self.index: Optional[faiss.IndexFlatIP] = None
        self.metadata: List[Dict] = []

    @property
    def index_path(self) -> Path:
        if self._index_path:
            return self._index_path
        return resolve_store_path("FAISS_INDEX_PATH", "faiss_index.bin")

    @index_path.setter
    def index_path(self, value: Path):
        self._index_path = Path(value)

    @property
    def metadata_path(self) -> Path:
        if self._metadata_path:
            return self._metadata_path
        return resolve_store_path("FAISS_METADATA_PATH", "faiss_metadata.json")

    @metadata_path.setter
    def metadata_path(self, value: Path):
        self._metadata_path = Path(value)

    def build_index(self, embeddings: np.ndarray) -> faiss.IndexFlatIP:
        """
        Build a fresh FAISS IndexFlatIP (cosine similarity on normalized vectors).
        """
        if embeddings.ndim != 2 or embeddings.shape[1] != self.dimension:
            raise ValueError(
                f"Expected embeddings shape (N, {self.dimension}), got {embeddings.shape}"
            )

        embeddings_f32 = np.ascontiguousarray(embeddings, dtype=np.float32)
        index = faiss.IndexFlatIP(self.dimension)
        index.add(embeddings_f32)
        self.index = index
        return index

    def save(
        self,
        index_path: Optional[Path] = None,
        metadata_path: Optional[Path] = None,
    ):
        """
        Persist FAISS index binary and metadata JSON to disk.
        """
        idx_p = Path(index_path) if index_path else self.index_path
        meta_p = Path(metadata_path) if metadata_path else self.metadata_path

        idx_p.parent.mkdir(parents=True, exist_ok=True)
        meta_p.parent.mkdir(parents=True, exist_ok=True)

        if self.index is not None:
            faiss.write_index(self.index, str(idx_p))

        with open(meta_p, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)

        print(f"FAISS index saved to {idx_p} ({self.index.ntotal if self.index else 0} vectors)")
        print(f"Metadata saved to {meta_p} ({len(self.metadata)} items)")

    def load(
        self,
        index_path: Optional[Path] = None,
        metadata_path: Optional[Path] = None,
    ) -> bool:
        """
        Load FAISS index and metadata from disk. Returns True if successful.
        """
        idx_p = Path(index_path) if index_path else self.index_path
        meta_p = Path(metadata_path) if metadata_path else self.metadata_path

        if not idx_p.exists() or not meta_p.exists():
            return False

        try:
            self.index = faiss.read_index(str(idx_p))
            with open(meta_p, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
            return True
        except Exception as e:
            print(f"Error loading FAISS store: {e}")
            return False

    def add_vectors_and_metadata(
        self,
        embeddings: np.ndarray,
        new_metadata: List[Dict],
    ):
        """
        Incrementally add new vectors and metadata items to existing or newly created index.
        """
        if len(new_metadata) == 0:
            return

        embeddings_f32 = np.ascontiguousarray(embeddings, dtype=np.float32)

        if self.index is None:
            self.index = faiss.IndexFlatIP(self.dimension)

        self.index.add(embeddings_f32)
        self.metadata.extend(new_metadata)

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 5,
    ) -> List[Tuple[Dict, float]]:
        """
        Perform nearest neighbor cosine search for query_vector.
        Returns list of (metadata_item, score).
        """
        if self.index is None or self.index.ntotal == 0:
            return []

        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)

        query_f32 = np.ascontiguousarray(query_vector, dtype=np.float32)
        k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(query_f32, k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1 and idx < len(self.metadata):
                results.append((self.metadata[idx], float(score)))

        return results


# Global singleton instance
faiss_store = FAISSStore()


def get_faiss_store() -> FAISSStore:
    """Dependency / accessor function to retrieve global FAISSStore instance."""
    return faiss_store
