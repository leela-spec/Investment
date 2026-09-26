"""Data schemas for Evidence, Source-Grounded Claims, and the Action/Watch Register."""

from __future__ import annotations

import datetime as dt
from typing import Any, List, Optional
from pydantic import BaseModel, Field


class TranscriptWord(BaseModel):
    """Individual aligned word with timestamps."""
    word: str
    start: Optional[float] = None
    end: Optional[float] = None
    score: Optional[float] = 1.0


class TranscriptSegment(BaseModel):
    """Segment of transcribed speech from WhisperX / ASR engine."""
    id: Optional[int] = None
    start: float
    end: float
    text: str
    words: List[TranscriptWord] = Field(default_factory=list)
    avg_logprob: Optional[float] = None


class SourceMedia(BaseModel):
    """Metadata and verified provenance for a research media artifact."""
    source_id: str
    title: str
    publisher: str
    url: str
    duration_seconds: float
    sha256: str
    segments: List[TranscriptSegment] = Field(default_factory=list)
    scenes: List[dict[str, Any]] = Field(default_factory=list)


class ExtractedClaim(BaseModel):
    """Source-grounded, falsifiable claim extracted from research evidence."""
    claim_id: str
    source_id: str
    source_sha256: str
    speaker: str = "Narrator / Analyst"
    theme: str
    instrument_or_topic: str
    assertion: str
    invalidation_condition: str
    quote_exact: str
    start_seconds: float
    end_seconds: float
    segment_indices: List[int] = Field(default_factory=list)
    evidence_frame_sha256: Optional[str] = None
    status: str = "ACTIVE"
    is_malicious: bool = False


class WatchItem(BaseModel):
    """Item in the single-writer Action / Watch Register (WF-07)."""
    item_id: str
    item_class: str = "WATCH"  # "WATCH" or "ACTION"
    instrument_or_topic: str
    action_or_condition: str
    reason_short: str
    linked_claim_ids: List[str] = Field(default_factory=list)
    evidence_refs: List[str] = Field(default_factory=list)
    status: str = "OPEN"  # "OPEN", "TRIGGERED", "RESOLVED", "EXPIRED"
    created_at: str = Field(default_factory=lambda: dt.datetime.now(dt.timezone.utc).isoformat())
    invalidation_metric: Optional[str] = None
    target_threshold: Optional[float] = None


class RegisterDocument(BaseModel):
    """Document format for data/action_watch_register.json."""
    schema_version: str = "1.0"
    updated_at: str = Field(default_factory=lambda: dt.datetime.now(dt.timezone.utc).isoformat())
    items: List[WatchItem] = Field(default_factory=list)
