"""
pipeline.py
Document ingestion and chunking pipeline for Multi-Agent RAG.
Implements Sub-phase 4.3 requirements:
- load_pdf(path: str) -> str: PDF text extraction using pdfplumber (table-aware) with PyPDF fallback
- split_into_chunks(text: str, chunk_size=512, overlap=50) -> list[str]: LangChain RecursiveCharacterTextSplitter
- assign_agent_scope(source_file: str) -> list[str]: maps document filenames to agent scopes
- Helper methods: load_pdf_pages, process_document, process_directory
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Union

# ── PDF extraction ──────────────────────────────────────────────────
# Prefer pdfplumber (table-aware) with pypdf as fallback
try:
    import pdfplumber
    _HAS_PDFPLUMBER = True
except ImportError:
    _HAS_PDFPLUMBER = False

import pypdf  # always available (in requirements.txt)

# ── Text splitter ───────────────────────────────────────────────────
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    try:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
    except ImportError:
        class RecursiveCharacterTextSplitter:  # type: ignore[no-redef]
            """Pure Python recursive character text splitter fallback."""

            def __init__(
                self,
                chunk_size: int = 512,
                chunk_overlap: int = 50,
                separators: Optional[List[str]] = None,
            ):
                self.chunk_size = chunk_size
                self.chunk_overlap = chunk_overlap
                self.separators = separators or ["\n\n", "\n", ". ", " ", ""]

            def split_text(self, text: str) -> List[str]:
                if not text or not text.strip():
                    return []
                if len(text) <= self.chunk_size:
                    return [text.strip()]

                chunks: List[str] = []
                start = 0
                while start < len(text):
                    end = min(start + self.chunk_size, len(text))
                    if end < len(text):
                        split_idx = -1
                        for sep in self.separators:
                            if sep == "":
                                continue
                            pos = text.rfind(sep, start, end)
                            if pos > start + self.chunk_overlap:
                                split_idx = pos + len(sep)
                                break
                        if split_idx != -1:
                            end = split_idx

                    chunk = text[start:end].strip()
                    if chunk:
                        chunks.append(chunk)
                    start = max(start + 1, end - self.chunk_overlap)

                return chunks


# ── Agent Scope Mapping (Implementation Plan §4.3) ─────────────────
SCOPE_MAP: Dict[str, List[str]] = {
    "faq.pdf":              ["faq", "complaint"],
    "refund_policy.pdf":    ["billing", "complaint"],
    "shipping_policy.pdf":  ["faq", "billing"],
    "warranty.pdf":         ["faq", "technical"],
    "pricing.pdf":          ["billing", "product"],
    "products.pdf":         ["product"],
    "installation_guide.pdf": ["technical"],
    "user_manual.pdf":      ["technical"],
}

DEFAULT_CHUNK_SIZE: int = 512
DEFAULT_CHUNK_OVERLAP: int = 50


# ── Helpers ─────────────────────────────────────────────────────────

def _normalize_name(name: str) -> str:
    """Normalize a filename for scope-map matching (strips dirs, lowercases, removes separators)."""
    base = Path(name).name.lower()
    return re.sub(r"[\s\-_]", "", base)


def _table_to_markdown(table: List[List[Optional[str]]]) -> str:
    """
    Convert a pdfplumber table (list-of-rows) to a readable Markdown table string.
    Handles None cells and multi-line cell text gracefully.
    """
    if not table:
        return ""

    def clean_cell(cell: Optional[str]) -> str:
        if cell is None:
            return ""
        # Collapse internal newlines within a cell to a single space
        return " ".join(cell.split())

    rows = [[clean_cell(c) for c in row] for row in table]

    # Determine column widths
    col_count = max(len(r) for r in rows)
    # Pad rows to uniform column count
    rows = [r + [""] * (col_count - len(r)) for r in rows]

    widths = [max(len(rows[ri][ci]) for ri in range(len(rows))) for ci in range(col_count)]

    def fmt_row(row: List[str]) -> str:
        return "| " + " | ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)) + " |"

    separator = "| " + " | ".join("-" * w for w in widths) + " |"

    lines = [fmt_row(rows[0]), separator]
    for row in rows[1:]:
        lines.append(fmt_row(row))

    return "\n".join(lines)


def _extract_page_pdfplumber(page) -> str:
    """
    Extract a single pdfplumber page as clean text.
    Tables are converted to Markdown; non-table text is extracted normally.
    This prevents garbled column-concatenation that occurs with raw PyPDF extraction.
    """
    # Get bounding boxes of detected tables so we can exclude them from plain text
    tables = page.extract_tables()
    table_bboxes = [t.bbox for t in page.find_tables()] if hasattr(page, "find_tables") else []

    parts: List[str] = []

    # Extract non-table text
    if table_bboxes:
        # Crop away table regions and extract surrounding text
        remaining_text = page.extract_text(x_tolerance=3, y_tolerance=3) or ""
    else:
        remaining_text = page.extract_text(x_tolerance=3, y_tolerance=3) or ""

    if remaining_text.strip():
        parts.append(remaining_text.strip())

    # Append each table as Markdown
    for table in tables:
        md = _table_to_markdown(table)
        if md:
            parts.append(md)

    return "\n\n".join(parts)


def _extract_page_pdfplumber_v2(page) -> str:
    """
    More robust extraction: collects plain text that falls OUTSIDE table bboxes,
    then appends table Markdown blocks. Prevents double-rendering table cells.
    """
    try:
        table_finder = page.find_tables()
    except Exception:
        table_finder = []

    if not table_finder:
        # No tables — just plain text
        return (page.extract_text(x_tolerance=3, y_tolerance=3) or "").strip()

    parts: List[str] = []

    # Extract words and separate table vs. non-table regions
    table_bboxes = [t.bbox for t in table_finder]

    def in_any_table(word) -> bool:
        wx0, wy0, wx1, wy1 = word["x0"], word["top"], word["x1"], word["bottom"]
        for (tx0, ty0, tx1, ty1) in table_bboxes:
            if wx0 >= tx0 - 2 and wy0 >= ty0 - 2 and wx1 <= tx1 + 2 and wy1 <= ty1 + 2:
                return True
        return False

    words = page.extract_words()
    non_table_words = [w for w in words if not in_any_table(w)]

    # Reconstruct non-table text respecting line positions
    if non_table_words:
        lines: Dict[int, List[str]] = {}
        for w in non_table_words:
            line_key = round(w["top"])
            lines.setdefault(line_key, []).append(w["text"])
        reconstructed = "\n".join(" ".join(words_on_line) for _, words_on_line in sorted(lines.items()))
        if reconstructed.strip():
            parts.append(reconstructed.strip())

    # Add each table as Markdown
    for t in table_finder:
        table_data = t.extract()
        md = _table_to_markdown(table_data)
        if md:
            parts.append(md)

    return "\n\n".join(parts)


# ── Public API ───────────────────────────────────────────────────────

def assign_agent_scope(source_file: str) -> List[str]:
    """
    Determine agent scopes for a given document filename or path.
    Maps file to agent scopes based on SCOPE_MAP.
    Falls back to ['faq'] for unmapped documents.
    """
    normalized_source = _normalize_name(source_file)
    for mapped_file, scopes in SCOPE_MAP.items():
        normalized_mapped = _normalize_name(mapped_file)
        if normalized_mapped == normalized_source:
            return list(scopes)
        stem_source = normalized_source.replace(".pdf", "")
        stem_mapped = normalized_mapped.replace(".pdf", "")
        if stem_mapped and stem_source and (stem_mapped in stem_source or stem_source in stem_mapped):
            return list(scopes)
    return ["faq"]


def load_pdf(path: Union[str, Path]) -> str:
    """
    Extract full text from a PDF file.

    Uses pdfplumber when available for table-aware extraction (converts tables
    to Markdown), falling back to PyPDF for plain text extraction.

    Args:
        path: File path (str or Path) to the PDF document.

    Returns:
        Extracted text as a single combined string.

    Raises:
        FileNotFoundError: If the PDF file does not exist.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"PDF file not found at: {file_path}")

    if _HAS_PDFPLUMBER:
        try:
            page_texts = []
            with pdfplumber.open(str(file_path)) as pdf:
                for page in pdf.pages:
                    text = _extract_page_pdfplumber_v2(page)
                    if text.strip():
                        page_texts.append(text.strip())
            if page_texts:
                return "\n\n".join(page_texts)
        except Exception as exc:
            print(f"  [Warning] pdfplumber failed for {file_path.name}: {exc}. Falling back to pypdf.")

    # PyPDF fallback
    reader = pypdf.PdfReader(str(file_path))
    pages_text = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            pages_text.append(text.strip())
    return "\n\n".join(pages_text)


