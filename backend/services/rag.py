"""
RAG service — loads company documents from knowledge_base/ and retrieves
relevant chunks for a given user query.

Supports: .txt, .pdf
Approach: TF-IDF keyword scoring (lightweight, no external vector DB needed).
"""

import math
import os
import re
from collections import Counter
from pathlib import Path

_KB_DIR = Path(__file__).resolve().parent.parent / "knowledge_base"

# ── Internal state (loaded once) ──
_chunks: list[dict] = []   # [{ "source": filename, "text": chunk_text }]
_idf: dict[str, float] = {}
_chunk_tfs: list[Counter] = []
_loaded = False

CHUNK_SIZE = 500       # characters per chunk
CHUNK_OVERLAP = 100    # overlap between consecutive chunks
TOP_K = 3              # number of chunks to return


def _tokenize(text: str) -> list[str]:
    """Lowercase, split on non-alphanumeric, drop short tokens."""
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if len(t) > 2]


def _read_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _read_pdf(path: Path) -> str:
    """Extract text from a PDF using pypdf."""
    try:
        from pypdf import PdfReader
    except ImportError:
        try:
            from PyPDF2 import PdfReader
        except ImportError:
            return ""

    try:
        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)
    except Exception:
        return ""


def _split_chunks(text: str, source: str) -> list[dict]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk_text = text[start:end].strip()
        if chunk_text:
            chunks.append({"source": source, "text": chunk_text})
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def _load_documents():
    """Scan knowledge_base/ for .txt and .pdf files, chunk them, and build TF-IDF index."""
    global _chunks, _idf, _chunk_tfs, _loaded

    if _loaded:
        return

    if not _KB_DIR.exists():
        _loaded = True
        return

    # Load all documents
    for file in sorted(_KB_DIR.iterdir()):
        if file.suffix.lower() == ".txt":
            text = _read_txt(file)
        elif file.suffix.lower() == ".pdf":
            text = _read_pdf(file)
        else:
            continue

        if text.strip():
            _chunks.extend(_split_chunks(text, file.name))

    if not _chunks:
        _loaded = True
        return

    # Build TF vectors per chunk
    _chunk_tfs = [Counter(_tokenize(c["text"])) for c in _chunks]

    # Build IDF
    doc_count = len(_chunks)
    all_terms: set[str] = set()
    for tf in _chunk_tfs:
        all_terms.update(tf.keys())

    for term in all_terms:
        df = sum(1 for tf in _chunk_tfs if term in tf)
        _idf[term] = math.log((doc_count + 1) / (df + 1)) + 1

    _loaded = True
    print(f"[RAG] Loaded {len(_chunks)} chunks from {_KB_DIR}")


def retrieve(query: str, top_k: int = TOP_K) -> list[dict]:
    """
    Return the top-k most relevant document chunks for a query.

    Args:
        query: The user's question.
        top_k: Number of chunks to return.

    Returns:
        List of {"source": filename, "text": chunk_text, "score": float}
    """
    _load_documents()

    if not _chunks:
        return []

    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    # Score each chunk via TF-IDF dot product
    query_tf = Counter(query_tokens)
    scored = []

    for i, chunk_tf in enumerate(_chunk_tfs):
        score = 0.0
        for term, q_count in query_tf.items():
            if term in chunk_tf:
                tf_score = chunk_tf[term]
                idf_score = _idf.get(term, 1.0)
                score += q_count * tf_score * idf_score
        if score > 0:
            scored.append((score, i))

    scored.sort(reverse=True)
    results = []
    for score, idx in scored[:top_k]:
        results.append({
            "source": _chunks[idx]["source"],
            "text": _chunks[idx]["text"],
            "score": round(score, 2),
        })

    return results


def get_context_block(query: str) -> str:
    """
    Return a formatted context string for injection into the Gemini prompt.
    Returns empty string if no relevant documents found.
    """
    results = retrieve(query)
    if not results:
        return ""

    lines = ["COMPANY DOCUMENTS (use these to answer policy/procedure questions):"]
    for r in results:
        lines.append(f"\n--- From: {r['source']} ---")
        lines.append(r["text"])

    return "\n".join(lines)
