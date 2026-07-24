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
    # every indicator is anchor-linkable
    assert 'id="SPX"' in html and 'id="HY_OAS"' in html


def test_html_has_svg_charts(populated_db, as_of):
    html = _render(populated_db, as_of)
    assert 'class="regime-map"' in html          # 2D regime trail
    assert html.count('class="spark"') >= 20      # a sparkline per indicator
    assert "<polyline" in html                    # line geometry, not an image ref


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