def load_pdf_pages(path: Union[str, Path]) -> List[Tuple[str, int]]:
    """
    Extract text from a PDF file page by page.

    Uses pdfplumber when available for table-aware extraction (converts tables
    to Markdown), falling back to PyPDF.

    Args:
        path: File path (str or Path) to the PDF document.

    Returns:
        List of tuples (page_text, page_number_1_indexed).

    Raises:
        FileNotFoundError: If the PDF file does not exist.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"PDF file not found at: {file_path}")

    pages_data: List[Tuple[str, int]] = []

    if _HAS_PDFPLUMBER:
        try:
            with pdfplumber.open(str(file_path)) as pdf:
                for idx, page in enumerate(pdf.pages):
                    text = _extract_page_pdfplumber_v2(page)
                    if text.strip():
                        pages_data.append((text.strip(), idx + 1))
            if pages_data:
                return pages_data
        except Exception as exc:
            print(f"  [Warning] pdfplumber failed for {file_path.name}: {exc}. Falling back to pypdf.")
            pages_data = []

    # PyPDF fallback
    reader = pypdf.PdfReader(str(file_path))
    for idx, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        text = text.strip()
        if text:
            pages_data.append((text, idx + 1))

    return pages_data


def split_into_chunks(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[str]:
    """
    Split text into chunks using LangChain's RecursiveCharacterTextSplitter.

    The separator hierarchy respects Markdown table structure: table blocks
    (lines starting with '|') are kept together before splitting at other
    boundaries.

    Args:
        text: Input string to be split.
        chunk_size: Maximum chunk size in characters (default: 512).
        overlap: Chunk overlap in characters (default: 50).

    Returns:
        List of non-empty text chunks.
    """
    if not text or not text.strip():
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    raw_chunks = splitter.split_text(text)
    return [c.strip() for c in raw_chunks if c.strip()]


def process_document(
    pdf_path: Union[str, Path],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    custom_scopes: Optional[List[str]] = None,
) -> List[Dict]:
    """
    Process a single PDF document end-to-end:
    1. Extract text per page (table-aware via pdfplumber)
    2. Split into semantic chunks using split_into_chunks
    3. Assign agent scopes and build metadata dict per chunk

    Returns:
        List of structured chunk dicts with keys:
        chunk_id, document, document_title, page, scopes, text
    """
    path = Path(pdf_path)
    filename = path.name
    scopes = custom_scopes or assign_agent_scope(filename)

    pages = load_pdf_pages(path)
    chunks: List[Dict] = []
    chunk_index = 0

    for page_text, page_num in pages:
        page_chunks = split_into_chunks(page_text, chunk_size=chunk_size, overlap=chunk_overlap)
        for chunk_text in page_chunks:
            chunk_id = f"{path.stem.lower()}_p{page_num}_c{chunk_index}"
            chunks.append({
                "chunk_id": chunk_id,
                "document": filename,
                "document_title": path.stem,
                "page": page_num,
                "scopes": scopes,
                "text": chunk_text,
            })
            chunk_index += 1

    return chunks


def process_directory(
    directory_path: Union[str, Path],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[Dict]:
    """
    Process all PDF documents within a target directory.

    Args:
        directory_path: Directory containing PDF files.
        chunk_size: Maximum chunk size in characters.
        chunk_overlap: Overlap between consecutive chunks.

    Returns:
        List of all chunk dicts across all documents.

    Raises:
        FileNotFoundError: If the directory does not exist.
    """
    dir_path = Path(directory_path)
    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {dir_path}")

    all_chunks: List[Dict] = []
    pdf_files = sorted(dir_path.glob("*.pdf"))

    pdf_list = list(pdf_files)
    print(f"Found {len(pdf_list)} PDF documents in {dir_path}")
    for pdf_file in pdf_list:
        doc_chunks = process_document(pdf_file, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        print(
            f"  Processed '{pdf_file.name}': generated {len(doc_chunks)} chunks "
            f"(Scopes: {assign_agent_scope(pdf_file.name)})"
        )
        all_chunks.extend(doc_chunks)

    return all_chunks
