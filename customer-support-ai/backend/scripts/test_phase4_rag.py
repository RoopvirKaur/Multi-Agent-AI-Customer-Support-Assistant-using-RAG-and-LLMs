"""
test_phase4_rag.py
Comprehensive verification test suite for Phase 4: RAG Pipeline.
Validates FAISS vector retrieval across all 5 agent domains.
"""

import sys
import os
from pathlib import Path

# Safe UTF-8 console output for Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.rag.retriever import get_retriever
from backend.vectorstore.faiss_store import get_faiss_store


def test_rag_pipeline():
    print("\n" + "=" * 70)
    print(">> Running Phase 4: Multi-Agent RAG Pipeline Verification Tests")
    print("=" * 70)

    # 1. Verify Vectorstore state
    store = get_faiss_store()
    loaded = store.load()
    assert loaded, "Failed to load FAISS store from disk!"
    assert store.index is not None, "FAISS index is None"
    assert store.index.ntotal > 0, "FAISS index is empty"
    assert store.index.ntotal == len(store.metadata), f"Mismatch between index count ({store.index.ntotal}) and metadata count ({len(store.metadata)})"
    print(f"[OK] Vector Store Verification: {store.index.ntotal} vectors loaded across 8 PDF documents.")

    # 2. Test domain-scoped queries
    retriever = get_retriever()

    test_queries = [
        {
            "domain": "Billing / Refund",
            "scope": "billing",
            "query": "What is the return window and refund policy timeline?",
            "expected_docs": ["RefundPolicy.pdf", "Pricing.pdf", "ShippingPolicy.pdf"],
        },
        {
            "domain": "Technical Support",
            "scope": "technical",
            "query": "How do I pair the SmartHub Pro with Wi-Fi and troubleshoot Bluetooth?",
            "expected_docs": ["InstallationGuide.pdf", "UserManual.pdf", "Warranty.pdf"],
        },
        {
            "domain": "Product Specialist",
            "scope": "product",
            "query": "What are the audio output specs and battery life for SoundWave 500?",
            "expected_docs": ["Products.pdf", "Pricing.pdf"],
        },
        {
            "domain": "Complaint Resolution",
            "scope": "complaint",
            "query": "I received a damaged item and want to file an immediate refund or replacement claim",
            "expected_docs": ["RefundPolicy.pdf", "FAQ.pdf"],
        },
        {
            "domain": "General FAQ / Warranty",
            "scope": "faq",
            "query": "What is covered under the 1-year and 2-year TechMart Care+ warranty?",
            "expected_docs": ["Warranty.pdf", "FAQ.pdf", "ShippingPolicy.pdf"],
        },
    ]

    print("\n--- Domain-Scoped Retrieval Tests ---")
    for idx, t in enumerate(test_queries, 1):
        print(f"\n[Test {idx}] Domain: {t['domain']} | Scope: '{t['scope']}'")
        print(f"Query: \"{t['query']}\"")

        results = retriever.retrieve(t["query"], agent_scope=t["scope"], top_k=3)
        assert len(results) > 0, f"No results returned for query: {t['query']}"

        top_match = results[0]
        print(f"  Top Match: [{top_match['document']}] (Page {top_match['page']}) - Score: {top_match['score']}")
        print(f"  Scopes: {top_match['scopes']}")
        print(f"  Snippet: {top_match['text'][:140]}...")

        # Verify scope matches
        assert (
            t["scope"] in top_match["scopes"] or "all" in top_match["scopes"]
        ), f"Scope mismatch: expected '{t['scope']}' in {top_match['scopes']}"

        # Verify expected document
        doc_names = [r["document"] for r in results]
        matched_expected = any(ed in doc_names for ed in t["expected_docs"])
        assert (
            matched_expected
        ), f"Expected one of {t['expected_docs']}, got {doc_names}"
        print("  [PASS] Semantically accurate chunk retrieved with correct agent scope.")

    # 3. Test Global Unscoped Query
    print("\n--- Global Unscoped Retrieval Test ---")
    global_query = "What is the standard shipping rate for orders under $50?"
    unscoped_results = retriever.retrieve(global_query, agent_scope=None, top_k=2)
    assert len(unscoped_results) > 0
    print(f"Query: \"{global_query}\"")
    print(f"  Top Match: [{unscoped_results[0]['document']}] - Score: {unscoped_results[0]['score']}")
    print(f"  Snippet: {unscoped_results[0]['text'][:140]}...")
    assert "shipping" in unscoped_results[0]["document"].lower() or "shipping" in unscoped_results[0]["text"].lower()
    print("  [PASS] Unscoped retrieval found correct document.")

    print("\n" + "=" * 70)
    print("ALL PHASE 4 RAG VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    test_rag_pipeline()
