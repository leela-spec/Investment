"""Deterministic ``report.md`` rendered from the snapshot alone (no LLM).

This is the resilience-rank-4 property: the weekly report is fully useful with
every AI option switched off. Phase 2 appends an LLM "Interpretation" section;
Phase 1 stops here.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

from jinja2 import Environment

from ipos.export.snapshot import EXPORTS_DIR

_TEMPLATE = """# IPOS Weekly Report — {{ as_of }}

_Scoring version {{ scoring_version }} · schema {{ schema_version }} · code computes, LLM narrates (narration disabled in Phase 1)._

## Overall
- **Risk budget:** {{ "%.1f"|format(overall.risk_budget) }} / 100
- **Confidence:** {{ "%.1f"|format(overall.confidence) }} / 100
- **Regime:** {{ regime.label or "n/a (Phase 2)" }}{% if flags.degraded %}
- ⚠️ **Degraded run:** {{ data_quality.n_stale }} stale, {{ data_quality.n_missing }} missing series{% endif %}

### Stance vector
| Dimension | Tilt |
|---|---|
{% for dim, val in stance_sorted %}| {{ dim }} | {{ "%+.2f"|format(val) }} |
{% endfor %}

## Modules
| Module | Score | Tilt | Confidence |
|---|---|---|---|
{% for m in modules_sorted %}| {{ m.module }} | {{ "%.1f"|format(m.score) }} | {{ "%+.2f"|format(m.tilt) }} | {{ "%.1f"|format(m.confidence) }} |
{% endfor %}

## Top movers (Δscore vs prior week)
{% if top_movers %}| Indicator | Δscore 1w |
|---|---|
{% for mv in top_movers %}| {{ mv.id }} | {{ "%+.1f"|format(mv.delta_score_1w) }} |
{% endfor %}{% else %}_No prior week available for comparison._
{% endif %}

## Contradictions
{% if contradictions %}{% for c in contradictions %}- **[{{ c.severity }}]** {{ c.summary }}
{% endfor %}{% else %}_None flagged (contradictions engine arrives in Phase 2)._
{% endif %}

## Indicators
| ID | Module | Value | Δ1w | Trend | Score | Conf | Stale |
|---|---|---|---|---|---|---|---|
{% for i in indicators %}| {{ i.id }} | {{ i.module }} | {{ i.value }} | {{ i.delta_1w if i.delta_1w is not none else "—" }} | {{ i.trend }} | {{ "%.1f"|format(i.score) }} | {{ "%.0f"|format(i.confidence) }} | {{ "yes" if i.stale else "" }} |
{% endfor %}

## Data quality
- Indicators: {{ data_quality.n_indicators }}
- Stale: {{ data_quality.n_stale }}{% if data_quality.stale_series %} ({{ data_quality.stale_series|join(", ") }}){% endif %}
- Missing: {{ data_quality.n_missing }}{% if data_quality.missing_series %} ({{ data_quality.missing_series|join(", ") }}){% endif %}
"""


def render_report(snapshot: dict) -> str:
    env = Environment(trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True)
    tmpl = env.from_string(_TEMPLATE)
    return tmpl.render(
        as_of=snapshot["as_of"],
        scoring_version=snapshot["scoring_version"],
        schema_version=snapshot["schema_version"],
        overall=snapshot["overall"],
        regime=snapshot.get("regime", {}),
        flags=snapshot["flags"],
        stance_sorted=sorted(snapshot["overall"]["stance_vector"].items()),
        modules_sorted=sorted(snapshot["modules"], key=lambda m: m["module"]),
        top_movers=snapshot["top_movers"],
        contradictions=snapshot["contradictions"],
        indicators=snapshot["indicators"],
        data_quality=snapshot["data_quality"],
    )


def write_report(snapshot: dict, as_of: dt.date, base_dir: Path | None = None) -> str:
    out_dir = (base_dir or EXPORTS_DIR) / as_of.isoformat()
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "report.md"
    path.write_text(render_report(snapshot), encoding="utf-8")
    return str(path)
