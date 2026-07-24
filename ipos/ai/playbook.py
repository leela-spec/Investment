"""Deterministic Playbook retrieval (C5, minimal) — no RAG/embeddings.

Selects only the Playbook modules relevant to *what the snapshot surfaced*
this week: modules behind contradictions (highest priority), then top movers,
then indicators at score extremes. Reads those module files from
``04_playbook/modules/`` in priority order for the prompt bundle.
"""

from __future__ import annotations

from ipos.config.load import PLAYBOOK_MODULES_DIR
from ipos.config.models import Registry

EXTREME_LOW = 20.0
EXTREME_HIGH = 80.0


def _module_refs(registry: Registry, module_id: str) -> list[str]:
    m = registry.modules.get(module_id)
    return list(m.playbook_refs) if m else []


def surfaced_playbook_refs(snapshot: dict, registry: Registry) -> list[str]:
    """Return an ordered, de-duplicated list of playbook module_ids to include,
    priority: contradictions -> movers -> extremes."""
    ordered: list[str] = []

    def _add(refs):
        for r in refs:
            if r not in ordered:
                ordered.append(r)

    ind_by_id = {i["id"]: i for i in snapshot["indicators"]}

    # 1) modules behind contradictions (via the module scores that triggered them)
    module_ids_in_play: list[str] = []
    for c in snapshot.get("contradictions", []):
        for key in c.get("details", {}):
            # keys look like "module(EquityRisk)" / "indicator(SPX)"
            if key.startswith("module(") or key.startswith("module_spread("):
                mid = key[key.index("(") + 1 : key.rindex(")")]
                if mid not in module_ids_in_play:
                    module_ids_in_play.append(mid)
    for mid in module_ids_in_play:
        _add(_module_refs(registry, mid))

    # 2) modules of top movers
    for mv in snapshot.get("top_movers", []):
        ind = ind_by_id.get(mv["id"])
        if ind:
            _add(_module_refs(registry, ind["module"]))
            _add(registry.by_id(mv["id"]).playbook_refs)

    # 3) indicators at score extremes
    for ind in snapshot["indicators"]:
        if ind["score"] is not None and (ind["score"] <= EXTREME_LOW or ind["score"] >= EXTREME_HIGH):
            _add(_module_refs(registry, ind["module"]))
            _add(registry.by_id(ind["id"]).playbook_refs)

    return ordered


def load_module_text(module_id: str) -> str | None:
    path = PLAYBOOK_MODULES_DIR / f"{module_id}.md"
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")
