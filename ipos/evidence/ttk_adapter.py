"""Read-only adapter for validated Transcript Toolkit V2 fixture artifacts."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any

from ipos.evidence.schemas import TranscriptSegment


@dataclass(frozen=True)
class TTKFixture:
    identity: str
    transcript_sha256: str
    segments: list[TranscriptSegment]
    original_segment_ids: list[str]
    candidate_claims: list[dict[str, Any]]
    validation: dict[str, Any]


def load_ttk_fixture(root: Path) -> TTKFixture:
    """Load a complete TTK V2 fixture without modifying its source tree."""
    json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    transcript_path = root / "source" / "transcript.json"
    transcript_bytes = transcript_path.read_bytes()
    transcript = json.loads(transcript_bytes.decode("utf-8"))
    evidence = json.loads((root / "ledger" / "evidence.json").read_text(encoding="utf-8"))
    validation = json.loads((root / "validation.json").read_text(encoding="utf-8"))
    if not validation.get("ok") or not validation.get("complete"):
        raise ValueError(f"TTK fixture is not complete: {root}")

    raw_segments = transcript["segments"]
    original_ids = [str(segment["id"]) for segment in raw_segments]
    segments = [
        TranscriptSegment(
            id=index,
            start=float(segment["start"]),
            end=float(segment["end"]),
            text=str(segment["text"]),
            words=[],
        )
        for index, segment in enumerate(raw_segments)
    ]
    return TTKFixture(
        identity=root.name,
        transcript_sha256=hashlib.sha256(transcript_bytes).hexdigest(),
        segments=segments,
        original_segment_ids=original_ids,
        candidate_claims=list(evidence.get("candidate_claims") or []),
        validation=validation,
    )


def build_watch_drop(
    fixture: TTKFixture,
    claim_index: int,
    topic: str,
) -> dict[str, Any]:
    """Convert one cited TTK candidate into an IPOS-groundable WATCH drop."""
    candidate = fixture.candidate_claims[claim_index]
    cited_ids = [str(value) for value in candidate.get("source_segment_ids") or []]
    unknown_ids = [
        segment_id
        for segment_id in cited_ids
        if segment_id not in fixture.original_segment_ids
    ]
    if not cited_ids or unknown_ids:
        missing = unknown_ids or ["<none>"]
        raise ValueError(f"candidate cites unknown transcript segment: {missing}")

    quote = str(candidate["claim_text"])
    return {
        "schema_version": "1.0",
        "source_id": fixture.identity,
        "transcript_sha256": fixture.transcript_sha256,
        "segments": [segment.model_dump() for segment in fixture.segments],
        "claims": [
            {
                "claim_id": f"CLM-TTK-{fixture.identity}-{claim_index + 1:03d}",
                "item_id": f"WATCH-TTK-{fixture.identity}-{claim_index + 1:03d}",
                "item_class": "WATCH",
                "theme": "RESEARCH_FIXTURE",
                "instrument_or_topic": topic,
                "assertion": quote,
                "invalidation_condition": "Reassess against newer verified evidence",
                "quote_exact": quote,
                "action_or_condition": "Monitor only; operator review required",
                "reason_short": "Validated transcript candidate claim",
                "source_segment_ids": cited_ids,
            }
        ],
    }
