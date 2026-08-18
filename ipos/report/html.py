"""Static, self-contained weekly HTML report (C7).

Renders every section from the snapshot + a short score history for the
heatmap, into one file with inline CSS. No network, no JS library — opens
offline by double-click. Written alongside the snapshot and copied to a stable
``data/exports/latest.html``.
"""

from __future__ import annotations

import datetime as dt
import html as _html
import re
from pathlib import Path

import duckdb
from jinja2 import Environment

from ipos.aggregate.contradictions import module_members
from ipos.aggregate.portfolio import portfolio_vs_stance
from ipos.aggregate.regime import RISK_SCALER
from ipos.export.snapshot import EXPORTS_DIR
from ipos.report.charts import (
    QUADRANTS,
    budget_bridge_svg,
    contribution_bars_svg,
    gauge_html,
    horizon_strip_svg,
    member_strip_svg,
    pctile_strip_svg,
    regime_map_svg,
    regime_ribbon_svg,
    score_color,
    sparkline_svg,
    text_on,
    tilt_bar_html,
)
from ipos.report.glossary import load_glossary, tooltip

HEATMAP_WEEKS = 52
# Aggregate-layer history window (module scores, stance values, regime trail
# and ribbon). Separate from the score-history windows above because
# agg_module/agg_regime are only as deep as `ipos-replay` has rebuilt them,
# whereas fact_score carries the full history.
AGG_WEEKS = 26

# Display order for the regime classifier's measurements. `overlap_index` and
# `atr_change_rate` are the two the label is actually decided on
# (regime.py::_raw_label); the rest are confirming context. Anything not listed
# sorts alphabetically after these, so adding a feature needs no edit here.
_FEATURE_ORDER = (
    "overlap_index",
    "atr_change_rate",
    "efficiency_ratio",
    "range_overlap",
    "swing_structure",
    "n_swings",
    "retracement_ratio",
    "atr_source",
)


def _score_history(con: duckdb.DuckDBPyConnection, as_of: dt.date, weeks: int):
    start = as_of - dt.timedelta(weeks=weeks - 1)
    rows = con.execute(
        """
        SELECT s.series_id, s.as_of_date, s.score_0_100
        FROM fact_score s JOIN dim_series d USING (series_id)
        WHERE s.as_of_date BETWEEN ? AND ? AND d.enabled
        ORDER BY s.series_id, s.as_of_date
        """,
        [start, as_of],
    ).fetchall()
    week_set = sorted({r[1] for r in rows})
    by_series: dict[str, dict] = {}
    for sid, wk, score in rows:
        by_series.setdefault(sid, {})[wk] = score
    return week_set, by_series


def _module_score_history(con, as_of, weeks):
    start = as_of - dt.timedelta(weeks=weeks - 1)
    rows = con.execute(
        "SELECT module_id, as_of_date, module_score FROM agg_module "
        "WHERE as_of_date BETWEEN ? AND ? ORDER BY module_id, as_of_date",
        [start, as_of],
    ).fetchall()
    out: dict[str, list] = {}
    for mid, _wk, score in rows:
        out.setdefault(mid, []).append(score)
    return out


def _regime_trail(con, as_of, weeks):
    """Ordered ``(week, growth, inflation)`` points over the trail window.
    X = growth stance dim; Y = commodities stance dim (inflation proxy).
    The week is carried so the map can label month boundaries and the
    start/now ends of the path."""
    start = as_of - dt.timedelta(weeks=weeks - 1)
    rows = con.execute(
        "SELECT as_of_date, stance_dim, stance_value FROM agg_module "
        "WHERE as_of_date BETWEEN ? AND ? AND stance_dim IN ('growth','commodities') "
        "ORDER BY as_of_date",
        [start, as_of],
    ).fetchall()
    by_week: dict = {}
    for wk, dim, val in rows:
        by_week.setdefault(wk, {})[dim] = val
    trail = []
    for wk in sorted(by_week):
        d = by_week[wk]
        if "growth" in d and "commodities" in d:
            trail.append((wk, float(d["growth"]), float(d["commodities"])))
    return trail


def _regime_history(con, as_of, weeks):
    """Ordered ``(week, label, regime_confidence, risk_scaler)`` for the ribbon."""
    start = as_of - dt.timedelta(weeks=weeks - 1)
    return [
        (wk, label, conf, scaler)
        for wk, label, conf, scaler in con.execute(
            "SELECT as_of_date, regime_label, regime_confidence, risk_scaler "
            "FROM agg_regime WHERE as_of_date BETWEEN ? AND ? ORDER BY as_of_date",
            [start, as_of],
        ).fetchall()
    ]


def _headline_history(con, as_of, weeks):
    """Ordered risk-budget and confidence history over the window.

    The two headline KPIs had no history anywhere in the report even though
    ``agg_regime`` has stored both columns per week all along — the ribbon query
    above simply never selected them."""
    start = as_of - dt.timedelta(weeks=weeks - 1)
    rows = con.execute(
        "SELECT risk_budget_0_100, confidence_0_100 FROM agg_regime "
        "WHERE as_of_date BETWEEN ? AND ? ORDER BY as_of_date",
        [start, as_of],
    ).fetchall()
    return [r[0] for r in rows], [r[1] for r in rows]


def _breadth_history(con, as_of, weeks):
    """Ordered "% of scored indicators above 50" per week.

    Computed straight from ``fact_score``, which holds the full history, so this
    line is available at full depth regardless of how far ``ipos-replay`` has
    rebuilt the aggregate layer."""
    start = as_of - dt.timedelta(weeks=weeks - 1)
    return [
        float(pct) for _wk, pct in con.execute(
            """
            SELECT s.as_of_date,
                   100.0 * count_if(s.score_0_100 > 50) / nullif(count(*), 0)
            FROM fact_score s JOIN dim_series d USING (series_id)
            WHERE s.as_of_date BETWEEN ? AND ? AND d.enabled
            GROUP BY s.as_of_date ORDER BY s.as_of_date
            """,
            [start, as_of],
        ).fetchall() if pct is not None
    ]


