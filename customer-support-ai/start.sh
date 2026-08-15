#!/usr/bin/env bash
set -e

echo "=========================================================="
echo "🚀 Initializing TechMart Multi-Agent AI Support Backend"
echo "=========================================================="

PORT=${PORT:-8000}
INDEX_FILE="vectorstore/faiss_index.bin"
METADATA_FILE="vectorstore/faiss_metadata.json"

# Check if FAISS index and metadata exist; if not, automatically ingest documents
if [ ! -f "$INDEX_FILE" ] || [ ! -f "$METADATA_FILE" ]; then
    echo "📦 FAISS vector index not found. Running automated document ingestion..."
    python backend/scripts/ingest_documents.py || echo "⚠️ Warning: Automated ingestion encountered issues. Continuing startup..."
else
    echo "✅ FAISS vector index and metadata verified."
fi

echo "🌐 Starting Uvicorn server on port ${PORT}..."
exec uvicorn backend.main:app --host 0.0.0.0 --port "${PORT}" --workers 1
