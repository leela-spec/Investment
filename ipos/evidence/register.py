"""Single-Writer Action & Watch Register Engine (WF-07 Stage 3 / M06).

Governing Rules:
1. Manages data/action_watch_register.json tracking active research watches and portfolio actions.
2. Enforces idempotent upserting by item_id (no duplicate registrations).
3. Defends against prompt injection at the register ingestion boundary.
4. Enforces strict lifecycle state machine:
   - OPEN -> TRIGGERED | EXPIRED | QUARANTINED
   - TRIGGERED -> RESOLVED | EXPIRED
   - Terminal states (RESOLVED, EXPIRED, QUARANTINED) cannot transition.
5. Atomic JSON persistence with strict BOM-free UTF-8.
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import List, Optional

from ipos.evidence.claims import sanitize_malicious_instruction
from ipos.evidence.schemas import RegisterDocument, WatchItem

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_REGISTER_PATH = REPO_ROOT / "data" / "action_watch_register.json"

ALLOWED_TRANSITIONS = {
    "OPEN": {"TRIGGERED", "EXPIRED", "QUARANTINED"},
    "TRIGGERED": {"RESOLVED", "EXPIRED"},
    "RESOLVED": set(),
    "EXPIRED": set(),
    "QUARANTINED": set(),
}


class ActionWatchRegister:
    """Single-writer manager for the Action & Watch Register."""

    def __init__(self, path: Path | str | None = None):
        self.path = Path(path) if path else DEFAULT_REGISTER_PATH
        self.doc: RegisterDocument = self._load_or_create()

    def _load_or_create(self) -> RegisterDocument:
        if self.path.exists():
            try:
                raw_text = self.path.read_text(encoding="utf-8")
                # Defend against BOM
                if raw_text.startswith("\ufeff"):
                    raw_text = raw_text.lstrip("\ufeff")
                data = json.loads(raw_text)
                return RegisterDocument(**data)
            except Exception:
                # If unparseable or corrupted, create fresh document
                return RegisterDocument(
                    schema_version="1.0",
                    updated_at=dt.datetime.now(dt.timezone.utc).isoformat(),
                    items=[],
                )
        return RegisterDocument(
            schema_version="1.0",
            updated_at=dt.datetime.now(dt.timezone.utc).isoformat(),
            items=[],
        )

    def save(self) -> None:
        """Atomically persist the register to disk using strict BOM-free UTF-8."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.doc.updated_at = dt.datetime.now(dt.timezone.utc).isoformat()
        serialized = self.doc.model_dump_json(indent=2)
        # Atomic write via temporary file
        temp_path = self.path.with_suffix(".tmp")
        temp_path.write_text(serialized, encoding="utf-8")
        temp_path.replace(self.path)

    def _sanitize_item(self, item: WatchItem) -> WatchItem:
        """Enforce prompt injection quarantine at the register boundary."""
        clean_action, mal_action = sanitize_malicious_instruction(item.action_or_condition)
        clean_reason, mal_reason = sanitize_malicious_instruction(item.reason_short)
        clean_topic, mal_topic = sanitize_malicious_instruction(item.instrument_or_topic)

        if mal_action or mal_reason or mal_topic:
            item.action_or_condition = clean_action
            item.reason_short = clean_reason
            item.instrument_or_topic = clean_topic
            item.status = "QUARANTINED"
        return item

    def upsert_item(self, item: WatchItem) -> WatchItem:
        """Idempotently add or update an item in the register, defending against prompt injections."""
        sanitized_item = self._sanitize_item(item)
        for idx, existing in enumerate(self.doc.items):
            if existing.item_id == sanitized_item.item_id:
                self.doc.items[idx] = sanitized_item
                self.save()
                return sanitized_item

        self.doc.items.append(sanitized_item)
        self.save()
        return sanitized_item

    def add_watch(
        self,
        item_id: str,
        instrument_or_topic: str,
        action_or_condition: str,
        reason_short: str,
        linked_claim_ids: Optional[List[str]] = None,
        evidence_refs: Optional[List[str]] = None,
        invalidation_metric: Optional[str] = None,
        target_threshold: Optional[float] = None,
    ) -> WatchItem:
        """Register a new qualitative macro watch condition."""
        item = WatchItem(
            item_id=item_id,
            item_class="WATCH",
            instrument_or_topic=instrument_or_topic,
            action_or_condition=action_or_condition,
            reason_short=reason_short,
            linked_claim_ids=linked_claim_ids or [],
            evidence_refs=evidence_refs or [],
            status="OPEN",
            created_at=dt.datetime.now(dt.timezone.utc).isoformat(),
            invalidation_metric=invalidation_metric,
            target_threshold=target_threshold,
        )
        return self.upsert_item(item)

    def add_action(
        self,
        item_id: str,
        instrument_or_topic: str,
        action_or_condition: str,
        reason_short: str,
        linked_claim_ids: Optional[List[str]] = None,
        evidence_refs: Optional[List[str]] = None,
    ) -> WatchItem:
        """Register a proposed qualitative rebalance action."""
        item = WatchItem(
            item_id=item_id,
            item_class="ACTION",
            instrument_or_topic=instrument_or_topic,
            action_or_condition=action_or_condition,
            reason_short=reason_short,
            linked_claim_ids=linked_claim_ids or [],
            evidence_refs=evidence_refs or [],
            status="OPEN",
            created_at=dt.datetime.now(dt.timezone.utc).isoformat(),
        )
        return self.upsert_item(item)

    def transition_status(self, item_id: str, new_status: str) -> WatchItem:
        """Transition the lifecycle status of an item according to the state machine."""
        for idx, item in enumerate(self.doc.items):
            if item.item_id == item_id:
                current_status = item.status
                allowed = ALLOWED_TRANSITIONS.get(current_status, set())
                if new_status not in allowed:
                    raise ValueError(
                        f"Invalid transition from '{current_status}' to '{new_status}'. "
                        f"Allowed transitions: {sorted(allowed) if allowed else 'None (terminal state)'}"
                    )

                item.status = new_status
                self.doc.items[idx] = item
                self.save()
                return item

        raise KeyError(f"Item not found in register: {item_id}")

    def get_item(self, item_id: str) -> Optional[WatchItem]:
        for item in self.doc.items:
            if item.item_id == item_id:
                return item
        return None

    def get_active_items(self) -> List[WatchItem]:
        """Return all items currently in OPEN or TRIGGERED state."""
        return [i for i in self.doc.items if i.status in ("OPEN", "TRIGGERED")]

    def to_dict(self) -> dict:
        return self.doc.model_dump()
