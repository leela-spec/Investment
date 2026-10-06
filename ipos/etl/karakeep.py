"""Karakeep Evidence Custody ETL Connector (WF-07 Stages 1–3).

Connects to the self-hosted Karakeep container REST API (running on port 3000)
to query, sync, and custody macroeconomic research bookmarks, PDF whitepapers,
web archives, and WhisperX audio transcript assets.

Governing Axioms:
1. Physical Boundary: Karakeep runs on WSL2 Ubuntu ext4; this connector queries
   the HTTP REST endpoint (default http://127.0.0.1:3000) natively from Windows NTFS.
2. Cryptographic Custody: Downloaded assets and drops compute exact SHA-256 digests.
   Foreign identity is strictly preserved as ``source_urn: "karakeep:entries:<id>"``.
3. Fail-Closed Resilience: Missing authentication, network divergence, or unexpected
   API schemas raise typed exceptions rather than returning silent empty data.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import datetime as dt
import hashlib
import json
import logging
import os
from pathlib import Path
import re
from typing import Any, List, Optional, Tuple

import requests

from ipos.config.load import REPO_ROOT

logger = logging.getLogger(__name__)

DEFAULT_KARAKEEP_URL = "http://127.0.0.1:3000"
DEFAULT_RESEARCH_INBOX = REPO_ROOT / "data" / "inbox" / "research"


class KarakeepError(Exception):
    """Base exception for all Karakeep ETL errors."""


class KarakeepConfigError(KarakeepError):
    """Raised when Karakeep URL or API key configuration is missing or invalid."""


class KarakeepConnectionError(KarakeepError):
    """Raised when Karakeep service is unreachable or network times out."""


class KarakeepResponseError(KarakeepError):
    """Raised when Karakeep returns an error status code or unexpected schema (mock-denial)."""


@dataclass
class KarakeepBookmark:
    """Normalized Karakeep bookmark representation."""

    id: str
    title: str
    url: str | None = None
    note: str | None = None
    tags: list[str] = field(default_factory=list)
    created_at: str | None = None
    assets: list[dict[str, Any]] = field(default_factory=list)
    content: str | None = None

    @property
    def source_urn(self) -> str:
        return f"karakeep:entries:{self.id}"


@dataclass
class KarakeepSyncSummary:
    """Summary metrics of a Karakeep sync operation."""

    bookmarks_discovered: int = 0
    drops_created: int = 0
    assets_downloaded: int = 0
    files_written: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class KarakeepClient:
    """Client for Karakeep v0.33.x REST API."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: float = 10.0,
    ) -> None:
        raw_url = base_url or os.environ.get("KARAKEEP_URL") or DEFAULT_KARAKEEP_URL
        self.base_url = raw_url.rstrip("/")
        self.api_key = api_key if api_key is not None else os.environ.get("KARAKEEP_API_KEY", "")
        self.timeout = timeout

        if not self.base_url.startswith(("http://", "https://")):
            raise KarakeepConfigError(f"Invalid KARAKEEP_URL schema (must begin with http:// or https://): {self.base_url}")

    def _headers(self) -> dict[str, str]:
        if not self.api_key:
            raise KarakeepConfigError("KARAKEEP_API_KEY is required for authenticating with Karakeep REST API.")
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "User-Agent": "IPOS-Quantitative-Connector/1.0",
        }

    def _request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        stream: bool = False,
    ) -> requests.Response:
        url = f"{self.base_url}{endpoint}"
        headers = self._headers()
        try:
            res = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                timeout=self.timeout,
                stream=stream,
            )
        except requests.exceptions.ConnectionError as exc:
            raise KarakeepConnectionError(f"Could not connect to Karakeep at {url}: {exc}") from exc
        except requests.exceptions.Timeout as exc:
            raise KarakeepConnectionError(f"Timeout connecting to Karakeep at {url} ({self.timeout}s): {exc}") from exc
        except requests.exceptions.RequestException as exc:
            raise KarakeepConnectionError(f"Network error querying Karakeep at {url}: {exc}") from exc

        if res.status_code == 401:
            raise KarakeepResponseError(f"Karakeep authentication failed (401 Unauthorized): verify KARAKEEP_API_KEY.")
        if res.status_code == 403:
            raise KarakeepResponseError(f"Karakeep access forbidden (403 Forbidden).")
        if not res.ok:
            raise KarakeepResponseError(
                f"Karakeep returned HTTP {res.status_code} on {endpoint}: {res.text[:200]}"
            )

        return res

    def list_bookmarks(
        self,
        tag: str | None = None,
        cursor: str | None = None,
        limit: int = 50,
        include_content: bool = True,
    ) -> tuple[list[dict[str, Any]], str | None]:
        """Fetch bookmarks matching tag filter.
        
        Enforces schema validation on return payload (mock-denial).
        """
        params: dict[str, Any] = {"limit": limit}
        if tag:
            params["tag"] = tag
        if cursor:
            params["cursor"] = cursor
        if include_content:
            params["includeContent"] = "true"

        res = self._request("GET", "/api/v1/bookmarks", params=params)
        try:
            data = res.json()
        except Exception as exc:
            raise KarakeepResponseError(f"Failed to parse Karakeep JSON response: {exc}") from exc

        if not isinstance(data, dict):
            raise KarakeepResponseError(f"Unexpected Karakeep response structure: expected JSON object, got {type(data).__name__}")

        raw_bookmarks = data.get("bookmarks")
        if raw_bookmarks is None:
            raw_bookmarks = data.get("items")
        if raw_bookmarks is None:
            raise KarakeepResponseError(f"Karakeep response missing required 'bookmarks' or 'items' key: {list(data.keys())}")

        if not isinstance(raw_bookmarks, list):
            raise KarakeepResponseError(f"Karakeep 'bookmarks' must be a list, got {type(raw_bookmarks).__name__}")

        # Validate each bookmark has required identifier
        for idx, b in enumerate(raw_bookmarks):
            if not isinstance(b, dict):
                raise KarakeepResponseError(f"Karakeep bookmark at index {idx} is not an object: {b}")
            if "id" not in b or not b["id"]:
                raise KarakeepResponseError(f"Karakeep bookmark at index {idx} missing required 'id' field: {b}")

        next_cursor = data.get("nextCursor") or data.get("cursor")
        return raw_bookmarks, str(next_cursor) if next_cursor else None

    def get_content(self, bookmark_id: str, format: str = "markdown", max_chars: int = 50000) -> str:
        """Fetch readable content of a bookmark."""
        params = {"format": format, "maxChars": max_chars}
        res = self._request("GET", f"/api/v1/bookmarks/{bookmark_id}/content", params=params)
        try:
            data = res.json()
            if isinstance(data, dict) and "content" in data:
                return str(data["content"])
            return res.text
        except Exception:
            return res.text

    def download_asset(self, asset_id: str, dest_path: Path) -> Path:
        """Download a binary asset from Karakeep, computing SHA-256."""
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        res = self._request("GET", f"/api/v1/assets/{asset_id}", stream=True)
        hasher = hashlib.sha256()
        with dest_path.open("wb") as fh:
            for chunk in res.iter_content(chunk_size=65536):
                if chunk:
                    fh.write(chunk)
                    hasher.update(chunk)
        logger.info("Downloaded Karakeep asset %s -> %s (sha256: %s)", asset_id, dest_path.name, hasher.hexdigest()[:12])
        return dest_path

    def fetch_tagged_evidence(
        self,
        tag: str = "macro",
        destination_dir: Path | None = None,
    ) -> list[Path]:
        """Query Karakeep REST endpoint for tagged bookmarks and write drops to inbox.
        
        Preserves Karakeep bookmark ID as source_urn: "karakeep:entries:<id>".
        """
        dest = destination_dir or DEFAULT_RESEARCH_INBOX
        dest.mkdir(parents=True, exist_ok=True)

        created_files: list[Path] = []
        cursor: str | None = None

        while True:
            bookmarks, next_cursor = self.list_bookmarks(tag=tag, cursor=cursor)
            for b in bookmarks:
                b_id = str(b["id"])
                source_urn = f"karakeep:entries:{b_id}"
                source_id = f"karakeep-{b_id}"
                nested_content = b.get("content")
                nested_url = (
                    nested_content.get("url")
                    if isinstance(nested_content, dict)
                    else None
                )

                # Extract normalized tags
                raw_tags = b.get("tags") or []
                clean_tags = []
                for t in raw_tags:
                    if isinstance(t, str):
                        clean_tags.append(t)
                    elif isinstance(t, dict) and "name" in t:
                        clean_tags.append(str(t["name"]))

                # Process attached assets
                assets_info = []
                raw_assets = b.get("assets") or []
                transcript_ref: str | None = None

                for a in raw_assets:
                    if not isinstance(a, dict):
                        continue
                    aid = str(a.get("id", ""))
                    if not aid:
                        continue
                    filename = a.get("fileName") or a.get("file_name") or f"asset_{aid}"
                    safe_name = f"karakeep_{b_id}_{re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)}"
                    asset_dest = dest / safe_name
                    try:
                        self.download_asset(aid, asset_dest)
                        file_bytes = asset_dest.read_bytes()
                        asset_sha = hashlib.sha256(file_bytes).hexdigest()
                        assets_info.append({
                            "id": aid,
                            "file_name": safe_name,
                            "sha256": asset_sha,
                            "asset_type": a.get("assetType") or a.get("type", "unknown"),
                        })
                        if safe_name.endswith(".json") and ("audio" in safe_name or "transcript" in safe_name):
                            transcript_ref = safe_name
                    except Exception as exc:
                        logger.warning("Failed to download Karakeep asset %s for bookmark %s: %exc", aid, b_id, exc)

                # Formulate research drop dictionary
                drop_data: dict[str, Any] = {
                    "schema_version": "1.0",
                    "source_id": source_id,
                    "source_urn": source_urn,
                    "custody_url": f"{self.base_url}/dashboard/preview/{b_id}",
                    "karakeep_bookmark_id": b_id,
                    "title": b.get("title", f"Karakeep Bookmark {b_id}"),
                    "url": b.get("url") or b.get("sourceUrl") or nested_url,
                    "note": b.get("note"),
                    "tags": clean_tags,
                    "created_at": b.get("createdAt") or dt.datetime.now(dt.timezone.utc).isoformat(),
                    "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                    "assets": assets_info,
                }

                if transcript_ref:
                    drop_data["transcript_path"] = transcript_ref

                # If bookmark has embedded content or claims in note
                content_str = b.get("content")
                if not content_str and b.get("hasContent"):
                    try:
                        content_str = self.get_content(b_id)
                    except Exception as exc:
                        logger.debug("Could not fetch extended content for %s: %s", b_id, exc)

                if content_str:
                    drop_data["content"] = content_str

                # Parse claims if present in note or content structure
                if "claims" in b and isinstance(b["claims"], list):
                    drop_data["claims"] = b["claims"]
                elif b.get("note") and "CLM-" in str(b.get("note")):
                    # Operator included YAML or JSON claim format inside the note
                    try:
                        parsed_note = json.loads(str(b["note"]))
                        if isinstance(parsed_note, dict) and "claims" in parsed_note:
                            drop_data["claims"] = parsed_note["claims"]
                    except Exception:
                        pass

                drop_file = dest / f"karakeep_{b_id}.json"
                drop_file.write_text(json.dumps(drop_data, indent=2), encoding="utf-8")
                created_files.append(drop_file)

            if not next_cursor or next_cursor == cursor:
                break
            cursor = next_cursor

        return created_files


def fetch_tagged_evidence(
    tag: str = "macro",
    destination_dir: Path | None = None,
    client: KarakeepClient | None = None,
) -> list[Path]:
    """Top-level functional interface to fetch tagged research evidence from Karakeep."""
    c = client or KarakeepClient()
    return c.fetch_tagged_evidence(tag=tag, destination_dir=destination_dir)


def sync_karakeep_evidence(
    tag: str = "macro",
    inbox_dir: Path | None = None,
    client: KarakeepClient | None = None,
) -> KarakeepSyncSummary:
    """Operational sync runner: queries Karakeep and reports detailed metrics."""
    summary = KarakeepSyncSummary()
    try:
        c = client or KarakeepClient()
        drops = c.fetch_tagged_evidence(tag=tag, destination_dir=inbox_dir)
        summary.drops_created = len(drops)
        summary.files_written = [str(p) for p in drops]
        summary.bookmarks_discovered = len(drops)
    except KarakeepError as exc:
        summary.errors.append(str(exc))
    except Exception as exc:
        summary.errors.append(f"Unexpected error syncing Karakeep: {exc}")
    return summary
