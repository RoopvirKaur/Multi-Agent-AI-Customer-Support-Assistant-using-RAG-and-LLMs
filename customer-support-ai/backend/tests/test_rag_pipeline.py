"""
test_rag_pipeline.py
Unit tests for Sub-phase 4.3: Document Ingestion Pipeline
Tests:
- load_pdf(path: str) -> str using PyPDF
- load_pdf_pages(path: str) -> list[tuple[str, int]]
- split_into_chunks(text: str, chunk_size=512, overlap=50) -> list[str]
- assign_agent_scope(source_file: str) -> list[str]
- process_document(pdf_path, chunk_size, chunk_overlap, custom_scopes)
- process_directory(directory_path, chunk_size, chunk_overlap)
"""

import os
import pytest
from pathlib import Path
from backend.rag.pipeline import (
    load_pdf,
    load_pdf_pages,
    split_into_chunks,
    assign_agent_scope,
    process_document,
    process_directory,
    SCOPE_MAP,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP,
)

# Project paths
KB_DIR = Path(__file__).resolve().parent.parent.parent / "knowledge_base"


# ==========================================
# 1. Scope Assignment Tests
# ==========================================

def test_scope_map_definitions():
    """Verify SCOPE_MAP contains all 8 required document scope definitions."""
    expected_mappings = {
        "faq.pdf": ["faq", "complaint"],
        "refund_policy.pdf": ["billing", "complaint"],
        "shipping_policy.pdf": ["faq", "billing"],
        "warranty.pdf": ["faq", "technical"],
        "pricing.pdf": ["billing", "product"],
        "products.pdf": ["product"],
        "installation_guide.pdf": ["technical"],
        "user_manual.pdf": ["technical"],
    }
    for doc, scopes in expected_mappings.items():
        assert doc in SCOPE_MAP, f"Expected {doc} in SCOPE_MAP"
        assert SCOPE_MAP[doc] == scopes, f"Scope mismatch for {doc}: {SCOPE_MAP[doc]} != {scopes}"


@pytest.mark.parametrize(
    "filename,expected_scopes",
    [
        ("faq.pdf", ["faq", "complaint"]),
        ("FAQ.pdf", ["faq", "complaint"]),
        ("refund_policy.pdf", ["billing", "complaint"]),
        ("RefundPolicy.pdf", ["billing", "complaint"]),
        ("shipping_policy.pdf", ["faq", "billing"]),
        ("ShippingPolicy.pdf", ["faq", "billing"]),
        ("warranty.pdf", ["faq", "technical"]),
        ("Warranty.pdf", ["faq", "technical"]),
        ("pricing.pdf", ["billing", "product"]),
        ("Pricing.pdf", ["billing", "product"]),
        ("products.pdf", ["product"]),
        ("Products.pdf", ["product"]),
        ("installation_guide.pdf", ["technical"]),
        ("InstallationGuide.pdf", ["technical"]),
        ("user_manual.pdf", ["technical"]),
        ("UserManual.pdf", ["technical"]),
        ("/var/data/knowledge_base/RefundPolicy.pdf", ["billing", "complaint"]),
        ("C:\\kb\\docs\\InstallationGuide.pdf", ["technical"]),
        ("unknown_internal_memo.pdf", ["faq"]),  # Fallback
    ],
)
def test_assign_agent_scope(filename, expected_scopes):
    """Test assign_agent_scope resolves correct scopes across various formats and fallbacks."""
    scopes = assign_agent_scope(filename)
    assert scopes == expected_scopes, f"Failed for filename '{filename}': got {scopes}, expected {expected_scopes}"


# ==========================================
# 2. Text Splitting Tests
# ==========================================

def test_split_into_chunks_empty_text():
    """Verify split_into_chunks returns empty list for empty/whitespace input."""
    assert split_into_chunks("") == []
    assert split_into_chunks("   \n\n\t  ") == []


def test_split_into_chunks_short_text():
    """Verify short text is returned as single chunk."""
    short_text = "TechMart Electronics offers a 30-day money-back guarantee on all audio products."
    chunks = split_into_chunks(short_text, chunk_size=512, overlap=50)
    assert len(chunks) == 1
    assert chunks[0] == short_text


