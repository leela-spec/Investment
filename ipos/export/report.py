"""Deterministic ``report.md`` rendered from the snapshot alone (no LLM).

This is the resilience-rank-4 property: the weekly report is fully useful with
every AI option switched off. Phase 2 appends an LLM "Interpretation" section;
Phase 1 stops here.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

from jinja2 import Environment

from ipos.aggregate.portfolio import portfolio_vs_stance
from ipos.export.snapshot import EXPORTS_DIR

# Whitespace-control note, kept in Python rather than a Jinja comment on purpose:
# the environment below sets ``trim_blocks``, which eats the first newline after a
# block tag. Any template line ENDING in ``{% endif %}`` therefore swallows the
# line that follows it -- which silently collapsed the Policy/Degraded bullets
# (fixed 2026-07-27) and then the Risk budget/Breadth bullets (2026-07-29). The
# fix is Jinja's per-tag override ``{% endif +%}``, NOT an extra ``{{ nl }}``:
# appending an expression tag stops ``{% endif %}`` from being newline-adjacent,
# so the literal newline survives too and you get a blank line instead.
# ``{{ nl }}`` remains correct for bullets that live entirely inside a conditional.
_TEMPLATE = """# IPOS Weekly Report — {{ as_of }}

_Scoring version {{ scoring_version }} · schema {{ schema_version }} · code computes, LLM narrates._
{% if flags.synthetic_data %}
> 🧪 **SYNTHETIC DEMO DATA** (`--seed-offline`) — does NOT reflect real markets; for illustration only.
{% endif %}

## Overall
- **Risk budget:** {{ "%.1f"|format(overall.risk_budget) }} / 100{% if regime.base_risk_budget is not none %} (base {{ "%.1f"|format(regime.base_risk_budget) }} × regime scaler {{ regime.risk_scaler }}){% endif +%}
- **Confidence:** {{ "%.1f"|format(overall.confidence) }} / 100
- **Breadth:** {% if breadth and breadth.pct_above_50 is not none %}{{ "%.0f"|format(breadth.pct_above_50) }}% of {{ breadth.n_scored }} indicators score above 50{% if breadth.pct_improving is not none %}; {{ "%.0f"|format(breadth.pct_improving) }}% improved this week{% endif %}{% else %}n/a{% endif +%}
- **Regime:** {{ regime.label or "n/a" }}{% if regime.confidence is not none %} (confidence {{ "%.0f"|format(regime.confidence) }}, risk_scaler {{ regime.risk_scaler }}){% endif %}{% if regime.policy_selectors %}{{ nl }}  - _Policy:_ size {{ regime.policy_selectors.position_size }} · entry {{ regime.policy_selectors.entry_style }} · trail {{ regime.policy_selectors.trailing_stop }} · stop {{ regime.policy_selectors.initial_stop }}{% endif %}{% if regime.features %}{{ nl }}  - _Classifier measurements:_ {% for k, v in regime.features|dictsort %}{{ k }} = {% if v is none %}—{% else %}{{ v }}{% endif %}{% if not loop.last %} · {% endif %}{% endfor %}{% endif %}{% if flags.degraded %}{{ nl }}- ⚠️ **Degraded run:** {{ data_quality.n_stale }} stale, {{ data_quality.n_missing }} missing series{% endif %}

{% if budget_attribution %}### What moved the risk budget
Change in the **base** budget (before the regime scaler) from {{ budget_attribution.prev_as_of }}: **{{ "%+.2f"|format(budget_attribution.delta) }}** points ({{ "%.1f"|format(budget_attribution.base_from) }} → {{ "%.1f"|format(budget_attribution.base_to) }}). Contributions are additive and sum to that change.

| Module | Contribution (score pts) |
|---|---|
{% for c in budget_attribution.contributions %}| {{ c.module }} | {{ "%+.2f"|format(c.contribution) }} |
{% endfor %}
{% endif %}
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

