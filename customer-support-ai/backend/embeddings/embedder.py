"""
embedder.py
Ultra-lightweight ONNX Embedding generator for Multi-Agent RAG.
Primary: fastembed (ONNX runtime ~40MB RAM footprint, zero OOM on Render 512MB limit)
Fallback: sentence-transformers / PyTorch
"""

import os
import gc
import ctypes
from typing import List, Union, Any
import numpy as np

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
    Ultra-lightweight ONNX-backed Embedder (with sentence-transformers fallback).
    Consumes ~40MB RAM instead of ~500MB PyTorch RAM.
    """

    _instance = None

    def __new__(cls, model_name: str = "BAAI/bge-small-en-v1.5"):
        if cls._instance is None:
            cls._instance = super(Embedder, cls).__new__(cls)
            cls._instance.model_name = model_name
            cls._instance._fastembed_model = None
            cls._instance._st_model = None
            cls._instance._use_fastembed = True
        return cls._instance

    @property
    def model(self) -> Any:
        if self._fastembed_model is not None or self._st_model is not None:
            return self._fastembed_model or self._st_model

        trim_memory()
        try:
            from fastembed import TextEmbedding
            print(f"Loading ONNX embedding model: {self.model_name} (RAM lightweight)...")
            self._fastembed_model = TextEmbedding(model_name=self.model_name)
            self._use_fastembed = True
            print("✅ ONNX FastEmbed model loaded successfully (~40MB RAM footprint).")
            trim_memory()
            return self._fastembed_model
        except Exception as err:
            print(f"FastEmbed unavailable ({err}). Falling back to SentenceTransformers...")
            self._use_fastembed = False
            from sentence_transformers import SentenceTransformer
            self._st_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")
            self._st_model.eval()
            trim_memory()
            return self._st_model

    def encode(self, text: str, normalize: bool = True) -> np.ndarray:
        """
        Encode a single text string into a 384-dimensional float32 vector.
        """
        if not text or not text.strip():
            return np.zeros((384,), dtype=np.float32)

        _ = self.model  # Ensure model is initialized
        clean_text = text.strip()

        if self._use_fastembed and self._fastembed_model is not None:
            vectors = list(self._fastembed_model.embed([clean_text]))
            vec = np.array(vectors[0], dtype=np.float32)
            if normalize:
                norm = np.linalg.norm(vec)
                if norm > 0:
                    vec = vec / norm
            return vec
        else:
            vector = self._st_model.encode(
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
        batch_size: int = 32,
    ) -> np.ndarray:
        """
        Encode a list of text strings into an (N, 384) float32 numpy array.
        """
        if not texts:
            return np.empty((0, 384), dtype=np.float32)

        _ = self.model
        cleaned_texts = [t.strip() if t and t.strip() else " " for t in texts]

        if self._use_fastembed and self._fastembed_model is not None:
            vectors_list = list(self._fastembed_model.embed(cleaned_texts, batch_size=batch_size))
            arr = np.array(vectors_list, dtype=np.float32)
            if normalize:
                norms = np.linalg.norm(arr, axis=1, keepdims=True)
                norms[norms == 0] = 1.0
                arr = arr / norms
            return arr
        else:
            vectors = self._st_model.encode(
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
