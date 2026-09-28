"""Deterministic, read-only PDF extraction and exact quote grounding."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import io
from pathlib import Path

from pypdf import PdfReader


@dataclass(frozen=True)
class DocumentPage:
    page_number: int
    text: str


@dataclass(frozen=True)
class DocumentEvidence:
    source_path: str
    sha256: str
    pages: list[DocumentPage]


@dataclass(frozen=True)
class PageGrounding:
    page_number: int
    start_char: int
    end_char: int
    quote_exact: str


def extract_pdf(path: Path) -> DocumentEvidence:
    """Extract page-addressable text directly from a PDF byte stream."""
    raw = path.read_bytes()
    reader = PdfReader(io.BytesIO(raw))
    pages = [
        DocumentPage(page_number=index + 1, text=page.extract_text() or "")
        for index, page in enumerate(reader.pages)
    ]
    return DocumentEvidence(
        source_path=str(path),
        sha256=hashlib.sha256(raw).hexdigest(),
        pages=pages,
    )


def verify_pdf_quote(document: DocumentEvidence, quote: str) -> PageGrounding:
    """Locate a quote after whitespace-only normalization; never match fuzzily."""
    normalized_quote = " ".join(quote.split())
    if not normalized_quote:
        raise ValueError("Quote not found in PDF: empty quote")

    for page in document.pages:
        normalized_page = " ".join(page.text.split())
        start = normalized_page.find(normalized_quote)
        if start >= 0:
            return PageGrounding(
                page_number=page.page_number,
                start_char=start,
                end_char=start + len(normalized_quote),
                quote_exact=normalized_quote,
            )
    raise ValueError(f"Quote not found in PDF: {quote}")
