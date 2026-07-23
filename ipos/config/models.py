"""Typed config models for the IPOS registry and its companion configs.

The registry (``configs/registry.yaml``) is the single source of truth for
every indicator: where its data comes from, how it is scored, its
directionality, which module it belongs to, and its provenance back to the
frozen extraction layer (``03_extract/*.jsonl``). Adding an indicator is a
YAML edit — no code change (registry-driven principle, D2->D3).

Everything here is validated at load time; a bad config aborts the run
*before* any network pull (fail-fast).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

ScoringMethod = Literal["percentile", "zscore", "band"]
Frequency = Literal["D", "W", "M"]
SourceType = Literal["fred", "stooq", "manual_csv"]
Status = Literal["active", "deferred"]


class Source(BaseModel):
    """One link in an ordered fallback chain for an indicator."""

    model_config = ConfigDict(extra="forbid")

    type: SourceType
    locator: str


class BandStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    upper: float | None  # exclusive upper bound; null => +inf (top band)
    score: float = Field(ge=0, le=100)


class ScoringParams(BaseModel):
    """Scoring knobs; only the fields relevant to the method are used."""

    model_config = ConfigDict(extra="forbid")

    lookback_weeks: int = 156
    z_lookback_weeks: int = 104
    z_k: float = 2.0
    # For band scoring: ascending list of (upper_bound, score). The final
    # entry uses null upper_bound to mean "+inf" (the top band).
    bands: list[BandStep] | None = None

    @model_validator(mode="after")
    def _bands_sorted(self) -> "ScoringParams":
        if self.bands:
            uppers = [b.upper for b in self.bands if b.upper is not None]
            if uppers != sorted(uppers):
                raise ValueError("band 'upper' bounds must be ascending")
            if self.bands[-1].upper is not None:
                raise ValueError("final band must have upper: null (the +inf band)")
        return self


class RegistryEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    series_id: str
    name: str
    asset_class: str
    region: str | None = None
    frequency: Frequency = "W"
    unit: str | None = None
    sources: list[Source] = Field(min_length=1)
    higher_is_better: bool
    scoring_method: ScoringMethod
    scoring_params: ScoringParams = Field(default_factory=ScoringParams)
    module_id: str
    critical: bool = False
    playbook_refs: list[str] = Field(default_factory=list)
    extract_ref: str | None = None
    status: Status = "active"
    needs_verification: bool = False

    @model_validator(mode="after")
    def _band_requires_bands(self) -> "RegistryEntry":
        if self.scoring_method == "band" and not self.scoring_params.bands:
            raise ValueError(
                f"{self.series_id}: scoring_method 'band' requires scoring_params.bands"
            )
        return self


class ModuleDef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    module_id: str
    name: str
    # stance dimension this module tilts (equity/duration/credit/usd/commodities/...)
    stance_dim: str
    playbook_refs: list[str] = Field(default_factory=list)


class Weights(BaseModel):
    """Intra-module indicator weights and inter-module risk-budget weights."""

    model_config = ConfigDict(extra="forbid")

    # module_id -> {series_id: weight}; weights within a module sum to 1.0
    module_indicator_weights: dict[str, dict[str, float]] = Field(default_factory=dict)
    # module_id -> weight in the overall risk budget; sum to 1.0
    risk_budget_weights: dict[str, float] = Field(default_factory=dict)


class ConfidenceWeights(BaseModel):
    model_config = ConfigDict(extra="forbid")

    quality: float = 0.45
    stability: float = 0.35
    coherence: float = 0.20


class ScoringDefaults(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scoring_version: str = "1.0"
    percentile_lookback_weeks: int = 156
    zscore_lookback_weeks: int = 104
    zscore_k: float = 2.0
    trend_slope_weeks: int = 5
    confidence_weights: ConfidenceWeights = Field(default_factory=ConfidenceWeights)
    # a canonical weekly value older than this many days is flagged stale
    staleness_days: dict[str, int] = Field(
        default_factory=lambda: {"D": 10, "W": 14, "M": 45}
    )


class Registry(BaseModel):
    """The fully-loaded, cross-validated config bundle."""

    model_config = ConfigDict(extra="forbid")

    entries: list[RegistryEntry]
    modules: dict[str, ModuleDef]
    weights: Weights
    defaults: ScoringDefaults

    def active(self) -> list[RegistryEntry]:
        return [e for e in self.entries if e.status == "active"]

    def by_id(self, series_id: str) -> RegistryEntry:
        for e in self.entries:
            if e.series_id == series_id:
                return e
        raise KeyError(series_id)
