"""Load and cross-validate the YAML config bundle into a typed ``Registry``.

Cross-checks that span multiple files (and therefore cannot live on a single
pydantic model):

* unique ``series_id``;
* every ``module_id`` used by an entry is defined in ``modules.yaml``;
* intra-module indicator weights sum to 1.0 and reference real series;
* risk-budget module weights sum to 1.0 and reference real modules;
* every ``playbook_ref`` resolves to a file in ``04_playbook/modules/``.

Any failure raises ``ConfigError`` — the run aborts before any network pull.
"""

from __future__ import annotations

import math
from pathlib import Path

import yaml

from ipos.config.models import (
    ModuleDef,
    Registry,
    RegistryEntry,
    ScoringDefaults,
    Weights,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = REPO_ROOT / "configs"
PLAYBOOK_MODULES_DIR = REPO_ROOT / "04_playbook" / "modules"

_SUM_TOL = 1e-6


class ConfigError(ValueError):
    """Raised when the config bundle is internally inconsistent."""


def _read_yaml(path: Path) -> dict:
    if not path.exists():
        raise ConfigError(f"missing config file: {path}")
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if data is None:
        raise ConfigError(f"empty config file: {path}")
    return data


def _known_playbook_modules() -> set[str]:
    if not PLAYBOOK_MODULES_DIR.exists():
        return set()
    return {p.stem for p in PLAYBOOK_MODULES_DIR.glob("*.md")}


def load_registry(config_dir: Path | None = None) -> Registry:
    cfg = Path(config_dir) if config_dir else CONFIG_DIR

    raw_registry = _read_yaml(cfg / "registry.yaml")
    raw_modules = _read_yaml(cfg / "modules.yaml")
    raw_weights = _read_yaml(cfg / "weights.yaml")
    raw_defaults = _read_yaml(cfg / "scoring_defaults.yaml")

    entries = [RegistryEntry(**row) for row in raw_registry.get("indicators", [])]
    modules = {
        m["module_id"]: ModuleDef(**m) for m in raw_modules.get("modules", [])
    }
    weights = Weights(**raw_weights)
    defaults = ScoringDefaults(**raw_defaults)

    _cross_validate(entries, modules, weights)

    return Registry(
        entries=entries, modules=modules, weights=weights, defaults=defaults
    )


def _cross_validate(
    entries: list[RegistryEntry],
    modules: dict[str, ModuleDef],
    weights: Weights,
) -> None:
    # --- unique series ids ---
    seen: set[str] = set()
    for e in entries:
        if e.series_id in seen:
            raise ConfigError(f"duplicate series_id: {e.series_id}")
        seen.add(e.series_id)

    # --- module references resolve ---
    for e in entries:
        if e.module_id not in modules:
            raise ConfigError(
                f"{e.series_id}: unknown module_id '{e.module_id}'"
            )

    # --- playbook_refs resolve to real module files ---
    known_modules = _known_playbook_modules()
    if known_modules:  # skip the check only if the playbook dir is absent
        refs: set[tuple[str, str]] = set()
        for e in entries:
            for ref in e.playbook_refs:
                refs.add((f"indicator {e.series_id}", ref))
        for mid, m in modules.items():
            for ref in m.playbook_refs:
                refs.add((f"module {mid}", ref))
        for owner, ref in sorted(refs):
            if ref not in known_modules:
                raise ConfigError(
                    f"{owner}: dangling playbook_ref '{ref}' "
                    f"(not a file in 04_playbook/modules/)"
                )

    active_ids = {e.series_id for e in entries if e.status == "active"}
    active_by_module: dict[str, set[str]] = {}
    for e in entries:
        if e.status == "active":
            active_by_module.setdefault(e.module_id, set()).add(e.series_id)

    # --- intra-module indicator weights ---
    for module_id, w in weights.module_indicator_weights.items():
        if module_id not in modules:
            raise ConfigError(f"weights: unknown module '{module_id}'")
        for sid in w:
            if sid not in active_ids:
                raise ConfigError(
                    f"weights[{module_id}]: references unknown/inactive series '{sid}'"
                )
        total = sum(w.values())
        if not math.isclose(total, 1.0, abs_tol=_SUM_TOL):
            raise ConfigError(
                f"weights[{module_id}]: indicator weights sum to {total}, expected 1.0"
            )
        # every active series in the module must have a weight
        missing = active_by_module.get(module_id, set()) - set(w)
        if missing:
            raise ConfigError(
                f"weights[{module_id}]: missing weights for active series {sorted(missing)}"
            )

    # every module with active indicators must have a weight block
    for module_id, members in active_by_module.items():
        if module_id not in weights.module_indicator_weights:
            raise ConfigError(
                f"weights: module '{module_id}' has active indicators but no weight block"
            )

    # --- risk-budget module weights ---
    rb = weights.risk_budget_weights
    for module_id in rb:
        if module_id not in modules:
            raise ConfigError(f"risk_budget_weights: unknown module '{module_id}'")
    total = sum(rb.values())
    if not math.isclose(total, 1.0, abs_tol=_SUM_TOL):
        raise ConfigError(
            f"risk_budget_weights sum to {total}, expected 1.0"
        )
    # risk budget must cover exactly the modules that have active indicators
    missing_rb = set(active_by_module) - set(rb)
    if missing_rb:
        raise ConfigError(
            f"risk_budget_weights: missing modules {sorted(missing_rb)}"
        )
