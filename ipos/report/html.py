"""Static, self-contained weekly HTML report (C7).

Renders every section from the snapshot + a short score history for the
heatmap, into one file with inline CSS. No network, no JS library — opens
offline by double-click. Written alongside the snapshot and copied to a stable
``data/exports/latest.html``.
"""

from __future__ import annotations

import datetime as dt
import html as _html
from pathlib import Path

import duckdb
from jinja2 import Environment

from ipos.export.snapshot import EXPORTS_DIR
from ipos.report.charts import (
    gauge_html,
    regime_map_svg,
    score_color,
    sparkline_svg,
    text_on,
    tilt_bar_html,
)

HEATMAP_WEEKS = 52
SPARK_WEEKS = 52
REGIME_TRAIL_WEEKS = 26


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
    """Ordered (growth, inflation) tilt points over the trail window.
    X = growth stance dim; Y = commodities stance dim (inflation proxy)."""
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
            trail.append((float(d["growth"]), float(d["commodities"])))
    return trail


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
.rm-quad { fill: var(--muted); font-size: 10px; opacity: .55; font-style: italic; }
.legend { display:flex; align-items:center; gap:6px; font-size:12px; color:var(--muted); margin-top:6px; }
.legend .sw { width:16px; height:12px; display:inline-block; border-radius:2px; }
.spark { vertical-align: middle; } .spark-na { color: var(--muted); }
.regime-wrap { display:flex; gap:20px; align-items:flex-start; flex-wrap:wrap; }
.rm-axis { stroke: var(--line); stroke-width: 1; }
.rm-lab { fill: var(--muted); font-size: 10px; }
.rm-now { fill: #b2182b; stroke: #fff; stroke-width: 1; }
.foot { color: var(--muted); font-size: 12px; margin-top: 28px; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#16171a; --fg:#e8e8e8; --muted:#9aa0a6; --line:#2c2e33; --card:#1e2024; }
  .gauge { background:#2a2c31; } .tilt { background:#2a2c31; }
}
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
{% if s.flags.degraded %}<div class="banner warn">⚠️ Degraded run — {{ s.data_quality.n_stale }} stale, {{ s.data_quality.n_missing }} missing series. Serving best-available data.</div>
{% else %}<div class="banner ok">✓ All {{ s.data_quality.n_indicators }} indicators fresh.</div>{% endif %}

<div class="kpis">
  <div class="kpi hero"><div class="label">Risk budget</div><div class="val">{{ "%.1f"|format(s.overall.risk_budget) }}<small> / 100</small></div>{{ gauge(s.overall.risk_budget)|safe }}
    <div class="sub">how much risk the process supports this week</div></div>
  <div class="kpi"><div class="label">Confidence</div><div class="val">{{ "%.1f"|format(s.overall.confidence) }}<small> / 100</small></div>{{ gauge(s.overall.confidence)|safe }}</div>
  <div class="kpi"><div class="label">Regime</div><div class="val">{{ s.regime.label or "n/a" }}</div>
    <div class="sub">{% if s.regime.confidence is not none %}conf {{ "%.0f"|format(s.regime.confidence) }} · risk ×{{ s.regime.risk_scaler }}{% endif %}</div></div>
</div>
{% if s.regime.policy_selectors %}<div class="sub">Policy — size <strong>{{ s.regime.policy_selectors.position_size }}</strong> · entry <strong>{{ s.regime.policy_selectors.entry_style }}</strong> · trail <strong>{{ s.regime.policy_selectors.trailing_stop }}</strong> · stop <strong>{{ s.regime.policy_selectors.initial_stop }}</strong></div>{% endif %}

<h2>Stance vector</h2>
<table><tbody>
{% for dim, val in stance %}<tr><td>{{ dim }}</td><td>{{ tilt(val)|safe }}</td><td class="num">{{ "%+.2f"|format(val) }}</td></tr>
{% endfor %}</tbody></table>

<h2>Regime map <span class="sub">(growth × inflation tilt, {{ trail_weeks }}-week trail)</span></h2>
<div class="regime-wrap">
{{ regime_svg|safe }}
<div class="sub" style="max-width:360px">The point is this week's macro tilt — horizontal = growth stance, vertical = inflation/commodities stance; the faded trail shows the path over the last {{ trail_weeks }} weeks. Regime label <strong>{{ s.regime.label or "n/a" }}</strong> governs the risk scaler.</div>
</div>

<h2>Contradictions</h2>
{% if s.contradictions %}<div class="cards">
{% for c in s.contradictions %}<div class="card {{ c.severity }}"><div class="sev">{{ c.severity }}</div>{{ c.summary }}
{% if c.details %}<div class="sub">{% for k, v in c.details.items() %}{{ k }}={{ v }}{% if not loop.last %} · {% endif %}{% endfor %}</div>{% endif %}</div>
{% endfor %}</div>{% else %}<div class="sub">None flagged this week.</div>{% endif %}

<h2>Events <span class="sub">(this / next week)</span></h2>
{% if s.events %}<table><thead><tr><th>Date</th><th>When</th><th>Event</th><th>Category</th></tr></thead><tbody>
{% for e in s.events %}<tr><td>{{ e.date }}{% if e.approximate %}~{% endif %}</td><td>{{ e.when.replace("_", " ") }}</td><td>{{ e.name }}</td><td>{{ e.category }}</td></tr>
{% endfor %}</tbody></table>{% else %}<div class="sub">No scheduled macro events in the window.</div>{% endif %}

<h2>Top movers <span class="sub">(Δscore vs prior week)</span></h2>
{% if s.top_movers %}<table><thead><tr><th>Indicator</th><th class="num">Δscore 1w</th></tr></thead><tbody>
{% for m in s.top_movers %}<tr><td>{{ m.id }}</td><td class="num">{{ "%+.1f"|format(m.delta_score_1w) }}</td></tr>
{% endfor %}</tbody></table>{% else %}<div class="sub">No prior week for comparison.</div>{% endif %}

<h2>Modules</h2>
<table><thead><tr><th>Module</th><th class="num">Score</th><th>52w</th><th>Tilt</th><th class="num">Confidence</th></tr></thead><tbody>
{% for m in modules %}<tr><td>{{ m.module }}</td>
  <td class="num"><span class="pill" style="background:{{ color(m.score) }};color:{{ txt(color(m.score)) }}">{{ "%.1f"|format(m.score) }}</span></td>
  <td>{{ module_spark.get(m.module, "")|safe }}</td>
  <td>{{ tilt(m.tilt)|safe }}</td><td class="num">{{ "%.1f"|format(m.confidence) }}</td></tr>
{% endfor %}</tbody></table>

<h2>Indicators</h2>
<table><thead><tr><th>ID</th><th>Module</th><th class="num">Value</th><th class="num">Δ1w</th><th>Trend</th><th class="num">Score</th><th>52w score</th><th class="num">Conf</th><th>Stale</th></tr></thead><tbody>
{% for i in indicators %}<tr id="{{ i.id }}"><td>{{ i.id }}</td><td>{{ i.module }}</td>
  <td class="num">{{ i.value }}</td><td class="num">{{ "%+.4g"|format(i.delta_1w) if i.delta_1w is not none else "—" }}</td>
  <td>{{ i.trend }}</td>
  <td class="num"><span class="pill" style="background:{{ color(i.score) }};color:{{ txt(color(i.score)) }}">{{ "%.1f"|format(i.score) }}</span></td>
  <td>{{ indicator_spark.get(i.id, "")|safe }}</td>
  <td class="num">{{ "%.0f"|format(i.confidence) }}</td><td>{{ "yes" if i.stale else "" }}</td></tr>
{% endfor %}</tbody></table>

<h2>Score heatmap <span class="sub">(last {{ weeks|length }} weeks)</span></h2>
<div class="hm"><table><tbody>
{% for sid in heat_series %}<tr><td class="rowlab">{{ sid }}</td>
{% for wk in weeks %}<td><div class="cell" title="{{ sid }} {{ wk }}: {{ heat[sid].get(wk) }}" style="background:{{ color(heat[sid].get(wk)) }}"></div></td>{% endfor %}
</tr>{% endfor %}
</tbody></table></div>
<div class="legend"><span>0 weak</span><span class="sw" style="background:{{ color(0) }}"></span><span class="sw" style="background:{{ color(25) }}"></span><span class="sw" style="background:{{ color(50) }}"></span><span class="sw" style="background:{{ color(75) }}"></span><span class="sw" style="background:{{ color(100) }}"></span><span>100 strong</span> · <span>colorblind-safe (RdBu)</span></div>

<h2>Interpretation</h2>
{% if s.interpretation %}<div>{{ s.interpretation|e|replace("\n", "<br>")|safe }}</div>
<div class="sub">Narrated by {{ s.interpretation_meta.provider }} · prompt v{{ s.interpretation_meta.prompt_version }}</div>
{% else %}<div class="sub">LLM narration disabled (provider: none). The report above is fully computed by code; enable a provider in configs/ai.yaml to append an interpretation.</div>{% endif %}

<div class="foot">IPOS — local-first weekly macro process. Deterministic artifact; re-runs are byte-identical for a fixed as_of.</div>
</div></body></html>
"""


def render_html(con: duckdb.DuckDBPyConnection, snapshot: dict, as_of: dt.date) -> str:
    weeks, heat = _score_history(con, as_of, HEATMAP_WEEKS)
    heat_series = sorted(heat.keys())

    # per-indicator score sparklines (ordered by week over the heatmap window)
    indicator_spark = {
        sid: sparkline_svg([heat[sid].get(wk) for wk in weeks])
        for sid in heat
    }
    # per-module 52-week score sparklines
    module_hist = _module_score_history(con, as_of, SPARK_WEEKS)
    module_spark = {mid: sparkline_svg(vals, color="#6a7fb5") for mid, vals in module_hist.items()}
    # regime 2D trail
    regime_svg = regime_map_svg(_regime_trail(con, as_of, REGIME_TRAIL_WEEKS))

    env = Environment(autoescape=False, keep_trailing_newline=True)
    tmpl = env.from_string(_TEMPLATE)
    return tmpl.render(
        css=_CSS,
        as_of=snapshot["as_of"],
        s=snapshot,
        stance=sorted(snapshot["overall"]["stance_vector"].items()),
        modules=sorted(snapshot["modules"], key=lambda m: m["module"]),
        indicators=snapshot["indicators"],
        weeks=weeks,
        heat=heat,
        heat_series=heat_series,
        indicator_spark=indicator_spark,
        module_spark=module_spark,
        regime_svg=regime_svg,
        trail_weeks=REGIME_TRAIL_WEEKS,
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
