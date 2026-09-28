from __future__ import annotations

from hashlib import sha256
from pathlib import Path

import pytest

from ipos.evidence.document_adapter import extract_pdf, verify_pdf_quote


PDF = Path("Sources/GER Elephant in The Room Analysis.pdf")
COMPANION = Path("Sources/GER Elephant in The Room Analysis.md")
PAGE_ONE_QUOTE = (
    "Die Welt ist nicht schwach genug für einen klassischen Deflations- oder "
    "Krisenmodus, aber auch nicht gesund genug für ein echtes, breites Risikoumfeld."
)


def test_real_research_pdf_is_hashed_and_page_addressable():
    document = extract_pdf(PDF)

    assert document.sha256 == (
        "f2d4b8dab16222893ddef1b039b2cca7a7b8f3ec3aea0b0e63befd15dcf8e39e"
    )
    assert len(document.pages) == 13
    assert all(page.page_number >= 1 for page in document.pages)
    assert sum(len(page.text.strip()) for page in document.pages) > 1000


def test_exact_pdf_quote_returns_page_and_normalized_character_offsets():
    document = extract_pdf(PDF)

    grounding = verify_pdf_quote(document, PAGE_ONE_QUOTE)

    normalized_page = " ".join(document.pages[0].text.split())
    assert grounding.page_number == 1
    assert normalized_page[grounding.start_char : grounding.end_char] == PAGE_ONE_QUOTE
    assert grounding.quote_exact == PAGE_ONE_QUOTE


def test_fabricated_pdf_quote_fails_closed():
    document = extract_pdf(PDF)

    with pytest.raises(ValueError, match="Quote not found in PDF"):
        verify_pdf_quote(
            document,
            "The source guarantees a risk-free return of 25 percent.",
        )


def test_companion_markdown_is_comparison_only():
    document = extract_pdf(PDF)

    assert sha256(COMPANION.read_bytes()).hexdigest() == (
        "157feb8d8d1bf014857a4bef80b1c1cff0698153c3b2dd2e633b1822c2f2cf13"
    )
    assert document.source_path == str(PDF)
    assert verify_pdf_quote(document, PAGE_ONE_QUOTE).page_number == 1
