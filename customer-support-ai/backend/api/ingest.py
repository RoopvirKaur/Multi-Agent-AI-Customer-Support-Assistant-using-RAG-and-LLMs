"""
Document Ingestion API Endpoints
Routes: /api/ingest/upload, /api/ingest/documents, /api/ingest/stats
"""

import os
from pathlib import Path
from typing import List, Dict, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status

from backend.rag.pipeline import process_document, assign_agent_scope
from backend.embeddings.embedder import get_embedder
from backend.vectorstore.faiss_store import get_faiss_store

router = APIRouter(prefix="/ingest", tags=["Document Ingestion"])

KNOWLEDGE_BASE_DIR = Path(__file__).resolve().parent.parent.parent / "knowledge_base"


@router.post(
    "/upload",
    summary="Upload a PDF document and ingest into FAISS vectorstore",
)
async def upload_document(
    file: UploadFile = File(...),
    custom_scope: Optional[str] = Form(None),
):
    """
    Accept PDF document uploads:
    - Verifies file format is PDF
    - Saves document to knowledge_base directory
    - Processes document into chunks
    - Generates embeddings with SentenceTransformer
    - Appends vectors and metadata to active FAISS index and persists to disk
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files (.pdf) are supported for knowledge base ingestion.",
        )

    # Ensure knowledge_base directory exists
    KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)
    destination_path = KNOWLEDGE_BASE_DIR / file.filename

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    with open(destination_path, "wb") as f:
        f.write(content)

    # 1. Process document into chunks
    custom_scopes_list = (
        [s.strip() for s in custom_scope.split(",") if s.strip()]
        if custom_scope
        else None
    )
    try:
        chunks = process_document(
            destination_path,
            custom_scopes=custom_scopes_list,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract and chunk PDF document: {str(e)}",
        )

    if not chunks:
        return {
            "status": "warning",
            "filename": file.filename,
            "size_bytes": len(content),
            "chunks_indexed": 0,
            "message": "File uploaded but no text content could be extracted.",
        }

    # 2. Generate embeddings
    embedder = get_embedder()
    texts = [c["text"] for c in chunks]
    embeddings = embedder.encode_batch(texts, normalize=True)

    # 3. Add to FAISS vectorstore and save
    store = get_faiss_store()
    # Load existing if available
    store.load()
    store.add_vectors_and_metadata(embeddings, chunks)
    store.save()

    return {
        "status": "success",
        "filename": file.filename,
        "size_bytes": len(content),
        "chunks_indexed": len(chunks),
        "assigned_scopes": chunks[0]["scopes"],
        "total_vectors_in_store": store.index.ntotal if store.index else 0,
        "message": f"Successfully ingested '{file.filename}' with {len(chunks)} chunks added to vector store.",
    }


@router.get(
    "/documents",
    summary="List all available documents in the knowledge base",
)
async def list_documents() -> Dict[str, List[Dict]]:
    """
    List all PDF files currently stored in the knowledge base directory with metadata.
    """
    KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(list(KNOWLEDGE_BASE_DIR.glob("*.pdf")))
    doc_list = []
    for f in files:
        doc_list.append(
            {
                "filename": f.name,
                "size_bytes": f.stat().st_size,
                "scopes": assign_agent_scope(f.name),
            }
        )
    return {"documents": doc_list}


@router.get(
    "/stats",
    summary="Get FAISS vectorstore indexing statistics",
)
async def get_vectorstore_stats():
    """
    Retrieve statistics regarding the loaded vector store index and chunks.
    """
    store = get_faiss_store()
    store.load()

    total_vectors = store.index.ntotal if store.index else 0
    total_metadata = len(store.metadata)

    # Count by scope
    scope_counts: Dict[str, int] = {}
    for item in store.metadata:
        for s in item.get("scopes", []):
            scope_counts[s] = scope_counts.get(s, 0) + 1

    return {
        "total_vectors": total_vectors,
        "total_chunks": total_metadata,
        "embedding_dimension": store.dimension,
        "scope_distribution": scope_counts,
        "index_file_exists": store.index_path.exists(),
        "metadata_file_exists": store.metadata_path.exists(),
    }
