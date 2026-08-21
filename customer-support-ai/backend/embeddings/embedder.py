"""
embedder.py
Ultra-lightweight ONNX Embedding generator for Multi-Agent RAG.
Model: BAAI/bge-small-en-v1.5 via fastembed (ONNX C++ runtime ~40MB RAM footprint)
Zero PyTorch memory overhead. Prevents 512MB OOM crashes on Render free tier.
"""

import os
import gc
import ctypes
from typing import List
import numpy as np

def trim_memory():
    """
    Force Garbage Collector and glibc memory allocator (libc.so.6 malloc_trim)
    to release unallocated C++ heap memory back to the OS on Linux/Docker containers.
    """
    gc.collect()
    try:
        ctypes.CDLL("libc.so.6").malloc_trim(0)
    except Exception:
        pass


class Embedder:
    """
    Ultra-lightweight ONNX FastEmbed Embedder.
    Consumes ~40MB RAM (Zero PyTorch memory overhead).
    """

    _instance = None
    _model = None

    def __new__(cls, model_name: str = "BAAI/bge-small-en-v1.5"):
        if cls._instance is None:
            cls._instance = super(Embedder, cls).__new__(cls)
            cls._instance.model_name = model_name
            cls._instance._model = None
        return cls._instance

    @property
    def model(self):
        if self._model is None:
            trim_memory()
            from fastembed import TextEmbedding
            print(f"Loading lightweight ONNX embedding model: {self.model_name}...")
            self._model = TextEmbedding(model_name=self.model_name)
            trim_memory()
            print("✅ ONNX FastEmbed model loaded successfully (~40MB RAM footprint).")
        return self._model

    def encode(self, text: str, normalize: bool = True) -> np.ndarray:
        """
        Encode a single text string into a 384-dimensional float32 vector using ONNX runtime.
        """
        if not text or not text.strip():
            return np.zeros((384,), dtype=np.float32)

        clean_text = text.strip()
        vectors = list(self.model.embed([clean_text]))
        vec = np.array(vectors[0], dtype=np.float32)
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
        Encode a list of text strings into an (N, 384) float32 numpy array.
        """
        if not texts:
            return np.empty((0, 384), dtype=np.float32)

        cleaned_texts = [t.strip() if t and t.strip() else " " for t in texts]
        vectors_list = list(self.model.embed(cleaned_texts, batch_size=batch_size))
        arr = np.array(vectors_list, dtype=np.float32)
        if normalize:
            norms = np.linalg.norm(arr, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            arr = arr / norms
        return arr


# Global helper instance
embedder = Embedder()


def get_embedder() -> Embedder:
    """Dependency / accessor function to retrieve global Embedder instance."""
    return embedder