def _stance_history(con, as_of, weeks):
    """stance_dim -> ordered list of stance values over the window."""
    start = as_of - dt.timedelta(weeks=weeks - 1)
    out: dict[str, list] = {}
    for dim, _wk, val in con.execute(
        "SELECT stance_dim, as_of_date, stance_value FROM agg_module "
        "WHERE as_of_date BETWEEN ? AND ? ORDER BY stance_dim, as_of_date",
        [start, as_of],
    ).fetchall():
        out.setdefault(dim, []).append(val)
    return out


_CSS = """
:root { --bg:#ffffff; --fg:#1a1a1a; --muted:#666; --line:#e2e2e2; --card:#f7f7f8; }
* { box-sizing: border-box; }
body { font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
  color: var(--fg); background: var(--bg); margin: 0; padding: 24px; line-height: 1.45; }
.wrap { max-width: 1080px; margin: 0 auto; }
h1 { font-size: 22px; margin: 0 0 2px; } h2 { font-size: 16px; margin: 28px 0 8px;
  border-bottom: 2px solid var(--line); padding-bottom: 4px; }
.sub { color: var(--muted); font-size: 13px; margin-bottom: 16px; }
.kpis { display: flex; gap: 16px; flex-wrap: wrap; margin: 14px 0 6px; }
.kpi { flex:1 1 220px; min-width: 200px; background: var(--card); border:1px solid var(--line);
  border-radius: 10px; padding: 12px 14px; }
.kpi.hero { flex: 2 1 300px; }
.kpi .label { font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; }
.kpi .val { font-size: 30px; font-weight: 700; line-height: 1.1; margin-top: 2px; }
.kpi.hero .val { font-size: 44px; }
.kpi .val small { font-size: 15px; font-weight: 500; color: var(--muted); }
.gauge { position: relative; height: 14px; background: #ececec; border-radius: 7px; margin-top: 10px; overflow: hidden; }
.gauge-fill { position:absolute; left:0; top:0; height:100%; border-radius:7px 0 0 7px; }
.gauge-marker { position:absolute; top:-2px; width:2px; height:18px; background:var(--fg); }
.gauge-tick { position:absolute; top:0; width:1px; height:100%; background:rgba(0,0,0,.18); }
.banner { padding: 8px 12px; border-radius: 6px; font-size: 13px; margin: 10px 0; }
.banner.warn { background:#fff4e5; border:1px solid #ffd8a8; }
.banner.ok { background:#eaf6ec; border:1px solid #b7e0c0; }
table { border-collapse: collapse; width: 100%; font-size: 13px; }
th, td { text-align: left; padding: 5px 8px; border-bottom: 1px solid var(--line); }
th { color: var(--muted); font-weight: 600; }
.num { text-align: right; font-variant-numeric: tabular-nums; }
.tilt { position: relative; height: 14px; background:#f0f0f0; border-radius:3px; width:200px; }
.tilt-center { position:absolute; left:50%; top:0; width:1px; height:100%; background:#999; }
.tilt-fill { position:absolute; top:0; height:100%; }
.cards { display:flex; flex-direction:column; gap:8px; }
.card { border-left: 4px solid #ccc; background: var(--card); padding: 8px 12px; border-radius: 4px; }
.card.high { border-color:#b2182b; } .card.med { border-color:#e08214; } .card.low { border-color:#999; }
.card .sev { font-size:11px; text-transform:uppercase; color:var(--muted); }
.pill { display:inline-block; padding:2px 8px; border-radius: 10px; font-size:12px; font-weight:600; }
.hm { overflow-x:auto; } .hm table { width:auto; } .hm td { padding:0; }
.hm .cell { width:16px; height:16px; transition: outline .05s; } .hm .rowlab { padding:2px 6px; font-size:12px; white-space:nowrap; }
.hm .cell:hover { outline: 2px solid var(--fg); outline-offset: -1px; position: relative; z-index: 2; }
.rm-quad { fill: var(--muted); font-size: 10.5px; opacity: .7; letter-spacing:.03em; }
.legend { display:flex; align-items:center; gap:6px; font-size:12px; color:var(--muted); margin-top:6px; flex-wrap:wrap; }
.legend .sw { width:16px; height:12px; display:inline-block; border-radius:2px; }
.spark { vertical-align: middle; } .spark-na { color: var(--muted); font-size:12px; }
.regime-wrap { display:flex; gap:20px; align-items:flex-start; flex-wrap:wrap; }
.rm-axis { stroke: var(--line); stroke-width: 1; }
.rm-lab { fill: var(--muted); font-size: 10px; }
.rm-now { fill: #b2182b; stroke: var(--bg); stroke-width: 2; }
/* regime trail: older half recedes, recent half leads and carries the arrow */
.rm-trail-old { stroke: var(--muted); stroke-width: 1.4; opacity: .5; }
.rm-trail-new { stroke: #2166ac; stroke-width: 2; }
.rm-arrowhead { fill: #b2182b; }
.rm-dot { fill: var(--muted); opacity: .55; }
.rm-dot-month { fill: #2166ac; opacity: .85; }
.rm-tick { fill: var(--muted); font-size: 9.5px; }
.rm-nowlab { fill: #b2182b; font-size: 10.5px; font-weight: 600; }
/* quadrant key panel — fills the space to the right of the map */
.quadkey { max-width: 330px; font-size: 12.5px; color: var(--muted); }
.quadkey .qk { margin-bottom: 9px; }
.quadkey .qk b { color: var(--fg); }
/* regime ribbon: ordinal one-hue ramp keyed to how much risk each regime allows */
:root { --rg-uncertain:#86b6ef; --rg-choppy:#5598e7; --rg-momentum:#2a78d6; --rg-trendy:#184f95; }
.ribbon { display:block; }
.ribbon-flip { stroke: var(--fg); stroke-width: 1.5; }
/* multi-horizon score-delta strip */
.hstrip { vertical-align: middle; }
.hs-base { stroke: var(--line); stroke-width: 1; }
.hs-up { fill: #2166ac; } .hs-down { fill: #b2182b; } .hs-flat { fill: var(--muted); }
.hs-na { fill: var(--muted); font-size: 9px; }
/* contradiction member strip */
.mstrip { display:block; margin: 6px 0 2px; }
.ms-axis { stroke: var(--line); stroke-width: 1; }
.ms-tick { stroke: var(--line); stroke-width: 1; }
.ms-ticklab { fill: var(--muted); font-size: 9px; }
.ms-span { stroke: #e08214; stroke-width: 2; }
.ms-spanlab { fill: #e08214; font-size: 9.5px; font-weight: 600; }
.ms-dot { stroke: var(--bg); stroke-width: 2; }
/* level-percentile strip: neutral ink on purpose — a level percentile is not
   direction-adjusted, so painting it on the risk ramp would assert a good/bad
   reading the number does not carry */
.pstrip { vertical-align: middle; }
.ps-track { fill: var(--track, #ececec); }
.ps-iqr { fill: var(--line); }
.ps-median { stroke: var(--muted); stroke-width: 1; }
.ps-dot { fill: var(--fg); stroke: var(--bg); stroke-width: 2; }
.pctval { font-size: 11px; color: var(--muted); font-variant-numeric: tabular-nums; }
/* base -> scaler -> headline budget bridge */
.bridge { display:block; margin: 4px 0 2px; }
.br-grid { stroke: var(--line); stroke-width: 1; }
.br-lab { fill: var(--muted); font-size: 10.5px; }
.br-strong { fill: var(--fg); font-weight: 600; }
.br-tick { fill: var(--muted); font-size: 9px; }
.br-cut { fill: #b2182b; opacity: .55; }
.br-add { fill: #2166ac; opacity: .55; }
/* per-module contribution bars, zero-anchored */
.cbars { display:block; margin: 4px 0 2px; }
.cb-zero { stroke: var(--muted); stroke-width: 1; }
.cb-lab { fill: var(--muted); font-size: 10.5px; }
.cb-tick { fill: var(--muted); font-size: 9px; }
.cb-up { fill: #2166ac; } .cb-down { fill: #b2182b; }
/* "what changed" hero panel */
.changed { display:flex; gap:10px; flex-wrap:wrap; margin: 8px 0 4px; }
.chg { flex:1 1 200px; min-width:180px; background:var(--card); border:1px solid var(--line);
  border-radius:8px; padding:9px 12px; }
.chg .k { font-size:11px; color:var(--muted); text-transform:uppercase; letter-spacing:.04em; }
.chg .v { font-size:17px; font-weight:600; margin-top:2px; }
.chg .n { font-size:12px; color:var(--muted); }
.badge { display:inline-block; padding:1px 7px; border-radius:9px; font-size:11px;
  font-weight:600; background:#b2182b; color:#fff; vertical-align:middle; }
.recur { font-size:11px; color:var(--muted); }
.hm .monlab { font-size: 9.5px; color: var(--muted); text-align: left; padding: 0 0 2px 0;
  white-space: nowrap; }
.hm .modlab { font-size: 10px; color: var(--muted); text-transform: uppercase;
  letter-spacing: .05em; padding: 6px 6px 2px; font-weight: 600; }
.foot { color: var(--muted); font-size: 12px; margin-top: 28px; }
.tt { position: relative; cursor: help; border-bottom: 1px dotted var(--muted); }
.tt .tt-pop { visibility: hidden; opacity: 0; position: absolute; z-index: 60;
  left: 0; top: 100%; margin-top: 6px; width: 260px; max-width: 70vw;
  background: var(--fg); color: var(--bg); font-size: 12px; font-weight: 400; line-height: 1.4;
  text-transform: none; letter-spacing: normal;
  padding: 8px 10px; border-radius: 6px; box-shadow: 0 4px 14px rgba(0,0,0,.3);
  transition: opacity .12s ease; pointer-events: none; }
.tt .tt-pop b { display: block; margin-bottom: 3px; }
.tt:hover .tt-pop, .tt:focus .tt-pop { visibility: visible; opacity: 1; }
/* Popovers in the right-hand columns open leftward. An absolutely-positioned
   popover still counts toward scrollWidth even while hidden, so left-anchoring
   every one of them made the whole page scroll sideways once the indicator table
   grew wide enough to push a tooltip past the viewport edge. */
th:nth-last-child(-n+4) .tt-pop, td:nth-last-child(-n+4) .tt-pop { left: auto; right: 0; }
h2 .tt { font-weight: 400; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#16171a; --fg:#e8e8e8; --muted:#9aa0a6; --line:#2c2e33; --card:#1e2024; --track:#2a2c31;
    /* the same one-hue ramp re-stepped for the dark surface (validated: every
       step clears the 2:1 floor against #16171a) — not an automatic flip */
    --rg-uncertain:#256abf; --rg-choppy:#5598e7; --rg-momentum:#86b6ef; --rg-trendy:#b7d3f6; }
}
/* viewer's explicit theme toggle wins over the OS media query, both directions */
:root[data-theme="dark"] { --bg:#16171a; --fg:#e8e8e8; --muted:#9aa0a6; --line:#2c2e33; --card:#1e2024; --track:#2a2c31;
  --rg-uncertain:#256abf; --rg-choppy:#5598e7; --rg-momentum:#86b6ef; --rg-trendy:#b7d3f6; }
:root[data-theme="light"] { --bg:#ffffff; --fg:#1a1a1a; --muted:#666; --line:#e2e2e2; --card:#f7f7f8; --track:#ececec;
  --rg-uncertain:#86b6ef; --rg-choppy:#5598e7; --rg-momentum:#2a78d6; --rg-trendy:#184f95; }
.gauge { background: var(--track, #ececec); } .tilt { background: var(--track, #f0f0f0); }
"""

_TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>IPOS Weekly — {{ as_of }}</title>
<style>{{ css }}</style></head>
<body><div class="wrap">
<h1>IPOS Weekly Report</h1>
<div class="sub">as of <strong>{{ as_of }}</strong> · scoring v{{ s.scoring_version }} · schema v{{ s.schema_version }} · code computes, LLM narrates</div>

{% if s.flags.synthetic_data %}<div class="banner warn">🧪 <strong>SYNTHETIC DEMO DATA</strong> — this report was generated with <code>--seed-offline</code> and does NOT reflect real markets. For illustration only.</div>
{% endif %}
{% if s.flags.degraded %}<div class="banner warn">⚠️ Degraded run — {{ s.data_quality.n_stale }} stale, {{ s.data_quality.n_missing }} missing series. Serving best-available data.
{% if s.data_quality.stale_series %}<div style="margin-top:3px">Stale: {% for sid in s.data_quality.stale_series %}<a href="#ind-{{ sid }}">{{ sid }}</a>{% if not loop.last %}, {% endif %}{% endfor %}</div>{% endif %}
{% if s.data_quality.missing_series %}<div style="margin-top:3px">Missing: {{ s.data_quality.missing_series|join(", ") }}</div>{% endif %}</div>
{% else %}<div class="banner ok">✓ All {{ s.data_quality.n_indicators }} indicators fresh.</div>{% endif %}

