"""Hermes Weekly Telegram Digest Dispatcher (WF-07 Stages 4–6).

Extracts and dispatches the pre-computed executive weekly summary from
data/exports/snapshots/YYYY-MM-DD/report.md to the operator's private Telegram topic.

Governing Axioms:
1. Zero LLM Arithmetic: Strictly formats pre-computed numeric indicators,
   regime scalers, and staged limit tickets from report.md. Never adjusts or sizes.
2. Message Bound: Strictly guarantees message length < 4,000 characters (Telegram max: 4,096).
3. Sovereign Execution Gate: Reminds operator that Batch 1 tickets are staged
   exclusively for manual portal entry.
"""

from __future__ import annotations

import datetime as dt
import logging
import os
from pathlib import Path
import re
from typing import Any, Optional

import requests

from ipos.config.load import REPO_ROOT
from ipos.export.snapshot import EXPORTS_DIR

logger = logging.getLogger(__name__)

DEFAULT_TELEGRAM_API_URL = "https://api.telegram.org"


class TelegramError(Exception):
    """Base exception for Telegram export errors."""


class TelegramConfigError(TelegramError):
    """Raised when Telegram bot credentials or chat ID are missing."""


class TelegramDispatchError(TelegramError):
    """Raised when Telegram API rejects or fails to deliver the digest."""


def find_latest_report(
    as_of: dt.date | str | None = None,
    base_dir: Path | None = None,
) -> Path:
    """Locate the pre-computed report.md for a given week or the most recent snapshot."""
    root = base_dir or EXPORTS_DIR
    if as_of:
        key = as_of.isoformat() if isinstance(as_of, dt.date) else str(as_of)
        target = root / key / "report.md"
        if not target.exists():
            raise FileNotFoundError(f"No pre-computed report.md found for week {key} at {target}")
        return target

    # Search for latest directory matching YYYY-MM-DD
    if not root.exists():
        raise FileNotFoundError(f"Snapshots directory does not exist: {root}")

    candidates = []
    for d in root.iterdir():
        if d.is_dir() and re.match(r"^\d{4}-\d{2}-\d{2}$", d.name):
            cand_file = d / "report.md"
            if cand_file.exists():
                candidates.append((d.name, cand_file))

    if not candidates:
        raise FileNotFoundError(f"No snapshot reports found in {root}")

    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


def extract_digest_from_report(report_text: str, max_chars: int = 3900) -> str:
    """Extract Executive Stance, Regime Scaler, Contradictions, and Priority Batch 1 Tickets.
    
    Guarantees message size < max_chars (default 3900 < Telegram 4096 ceiling).
    Strictly preserves numeric values without modification.
    """
    # 1. As-of date
    date_match = re.search(r"#\s*IPOS Weekly Report\s*—\s*([0-9]{4}-[0-9]{2}-[0-9]{2})", report_text)
    as_of = date_match.group(1) if date_match else "Weekly Snapshot"

    # 2. Overall Macro Stance & Regime
    risk_budget = "N/A"
    confidence = "N/A"
    breadth = "N/A"
    regime = "N/A"
    risk_scaler = "1.0"

    rb_match = re.search(r"-\s*\*\*Risk budget:\*\*\s*(.+)", report_text)
    if rb_match:
        risk_budget = rb_match.group(1).strip()

    conf_match = re.search(r"-\s*\*\*Confidence:\*\*\s*(.+)", report_text)
    if conf_match:
        confidence = conf_match.group(1).strip()

    breadth_match = re.search(r"-\s*\*\*Breadth:\*\*\s*(.+)", report_text)
    if breadth_match:
        breadth = breadth_match.group(1).strip()

    regime_match = re.search(r"-\s*\*\*Regime:\*\*\s*([A-Za-z0-9_-]+)", report_text)
    if regime_match:
        regime = regime_match.group(1).strip()

    scaler_match = re.search(r"risk_scaler\s*([0-9.]+)", report_text)
    if scaler_match:
        risk_scaler = scaler_match.group(1).strip()

    # 3. Stance Vector Tilts
    tilts: list[str] = []
    stance_sec = re.search(r"### Stance vector\s*\n\| Dimension \| Tilt \|\s*\n\|---\|---\|\s*\n([\s\S]*?)(?=\n## |\Z)", report_text)
    if stance_sec:
        for line in stance_sec.group(1).strip().splitlines():
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 2:
                dim, val = parts[0], parts[1]
                tilts.append(f"{dim}: `{val}`")

    # 4. Contradictions
    contradictions: list[str] = []
    contra_sec = re.search(r"## Contradictions\s*\n([\s\S]*?)(?=\n## |\Z)", report_text)
    if contra_sec:
        c_lines = contra_sec.group(1).strip().splitlines()
        for cl in c_lines:
            cl_clean = cl.strip()
            if cl_clean.startswith("- **["):
                # Clean markdown formatting for telegram
                clean_contra = re.sub(r"\s+_\(.*?\)_", "", cl_clean)
                contradictions.append(clean_contra)
            elif "_None flagged this week._" in cl_clean:
                contradictions.append("• None flagged this week.")

    # 5. Staged Order Tickets Summary & Batch 1
    batch_1_summary = ""
    order_sum_match = re.search(r"## Staged Broker Order Tickets[^\n]*\n_([^_]+)_", report_text)
    if order_sum_match:
        batch_1_summary = order_sum_match.group(1).strip()

    batch_1_tickets: list[str] = []
    b1_sec = re.search(r"### Batch 1: Capital Release & Risk Reduction[\s\S]*?\| Priority \| Broker[\s\S]*?\n([\s\S]*?)(?=\n### |\n## |\Z)", report_text)
    if b1_sec:
        for line in b1_sec.group(1).strip().splitlines():
            cols = [c.strip() for c in line.split("|") if c.strip()]
            if len(cols) >= 10:
                prio = cols[0].replace("*", "")
                broker = cols[1].replace("`", "")
                action = cols[2].replace("*", "")
                instrument = cols[3].replace("`", "")
                name = cols[4].replace("*", "")
                shares = cols[5]
                limit = cols[7]
                est_val = cols[8]
                ticket_line = f"• *{prio}* `{broker}` *{action}* {shares}x {name} @ {limit} (~{est_val})"
                batch_1_tickets.append(ticket_line)

    # Assemble Telegram Markdown digest
    lines: list[str] = [
        f"🏛️ *IPOS Weekly Executive Digest — {as_of}*",
        "_Deterministic Output · Zero LLM Arithmetic_",
        "",
        "📊 *Executive Macro Stance & Regime*",
        f"• *Risk Budget:* {risk_budget}",
        f"• *Confidence:* {confidence}",
        f"• *Breadth:* {breadth}",
        f"• *Regime:* `{regime}` (Scaler: `{risk_scaler}`)",
    ]

    if tilts:
        lines.append(f"• *Key Tilts:* {', '.join(tilts)}")

    lines.append("")
    lines.append("⚡ *Active Contradictions*")
    if contradictions:
        for c in contradictions:
            lines.append(f"• {c.lstrip('- ').strip()}")
    else:
        lines.append("• None flagged this week.")

    lines.append("")
    lines.append("📋 *Priority Batch 1 Order Tickets (Capital Release)*")
    if batch_1_summary:
        lines.append(f"_{batch_1_summary}_")

    if batch_1_tickets:
        # Check budget for tickets
        remaining_chars = max_chars - sum(len(l) + 1 for l in lines) - 250
        included_tickets = []
        for t in batch_1_tickets:
            if remaining_chars - len(t) - 50 > 0:
                included_tickets.append(t)
                remaining_chars -= (len(t) + 1)
            else:
                break

        lines.extend(included_tickets)
        if len(included_tickets) < len(batch_1_tickets):
            lines.append(f"• _... and {len(batch_1_tickets) - len(included_tickets)} more tickets (see full report)_")
    else:
        lines.append("• No capital release actions staged this week.")

    lines.append("")
    lines.append("🔒 *Sovereign Execution Gate:* Manual portal entry only; zero auto-execution.")

    digest = "\n".join(lines)
    if len(digest) > max_chars:
        digest = digest[:max_chars - 30] + "\n\n_[Truncated to 4,000 chars]_"

    return digest


