"""
ingest_documents.py
CLI ingestion utility to parse all PDFs in knowledge_base/, embed chunks, and build the FAISS vector index.
Usage:
    python backend/scripts/ingest_documents.py [--kb-dir PATH]
"""

import sys
import os
import time
import argparse
from pathlib import Path

# Safe UTF-8 console output for Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.embeddings.embedder import get_embedder
from backend.vectorstore.faiss_store import get_faiss_store
from backend.rag.pipeline import process_all_sources


def main():
    parser = argparse.ArgumentParser(description="Ingest Knowledge Base PDFs and Datasets into FAISS vector index.")
    parser.add_argument(
        "--kb-dir",
        type=str,
        default=str(PROJECT_ROOT / "knowledge_base"),
        help="Path to directory containing PDF documents",
    )
    parser.add_argument(
        "--datasets-dir",
        type=str,
        default=str(PROJECT_ROOT / "datasets"),
        help="Path to directory containing datasets CSV files",
    )
    parser.add_argument(
        "--index-path",
        type=str,
        default=str(PROJECT_ROOT / "backend" / "vectorstore" / "faiss_index.bin"),
        help="Path to output FAISS index binary",
    )
    parser.add_argument(
        "--metadata-path",
        type=str,
        default=str(PROJECT_ROOT / "backend" / "vectorstore" / "faiss_metadata.json"),
        help="Path to output metadata JSON",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=512,
        help="Chunk size in characters",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=50,
        help="Chunk overlap in characters",
    )
    args = parser.parse_args()

    kb_dir = Path(args.kb_dir)
    datasets_dir = Path(args.datasets_dir)
    index_path = Path(args.index_path)
    metadata_path = Path(args.metadata_path)

    print("\n" + "=" * 65)
    print(">> Starting TechMart Multi-Agent RAG Ingestion (KB + Datasets)...")
    print("=" * 65)
    print(f"Knowledge Base Dir: {kb_dir}")
    print(f"Datasets Dir:       {datasets_dir}")
    print(f"Output Index Path:  {index_path}")
    print(f"Output Meta Path:   {metadata_path}")
    print(f"Chunk Parameters:   size={args.chunk_size}, overlap={args.chunk_overlap}")
    print("-" * 65)

    start_time = time.time()

    # 1. Process all documents and datasets
    chunks = process_all_sources(
        kb_directory=kb_dir,
        datasets_directory=datasets_dir,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )

    if not chunks:
        print(f"[ERROR] No chunks extracted. Ensure PDF files are placed in '{kb_dir}'.")
        sys.exit(1)

    print(f"\nExtracted {len(chunks)} text chunks across all documents.")

    # 2. Extract chunk texts for batch embedding
    texts = [c["text"] for c in chunks]

    # 3. Generate embeddings
    embedder = get_embedder()
    print(f"Generating 384-dim embeddings for {len(texts)} chunks...")
    embeddings = embedder.encode_batch(texts, normalize=True, batch_size=32)
    print(f"[OK] Generated embeddings matrix of shape: {embeddings.shape}")

    # 4. Build and save FAISS store
    store = get_faiss_store()
    store.index_path = index_path
    store.metadata_path = metadata_path

    print("Building FAISS IndexFlatIP (cosine similarity)...")
    store.build_index(embeddings)
    store.metadata = chunks
    store.save(index_path=index_path, metadata_path=metadata_path)

    elapsed = round(time.time() - start_time, 2)
    print("=" * 65)
    print(f"[SUCCESS] Ingestion completed in {elapsed}s!")
    print(f"   • Total Chunks Indexed: {len(chunks)}")
    print(f"   • Index File:           {index_path} ({os.path.getsize(index_path):,} bytes)")
    print(f"   • Metadata File:        {metadata_path} ({os.path.getsize(metadata_path):,} bytes)")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
