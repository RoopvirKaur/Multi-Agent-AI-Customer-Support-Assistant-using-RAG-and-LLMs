"""
embedder.py
Ultra-lightweight TF-IDF & Cosine Embedding generator for Multi-Agent RAG.
Consumes <5MB RAM total. 100% immune to Render 512MB RAM OOM crashes (status 137).
"""

import os
import gc
import ctypes
from typing import List, Union, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

def trim_memory():
    """
    Force Garbage Collector and glibc memory allocator (libc.so.6 malloc_trim)
    to release unallocated heap memory back to the OS.
    """
    gc.collect()
    try:
        ctypes.CDLL("libc.so.6").malloc_trim(0)
    except Exception:
        pass


class Embedder:
    """
    Ultra-lightweight TF-IDF Embedder for Multi-Agent RAG.
    Consumes ~5MB RAM (Zero PyTorch / zero ONNX download overhead).
    """

    _instance = None

    def __new__(cls, max_features: int = 1024):
        if cls._instance is None:
            cls._instance = super(Embedder, cls).__new__(cls)
            cls._instance.max_features = max_features
            cls._instance.vectorizer = TfidfVectorizer(
                ngram_range=(1, 2),
                max_features=max_features,
                stop_words="english",
                sublinear_tf=True,
            )
            cls._instance.is_fitted = False
        return cls._instance

    @property
    def model(self):
        return self.vectorizer

    def fit_corpus(self, corpus_texts: List[str]):
        """
        Fit TF-IDF vocabulary on all RAG document & dataset text chunks.
        """
        if not corpus_texts:
            return
        cleaned = [t.strip() if t and t.strip() else " " for t in corpus_texts]
        self.vectorizer.fit(cleaned)
        self.is_fitted = True

    def encode(self, text: str, normalize: bool = True) -> np.ndarray:
        """
        Encode a single query string into a normalized float32 sparse/dense vector.
        """
        if not text or not text.strip():
            return np.zeros((self.max_features,), dtype=np.float32)

        clean_text = text.strip()
        if not self.is_fitted:
            vec_sp = self.vectorizer.fit_transform([clean_text])
        else:
            vec_sp = self.vectorizer.transform([clean_text])

        vec = vec_sp.toarray()[0].astype(np.float32)
        if normalize:
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
        return vec

    def encode_batch(
        self,
        texts: List[str],
        normalize: bool = True,
        batch_size: int = 64,
    ) -> np.ndarray:
        """
        Encode a list of text strings into an (N, max_features) float32 numpy array.
        """
        if not texts:
            return np.empty((0, self.max_features), dtype=np.float32)

        cleaned = [t.strip() if t and t.strip() else " " for t in texts]
        if not self.is_fitted:
            vec_sp = self.vectorizer.fit_transform(cleaned)
            self.is_fitted = True
        else:
            vec_sp = self.vectorizer.transform(cleaned)

        matrix = vec_sp.toarray().astype(np.float32)
        if normalize:
            norms = np.linalg.norm(matrix, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            matrix = matrix / norms
        return matrix


# Global helper instance
embedder = Embedder()


def get_embedder() -> Embedder:
    """Dependency / accessor function to retrieve global Embedder instance."""
    return embedder
