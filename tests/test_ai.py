"""AI narration layer tests (C6): $0 default (provider none) makes no call and
attaches no interpretation; prompt bundle is well-formed and within budget;
playbook retrieval is deterministic and relevance-ordered; a (fake) live
provider's interpretation flows into snapshot + report. No real API calls."""

from __future__ import annotations

import ipos.ai.bundle as bundle_mod
from ipos.ai.bundle import build_user_message, est_tokens, narrate, write_bundle
from ipos.ai.playbook import surfaced_playbook_refs
from ipos.ai.provider import AIConfig, NoneProvider, get_provider, load_ai_config
from ipos.export.snapshot import build_snapshot
from ipos.report.html import render_html
from ipos.warehouse.db import connect


def _snapshot(populated_db, as_of):
    db, reg = populated_db
    with connect(db, read_only=True) as con:
        return build_snapshot(con, reg, as_of), reg


def test_default_provider_is_none():
    cfg = load_ai_config()
    assert cfg.provider == "none"
    assert isinstance(get_provider(cfg), NoneProvider)
    assert get_provider(cfg).narrate("sys", "user") is None


def test_narrate_none_returns_nothing(populated_db, as_of):
    snap, reg = _snapshot(populated_db, as_of)
    assert narrate(snap, reg, AIConfig(provider="none")) is None


def test_bundle_within_budget_and_structured(populated_db, as_of, tmp_path):
    snap, reg = _snapshot(populated_db, as_of)
    cfg = AIConfig(provider="manual")
    user, meta = build_user_message(snap, reg, cfg.budget)
    assert meta["tokens"]["playbook"] <= cfg.budget["playbook"]
    assert meta["tokens"]["snapshot"] <= cfg.budget["snapshot"]
    res = write_bundle(snap, reg, cfg, as_of, base_dir=tmp_path)
    text = open(res["prompt_bundle"]).read()
    assert "## SYSTEM" in text and "## USER" in text
    assert "snapshot.min.json" in text


def test_playbook_retrieval_deterministic_and_relevant(populated_db, as_of):
    snap, reg = _snapshot(populated_db, as_of)
    a = surfaced_playbook_refs(snap, reg)
    b = surfaced_playbook_refs(snap, reg)
    assert a == b  # deterministic order
    # every returned id is a real playbook module referenced by some module
    all_refs = {r for m in reg.modules.values() for r in m.playbook_refs}
    all_refs |= {r for e in reg.active() for r in e.playbook_refs}
    assert set(a) <= all_refs


def test_live_provider_interpretation_flows_to_report(populated_db, as_of, monkeypatch):
    snap, reg = _snapshot(populated_db, as_of)

    class FakeProvider:
        name = "fake"
        def narrate(self, system, user):
            return "Situation: risk budget is moderate.\nStance: small size."

    monkeypatch.setattr(bundle_mod, "get_provider", lambda cfg: FakeProvider())
    out = narrate(snap, reg, AIConfig(provider="fake"))
    assert out is not None
    assert "interpretation" in out and out["interpretation_meta"]["provider"] == "fake"

    snap.update(out)
    db, _ = populated_db
    with connect(db, read_only=True) as con:
        html = render_html(con, snap, as_of)
    assert "risk budget is moderate" in html
    assert "Narrated by fake" in html


def test_est_tokens():
    assert est_tokens("abcd") == 1
    assert est_tokens("") == 0


def test_file_provider_reads_dropped_narration(populated_db, as_of, tmp_path):
    snap, reg = _snapshot(populated_db, as_of)
    d = tmp_path / as_of.isoformat()
    d.mkdir(parents=True)
    (d / "narration.md").write_text("Situation: test narration.", encoding="utf-8")
    out = narrate(snap, reg, AIConfig(provider="file"), as_of=as_of, base_dir=tmp_path)
    assert out is not None
    assert out["interpretation"] == "Situation: test narration."
    assert "file" in out["interpretation_meta"]["provider"]
    # absent file -> no narration, no crash
    assert narrate(snap, reg, AIConfig(provider="file"), as_of=as_of,
                   base_dir=tmp_path / "empty") is None


def test_anthropic_provider_posts_and_parses(populated_db, as_of, monkeypatch):
    snap, reg = _snapshot(populated_db, as_of)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    captured = {}

    class Resp:
        def raise_for_status(self): pass
        def json(self):
            return {"content": [{"type": "text", "text": "Situation: live narration."}]}

    def fake_post(url, headers=None, json=None, timeout=None):
        captured["url"] = url
        captured["model"] = json["model"]
        captured["key"] = headers["x-api-key"]
        return Resp()

    monkeypatch.setattr("requests.post", fake_post)
    out = narrate(snap, reg, AIConfig(provider="anthropic", model="claude-haiku-4-5-20251001"))
    assert out["interpretation"] == "Situation: live narration."
    assert captured["url"].endswith("/v1/messages")
    assert captured["key"] == "test-key"
