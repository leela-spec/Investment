"""Static HTML report tests (C7): renders all sections offline from fixture
data, is self-contained (no external network references), and is deterministic."""

from __future__ import annotations

import re

from ipos.export.snapshot import build_snapshot
from ipos.report.html import render_html
from ipos.warehouse.db import connect


def _render(populated_db, as_of):
    db, reg = populated_db
    with connect(db, read_only=True) as con:
        snap = build_snapshot(con, reg, as_of)
        return render_html(con, snap, as_of)


def test_html_has_all_sections(populated_db, as_of):
    html = _render(populated_db, as_of)
    for heading in ["Stance vector", "Regime map", "Contradictions", "Top movers",
                    "Modules", "Indicators", "Score heatmap", "Interpretation"]:
        assert heading in html
    assert "IPOS Weekly Report" in html
    assert as_of.isoformat() in html
    # every indicator is anchor-linkable, so a contradiction can point at it
    assert 'id="ind-SPX"' in html and 'id="ind-HY_OAS"' in html


def test_html_has_svg_charts(populated_db, as_of):
    html = _render(populated_db, as_of)
    assert 'class="regime-map"' in html          # 2D regime path
    assert html.count('class="spark"') >= 20      # a sparkline per indicator
    assert "<polyline" in html                    # line geometry, not an image ref
    assert 'class="hstrip"' in html               # multi-horizon score deltas
    assert 'id="rm-arrow"' in html                # path carries direction of travel


def test_html_regime_map_labels_quadrants_and_path_ends(populated_db, as_of):
    html = _render(populated_db, as_of)
    for quadrant in ("Reflation", "Stagflation", "Goldilocks", "Deflation"):
        assert quadrant in html
    # the quadrants are explained, not just drawn (the 2026-07-27 complaint)
    assert "expansion with rising" in html.lower()
    assert "start " in html  # oldest end of the path is labelled


def test_html_contradiction_shows_the_disagreeing_members(populated_db, as_of):
    """A mixed-signal contradiction must name WHERE the disagreement is, not
    just print a spread number."""
    html = _render(populated_db, as_of)
    assert 'class="mstrip"' in html          # member positions on the 0-100 scale
    assert "apart</text>" in html            # the spread annotated on the strip
    assert re.search(r"lowest\(\w+\)=\w+ [\d.]+", html)   # named low end
    assert re.search(r"highest\(\w+\)=\w+ [\d.]+", html)  # named high end
    assert "_modules" not in html            # reserved key must stay out of the UI


def test_html_every_heading_and_column_is_explained(populated_db, as_of):
    """Coverage guard for the hover glossary.

    A missing glossary key fails SILENTLY (``glossary.tooltip`` returns the bare
    label), which is exactly how tooltip coverage rotted before 2026-07-27. This
    test fails instead, so a new section or column cannot ship unexplained.
    """
    html = _render(populated_db, as_of)

    # Purely visual or self-evident columns that carry no jargon.
    ALLOWED_BARE = {
        "Module", "Dimension", "ID", "Value", "Trend", "Now", "Date", "When",
        "Event", "Category", "Indicator", "Read", "Your weight", "Suggested tilt",
        "vs 1m", "52w score", "26w path", "26w",
    }

    def _text(fragment: str) -> str:
        return re.sub(r"<[^>]+>", "", fragment).strip()

    bare: list[str] = []
    for tag in ("h2", "th"):
        for m in re.finditer(rf"<{tag}[^>]*>(.*?)</{tag}>", html, re.S):
            inner = m.group(1)
            label = _text(inner)
            if not label:
                continue
            # strip the parenthetical sub-caption, which is prose not a term
            label = re.sub(r"\s*\(.*?\)\s*$", "", label).strip()
            if 'class="tt"' in inner or label in ALLOWED_BARE:
                continue
            bare.append(f"<{tag}> {label!r}")
    assert not bare, (
        "these report headings/columns have no glossary tooltip — add an entry to "
        f"configs/glossary.yaml and wire it up, or allow-list it: {bare}"
    )


def test_html_is_self_contained(populated_db, as_of):
    html = _render(populated_db, as_of)
    # no external stylesheets/scripts/images or CDN references
    assert "<script" not in html.lower()
    assert not re.search(r'src\s*=', html)
    assert not re.search(r'https?://[a-z0-9.]+\.(com|net|org|io)/', html)
    assert "cdn" not in html.lower()
    # CSS is inlined
    assert "<style>" in html


def test_html_deterministic(populated_db, as_of):
    assert _render(populated_db, as_of) == _render(populated_db, as_of)


def test_html_has_glossary_tooltips(populated_db, as_of):
    html = _render(populated_db, as_of)
    # CSS-only popovers (C7 UX pass): no JS is added, hover/focus is pure CSS.
    assert 'class="tt"' in html and 'class="tt-pop"' in html
    assert "<script" not in html.lower()
    # a known indicator and module explanation actually surfaced
    assert "yield-curve recession indicator" in html  # T10Y2Y
    assert "High score = broad-based risk-on" in html  # EquityRisk module
