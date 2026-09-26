"""IPOS Evidence and Research Understanding Layer (E05 / E06).

Provides:
- Cryptographically grounded media transcripts and visual scene frames
- Verifiable, source-grounded claim extraction with verbatim quote matching
- Single-writer Action & Watch Register for thesis invalidation and monitoring
"""

from ipos.evidence.schemas import (
    ExtractedClaim,
    RegisterDocument,
    SourceMedia,
    TranscriptSegment,
    WatchItem,
)

__all__ = [
    "ExtractedClaim",
    "RegisterDocument",
    "SourceMedia",
    "TranscriptSegment",
    "WatchItem",
]
