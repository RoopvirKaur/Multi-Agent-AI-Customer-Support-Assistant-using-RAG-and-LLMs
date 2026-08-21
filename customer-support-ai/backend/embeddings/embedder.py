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
    Ultra-lightweight Embedder with ONNX FastEmbed and SentenceTransformers fallback.
    Prevents import errors on Render while keeping memory footprint low.
    """

    _instance = None
    _model = None

    def __new__(cls, model_name: str = "BAAI/bge-small-en-v1.5"):
        if cls._instance is None:
            cls._instance = super(Embedder, cls).__new__(cls)
            cls._instance.model_name = model_name
            cls._instance._model = None
            cls._instance._is_fastembed = False
        return cls._instance

    @property
    def model(self):
        if self._model is None:
            trim_memory()
            try:
                from fastembed import TextEmbedding
                print(f"Loading lightweight ONNX embedding model: {self.model_name}...")
                self._model = TextEmbedding(model_name=self.model_name)
                self._is_fastembed = True
                print("✅ ONNX FastEmbed model loaded successfully (~40MB RAM footprint).")
            except Exception as e:
                print(f"FastEmbed unavailable ({e}). Fallback to SentenceTransformer...")
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")
                self._is_fastembed = False
            trim_memory()
        return self._model

    def encode(self, text: str, normalize: bool = True) -> np.ndarray:
        """
        Encode a single text string into a 384-dimensional float32 vector.
        """
        if not text or not text.strip():
            return np.zeros((384,), dtype=np.float32)

        clean_text = text.strip()
        model_obj = self.model
        if getattr(self, "_is_fastembed", False):
            vectors = list(model_obj.embed([clean_text]))
            vec = np.array(vectors[0], dtype=np.float32)
            if normalize:
                norm = np.linalg.norm(vec)
                if norm > 0:
                    vec = vec / norm
            return vec
        else:
            vector = model_obj.encode(
                clean_text,
                normalize_embeddings=normalize,
                show_progress_bar=False,
                convert_to_numpy=True,
            )
            return np.array(vector, dtype=np.float32)

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
        model_obj = self.model
        if getattr(self, "_is_fastembed", False):
            vectors_list = list(model_obj.embed(cleaned_texts, batch_size=batch_size))
            arr = np.array(vectors_list, dtype=np.float32)
            if normalize:
                norms = np.linalg.norm(arr, axis=1, keepdims=True)
                norms[norms == 0] = 1.0
                arr = arr / norms
            return arr
        else:
            vectors = model_obj.encode(
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