def send_telegram_message(
    text: str,
    bot_token: str | None = None,
    chat_id: str | None = None,
    thread_id: str | int | None = None,
    api_url: str = DEFAULT_TELEGRAM_API_URL,
    timeout: float = 10.0,
) -> dict[str, Any]:
    """Dispatch text message to Telegram Bot API."""
    token = bot_token or os.environ.get("TELEGRAM_BOT_TOKEN")
    cid = chat_id or os.environ.get("TELEGRAM_CHAT_ID")
    tid = thread_id or os.environ.get("TELEGRAM_THREAD_ID")

    if not token:
        raise TelegramConfigError("TELEGRAM_BOT_TOKEN is required to send Telegram digest.")
    if not cid:
        raise TelegramConfigError("TELEGRAM_CHAT_ID is required to send Telegram digest.")

    url = f"{api_url.rstrip('/')}/bot{token}/sendMessage"
    payload: dict[str, Any] = {
        "chat_id": cid,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }
    if tid:
        try:
            payload["message_thread_id"] = int(tid)
        except ValueError:
            payload["message_thread_id"] = str(tid)

    try:
        res = requests.post(url, json=payload, timeout=timeout)
    except requests.exceptions.RequestException as exc:
        raise TelegramDispatchError(f"Network error sending message to Telegram: {exc}") from exc

    if not res.ok:
        raise TelegramDispatchError(
            f"Telegram API error HTTP {res.status_code}: {res.text[:300]}"
        )

    try:
        data = res.json()
    except Exception as exc:
        raise TelegramDispatchError(f"Invalid JSON returned by Telegram API: {exc}") from exc

    if not data.get("ok"):
        raise TelegramDispatchError(f"Telegram API returned ok=false: {data}")

    return data


def dispatch_weekly_digest(
    as_of: dt.date | str | None = None,
    report_path: Path | None = None,
    dry_run: bool = False,
    bot_token: str | None = None,
    chat_id: str | None = None,
    thread_id: str | int | None = None,
    api_url: str = DEFAULT_TELEGRAM_API_URL,
) -> dict[str, Any]:
    """Full workflow: reads pre-computed report.md, formats digest, and dispatches."""
    rep_file = report_path or find_latest_report(as_of)
    if not rep_file.exists():
        raise FileNotFoundError(f"Report not found: {rep_file}")

    report_text = rep_file.read_text(encoding="utf-8")
    digest = extract_digest_from_report(report_text)

    result: dict[str, Any] = {
        "report_file": str(rep_file),
        "message_length": len(digest),
        "dry_run": dry_run,
    }

    if dry_run:
        result["status"] = "DRY_RUN"
        result["digest"] = digest
        return result

    resp = send_telegram_message(
        text=digest,
        bot_token=bot_token,
        chat_id=chat_id,
        thread_id=thread_id,
        api_url=api_url,
    )
    result["status"] = "SENT"
    result["telegram_response"] = resp
    return result
