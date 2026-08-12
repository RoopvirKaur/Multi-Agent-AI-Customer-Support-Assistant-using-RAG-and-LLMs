"""
Document Ingestion API Endpoints
Routes: /api/ingest/upload, /api/ingest/documents
"""

import os
from pathlib import Path
from typing import List, Dict
from fastapi import APIRouter, UploadFile, File, HTTPException, status

router = APIRouter(prefix="/ingest", tags=["Document Ingestion"])

KNOWLEDGE_BASE_DIR = Path(__file__).resolve().parent.parent.parent / "knowledge_base"


@router.post(
    "/upload",
    summary="Upload a PDF document to the knowledge base",
)
async def upload_document(
    file: UploadFile = File(...),
):
    """
    Accept PDF document uploads:
    - Verifies file format is PDF
    - Saves document to knowledge_base directory
    - In Phase 4, automatically triggers embedding & FAISS vectorstore update
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

    return {
        "status": "received",
        "filename": file.filename,
        "size_bytes": len(content),
        "message": f"Document '{file.filename}' uploaded successfully. Vector ingestion will process this in Phase 4.",
    }


@router.get(
    "/documents",
    summary="List all available documents in the knowledge base",
)
async def list_documents() -> Dict[str, List[str]]:
    """
    List all PDF files currently stored in the knowledge base directory.
    """
    KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)
    files = [f.name for f in KNOWLEDGE_BASE_DIR.glob("*.pdf")]
    return {"documents": sorted(files)}
