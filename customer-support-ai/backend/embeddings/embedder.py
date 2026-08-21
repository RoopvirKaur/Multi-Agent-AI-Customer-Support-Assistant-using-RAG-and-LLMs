"""
embedder.py
Sentence Transformers embedding generator for Multi-Agent RAG.
Model: sentence-transformers/all-MiniLM-L6-v2 (384-dim vectors)
"""

import os
from typing import List, Union
import numpy as np
import torch

# Limit PyTorch CPU thread count to minimize RAM footprint on cloud containers
try:
    torch.set_num_threads(1)
    if hasattr(torch, "set_num_interop_threads"):
        torch.set_num_interop_threads(1)
except Exception:
    pass

from sentence_transformers import SentenceTransformer

DEFAULT_EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
)


import gc
import ctypes

def trim_memory():
    """
    Force Garbage Collector and glibc memory allocator (libc.so.6 malloc_trim)
    to release unallocated C++ heap memory back to the OS on Linux/Docker containers.
    Drastically reduces RSS memory consumption on Render 512MB free tier.
    """
    gc.collect()
    try:
        ctypes.CDLL("libc.so.6").malloc_trim(0)
    except Exception:
        pass


class Embedder:
    """
    Singleton Embedder wrapper around SentenceTransformer.
    Ensures the embedding model is loaded once into memory lazily.
    """

    _instance = None
    _model = None

    def __new__(cls, model_name: str = DEFAULT_EMBEDDING_MODEL):
        if cls._instance is None:
            cls._instance = super(Embedder, cls).__new__(cls)
            cls._instance.model_name = model_name
            cls._instance._model = None
        return cls._instance

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            print(f"Loading embedding model: {self.model_name}...")
            trim_memory()
            with torch.no_grad():
                self._model = SentenceTransformer(self.model_name, device="cpu")
                self._model.eval()
            trim_memory()
            print("Embedding model loaded successfully.")
        return self._model

    def encode(self, text: str, normalize: bool = True) -> np.ndarray:
        """
        Encode a single text string into a 384-dimensional float32 vector.
        """
        if not text or not text.strip():
            return np.zeros((384,), dtype=np.float32)

        with torch.no_grad():
            vector = self.model.encode(
                text.strip(),
                normalize_embeddings=normalize,
                show_progress_bar=False,
                convert_to_numpy=True,
            )
        return np.array(vector, dtype=np.float32)

    def encode_batch(
        self,
        texts: List[str],
        normalize: bool = True,
        batch_size: int = 32,
    ) -> np.ndarray:
        """
        Encode a list of text strings into an (N, 384) float32 numpy array.
        """
        if not texts:
            return np.empty((0, 384), dtype=np.float32)

        cleaned_texts = [t.strip() if t and t.strip() else " " for t in texts]
        vectors = self.model.encode(
            cleaned_texts,
            normalize_embeddings=normalize,
            batch_size=batch_size,
            show_progress_bar=False,
        )
        return np.array(vectors, dtype=np.float32)


# Global helper instance
embedder = Embedder()


def get_embedder() -> Embedder:
    """Dependency / accessor function to retrieve global Embedder instance."""
    return embedder
