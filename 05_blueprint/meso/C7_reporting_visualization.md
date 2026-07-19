# C7 — Reporting & Visualization (Meso Plan)

**Owns:** the weekly **static HTML report** (primary UI) and the optional on-demand explorer.
**Depends on:** C3, C4, C6 (reads DB read-only / Parquet marts).

## Options considered (2026 web-validated)

| Option | Verdict |
|--------|---------|
| **Static self-contained HTML (Plotly) per week** | ✅ **Chosen for Phase 2.** Server-less, archivable, diffable, e-mailable, opens by double-click; recognized 2026 pattern for batch cadence. Zero always-on processes = max resilience + simplicity. |
| Quarto dashboard | 🔶 Nice upgrade path (same batch pattern, prettier layout) — adopt later only if plain Plotly HTML feels limiting; adds a rendering toolchain dependency. |
| Streamlit multipage (Blueprint's choice) | 🔶 Demoted to **optional on-demand explorer (Phase 4)** — launched manually when drill-down is wanted; never load-bearing. Reads read-only (DuckDB single-writer). |
| Evidence.dev / Observable Framework / Dash / Panel | ❌ JS toolchains, company-viability risk (Evidence), or app-engineering overhead — wrong trade for a single user. Datapane is dead. |

## Decisions

1. **One file per week:** `data/exports/reports/YYYY-MM-DD/report.html`, self-contained (plotly.js inlined), plus stable copy at `reports/latest.html`. History accumulates — visual time travel for free.
2. **Page layout = Blueprint's five pages collapsed into one scrolling report** (simplest thing that shows everything):
   - **Header:** as_of, risk budget (0–100 bullet gauge), confidence, regime label + policy selectors, data-quality banner (stale/failed series).
   - **Stance vector:** horizontal tilt bars (−1…+1) per dim.
   - **Contradictions panel:** severity-sorted cards with triggering values (from `details_json`).
   - **Top movers & key drivers:** two compact tables.
   - **Module section:** per module — score line (52w), member-indicator table (score, confidence, Δ12w).
   - **Heatmap:** indicators × last 52 weeks, cell = score (the Blueprint heatmap, static).
   - **Regime map:** 2D (growth vs inflation/conditions coordinates from `agg_regime`) with 26-week trail.
   - **Indicator sparklines:** grid of value+score mini-charts; anchors linkable (`#HY_OAS`).
   - **Interpretation:** the C6 narration (when enabled) + link to `report.md`.
3. **Charts via one helper module** (`ipos/report/charts.py`) with a single visual language: score color scale fixed (0=red→50=grey→100=green shifted for color-blind safety), thresholds 20/50/80 shaded, consistent fonts; all figures from `fact_*`/`agg_*` queries — no computation in the report layer.
4. **Data access:** report job runs inside the weekly run (same process, after export) — single writer preserved; optional explorer reads `read_only=True`.
5. **"Good" test (from Blueprint):** week understandable in <60 s from the header; every contradiction inspectable to its inputs; every indicator has value+score history; snapshot/report exportable in one click (they *are* files already).

## Implementation steps

1. `ipos/report/queries.py` — the ~10 read queries (SQL, read-only).
2. `ipos/report/charts.py` — gauge, tilt bars, heatmap, regime trail, sparkline grid (Plotly express; ~200 lines total).
3. `ipos/report/html.py` — jinja2 shell, inline plotly, `latest.html` copy.
4. Golden-render test: fixture DB → HTML contains expected anchors/values (string asserts, no pixel testing).
5. Phase 4 (optional): `app/explorer.py` Streamlit thin client over the same `queries.py`.

## Definition of done
- Weekly run emits self-contained `report.html` rendering all sections from fixture data with zero network access; opens offline in a browser; `latest.html` updated.

**Effort:** M. **Recurring tokens:** 0.