<div class="kpis">
  <div class="kpi hero"><div class="label">{{ concept_tt("risk_budget", "Risk budget")|safe }}</div><div class="val">{{ "%.1f"|format(s.overall.risk_budget) }}<small> / 100</small></div>{{ gauge(s.overall.risk_budget)|safe }}
    <div class="sub">how much risk the process supports this week{% if budget_spark %} · {{ agg_weeks }}w {{ budget_spark|safe }}{% endif %}</div></div>
  <div class="kpi"><div class="label">{{ concept_tt("confidence", "Confidence")|safe }}</div><div class="val">{{ "%.1f"|format(s.overall.confidence) }}<small> / 100</small></div>{{ gauge(s.overall.confidence)|safe }}
    <div class="sub">{% if conf_spark %}{{ agg_weeks }}w {{ conf_spark|safe }}{% endif %}</div></div>
  <div class="kpi"><div class="label">{{ concept_tt("regime", "Regime")|safe }}</div><div class="val">{{ regime_tt(s.regime.label)|safe }}</div>
    <div class="sub">{% if s.regime.confidence is not none %}conf {{ "%.0f"|format(s.regime.confidence) }} · risk ×{{ s.regime.risk_scaler }}{% endif %}</div></div>
</div>
{% if s.regime.policy_selectors %}<div class="sub">Policy — size <strong>{{ s.regime.policy_selectors.position_size }}</strong> · entry <strong>{{ s.regime.policy_selectors.entry_style }}</strong> · trail <strong>{{ s.regime.policy_selectors.trailing_stop }}</strong> · stop <strong>{{ s.regime.policy_selectors.initial_stop }}</strong></div>{% endif %}

<h2>{{ concept_tt("what_changed", "What changed this week")|safe }}</h2>
<div class="changed">
  <div class="chg"><div class="k">{{ concept_tt("risk_budget", "Risk budget")|safe }}</div>
    <div class="v">{% if s.budget_attribution %}{{ "%+.1f"|format(s.budget_attribution.delta) }} pts{% else %}—{% endif %}</div>
    <div class="n">{% if s.budget_attribution %}base {{ "%.1f"|format(s.budget_attribution.base_from) }} → {{ "%.1f"|format(s.budget_attribution.base_to) }}{% else %}no prior week in the aggregate layer{% endif %}</div></div>
  <div class="chg"><div class="k">{{ concept_tt("regime", "Regime")|safe }}</div>
    <div class="v">{% if regime_flip %}{{ regime_flip[0] }} → {{ regime_flip[1] }}{% else %}{{ s.regime.label or "—" }}{% endif %}</div>
    <div class="n">{% if regime_flip %}flipped this week{% elif regime_age %}unchanged for {{ regime_age }} week{{ "s" if regime_age != 1 }}{% else %}no prior week{% endif %}</div></div>
  <div class="chg"><div class="k">{{ concept_tt("breadth", "Breadth")|safe }}</div>
    <div class="v">{% if s.breadth.pct_above_50 is not none %}{{ "%.0f"|format(s.breadth.pct_above_50) }}%{% else %}—{% endif %}</div>
    <div class="n">{{ s.breadth.n_above_50 }} of {{ s.breadth.n_scored }} above 50{% if breadth_spark %} {{ breadth_spark|safe }}{% endif %}</div></div>
  <div class="chg"><div class="k">{{ concept_tt("contradictions", "Contradictions")|safe }}</div>
    <div class="v">{{ s.contradictions|length }}{% if s.flags.n_high_severity %} <span class="badge">{{ s.flags.n_high_severity }} high</span>{% endif %}</div>
    <div class="n">{% if new_contradictions %}new: {{ new_contradictions|join(", ") }}{% elif s.contradictions %}all carried over from last week{% else %}none flagged{% endif %}</div></div>
  <div class="chg"><div class="k">{{ concept_tt("top_movers", "Biggest mover")|safe }}</div>
    <div class="v">{% if s.top_movers %}{{ s.top_movers[0].id }} {{ "%+.1f"|format(s.top_movers[0].delta_score_1w) }}{% else %}—{% endif %}</div>
    <div class="n">{% for m in s.top_movers[1:4] %}{{ m.id }} {{ "%+.1f"|format(m.delta_score_1w) }}{% if not loop.last %} · {% endif %}{% endfor %}</div></div>
</div>
{% if s.budget_attribution %}
<h3 class="sub" style="margin:16px 0 4px">{{ concept_tt("budget_attribution", "Which modules moved the budget")|safe }}</h3>
{{ contribution_bars|safe }}
<div class="sub" style="margin:2px 0 0">Contributions to the {{ concept_tt("base_risk_budget", "base budget")|safe }} sum to {{ "%+.2f"|format(s.budget_attribution.delta) }} points ({{ s.budget_attribution.prev_as_of }} → {{ as_of }}). Blue lifted the budget, red cut it.</div>
{% endif %}

<h2>{{ concept_tt("stance_vector", "Stance vector")|safe }}</h2>
<table><thead><tr><th>Dimension</th><th>{{ concept_tt("tilt", "Tilt")|safe }}</th><th class="num">Now</th><th>{{ agg_weeks }}w path</th><th class="num">vs 1m</th></tr></thead><tbody>
{% for dim, val in stance %}<tr><td>{{ stance_tt(dim)|safe }}</td><td>{{ tilt(val)|safe }}</td><td class="num">{{ "%+.2f"|format(val) }}</td>
  <td>{{ stance_spark.get(dim, "")|safe }}</td>
  <td class="num">{% if stance_delta.get(dim) is not none %}{{ "%+.2f"|format(stance_delta[dim]) }}{% else %}—{% endif %}</td></tr>
{% endfor %}</tbody></table>

