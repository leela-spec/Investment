"""Plain-language explanations for the HTML report's hover popovers (C7 UX
pass). Content lives in ``configs/glossary.yaml``; this module only loads it
and renders a CSS-only popover span. A missing key degrades to the bare
label — a documentation gap never breaks the report."""

from __future__ import annotations

import html as _html
from pathlib import Path

import yaml

from ipos.config.load import REPO_ROOT

GLOSSARY_PATH = REPO_ROOT / "configs" / "glossary.yaml"


def load_glossary(path: Path | None = None) -> dict:
    p = path or GLOSSARY_PATH
    if not p.exists():
        return {}
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def tooltip(label: str, entry: dict | None, *, title: str | None = None) -> str:
    """Wrap ``label`` in a hover/focus-triggered popover. ``entry`` is a
    glossary.yaml leaf ({"title": ..., "body": ...}); falls back to the bare
    escaped label if there's no body to show."""
    esc_label = _html.escape(str(label))
    body = (entry or {}).get("body")
    if not body:
        return esc_label
    heading = title or (entry or {}).get("title") or label
    esc_title = _html.escape(str(heading))
    esc_body = _html.escape(" ".join(str(body).split()))
    return (
        f'<span class="tt" tabindex="0">{esc_label}'
        f'<span class="tt-pop"><b>{esc_title}</b><br>{esc_body}</span></span>'
    )