## Portfolio vs. Stance
{% if portfolio and portfolio.freshness and portfolio.freshness.stale %}> ⚠️ **Portfolio CSV is {{ portfolio.freshness.age_days }} days old** — this comparison may be out of date.
{% endif %}
{% if portfolio and portfolio.fx_warnings %}> ⚠️ **Currency conversion skipped** for {{ portfolio.fx_warnings|length }} position(s) — **excluded from every weight below**: {{ portfolio.fx_warnings|join(" · ") }}
{% endif %}
{% if portfolio_rows %}| Module | Your weight | Suggested tilt | Read |
|---|---|---|---|
{% for r in portfolio_rows %}| {{ r.module }} | {{ "%.1f"|format(r.weight_pct) }}% | {{ "%+.2f"|format(r.tilt) }} | {{ r.read }} |
{% endfor %}{% if portfolio.unmapped %}
_Unmapped in `configs/portfolio_mapping.yaml` (not counted toward any module's weight): {{ portfolio.unmapped|map(attribute='instrument')|join(", ") }}_
{% endif %}
_Total portfolio value: €{{ "%.0f"|format(portfolio.total_value_eur) }}_
{% else %}_Drop a portfolio CSV export in `data/inbox/` (`portfolio*.csv`) to compare your actual exposure against this week's stance vector._
{% endif %}

## Top movers (Δscore vs prior week)
{% if top_movers %}| Indicator | Δscore 1w |
|---|---|
{% for mv in top_movers %}| {{ mv.id }} | {{ "%+.1f"|format(mv.delta_score_1w) }} |
{% endfor %}{% else %}_No prior week available for comparison._
{% endif %}

## Contradictions
{% if contradictions %}{% for c in contradictions %}- **[{{ c.severity }}]** {{ c.summary }}{% if c.weeks_observed and c.weeks_observed > 1 %} _(fired {{ c.weeks_fired }} of the last {{ c.weeks_observed }} weeks)_{% endif %}{{ bullets(c) }}
{% endfor %}{% else %}_None flagged this week._
{% endif %}

## Events this / next week
{% if events %}| Date | When | Event | Category |
|---|---|---|---|
{% for e in events %}| {{ e.date }}{% if e.approximate %}~{% endif %} | {{ e.when.replace("_", " ") }} | {{ e.name }} | {{ e.category }} |
{% endfor %}{% else %}_No scheduled macro events in the window._
{% endif %}

## Indicators
Δ value = change in the indicator's own units (not comparable between indicators).
Δscore 1w/1m/1q/1y = change in the 0-100 score, which _is_ comparable.
Level %ile = where the raw level sits in its own trailing ~3-year distribution.
It is **not** direction-adjusted: for an inverted indicator (e.g. VIXCLS, HY_OAS)
a high percentile means a _low_ score. `hist` = weeks of history behind it.

| ID | Module | Value | Δ value 1w | 4w | 12w | Level %ile | z | hist | Trend | Score | Δscore 1w | 1m | 1q | 1y | Conf | Stale |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
{% for i in indicators %}| {{ i.id }} | {{ i.module }} | {{ i.value }} | {{ i.delta_1w if i.delta_1w is not none else "—" }} | {{ i.delta_4w if i.delta_4w is not none else "—" }} | {{ i.delta_12w if i.delta_12w is not none else "—" }} | {{ "%.0f"|format(i.pctile_156w) if i.pctile_156w is not none else "—" }} | {{ "%+.2f"|format(i.z_104w) if i.z_104w is not none else "—" }} | {{ i.history_weeks or "—" }} | {{ i.trend }} | {{ "%.1f"|format(i.score) }} | {{ sd(i, "1w") }} | {{ sd(i, "4w") }} | {{ sd(i, "12w") }} | {{ sd(i, "52w") }} | {{ "%.0f"|format(i.confidence) }} | {{ "yes" if i.stale else "" }} |
{% endfor %}

## Data quality
- Indicators: {{ data_quality.n_indicators }}
- Stale: {{ data_quality.n_stale }}{% if data_quality.stale_series %} ({{ data_quality.stale_series|join(", ") }}){% endif %}
- Missing: {{ data_quality.n_missing }}{% if data_quality.missing_series %} ({{ data_quality.missing_series|join(", ") }}){% endif %}
{% if playbook_selection %}- Playbook modules surfaced for narration: {{ playbook_selection|join(", ") }}
{% endif %}"""


def _score_delta(indicator: dict, horizon: str) -> str:
    """Format one score-horizon delta for the markdown table."""
    v = (indicator.get("score_deltas") or {}).get(horizon)
    return f"{v:+.1f}" if v is not None else "—"


def _detail_bullets(contradiction: dict) -> str:
    """Indented markdown bullets naming what triggered a contradiction —
    built in Python because Jinja's ``trim_blocks`` eats the newline after a
    block tag, which would collapse nested loop output onto one line.
    Underscore keys are machine-readable refs, not display."""
    items = [
        (k, v) for k, v in (contradiction.get("details") or {}).items()
        if not k.startswith("_")
    ]
    return "".join(f"\n  - {k} = {v}" for k, v in items)


def render_report(snapshot: dict) -> str:
    env = Environment(trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True)
    tmpl = env.from_string(_TEMPLATE)
    return tmpl.render(
        sd=_score_delta,
        bullets=_detail_bullets,
        nl="\n",
        as_of=snapshot["as_of"],
        scoring_version=snapshot["scoring_version"],
        schema_version=snapshot["schema_version"],
        overall=snapshot["overall"],
        regime=snapshot.get("regime", {}),
        flags=snapshot["flags"],
        stance_sorted=sorted(snapshot["overall"]["stance_vector"].items()),
        modules_sorted=sorted(snapshot["modules"], key=lambda m: m["module"]),
        portfolio_rows=portfolio_vs_stance(snapshot),
        portfolio=snapshot.get("portfolio"),
        top_movers=snapshot["top_movers"],
        contradictions=snapshot["contradictions"],
        events=snapshot.get("events", []),
        indicators=snapshot["indicators"],
        data_quality=snapshot["data_quality"],
        breadth=snapshot.get("breadth"),
        budget_attribution=snapshot.get("budget_attribution"),
        playbook_selection=snapshot.get("playbook_selection"),
    )


def write_report(snapshot: dict, as_of: dt.date, base_dir: Path | None = None) -> str:
    out_dir = (base_dir or EXPORTS_DIR) / as_of.isoformat()
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "report.md"
    path.write_text(render_report(snapshot), encoding="utf-8")
    return str(path)
