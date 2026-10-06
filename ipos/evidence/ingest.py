"""Automated Evidence Ingestion Engine (WF-07 Stages 1–3).

Discovers, verifies, and ingests qualitative macroeconomic and market research drops
from data/inbox/research/ into the single-writer Action & Watch Register.

Governing Axioms:
1. Strict Grounding: Every claim must be mathematically verified against verbatim ASR
   transcript quotes with exact millisecond timestamps [start_seconds, end_seconds].
2. Anti-Injection Quarantine: Any adversarial prompt injection or execution trigger is
   defanged and quarantined before touching register or portfolio rules.
3. Canonical Taxonomy: Qualitative sectors are deterministically mapped to the 6 IPOS
   sector clusters (e.g. TECHNOLOGY_AI, ENERGY_COMMODITIES).
4. Idempotency & Provenance: Drops are content-addressed and idempotently tracked via
   ingestion receipts. Re-running the pipeline never creates duplicates.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
from typing import Any, List, Optional, Tuple
import yaml

from ipos.config.load import REPO_ROOT
from ipos.evidence.claims import (
    build_claim,
    sanitize_malicious_instruction,
    verify_quote_grounding,
)
from ipos.evidence.register import ActionWatchRegister
from ipos.evidence.schemas import ExtractedClaim, TranscriptSegment, TranscriptWord, WatchItem

DEFAULT_RESEARCH_INBOX = REPO_ROOT / "data" / "inbox" / "research"
RECEIPTS_DIR = DEFAULT_RESEARCH_INBOX / ".ingested"

SECTOR_SYNONYMS: dict[str, list[str]] = {
    "TECHNOLOGY_AI": [
        "TECHNOLOGY", "TECH", "AI", "SEMICONDUCTOR", "SEMIS", "SEMICONDUCTORS",
        "SOFTWARE", "INFORMATION_TECHNOLOGY", "CLOUD", "HARDWARE",
    ],
    "CRYPTO_DIGITAL_ASSETS": [
        "CRYPTO", "BITCOIN", "BTC", "DIGITAL_ASSETS", "ETHEREUM", "ETH",
        "BLOCKCHAIN", "MINING", "DEFI",
    ],
    "HEALTHCARE_BIOTECH": [
        "HEALTHCARE", "BIOTECH", "BIOTECHNOLOGY", "PHARMA", "THERAPEUTICS",
        "MEDTECH", "LIFE_SCIENCES",
    ],
    "ENERGY_COMMODITIES": [
        "ENERGY", "COMMODITIES", "OIL", "GAS", "CRUDE", "COPPER", "GOLD",
        "METALS", "MINING_COMMODITIES", "WTI", "BRENT",
    ],
    "DEFENSE_INDUSTRIALS": [
        "DEFENSE", "INDUSTRIALS", "AEROSPACE", "MANUFACTURING", "ENGINEERING",
        "CAPITAL_GOODS", "MILITARY",
    ],
    "FINANCIALS_VALUE": [
        "FINANCIALS", "BANKS", "INSURANCE", "VALUE", "BROKERS", "EXCHANGES",
    ],
}


def normalize_sector_cluster(raw_sector: str | None) -> str:
    """Map arbitrary research sector tags to one of the 6 canonical IPOS sector clusters."""
    if not raw_sector:
        return "OTHER_UNCLASSIFIED"
    clean = re.sub(r"[\s\-_]+", "_", raw_sector.strip().upper())
    for cluster_id, synonyms in SECTOR_SYNONYMS.items():
        if clean == cluster_id or clean in synonyms:
            return cluster_id
        for syn in synonyms:
            if syn in clean:
                return cluster_id
    return clean


@dataclass
class IngestionResult:
    """Summary metrics of an evidence ingestion run."""

    files_discovered: int = 0
    files_processed: int = 0
    files_skipped_receipt: int = 0
    claims_verified: int = 0
    watches_registered: int = 0
    actions_registered: int = 0
    quarantined_count: int = 0
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def discover_research_inbox(inbox_dir: Path | None = None) -> list[Path]:
    """Find all candidate research drops (.json, .yaml, .yml) in inbox directories."""
    base = inbox_dir or DEFAULT_RESEARCH_INBOX
    candidates: list[Path] = []

    if base.exists():
        for p in base.glob("**/*"):
            if p.is_file() and p.suffix.lower() in (".json", ".yaml", ".yml"):
                if ".ingested" in p.parts or p.name.startswith("."):
                    continue
                # Skip register itself if pointed at data/
                if p.name == "action_watch_register.json":
                    continue
                candidates.append(p)

    # Also check data/inbox/ directly for research_*.json or claim_*.yaml
    root_inbox = REPO_ROOT / "data" / "inbox"
    if root_inbox.exists() and root_inbox != base:
        for pat in ("research*.json", "research*.yaml", "claim*.json", "claim*.yaml"):
            for p in root_inbox.glob(pat):
                if p.is_file() and p not in candidates:
                    candidates.append(p)

    return sorted(candidates)


def _load_transcript_segments(
    drop_dir: Path, data: dict[str, Any]
) -> tuple[list[TranscriptSegment], str]:
    """Resolve and parse transcript segments from drop dict or referenced audio.json."""
    # 1. Embedded segments in the drop file
    if "segments" in data and isinstance(data["segments"], list) and data["segments"]:
        segments: list[TranscriptSegment] = []
        for idx, s in enumerate(data["segments"]):
            words = [
                TranscriptWord(
                    word=w.get("word", ""),
                    start=w.get("start"),
                    end=w.get("end"),
                    score=w.get("score", 1.0),
                )
                for w in s.get("words", [])
            ]
            segments.append(
                TranscriptSegment(
                    id=s.get("id", idx),
                    start=float(s.get("start", 0.0)),
                    end=float(s.get("end", 0.0)),
                    text=str(s.get("text", "")).strip(),
                    words=words,
                    avg_logprob=s.get("avg_logprob"),
                )
            )
        computed_sha = hashlib.sha256(json.dumps(data["segments"]).encode("utf-8")).hexdigest()
        return segments, computed_sha

    # 2. Referenced transcript file
    tr_ref = data.get("transcript_path") or data.get("audio_json") or "audio.json"
    candidate_paths = [
        drop_dir / tr_ref,
        DEFAULT_RESEARCH_INBOX / tr_ref,
        REPO_ROOT / "data" / "inbox" / tr_ref,
        REPO_ROOT / "implementation-runs" / "E05" / "20260923-230911" / "audio.json",
    ]

    for cand in candidate_paths:
        if cand.exists():
            content_bytes = cand.read_bytes()
            computed_sha = hashlib.sha256(content_bytes).hexdigest()
            parsed = json.loads(content_bytes.decode("utf-8"))
            raw_segs = parsed.get("segments", [])
            segments = []
            for idx, s in enumerate(raw_segs):
                words = [
                    TranscriptWord(
                        word=w.get("word", ""),
                        start=w.get("start"),
                        end=w.get("end"),
                        score=w.get("score", 1.0),
                    )
                    for w in s.get("words", [])
                ]
                segments.append(
                    TranscriptSegment(
                        id=idx,
                        start=float(s.get("start", 0.0)),
                        end=float(s.get("end", 0.0)),
                        text=str(s.get("text", "")).strip(),
                        words=words,
                        avg_logprob=s.get("avg_logprob"),
                    )
                )
            return segments, computed_sha

    raise FileNotFoundError(
        f"No transcript segments found embedded or in candidate paths for drop in {drop_dir}"
    )


def process_research_drop(
    drop_path: Path,
    register: ActionWatchRegister | None = None,
    receipts_dir: Path | None = None,
) -> IngestionResult:
    """Ingest a single research drop file into the ActionWatchRegister."""
    reg = register or ActionWatchRegister()
    r_dir = receipts_dir or RECEIPTS_DIR
    r_dir.mkdir(parents=True, exist_ok=True)
    res = IngestionResult(files_discovered=1)

    file_bytes = drop_path.read_bytes()
    file_sha256 = hashlib.sha256(file_bytes).hexdigest()
    receipt_file = r_dir / f"{drop_path.stem}_{file_sha256[:12]}.receipt.json"

    if receipt_file.exists():
        res.files_skipped_receipt += 1
        return res

    try:
        raw_text = file_bytes.decode("utf-8")
        if drop_path.suffix.lower() in (".yaml", ".yml"):
            data = yaml.safe_load(raw_text) or {}
        else:
            data = json.loads(raw_text)
    except Exception as exc:
        res.errors.append(f"Failed to parse {drop_path.name}: {exc}")
        return res

    source_id = str(data.get("source_id", drop_path.stem))
    source_ref = str(
        data.get("custody_url")
        or data.get("url")
        or data.get("source_urn")
        or source_id
    )
    claims_raw = data.get("claims") or []
    if not claims_raw and "quote_exact" in data:
        # Single claim card format
        claims_raw = [data]

    if not claims_raw:
        res.errors.append(f"{drop_path.name}: contains no claims")
        return res

    try:
        segments, transcript_sha256 = _load_transcript_segments(drop_path.parent, data)
    except Exception as exc:
        res.errors.append(f"{drop_path.name}: transcript error: {exc}")
        return res

    processed_claims = []

    for c_raw in claims_raw:
        cid = str(c_raw.get("claim_id", f"CLM-{source_id}-{len(processed_claims)+1:03d}"))
        theme = str(c_raw.get("theme", "MACRO"))
        topic = str(c_raw.get("instrument_or_topic", "MACRO_GENERAL"))
        raw_sector = c_raw.get("sector")
        canon_sector = normalize_sector_cluster(raw_sector)
        assertion = str(c_raw.get("assertion", ""))
        inval = str(c_raw.get("invalidation_condition", ""))
        quote = str(c_raw.get("quote_exact", ""))
        speaker = str(c_raw.get("speaker", "Analyst"))
        item_class = str(c_raw.get("item_class", "WATCH")).upper()
        if item_class not in ("WATCH", "ACTION"):
            item_class = "WATCH"

        reason = str(c_raw.get("reason_short", assertion or inval))
        metric = c_raw.get("invalidation_metric")
        threshold = float(c_raw["target_threshold"]) if "target_threshold" in c_raw and c_raw["target_threshold"] is not None else None

        try:
            claim_obj = build_claim(
                claim_id=cid,
                source_id=source_id,
                source_sha256=transcript_sha256,
                theme=theme,
                instrument_or_topic=topic,
                assertion=assertion,
                invalidation_condition=inval,
                quote_exact=quote,
                segments=segments,
                speaker=speaker,
            )
            res.claims_verified += 1
            if claim_obj.is_malicious:
                res.quarantined_count += 1
        except Exception as exc:
            res.errors.append(f"{cid} quote grounding failed: {exc}")
            continue

        # Build WatchItem for ActionWatchRegister
        item_id = str(c_raw.get("item_id", f"{item_class}-{cid.replace('CLM-', '')}"))
        action_or_cond = str(c_raw.get("action_or_condition", inval or assertion))

        watch_item = WatchItem(
            item_id=item_id,
            item_class=item_class,
            instrument_or_topic=canon_sector if item_class == "ACTION" else topic,
            action_or_condition=action_or_cond,
            reason_short=reason,
            linked_claim_ids=[cid],
            evidence_refs=[f"{source_ref}#t={claim_obj.start_seconds:.1f}"],
            status="QUARANTINED" if claim_obj.is_malicious else "OPEN",
            invalidation_metric=metric,
            target_threshold=threshold,
        )

        reg.upsert_item(watch_item)
        if item_class == "ACTION":
            res.actions_registered += 1
        else:
            res.watches_registered += 1
        processed_claims.append(cid)

    res.files_processed += 1

    # Write persistent receipt to avoid reprocessing
    receipt = {
        "drop_file": str(drop_path),
        "source_id": source_id,
        "file_sha256": file_sha256,
        "transcript_sha256": transcript_sha256,
        "claims_processed": processed_claims,
        "ingested_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    receipt_file.write_text(json.dumps(receipt, indent=2), encoding="utf-8")

    return res


def ingest_all_pending_evidence(
    inbox_dir: Path | None = None,
    register: ActionWatchRegister | None = None,
) -> IngestionResult:
    """Master inbox runner: scans inbox and processes all uningested research drops."""
    candidates = discover_research_inbox(inbox_dir)
    reg = register or ActionWatchRegister()
    total_result = IngestionResult(files_discovered=len(candidates))

    for drop_path in candidates:
        single_res = process_research_drop(drop_path, register=reg)
        total_result.files_processed += single_res.files_processed
        total_result.files_skipped_receipt += single_res.files_skipped_receipt
        total_result.claims_verified += single_res.claims_verified
        total_result.watches_registered += single_res.watches_registered
        total_result.actions_registered += single_res.actions_registered
        total_result.quarantined_count += single_res.quarantined_count
        total_result.errors.extend(single_res.errors)

    return total_result