<h2>{{ concept_tt("regime_map", "Regime map")|safe }} <span class="sub">(growth × inflation tilt, {{ agg_weeks }}-week path)</span></h2>
<div class="regime-wrap">
{{ regime_svg|safe }}
<div class="quadkey">
{% for name, body in quadrants %}<div class="qk"><b>{{ quadrant_tt(name)|safe }}</b> — {{ body }}</div>
{% endfor %}
<div class="sub" style="margin:0">Horizontal = growth stance, vertical = inflation/commodities stance. Larger dots mark month starts; the red dot is this week. Regime <strong>{{ regime_tt(s.regime.label)|safe }}</strong> sets the {{ concept_tt("risk_scaler", "risk scaler")|safe }}.</div>
</div>
</div>

<h3 class="sub" style="margin:16px 0 4px">{{ concept_tt("regime_ribbon", "Regime timeline")|safe }}</h3>
{{ regime_ribbon|safe }}
<div class="legend">{% for label, scaler in regime_ramp %}<span class="sw" style="background:var(--rg-{{ label|lower }})"></span><span>{{ label }} <span style="opacity:.7">×{{ scaler }}</span></span>{% endfor %} · <span>darker = more risk allowed</span></div>

<h3 class="sub" style="margin:16px 0 4px">{{ concept_tt("why_this_regime", "Why this regime, and what it did to the budget")|safe }}</h3>
{% if budget_bridge %}{{ budget_bridge|safe }}
<div class="sub" style="margin:2px 0 6px">The {{ concept_tt("base_risk_budget", "base budget")|safe }} is the weighted blend of module scores; the {{ regime_tt(s.regime.label)|safe }} regime's {{ concept_tt("risk_scaler", "risk scaler")|safe }} then multiplies it into the headline number.</div>
{% endif %}
{% if regime_features %}<table><thead><tr><th>{{ concept_tt("regime_feature", "Classifier measurement")|safe }}</th><th class="num">Value</th></tr></thead><tbody>
{% for k, v in regime_features %}<tr><td>{{ feature_tt(k)|safe }}</td><td class="num">{% if v is none %}—{% else %}{{ v }}{% endif %}</td></tr>
{% endfor %}</tbody></table>
{% else %}<div class="sub">No classifier measurements stored for this week.</div>{% endif %}

<h2>{{ concept_tt("contradictions", "Contradictions")|safe }}</h2>
{% if s.contradictions %}<div class="cards">
{% for c in s.contradictions %}<div class="card {{ c.severity }}"><div class="sev">{{ c.severity }}{% if c.weeks_observed and c.weeks_observed > 1 %} · <span class="recur">{{ concept_tt("recurrence", "fired " ~ c.weeks_fired ~ " of last " ~ c.weeks_observed ~ " weeks")|safe }}</span>{% endif %}</div>{{ contradiction_tt(c.id, c.summary)|safe }}
{% set shown = visible_details(c.details) %}
{% if shown %}<div class="sub" style="margin:4px 0 0">{% for k, v in shown %}{{ k }}={{ v }}{% if not loop.last %} · {% endif %}{% endfor %}</div>{% endif %}
{% for mod in c.details.get("_modules", []) %}{% if members.get(mod) %}
<div class="sub" style="margin:6px 0 0">{{ module_tt(mod)|safe }} members on the shared {{ concept_tt("score", "score")|safe }} scale — the span is the {{ concept_tt("module_spread", "module spread")|safe }}:</div>
{{ member_strip(members[mod])|safe }}
<div class="sub" style="margin:0">{% for sid, sc in members[mod] %}<a href="#ind-{{ sid }}">{{ sid }}</a> {{ "%.0f"|format(sc) }}{% if not loop.last %} · {% endif %}{% endfor %}</div>
{% endif %}{% endfor %}
</div>
{% endfor %}</div>{% else %}<div class="sub">None flagged this week.</div>{% endif %}

<h2>{{ concept_tt("events", "Events")|safe }} <span class="sub">(this / next week)</span></h2>
{% if s.events %}<table><thead><tr><th>Date</th><th>When</th><th>Event</th><th>Category</th></tr></thead><tbody>
{% for e in s.events %}<tr><td>{{ e.date }}{% if e.approximate %}~{% endif %}</td><td>{{ e.when.replace("_", " ") }}</td><td>{{ e.name }}</td><td>{{ e.category }}</td></tr>
{% endfor %}</tbody></table>{% else %}<div class="sub">No scheduled macro events in the window.</div>{% endif %}

<h2>{{ concept_tt("top_movers", "Top movers")|safe }} <span class="sub">(biggest {{ concept_tt("delta_score", "Δscore")|safe }} vs prior week)</span></h2>
{% if s.top_movers %}<table><thead><tr><th>Indicator</th><th>Module</th><th class="num">{{ concept_tt("score", "Score")|safe }}</th><th>52w score</th><th>{{ concept_tt("score_horizons", "1w · 1m · 1q · 1y")|safe }}</th><th class="num">{{ concept_tt("delta_score", "Δscore 1w")|safe }}</th></tr></thead><tbody>
{% for m in s.top_movers %}{% set ind = ind_by_id.get(m.id) %}<tr><td>{{ indicator_tt(m.id)|safe }}</td>
  <td>{% if ind %}{{ module_tt(ind.module)|safe }}{% endif %}</td>
  <td class="num">{% if ind %}<span class="pill" style="background:{{ color(ind.score) }};color:{{ txt(color(ind.score)) }}">{{ "%.1f"|format(ind.score) }}</span>{% endif %}</td>
  <td>{{ indicator_spark.get(m.id, "")|safe }}</td>
  <td>{% if ind %}{{ hstrip(ind.score_deltas, m.id)|safe }}{% endif %}</td>
  <td class="num">{{ "%+.1f"|format(m.delta_score_1w) }}</td></tr>
{% endfor %}</tbody></table>{% else %}<div class="sub">No prior week for comparison.</div>{% endif %}

