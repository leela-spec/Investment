"""LLM provider interface + the $0 default (none/manual).

The system runs fully with ``provider: none``. ``manual`` also makes no API
call — it just signals that the human will paste ``prompt_bundle.md`` into a
Claude/ChatGPT subscription. Live providers (gemini/anthropic/ollama) are
Phase-2-live: they need a key and network egress (deferred), so they are not
implemented here — asking for one raises a clear, actionable error rather than
shipping untested, key-dependent code.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import yaml

from ipos.config.load import REPO_ROOT

AI_CONFIG = REPO_ROOT / "configs" / "ai.yaml"


@dataclass
class AIConfig:
    provider: str = "none"
    model: str | None = None
    prompt_version: str = "1.0"
    budgets: dict | None = None

    @property
    def budget(self) -> dict:
        return self.budgets or {"system": 600, "playbook": 3000, "snapshot": 4000, "output": 1800}


def load_ai_config(path: Path | None = None) -> AIConfig:
    p = path or AI_CONFIG
    if not p.exists():
        return AIConfig()
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    return AIConfig(
        provider=data.get("provider", "none"),
        model=data.get("model"),
        prompt_version=str(data.get("prompt_version", "1.0")),
        budgets=data.get("budgets"),
    )


class Provider(Protocol):
    def narrate(self, system: str, user: str) -> str | None: ...


class NoneProvider:
    """No narration. The deterministic report stands on its own."""

    name = "none"

    def narrate(self, system: str, user: str) -> str | None:
        return None


class ManualProvider:
    """No API call — the prompt bundle is written for one-click manual paste."""

    name = "manual"

    def narrate(self, system: str, user: str) -> str | None:
        return None


class AnthropicProvider:
    """Live narration via the Claude API (api.anthropic.com — allowlisted).

    Requires an operator-provided ``ANTHROPIC_API_KEY`` (this is a paid API, so
    it stays opt-in and off by default). Weekly cost is a few cents; structured,
    temperature-0, pinned model. If the call fails the caller keeps the
    deterministic report (fail-degraded)."""

    name = "anthropic"
    URL = "https://api.anthropic.com/v1/messages"

    def __init__(self, config: "AIConfig"):
        self.model = config.model or "claude-haiku-4-5-20251001"
        self.max_tokens = int((config.budget or {}).get("output", 1800))

    def narrate(self, system: str, user: str) -> str | None:
        import os

        import requests

        key = os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError("ANTHROPIC_API_KEY not set (provider: anthropic)")
        resp = requests.post(
            self.URL,
            headers={
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": self.model,
                "max_tokens": self.max_tokens,
                "temperature": 0,
                "system": system,
                "messages": [{"role": "user", "content": user}],
            },
            timeout=60,
        )
        resp.raise_for_status()
        blocks = resp.json().get("content", [])
        text = "".join(b.get("text", "") for b in blocks if b.get("type") == "text")
        return text.strip() or None


def get_provider(config: AIConfig) -> Provider:
    if config.provider in ("none", None):
        return NoneProvider()
    if config.provider == "manual":
        return ManualProvider()
    if config.provider == "anthropic":
        return AnthropicProvider(config)
    raise NotImplementedError(
        f"provider '{config.provider}' is not implemented. Use: none | manual "
        f"(write prompt_bundle.md for $0 subscription paste) | file (drop a "
        f"narration.md) | anthropic (operator ANTHROPIC_API_KEY). gemini/ollama "
        f"are deferred."
    )
