"""Config loader tests: the real golden-20 loads, and each cross-check rejects
a specific class of broken config (C1 Definition of Done)."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml

from ipos.config.load import CONFIG_DIR, ConfigError, load_registry


def test_real_registry_loads():
    reg = load_registry()
    assert len(reg.active()) == 22
    assert len(reg.modules) == 8
    # every active indicator's module is defined
    for e in reg.active():
        assert e.module_id in reg.modules


def _clone_configs(tmp_path: Path) -> Path:
    dst = tmp_path / "configs"
    shutil.copytree(CONFIG_DIR, dst)
    return dst


def _edit_yaml(path: Path, mutate):
    data = yaml.safe_load(path.read_text())
    mutate(data)
    path.write_text(yaml.safe_dump(data))


def test_rejects_duplicate_series_id(tmp_path):
    cfg = _clone_configs(tmp_path)

    def dup(data):
        data["indicators"].append(dict(data["indicators"][0]))

    _edit_yaml(cfg / "registry.yaml", dup)
    with pytest.raises(ConfigError, match="duplicate series_id"):
        load_registry(cfg)


def test_rejects_unknown_module(tmp_path):
    cfg = _clone_configs(tmp_path)

    def bad(data):
        data["indicators"][0]["module_id"] = "NoSuchModule"

    _edit_yaml(cfg / "registry.yaml", bad)
    with pytest.raises(ConfigError, match="unknown module_id"):
        load_registry(cfg)


def test_rejects_weights_not_summing_to_one(tmp_path):
    cfg = _clone_configs(tmp_path)

    def bad(data):
        data["module_indicator_weights"]["GrowthRisk"]["T10Y2Y"] = 0.9

    _edit_yaml(cfg / "weights.yaml", bad)
    with pytest.raises(ConfigError, match="sum to"):
        load_registry(cfg)


def test_rejects_risk_budget_not_summing_to_one(tmp_path):
    cfg = _clone_configs(tmp_path)

    def bad(data):
        data["risk_budget_weights"]["EquityRisk"] = 0.9

    _edit_yaml(cfg / "weights.yaml", bad)
    with pytest.raises(ConfigError, match="risk_budget_weights sum"):
        load_registry(cfg)


def test_rejects_dangling_playbook_ref(tmp_path):
    cfg = _clone_configs(tmp_path)

    def bad(data):
        data["modules"][0]["playbook_refs"] = ["NOT_A_REAL_MODULE"]

    _edit_yaml(cfg / "modules.yaml", bad)
    with pytest.raises(ConfigError, match="dangling playbook_ref"):
        load_registry(cfg)


def test_rejects_band_without_bands(tmp_path):
    cfg = _clone_configs(tmp_path)

    def bad(data):
        # DGS10 is zscore; flip to band without providing bands
        for ind in data["indicators"]:
            if ind["series_id"] == "DGS10":
                ind["scoring_method"] = "band"

    _edit_yaml(cfg / "registry.yaml", bad)
    with pytest.raises(Exception, match="band"):
        load_registry(cfg)