<h2>{{ concept_tt("modules_section", "Modules")|safe }}</h2>
<table><thead><tr><th>Module</th><th class="num">{{ concept_tt("score", "Score")|safe }}</th><th>{{ agg_weeks }}w</th><th>{{ concept_tt("tilt", "Tilt")|safe }}</th><th class="num">{{ concept_tt("confidence", "Confidence")|safe }}</th></tr></thead><tbody>
{% for m in modules %}<tr><td>{{ module_tt(m.module)|safe }}</td>
  <td class="num"><span class="pill" style="background:{{ color(m.score) }};color:{{ txt(color(m.score)) }}">{{ "%.1f"|format(m.score) }}</span></td>
  <td>{{ module_spark.get(m.module, "")|safe }}</td>
  <td>{{ tilt(m.tilt)|safe }}</td><td class="num">{{ "%.1f"|format(m.confidence) }}</td></tr>
{% endfor %}</tbody></table>

<h2>{{ concept_tt("portfolio_vs_stance", "Portfolio vs. Stance")|safe }}</h2>
{% if s.portfolio and s.portfolio.freshness and s.portfolio.freshness.stale %}<div class="banner warn">⚠️ Portfolio CSV is {{ s.portfolio.freshness.age_days }} days old — this comparison may be out of date.</div>{% endif %}
{% if s.portfolio and s.portfolio.fx_warnings %}<div class="banner warn">⚠️ Currency conversion skipped for {{ s.portfolio.fx_warnings|length }} position{{ "s" if s.portfolio.fx_warnings|length != 1 }} — these are <strong>excluded from every weight below</strong>: {% for wmsg in s.portfolio.fx_warnings %}{{ wmsg }}{% if not loop.last %} · {% endif %}{% endfor %}</div>{% endif %}
{% if portfolio_rows %}
<table><thead><tr><th>Module</th><th class="num">Your weight</th><th colspan="2">Suggested tilt</th><th>Read</th></tr></thead><tbody>
{% for r in portfolio_rows %}<tr><td>{{ module_tt(r.module)|safe }}</td>
  <td class="num">{{ "%.1f"|format(r.weight_pct) }}%</td>
  <td>{{ tilt(r.tilt)|safe }}</td><td class="num">{{ "%+.2f"|format(r.tilt) }}</td>
  <td>{{ r.read }}</td></tr>
{% endfor %}</tbody></table>
{% if s.portfolio.unmapped %}<div class="sub">Unmapped in <code>configs/portfolio_mapping.yaml</code> (not counted toward any module's weight): {% for u in s.portfolio.unmapped %}{{ u.instrument }} (€{{ "%.0f"|format(u.value_eur) }}){% if not loop.last %}, {% endif %}{% endfor %}</div>{% endif %}
<div class="sub">Total portfolio value: €{{ "%.0f"|format(s.portfolio.total_value_eur) }}</div>
{% else %}<div class="sub">Drop a portfolio CSV export in <code>data/inbox/</code> (<code>portfolio*.csv</code>) to compare your actual exposure against this week's stance vector.</div>{% endif %}

<h2>{{ concept_tt("indicators_section", "Indicators")|safe }}</h2>
<table><thead><tr><th>ID</th><th>Module</th><th class="num">Value</th><th class="num">{{ concept_tt("delta_value", "Δ value 1w / 4w / 12w")|safe }}</th><th>{{ concept_tt("level_pctile", "Level %ile")|safe }}</th><th>Trend</th><th class="num">{{ concept_tt("score", "Score")|safe }}</th><th>{{ concept_tt("score_horizons", "1w · 1m · 1q · 1y")|safe }}</th><th>52w score</th><th class="num">{{ concept_tt("confidence", "Conf")|safe }}</th><th>{{ concept_tt("stale", "Stale")|safe }}</th></tr></thead><tbody>
{% for i in indicators %}<tr id="ind-{{ i.id }}"><td>{{ indicator_tt(i.id)|safe }}</td><td>{{ module_tt(i.module)|safe }}</td>
  <td class="num">{{ i.value }}</td>
  <td class="num">{% for d in (i.delta_1w, i.delta_4w, i.delta_12w) %}{{ "%+.4g"|format(d) if d is not none else "—" }}{% if not loop.last %} / {% endif %}{% endfor %}</td>
  <td>{{ pstrip(i.pctile_156w, i.history_weeks, i.id)|safe }}{% if i.pctile_156w is not none %} <span class="pctval">{{ "%.0f"|format(i.pctile_156w) }}</span>{% endif %}</td>
  <td>{{ i.trend }}</td>
  <td class="num"><span class="pill" style="background:{{ color(i.score) }};color:{{ txt(color(i.score)) }}">{{ "%.1f"|format(i.score) }}</span></td>
  <td>{{ hstrip(i.score_deltas, i.id)|safe }}</td>
  <td>{{ indicator_spark.get(i.id, "")|safe }}</td>
  <td class="num">{{ "%.0f"|format(i.confidence) }}</td><td>{{ "yes" if i.stale else "" }}</td></tr>
{% endfor %}</tbody></table>

<h2>{{ concept_tt("score_heatmap", "Score heatmap")|safe }} <span class="sub">(last {{ weeks|length }} weeks, newest right)</span></h2>
<div class="hm"><table><tbody>
<tr><td></td>{% for wk in weeks %}<td class="monlab">{{ month_tick(wk, loop.index0) }}</td>{% endfor %}</tr>
{% for mod, sids in heat_groups %}<tr><td class="modlab" colspan="{{ weeks|length + 1 }}">{{ module_tt(mod)|safe }}</td></tr>
{% for sid in sids %}<tr><td class="rowlab">{{ indicator_tt(sid)|safe }}</td>
{% for wk in weeks %}<td><div class="cell" title="{{ sid }} {{ wk }}: {{ heat[sid].get(wk) }}" style="background:{{ color(heat[sid].get(wk)) }}"></div></td>{% endfor %}
</tr>{% endfor %}{% endfor %}
</tbody></table></div>
<div class="legend"><span>0 weak</span><span class="sw" style="background:{{ color(0) }}"></span><span class="sw" style="background:{{ color(25) }}"></span><span class="sw" style="background:{{ color(50) }}"></span><span class="sw" style="background:{{ color(75) }}"></span><span class="sw" style="background:{{ color(100) }}"></span><span>100 strong</span> · <span>colorblind-safe (RdBu)</span></div>

<h2>{{ concept_tt("interpretation", "Interpretation")|safe }}</h2>
{% if s.interpretation %}<div>{{ interpretation_html|safe }}</div>
<div class="sub">Narrated by {{ s.interpretation_meta.provider }} · prompt v{{ s.interpretation_meta.prompt_version }}</div>
{% else %}<div class="sub">LLM narration disabled (provider: none). The report above is fully computed by code; enable a provider in configs/ai.yaml to append an interpretation.</div>{% endif %}
{% if s.interpretation_meta and s.interpretation_meta.model %}<div class="sub">Model: <code>{{ s.interpretation_meta.model }}</code></div>{% endif %}

<div class="foot">IPOS — local-first weekly macro process. Deterministic artifact; re-runs are byte-identical for a fixed as_of.
{% if s.playbook_selection %}<div style="margin-top:4px">{{ concept_tt("playbook_selection", "Playbook modules surfaced")|safe }} for this week's narration: {% for ref in s.playbook_selection %}<code>{{ ref }}</code>{% if not loop.last %}, {% endif %}{% endfor %}</div>{% endif %}</div>
</div></body></html>
"""


_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")


def _inline(text: str) -> str:
    return _BOLD_RE.sub(r"<strong>\1</strong>", _html.escape(text))


def _render_interpretation(text: str) -> str:
    """Dependency-free renderer for the narration's markdown subset (## headers,
    **bold**, - bullets) per prompts/weekly_checkup.md's fixed output format."""
    out: list[str] = []
    in_list = False
    for raw in text.strip().splitlines():
        line = raw.strip()
        if not line:
            if in_list:
                out.append("</ul>")
                in_list = False
            continue
        if line.startswith("## "):
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<h3>{_inline(line[3:])}</h3>")
        elif line.startswith("- "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{_inline(line[2:])}</li>")
        else:
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<p>{_inline(line)}</p>")
    if in_list:
        out.append("</ul>")
    return "".join(out)


def render_html(con: duckdb.DuckDBPyConnection, snapshot: dict, as_of: dt.date) -> str:
    weeks, heat = _score_history(con, as_of, HEATMAP_WEEKS)
    heat_series = sorted(heat.keys())

    # per-indicator score sparklines (ordered by week over the heatmap window)
    indicator_spark = {
        sid: sparkline_svg([heat[sid].get(wk) for wk in weeks])
        for sid in heat
    }
    # per-module score sparklines over the aggregate-history window
    module_hist = _module_score_history(con, as_of, AGG_WEEKS)
    module_spark = {mid: sparkline_svg(vals, color="#6a7fb5") for mid, vals in module_hist.items()}
    # stance-dimension paths + change vs ~1 month ago (4 aggregate weeks back)
    stance_hist = _stance_history(con, as_of, AGG_WEEKS)
    stance_spark = {
        dim: sparkline_svg(vals, color="#6a7fb5") for dim, vals in stance_hist.items()
    }
    stance_delta = {
        dim: (vals[-1] - vals[-5]) if len(vals) >= 5 else None
        for dim, vals in stance_hist.items()
    }
    # regime 2D path + the label timeline beneath it
    regime_hist = _regime_history(con, as_of, AGG_WEEKS)
    regime_svg = regime_map_svg(_regime_trail(con, as_of, AGG_WEEKS))
    regime_ribbon = regime_ribbon_svg(regime_hist)

    # headline KPI history — stored per week all along, never selected until now
    budget_hist, conf_hist = _headline_history(con, as_of, AGG_WEEKS)
    budget_spark = sparkline_svg(budget_hist) if len(budget_hist) > 1 else ""
    conf_spark = sparkline_svg(conf_hist, color="#6a7fb5") if len(conf_hist) > 1 else ""
    breadth_hist = _breadth_history(con, as_of, HEATMAP_WEEKS)
    breadth_spark = sparkline_svg(breadth_hist, color="#6a7fb5") if len(breadth_hist) > 1 else ""

    # regime flip vs. prior week, and how long the current label has held. Both
    # read off the ribbon history rather than a new query.
    labels = [lab for _wk, lab, _c, _s in regime_hist]
    regime_flip = None
    regime_age = 0
    if len(labels) > 1:
        if labels[-1] != labels[-2]:
            regime_flip = (labels[-2] or "n/a", labels[-1] or "n/a")
        for lab in reversed(labels):
            if lab != labels[-1]:
                break
            regime_age += 1

    # which contradictions are new this week (the rest carried over)
    prev_ids = {
        r[0] for r in con.execute(
            "SELECT contradiction_id FROM log_contradiction WHERE as_of_date = ?",
            [as_of - dt.timedelta(weeks=1)],
        ).fetchall()
    }
    new_contradictions = [
        c["id"] for c in snapshot.get("contradictions", []) if c["id"] not in prev_ids
    ] if prev_ids else []

    attribution = snapshot.get("budget_attribution")
    contribution_bars = contribution_bars_svg(
        [(c["module"], c["contribution"]) for c in attribution["contributions"]]
    ) if attribution else ""
    budget_bridge = budget_bridge_svg(
        snapshot["regime"].get("base_risk_budget"),
        snapshot["regime"].get("risk_scaler"),
        snapshot["overall"].get("risk_budget"),
    )
    # Ordered by how much each measurement actually drives the label (see
    # regime.py::_raw_label), not alphabetically — this table exists to explain
    # the classification, so the deciding inputs belong at the top.
    feats = snapshot["regime"].get("features") or {}
    regime_features = sorted(
        feats.items(),
        key=lambda kv: (_FEATURE_ORDER.index(kv[0]) if kv[0] in _FEATURE_ORDER
                        else len(_FEATURE_ORDER), kv[0]),
    )

    # heatmap rows grouped by module (module_id -> its series, both sorted)
    module_of = dict(con.execute(
        "SELECT series_id, module_id FROM dim_series WHERE enabled"
    ).fetchall())
    grouped: dict[str, list[str]] = {}
    for sid in heat_series:
        grouped.setdefault(module_of.get(sid, "—"), []).append(sid)
    heat_groups = sorted((mod, sorted(sids)) for mod, sids in grouped.items())

    def month_tick(week, idx: int) -> str:
        """Label a heatmap column only at a month boundary, so the 52-column
        axis stays readable."""
        if idx == 0 or week.month != weeks[idx - 1].month:
            return week.strftime("%b")
        return ""

    interpretation_html = (
        _render_interpretation(snapshot["interpretation"])
        if snapshot.get("interpretation") else None
    )

    portfolio_rows = portfolio_vs_stance(snapshot)
    gloss = load_glossary()

    # regime legend, ordered by how much risk each regime allows
    regime_ramp = sorted(RISK_SCALER.items(), key=lambda kv: -kv[1])
    # quadrant key: the name (tooltip carries the full explanation) plus the
    # axis signs, which are the definition and need no prose
    quadrant_bodies = [
        (name, f"growth {'+' if qx > 0 else '−'} · inflation {'+' if qy > 0 else '−'}")
        for name, qx, qy in QUADRANTS
    ]
    # member scores per module, for the contradiction drill-down strips
    members = module_members(con, as_of)

    def concept_tt(key: str, label: str) -> str:
        return tooltip(label, gloss.get("concepts", {}).get(key))

    def stance_tt(dim: str) -> str:
        entry = gloss.get("stance_dimensions", {}).get(dim)
        label = (entry or {}).get("title") or dim
        return tooltip(label, entry)

    def module_tt(module_id: str) -> str:
        return tooltip(module_id, gloss.get("modules", {}).get(module_id), title=module_id)

    def indicator_tt(series_id: str) -> str:
        return tooltip(series_id, gloss.get("indicators", {}).get(series_id), title=series_id)

    def regime_tt(label: str | None) -> str:
        if not label:
            return "n/a"
        return tooltip(label, gloss.get("regime_labels", {}).get(label), title=label)

    def quadrant_tt(name: str) -> str:
        return tooltip(name, gloss.get("macro_quadrants", {}).get(name), title=name)

    def feature_tt(key: str) -> str:
        entry = gloss.get("regime_features", {}).get(key)
        return tooltip((entry or {}).get("title") or key, entry, title=key)

    def contradiction_tt(cid: str, summary: str) -> str:
        """Explain a contradiction by exact id, else by kind (any
        ``*_MIXED_SIGNAL`` / ``*_MISMATCH`` shares one entry), else fall back to
        the general concept — so a new per-module rule needs no glossary edit."""
        entry = gloss.get("contradictions_by_id", {}).get(cid)
        if entry is None:
            kinds = gloss.get("contradiction_kinds", {})
            if cid.endswith("_MIXED_SIGNAL"):
                entry = kinds.get("mixed_signal")
            elif cid.endswith("_MISMATCH"):
                entry = kinds.get("portfolio_mismatch")
        if entry is None:
            entry = gloss.get("concepts", {}).get("contradictions")
        return tooltip(summary, entry, title=(entry or {}).get("title") or cid)

    env = Environment(autoescape=False, keep_trailing_newline=True)
    tmpl = env.from_string(_TEMPLATE)
    return tmpl.render(
        css=_CSS,
        as_of=snapshot["as_of"],
        s=snapshot,
        interpretation_html=interpretation_html,
        concept_tt=concept_tt,
        stance_tt=stance_tt,
        module_tt=module_tt,
        indicator_tt=indicator_tt,
        regime_tt=regime_tt,
        quadrant_tt=quadrant_tt,
        feature_tt=feature_tt,
        contradiction_tt=contradiction_tt,
        budget_spark=budget_spark,
        conf_spark=conf_spark,
        breadth_spark=breadth_spark,
        regime_flip=regime_flip,
        regime_age=regime_age,
        new_contradictions=new_contradictions,
        contribution_bars=contribution_bars,
        budget_bridge=budget_bridge,
        regime_features=regime_features,
        pstrip=lambda p, hw, sid: pctile_strip_svg(p, history_weeks=hw or 0, label=sid),
        stance=sorted(snapshot["overall"]["stance_vector"].items()),
        modules=sorted(snapshot["modules"], key=lambda m: m["module"]),
        portfolio_rows=portfolio_rows,
        indicators=snapshot["indicators"],
        ind_by_id={i["id"]: i for i in snapshot["indicators"]},
        weeks=weeks,
        heat=heat,
        heat_series=heat_series,
        heat_groups=heat_groups,
        month_tick=month_tick,
        indicator_spark=indicator_spark,
        module_spark=module_spark,
        stance_spark=stance_spark,
        stance_delta=stance_delta,
        regime_svg=regime_svg,
        regime_ribbon=regime_ribbon,
        regime_ramp=regime_ramp,
        quadrants=quadrant_bodies,
        members=members,
        member_strip=member_strip_svg,
        # underscore keys are machine-readable refs (e.g. _modules), not display
        visible_details=lambda d: [
            (k, v) for k, v in (d or {}).items() if not k.startswith("_")
        ],
        hstrip=lambda deltas, label="": horizon_strip_svg(deltas or {}, label=label),
        agg_weeks=AGG_WEEKS,
        gauge=gauge_html,
        tilt=tilt_bar_html,
        color=score_color,
        txt=text_on,
        esc=_html.escape,
    )


def write_html(
    con: duckdb.DuckDBPyConnection, snapshot: dict, as_of: dt.date,
    base_dir: Path | None = None,
) -> dict:
    base = base_dir or EXPORTS_DIR
    out_dir = base / as_of.isoformat()
    out_dir.mkdir(parents=True, exist_ok=True)
    content = render_html(con, snapshot, as_of)
    report_html = out_dir / "report.html"
    report_html.write_text(content, encoding="utf-8")
    latest = base.parent / "latest.html"
    latest.parent.mkdir(parents=True, exist_ok=True)
    latest.write_text(content, encoding="utf-8")
    return {"report_html": str(report_html), "latest_html": str(latest)}
