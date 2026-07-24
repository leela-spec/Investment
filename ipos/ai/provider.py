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


def get_provider(config: AIConfig) -> Provider:
    if config.provider in ("none", None):
        return NoneProvider()
    if config.provider == "manual":
        return ManualProvider()
    raise NotImplementedError(
        f"provider '{config.provider}' is a live provider (needs an API key + "
        f"network egress) and is deferred. Use provider: none or manual, and "
        f"paste data/exports/snapshots/<week>/prompt_bundle.md into your "
        f"Claude/ChatGPT subscription for the $0 narration path."
    )