def test_split_into_chunks_long_text():
    """Verify long text is broken into multiple chunks honoring chunk size and overlap."""
    paragraph = (
        "TechMart Electronics customer support policy covers all standard hardware devices. "
        "Customers may request technical diagnostics, firmware updates, or replacement parts. "
        "All warranty claims must include original proof of purchase and serial number. "
        "Our customer support team operates Monday through Friday from 9 AM to 6 PM EST. "
    )
    long_text = "\n\n".join([paragraph] * 10)  # ~2400 chars
    chunk_size = 300
    overlap = 40

    chunks = split_into_chunks(long_text, chunk_size=chunk_size, overlap=overlap)
    assert len(chunks) > 1

    for chunk in chunks:
        assert len(chunk) > 0
        # Check that individual chunks roughly respect chunk_size
        assert len(chunk) <= chunk_size + 100  # allowing for word-boundary padding


# ==========================================
# 3. PDF Loading Tests
# ==========================================

def test_load_pdf_nonexistent_file():
    """Verify load_pdf raises FileNotFoundError for missing paths."""
    with pytest.raises(FileNotFoundError):
        load_pdf("nonexistent_path_to_doc.pdf")


def test_load_pdf_pages_nonexistent_file():
    """Verify load_pdf_pages raises FileNotFoundError for missing paths."""
    with pytest.raises(FileNotFoundError):
        load_pdf_pages("nonexistent_path_to_doc.pdf")


def test_load_pdf_knowledge_base():
    """Verify load_pdf successfully extracts text string from actual knowledge base PDFs."""
    faq_path = KB_DIR / "FAQ.pdf"
    if not faq_path.exists():
        pytest.skip(f"Knowledge base file {faq_path} not found")

    text = load_pdf(faq_path)
    assert isinstance(text, str)
    assert len(text.strip()) > 0
    assert "TechMart" in text or "FAQ" in text or "support" in text.lower()


def test_load_pdf_pages_knowledge_base():
    """Verify load_pdf_pages returns page tuples with 1-indexed page numbers."""
    refund_path = KB_DIR / "RefundPolicy.pdf"
    if not refund_path.exists():
        pytest.skip(f"Knowledge base file {refund_path} not found")

    pages = load_pdf_pages(refund_path)
    assert isinstance(pages, list)
    assert len(pages) >= 1

    for text, page_num in pages:
        assert isinstance(text, str)
        assert len(text.strip()) > 0
        assert isinstance(page_num, int)
        assert page_num >= 1


# ==========================================
# 4. Document Processing Tests
# ==========================================

def test_process_document():
    """Verify process_document chunks and annotates metadata correctly."""
    warranty_path = KB_DIR / "Warranty.pdf"
    if not warranty_path.exists():
        pytest.skip(f"Knowledge base file {warranty_path} not found")

    chunks = process_document(warranty_path, chunk_size=400, chunk_overlap=40)
    assert len(chunks) >= 1

    for chunk in chunks:
        assert "chunk_id" in chunk
        assert "document" in chunk
        assert chunk["document"] == "Warranty.pdf"
        assert "document_title" in chunk
        assert chunk["document_title"] == "Warranty"
        assert "page" in chunk
        assert chunk["page"] >= 1
        assert "scopes" in chunk
        assert chunk["scopes"] == ["faq", "technical"]
        assert "text" in chunk
        assert len(chunk["text"]) > 0


def test_process_document_custom_scopes():
    """Verify custom_scopes parameter overrides automatic mapping."""
    warranty_path = KB_DIR / "Warranty.pdf"
    if not warranty_path.exists():
        pytest.skip(f"Knowledge base file {warranty_path} not found")

    custom = ["custom_agent", "testing"]
    chunks = process_document(warranty_path, custom_scopes=custom)
    assert len(chunks) >= 1
    for chunk in chunks:
        assert chunk["scopes"] == custom


def test_process_directory():
    """Verify process_directory extracts chunks across all PDFs in knowledge_base directory."""
    if not KB_DIR.exists():
        pytest.skip("Knowledge base directory not found")

    all_chunks = process_directory(KB_DIR, chunk_size=512, chunk_overlap=50)
    assert len(all_chunks) >= 8  # At least 1 chunk per document

    docs_found = {c["document"] for c in all_chunks}
    expected_docs = {
        "FAQ.pdf",
        "RefundPolicy.pdf",
        "ShippingPolicy.pdf",
        "Warranty.pdf",
        "Pricing.pdf",
        "Products.pdf",
        "InstallationGuide.pdf",
        "UserManual.pdf",
    }
    for doc in expected_docs:
        assert doc in docs_found, f"Missing document in processed directory chunks: {doc}"


def test_process_directory_invalid_dir():
    """Verify process_directory raises FileNotFoundError for nonexistent directory."""
    with pytest.raises(FileNotFoundError):
        process_directory("nonexistent_directory_path")
