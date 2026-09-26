"""Source-Grounded Claim Extraction & Verification Engine (E06).

Governing Rules:
1. Every claim must mathematically ground its exact quote against content-addressed transcript segments.
2. Exact timestamps [start_seconds, end_seconds] and segment indices are derived strictly from ASR alignment.
3. Malicious instructions inside transcripts are quarantined as passive text and blocked from rule/portfolio mutation.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any, List, Optional, Tuple
import yaml

from ipos.evidence.schemas import ExtractedClaim, SourceMedia, TranscriptSegment, TranscriptWord

# Common prompt-injection and tool-override signatures
MALICIOUS_PATTERNS = [
    r"(?i)ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"(?i)system\s+prompt\s+override",
    r"(?i)you\s+are\s+now\s+in\s+developer\s+mode",
    r"(?i)(execute|run)\s+(command|tool|shell|script)",
    r"(?i)(buy|sell)\s+100%\s+of",
    r"(?i)delete\s+from\s+",
    r"(?i)drop\s+table\s+",
    r"(?i)override\s+all\s+risk\s+rules",
]


def normalize_whitespace(text: str) -> str:
    """Standardize spacing while preserving character content."""
    return re.sub(r"\s+", " ", text).strip()


def sanitize_malicious_instruction(text: str) -> Tuple[str, bool]:
    """Inspect text for adversarial prompt injection or execution triggers.

    Returns:
        (sanitized_text, is_malicious)
    """
    for pattern in MALICIOUS_PATTERNS:
        if re.search(pattern, text):
            sanitized = f"[QUARANTINED_PROMPT_INJECTION: {text}]"
            return sanitized, True
    return text, False


def _find_word_span_timestamps(
    words: List[TranscriptWord], cleaned_quote: str
) -> Tuple[Optional[float], Optional[float]]:
    """Attempt to find exact start and end timestamps from aligned words."""
    if not words:
        return None, None
    quote_tokens = [w.lower() for w in re.findall(r"\w+", cleaned_quote)]
    if not quote_tokens:
        return None, None
    m = len(quote_tokens)
    word_tokens = [re.sub(r"\W+", "", (w.word or "").lower()) for w in words]
    for i in range(len(word_tokens) - m + 1):
        if word_tokens[i : i + m] == quote_tokens:
            w_start = words[i].start
            w_end = words[i + m - 1].end
            if w_start is not None and w_end is not None:
                return float(w_start), float(w_end)
    return None, None


def verify_quote_grounding(
    quote: str,
    segments: List[TranscriptSegment] | List[dict[str, Any]],
) -> Tuple[bool, float, float, List[int]]:
    """Ground a quote in transcript segments, determining exact timestamps and segment indices.

    Supports quotes contained within a single segment or spanning consecutive segments.
    Derives exact word-level timestamps when phoneme/word alignment is available.

    Returns:
        (is_grounded, start_seconds, end_seconds, segment_indices)

    Raises:
        ValueError if the quote is not present in the transcript.
    """
    cleaned_quote = normalize_whitespace(quote).lower()
    if not cleaned_quote:
        raise ValueError("Empty quote cannot be grounded")

    # Normalize segments and ensure integer id
    seg_list: List[TranscriptSegment] = []
    for idx, s in enumerate(segments):
        if isinstance(s, dict):
            seg = TranscriptSegment(**s)
        else:
            seg = s
        if seg.id is None:
            seg.id = idx
        seg_list.append(seg)

    if not seg_list:
        raise ValueError("Transcript contains zero segments")

    # 1. Check within single segment (with word-level timestamp refinement)
    for s in seg_list:
        clean_text = normalize_whitespace(s.text).lower()
        if cleaned_quote in clean_text:
            w_start, w_end = _find_word_span_timestamps(s.words, cleaned_quote)
            start_sec = w_start if w_start is not None else s.start
            end_sec = w_end if w_end is not None else s.end
            return True, start_sec, end_sec, [s.id]

    # 2. Check across consecutive segments (sliding window of up to 4 segments)
    n = len(seg_list)
    for window_size in range(2, min(5, n + 1)):
        for i in range(n - window_size + 1):
            combined_window = seg_list[i : i + window_size]
            combined_text = normalize_whitespace(
                " ".join(s.text for s in combined_window)
            ).lower()
            if cleaned_quote in combined_text:
                start_sec = combined_window[0].start
                end_sec = combined_window[-1].end
                indices = [s.id for s in combined_window]
                return True, start_sec, end_sec, indices

    # 3. Flexible punctuation-agnostic match
    quote_words = re.findall(r"\w+", cleaned_quote)
    if quote_words:
        target_seq = " ".join(quote_words)
        for s in seg_list:
            seg_words = " ".join(re.findall(r"\w+", s.text.lower()))
            if target_seq in seg_words:
                w_start, w_end = _find_word_span_timestamps(s.words, cleaned_quote)
                start_sec = w_start if w_start is not None else s.start
                end_sec = w_end if w_end is not None else s.end
                return True, start_sec, end_sec, [s.id]

        # Multi-segment punctuation-agnostic
        for window_size in range(2, min(5, n + 1)):
            for i in range(n - window_size + 1):
                combined_window = seg_list[i : i + window_size]
                comb_words = " ".join(
                    re.findall(r"\w+", " ".join(s.text for s in combined_window).lower())
                )
                if target_seq in comb_words:
                    return (
                        True,
                        combined_window[0].start,
                        combined_window[-1].end,
                        [s.id for s in combined_window],
                    )

    raise ValueError(f"Quote not found in transcript: '{quote}'")


def build_claim(
    claim_id: str,
    source_id: str,
    source_sha256: str,
    theme: str,
    instrument_or_topic: str,
    assertion: str,
    invalidation_condition: str,
    quote_exact: str,
    segments: List[TranscriptSegment] | List[dict[str, Any]],
    speaker: str = "Narrator / Analyst",
    evidence_frame_sha256: Optional[str] = None,
    status: str = "ACTIVE",
) -> ExtractedClaim:
    """Verify quote grounding, defend against prompt injection, and build a verified ExtractedClaim."""
    clean_assertion, assertion_malicious = sanitize_malicious_instruction(assertion)
    clean_quote, quote_malicious = sanitize_malicious_instruction(quote_exact)
    is_malicious = assertion_malicious or quote_malicious

    is_grounded, start_sec, end_sec, seg_indices = verify_quote_grounding(
        quote=quote_exact,
        segments=segments,
    )

    return ExtractedClaim(
        claim_id=claim_id,
        source_id=source_id,
        source_sha256=source_sha256,
        speaker=speaker,
        theme=theme,
        instrument_or_topic=instrument_or_topic,
        assertion=clean_assertion,
        invalidation_condition=invalidation_condition,
        quote_exact=clean_quote if not is_malicious else quote_exact,
        start_seconds=start_sec,
        end_seconds=end_sec,
        segment_indices=seg_indices,
        evidence_frame_sha256=evidence_frame_sha256,
        status="QUARANTINED" if is_malicious else status,
        is_malicious=is_malicious,
    )


def load_e05_research_artifact(path: Path | str | None = None) -> SourceMedia:
    """Load the E05 research artifact and its verified transcript segments directly from authentic WhisperX JSON."""
    if path is None:
        path = (
            Path(__file__).resolve().parent.parent.parent
            / "implementation-runs"
            / "E05"
            / "20260923-230911"
            / "RESEARCH_ARTIFACT.yaml"
        )
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Research artifact not found at: {p}")

    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    src = data.get("source", {})
    vis = data.get("visual_evidence", {})
    tr_meta = data.get("transcript", {})
    expected_sha256 = tr_meta.get("json_sha256")
    json_path_str = tr_meta.get("json_path", "")

    candidate_paths = [
        p.parent / "audio.json",
        Path(json_path_str) if json_path_str else None,
        Path(r"\\wsl.localhost\Ubuntu" + json_path_str) if json_path_str else None,
    ]

    resolved_json_path = None
    for cand in candidate_paths:
        if cand and cand.exists():
            content_bytes = cand.read_bytes()
            computed_sha = hashlib.sha256(content_bytes).hexdigest()
            if expected_sha256 and computed_sha == expected_sha256:
                resolved_json_path = cand
                break
            elif not expected_sha256:
                resolved_json_path = cand
                break

    if not resolved_json_path:
        raise FileNotFoundError(
            f"Authentic WhisperX audio.json matching SHA256 {expected_sha256} not found among candidates: {candidate_paths}"
        )

    transcript_data = json.loads(resolved_json_path.read_text(encoding="utf-8"))
    raw_segments = transcript_data.get("segments", [])

    imf_segments: List[TranscriptSegment] = []
    for idx, s in enumerate(raw_segments):
        words = [
            TranscriptWord(
                word=w.get("word", ""),
                start=w.get("start"),
                end=w.get("end"),
                score=w.get("score", 1.0),
            )
            for w in s.get("words", [])
        ]
        seg = TranscriptSegment(
            id=idx,
            start=float(s.get("start", 0.0)),
            end=float(s.get("end", 0.0)),
            text=s.get("text", "").strip(),
            words=words,
            avg_logprob=s.get("avg_logprob"),
        )
        imf_segments.append(seg)

    return SourceMedia(
        source_id=data.get("artifact_id", "imf-weo-update-2026-07-vzZpKJlpqKo"),
        title=src.get("title", ""),
        publisher=src.get("publisher", ""),
        url=src.get("url", ""),
        duration_seconds=float(src.get("duration_seconds", 128.948)),
        sha256=src.get("sha256", ""),
        segments=imf_segments,
        scenes=vis.get("selected_frames", []),
    )
