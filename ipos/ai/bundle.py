"""Prompt bundle builder + narration orchestration (C6).

Assembles system + selected Playbook excerpts + minified snapshot under the
hard token budget (token ~= chars/4), trimming the lowest-priority Playbook
modules first. Always writes ``prompt_bundle.md`` (the $0 manual-paste path);
if a live provider is configured it also attaches an interpretation to the
snapshot. Never interpolates values into the frozen system prompt.
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

from ipos.ai.playbook import load_module_text, surfaced_playbook_refs
from ipos.ai.provider import AIConfig, get_provider
from ipos.config.load import REPO_ROOT
from ipos.config.models import Registry
from ipos.export.snapshot import EXPORTS_DIR

SYSTEM_PROMPT_PATH = REPO_ROOT / "prompts" / "weekly_checkup.md"


def est_tokens(text: str) -> int:
    return (len(text) + 3) // 4


def _system_prompt() -> str:
    return SYSTEM_PROMPT_PATH.read_text(encoding="utf-8") if SYSTEM_PROMPT_PATH.exists() else ""


def _truncate_at_h2(text: str, cap_tokens: int) -> str:
    """Keep a module's front matter + as many H2 (`## `) sections as fit the
    cap, so a large module contributes its highest-priority sections instead of
    being dropped whole (WS-B fix for SENTIMENT_POSITIONING)."""
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    used = 0
    truncated = False
    for line in lines:
        t = est_tokens(line)
        if used + t > cap_tokens and line.startswith("## "):
            truncated = True
            break
        if used + t > cap_tokens:
            truncated = True
            break
        out.append(line)
        used += t
    body = "".join(out).rstrip()
    if truncated:
        body += "\n\n_[excerpt truncated to fit token budget]_"
    return body


def build_playbook_excerpt(snapshot: dict, registry: Registry, cap_tokens: int) -> tuple[str, list[str]]:
    """Concatenate surfaced Playbook modules in priority order under the token
    cap. A module too large to fit whole is truncated at an H2 boundary rather
    than dropped, so the most-relevant module always contributes something.
    Returns (text, included_ids)."""
    refs = surfaced_playbook_refs(snapshot, registry)
    parts: list[str] = []
    included: list[str] = []
    used = 0
    for mid in refs:
        text = load_module_text(mid)
        if not text:
            continue
        remaining = cap_tokens - used
        if remaining < 150:  # not enough room for a meaningful excerpt
            break
        header = f"\n\n### Playbook module: {mid}\n"
        header_t = est_tokens(header)
        body = text
        if est_tokens(header + text) > remaining:
            body = _truncate_at_h2(text, remaining - header_t)
        block = header + body
        parts.append(block)
        included.append(mid)
        used += est_tokens(block)
    return "".join(parts).strip(), included


def build_user_message(snapshot: dict, registry: Registry, budget: dict) -> tuple[str, dict]:
    playbook, included = build_playbook_excerpt(snapshot, registry, budget["playbook"])
    snap_min = json.dumps(snapshot, separators=(",", ":"), sort_keys=True)
    # snapshot cap: if over, the report still holds; we note the trim rather than
    # silently dropping fields (Phase 1 golden-20 is well within 4k anyway).
    snap_trimmed = False
    if est_tokens(snap_min) > budget["snapshot"]:
        snap_trimmed = True
    user = (
        "CONTEXT — Playbook excerpts (relevant modules only):\n"
        f"{playbook or '(none surfaced this week)'}\n\n"
        "CONTEXT — snapshot.min.json:\n"
        f"{snap_min}\n"
    )
    meta = {
        "playbook_modules": included,
        "tokens": {
            "system": est_tokens(_system_prompt()),
            "playbook": est_tokens(playbook),
            "snapshot": est_tokens(snap_min),
        },
        "snapshot_over_cap": snap_trimmed,
    }
    meta["tokens"]["total_input"] = sum(
        meta["tokens"][k] for k in ("system", "playbook", "snapshot")
    )
    return user, meta


def write_bundle(
    snapshot: dict, registry: Registry, config: AIConfig, as_of: dt.date,
    base_dir: Path | None = None,
) -> dict:
    """Write prompt_bundle.md for the manual-paste path. Returns paths + meta."""
    user, meta = build_user_message(snapshot, registry, config.budget)
    system = _system_prompt()
    bundle = (
        f"# IPOS prompt bundle — {as_of.isoformat()} "
        f"(prompt v{config.prompt_version})\n\n"
        f"Paste everything below into your LLM of choice for the weekly check-up.\n\n"
        f"---\n## SYSTEM\n\n{system}\n\n---\n## USER\n\n{user}"
    )
    out_dir = (base_dir or EXPORTS_DIR) / as_of.isoformat()
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "prompt_bundle.md"
    path.write_text(bundle, encoding="utf-8")
    return {"prompt_bundle": str(path), "meta": meta}


def narrate(snapshot: dict, registry: Registry, config: AIConfig) -> dict | None:
    """Call the configured provider. Returns {interpretation, meta} or None
    (provider: none/manual make no call). Attaching to the snapshot is the
    caller's choice."""
    provider = get_provider(config)
    user, meta = build_user_message(snapshot, registry, config.budget)
    text = provider.narrate(_system_prompt(), user)
    if text is None:
        return None
    return {
        "interpretation": text,
        "interpretation_meta": {
            "provider": getattr(provider, "name", config.provider),
            "prompt_version": config.prompt_version,
            "model": config.model,
        },
    }
