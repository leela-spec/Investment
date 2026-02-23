# Investment Process OS Blueprint for a Local-First Weekly Macro Stack on Windows

## Recommended Default Stack

**Default choice: DuckDB + Python + Streamlit + Windows Task Scheduler (with `schtasks` / PowerShell fallback).** This combination is “local-first,” resilient (single-file DB + local logs), analytics-friendly (window functions + fast scans), and extremely ergonomic for weekly time-series feature engineering and dashboarding on Windows. citeturn0search0turn4search17turn2search16turn0search13turn0search2turn3search16

**Database: DuckDB (over SQLite) for time-series analytics.**  
DuckDB is an in-process SQL database focused on analytical query processing (OLAP) and is designed to be easy to install and use without external dependencies. citeturn4search17turn0search0 For IPOS, you want fast aggregations, rolling windows, joins across many derived tables (observations → features → scores → regimes), and painless exports. DuckDB’s native Parquet read/write plus predicate/pushdown support makes it ideal for “warehouse-in-a-file” plus “export Parquet snapshots” patterns. citeturn2search1turn2search25  
SQLite can still work for smaller, transactional-ish workloads, but your core workload is analytical (rolling stats, wide joins, lots of aggregation), where DuckDB is generally a better default fit. citeturn4search17turn0search4

**ETL tooling (Python libs).**  
Use a standard Python data stack and keep connectors pluggable:
- `duckdb` (DB + SQL execution), `pyarrow` (Arrow/Parquet interchange), plus either `pandas` or `polars` for quick transforms (keep “heavy” transforms in SQL when possible). DuckDB’s Python client supports persistent files via `duckdb.connect("file.duckdb")` for local-first storage. citeturn0search0turn2search1  
- Validation: `pandera` (DataFrame schema checks) or Great Expectations (heavier).  
- Config/registry: `pydantic` for typed configs; YAML via `ruamel.yaml` or `PyYAML`.  
- Logging: standard `logging` + rotating file handler; optionally `rich` for readable CLI logs.

**Visualization tooling: Streamlit-first (with brief alternatives).**  
Streamlit is a strong default for personal dashboards: fast iteration, multipage navigation, and built-in chart primitives (plus Altair/Plotly integrations). Streamlit’s multipage apps can be structured using `st.Page` + `st.navigation`, which is clean for an IPOS with “Home / Modules / Indicator / Heatmap / Regime Map.” citeturn0search13turn0search25  
For charting, you can use `st.line_chart` (quick) or `st.altair_chart` (more control). citeturn2search2turn2search18 For exporting, `st.download_button` is the built-in mechanism (note: downloaded content lives in memory while the user is connected, so keep exports compact). citeturn2search3turn2search11  
Alternatives:
- **Dash**: more “app engineering” overhead; good if you need complex UI states or enterprise-grade components.
- **Grafana**: great observability/time-series UI, but usually implies a metrics backend (Prometheus/Influx/Timescale) and more ops than you want for a personal Windows local-first MVP.

**Scheduling on Windows: Task Scheduler (default) + CLI/PowerShell creation.**  
Windows Task Scheduler is built-in and trigger-based. It executes tasks based on triggers like time or events. citeturn3search16turn3search25  
Automation options:
- CLI: `schtasks.exe` create/run/query tasks. citeturn0search2turn3search28turn0search38  
- PowerShell: `ScheduledTasks` module (`New-ScheduledTaskTrigger`, `Register-ScheduledTask`) for more maintainable task definitions in scripts. citeturn3search0turn3search9  
Fallback for “always-on background service” needs: NSSM (optional), but for weekly cadence Task Scheduler is simpler and cleaner. citeturn3search20turn3search2  

---

## Architecture blueprint

### Components

**Registry**
- Single source of truth for indicator definitions (IDs, frequency, transformations, scoring method, directionality, module mapping, data source, revision behavior, and “Playbook module IDs” required for interpretation).

**ETL**
- Weekly ingestion pipeline that pulls data from connectors (API / local files), validates, and writes **raw observations** and **weekly canonical observations**.

**DB (DuckDB)**
- Stores raw/canonical observations, features, scores, regime aggregates, and contradictions log.

**Transforms**
- Feature engineering (deltas, rolling z-scores, percentiles, trend flags).
- Scoring (0–100), confidence, and module/regime aggregation.

**Dashboard (Streamlit)**
- Multipage app using `st.navigation` + `st.Page`. citeturn0search13turn0search25  
- Caching: `st.cache_data` for query results, `st.cache_resource` for DB connections. citeturn5search0turn5search12

**Exports**
- `snapshot.json` (required, compact), `snapshot.md` (optional), `report.md` (optional).
- Optional image export of key charts.

**AI prompt kit**
- Prompt templates + retrieval rules for Playbook modules.
- “Snapshot-first” prompt pattern (AI sees only snapshot + minimal rule excerpts).

### Data flow diagram

Textual flow (files + stages):

1. `configs/registry.yaml`  
2. `data/inbox/` (manual CSV/XLSX drops) + `data/connectors/` (API pulls)  
3. `etl/run_weekly.py`  
   - pulls raw data → validates → writes to DB tables  
   - computes canonical weekly series (aligned to `as_of`)  
4. `transforms/build_features.sql` / `transforms/build_scores.sql`  
5. `transforms/build_regimes.sql` + `transforms/build_contradictions.py`  
6. `exports/snapshots/YYYY-MM-DD/snapshot.json` (+ optional markdown)  
7. `app/streamlit_app.py` reads DB → visualizes → exports images/files  
8. Task Scheduler triggers (weekly): `etl/run_weekly.py` → then optionally runs “export snapshot” step

### Folder/repo structure

A minimal structure that scales from 60 to 120 indicators without refactor (registry-driven):

```
ipos/
  app/
    streamlit_app.py
    pages/
      home.py
      modules.py
      indicator_detail.py
      heatmap.py
      regime_map.py
  configs/
    registry.yaml
    modules.yaml
    weights.yaml
    scoring_defaults.yaml
  data/
    warehouse.duckdb
    inbox/              # manual drops (CSV/XLSX)
    staging/            # intermediate extracts (Parquet)
    exports/
      snapshots/
      charts/
  etl/
    run_weekly.py
    connectors/
      fred.py
      ecb.py
      manual_csv.py
    validators.py
  transforms/
    sql/
      canonical_weekly.sql
      features.sql
      scores.sql
      regimes.sql
    python/
      contradictions.py
      confidence.py
  playbook/
    modules/
      liquidity.md
      sentiment.md
      fundamentals.md
      rates.md
      credit.md
      fx.md
      commodities.md
    indicators/
      T10Y2Y.md
      AAII.md
      PUT_CALL.md
  prompts/
    system.md
    weekly_checkup.md
    suitability.md
    contradiction_deepdive.md
  logs/
    etl.log
    app.log
  tests/
    test_integrity.py
    test_scoring.py
    test_regression_snapshots.py
```

---

## Data model

### Core timestamp conventions

**Weekly cadence canonical key:**  
- `as_of_date` is the **week-end date** (recommend: Friday date of the week for market time-series; macro releases use “latest available up to week-end”).  
- Store `ingested_at` as UTC timestamp; store `source_timestamp`/`release_date` when known (macro series).  
- Temporal functions like `date_trunc` and `date_part` are used for alignment/grouping. citeturn2search16turn2search0  

### Schemas

Below are schemas designed to prevent duplicates, support incremental updates, and keep revision-aware history.

**Series metadata**
```sql
CREATE TABLE IF NOT EXISTS dim_series (
  series_id         VARCHAR PRIMARY KEY,
  name              VARCHAR NOT NULL,
  asset_class       VARCHAR NOT NULL, -- Equity/Rates/Credit/FX/Commodities
  region            VARCHAR,
  frequency         VARCHAR NOT NULL, -- 'D', 'W', 'M'
  unit              VARCHAR,
  source_type       VARCHAR NOT NULL, -- api/manual_csv/manual_xlsx
  source_locator    VARCHAR,          -- URL, API key name, filename pattern
  higher_is_better  BOOLEAN NOT NULL,
  scoring_method    VARCHAR NOT NULL, -- percentile|zscore|band
  module_id         VARCHAR NOT NULL,
  enabled           BOOLEAN NOT NULL DEFAULT TRUE,
  created_at        TIMESTAMP NOT NULL DEFAULT now()
);
```

**Observations (raw / revision-aware)**
```sql
CREATE TABLE IF NOT EXISTS fact_observation (
  series_id      VARCHAR NOT NULL,
  obs_date       DATE    NOT NULL,    -- observation date as published
  value          DOUBLE  NOT NULL,
  vintage_id     VARCHAR NOT NULL,    -- e.g., '2026-02-13T18:00Z' or provider version
  ingested_at    TIMESTAMP NOT NULL,
  source_hash    VARCHAR,             -- dedupe guard for identical content
  PRIMARY KEY (series_id, obs_date, vintage_id)
);
```

**Weekly canonical observations (what scoring uses)**
```sql
CREATE TABLE IF NOT EXISTS fact_weekly (
  series_id      VARCHAR NOT NULL,
  as_of_date     DATE    NOT NULL,    -- canonical week key
  value          DOUBLE  NOT NULL,
  vintage_id     VARCHAR NOT NULL,    -- points to the data vintage used
  ingested_at    TIMESTAMP NOT NULL,
  PRIMARY KEY (series_id, as_of_date)
);
```

**Features**
```sql
CREATE TABLE IF NOT EXISTS fact_feature (
  series_id      VARCHAR NOT NULL,
  as_of_date     DATE    NOT NULL,
  feature_id     VARCHAR NOT NULL,    -- e.g., 'delta_1w', 'delta_12w', 'z_52w'
  value          DOUBLE,
  PRIMARY KEY (series_id, as_of_date, feature_id)
);
```

**Scores**
```sql
CREATE TABLE IF NOT EXISTS fact_score (
  series_id        VARCHAR NOT NULL,
  as_of_date       DATE    NOT NULL,
  score_0_100      DOUBLE  NOT NULL,
  scoring_method   VARCHAR NOT NULL,
  lookback_weeks   INTEGER,
  params_json      VARCHAR,           -- frozen params for reproducibility
  confidence_0_100 DOUBLE  NOT NULL,
  PRIMARY KEY (series_id, as_of_date)
);
```

**Regime aggregates**
```sql
CREATE TABLE IF NOT EXISTS agg_regime (
  as_of_date        DATE   PRIMARY KEY,
  module_id         VARCHAR NOT NULL,
  module_score      DOUBLE NOT NULL,
  module_confidence DOUBLE NOT NULL,
  stance_dim        VARCHAR NOT NULL,  -- e.g. 'equity', 'duration', 'credit', 'usd', 'commodities'
  stance_value      DOUBLE NOT NULL,   -- normalized -1..+1 or 0..100, pick one and stay consistent
  risk_budget_0_100 DOUBLE NOT NULL,
  params_json       VARCHAR
);
```

**Contradictions log**
```sql
CREATE TABLE IF NOT EXISTS log_contradiction (
  as_of_date     DATE NOT NULL,
  contradiction_id VARCHAR NOT NULL,
  severity      VARCHAR NOT NULL,      -- low/med/high
  summary       VARCHAR NOT NULL,
  details_json  VARCHAR,
  created_at    TIMESTAMP NOT NULL DEFAULT now(),
  PRIMARY KEY (as_of_date, contradiction_id)
);
```

### Incremental update strategy (dedupe + upsert)

Prefer SQL-native **upserts**:
- `INSERT OR REPLACE` / `INSERT OR IGNORE` for simple cases. citeturn4search8  
- `MERGE INTO` for controlled incremental loads (especially when “match condition” is not a single PK or when using staged data). DuckDB documents `MERGE INTO` as an alternative to `INSERT ... ON CONFLICT`, useful for upserting without requiring a primary key constraint on the destination. citeturn4search1turn4search14turn4search18  

---

## ETL design

### Weekly cadence strategy

**Week-end snapshot policy**
- Define `as_of_date` = Friday date (or last business day) for the week.
- You run ETL on Saturday morning (local time) so Friday market closes and many weekly series are available.
- Canonical rule: for each series, the canonical weekly value is the last available observation at or before `as_of_date` (or a series-specific rule like “Wednesday close” for a weekly survey).

This stabilizes comparisons and makes charts consistent across asset classes.

### Connectors strategy (API + manual + fallbacks)

A connector interface per source type:
- `pull(series_id, start_date, end_date) -> DataFrame[obs_date, value, vintage_id]`
- Implement connectors:
  - **API connector**: rate-limited, retries, stores raw responses in `data/staging/`.
  - **Manual CSV/XLSX connector**: reads latest files in `data/inbox/`, validates schema, and moves to an “archive/” folder after successful load.
  - **Fallback chain**: API fails → use last cached extract → if missing, mark series stale.

### Validation rules (before DB write)

Apply validation at three layers:

**Schema**
- Required columns present; types parseable.
- Dates monotonic per series.

**Data quality**
- Missingness: percent missing in weekly window; hard fail if new gaps appear in required series (configurable).
- Duplicates:
  - raw: duplicates by `(series_id, obs_date, vintage_id)` blocked by PK.
  - weekly: duplicates by `(series_id, as_of_date)` blocked by PK; load via `MERGE` or `REPLACE`.
- Outliers:
  - robust z-score or MAD threshold on `delta_1w` flags (doesn’t necessarily fail; influences confidence).
- Revisions:
  - if a macro series revises historically, write new `vintage_id` rows to `fact_observation`, then recompute canonical weekly for affected windows.

### Logging/monitoring (local-first)

**What to log**
- Run header: `run_id`, `as_of_date`, git hash (if any), config hash.
- Per connector: start/end, rows pulled, failures, retry counts.
- Data validation summary (counts of missing/outliers/duplicates).
- DB load summary (inserted/updated row counts).
- Snapshot export summary (paths written, file sizes).

**Where**
- Rotating file logs in `logs/etl.log`.
- Optional: write `run_log` table in DuckDB for structured run history.

**Fail-safe behavior**
- If a critical series is missing: do not overwrite previous week’s snapshot; write a “FAILED snapshot attempt” record and keep last good snapshot.
- If non-critical series is missing: proceed, but reduce confidence for impacted modules and flag “stale data” contradictions.

---

## Scoring & regime logic

### Standard scoring functions (0–100)

All scores output **0–100**, where **higher is “more supportive of the module’s desired condition”** (you choose the desired condition in the module definition). Directionality is handled explicitly per indicator.

#### Percentile score

Use a rolling lookback window `L` (default recommendation: 156 weeks ≈ 3 years for weekly cadence; override per indicator).

For a value \(x_t\) and window \(W_t = \{x_{t-L+1}, \dots, x_t\}\), define percentile rank:
\[
p_t = \frac{ \#\{x \in W_t : x \le x_t\}}{|W_t|}\times 100
\]
Then the score:
- If higher-is-better: \(\text{score}_t = p_t\)
- If lower-is-better: \(\text{score}_t = 100 - p_t\)

**Trend-aware tweak (optional, recommended for “slow” indicators):** percentile on a transformed feature (e.g., YoY change) rather than the level.

#### Z-score score (rolling mean/std + outlier damping)

Compute rolling z-score:
\[
z_t = \frac{x_t - \mu_t}{\sigma_t}
\]
with rolling \(\mu_t, \sigma_t\) over `Lz` weeks (default: 104 weeks). Then **damp** extremes to avoid “one print dominates”:
\[
z'_t = \tanh\left(\frac{z_t}{k}\right)
\]
with `k` default 2.0. Map to 0–100:
\[
\text{score}_t = 50 + 50 \cdot \frac{z'_t + 1}{2}
\]
Then apply directionality inversion if needed.

#### Band/threshold scoring (interpretable rules)

Define bands \(b_0 < b_1 < \dots < b_n\) with predefined scores \(s_0, \dots, s_n\). Example for yield-curve spread (growth risk indicator):
- \(x < -0.5\%\) → 10  
- \([-0.5, 0)\) → 35  
- \([0, 0.5)\) → 60  
- \([0.5, 1.0)\) → 75  
- \(\ge 1.0\%\) → 90  

This is the “most explainable” scoring style and is ideal when your Playbook gives explicit thresholds.

### Directionality handling

Every indicator defines `higher_is_better` relative to its **module objective** (not the real-world “good/bad”). This avoids confusion like:
- “Higher VIX is bad for risk” → In a **Risk-On** module, `higher_is_better = False`
- “Higher put/call ratio indicates fear” → Could be `higher_is_better = True` in a **Contrarian Risk-On** module if your Playbook treats extremes as opportunity signals.

Store directionality in `dim_series` and record it in `fact_score.params_json` for full reproducibility.

### Confidence scoring (0–100)

Confidence should express: “how much should I trust this score this week?”

A practical composite:
1. **Data quality subscore (0–100)**  
   - freshness (days since last obs)  
   - missingness in last N weeks  
   - revision instability (how often past values changed recently)
2. **Signal stability subscore (0–100)**  
   - volatility of score (e.g., std of score changes last 8 weeks)  
   - outlier flags
3. **Coherence subscore (0–100)**  
   - agreement with neighboring indicators in same module

Then:
\[
\text{confidence} = 0.45\cdot Q + 0.35\cdot S + 0.20\cdot C
\]
Keep weights configurable per module.

### Contradictions detection

There are two classes:

**Module disagreement (macro-level)**
- Example: Equity Risk module says “risk-on” (score > 70) but Credit module says “stress” (score < 40).  
This is the classic “stocks up, credit warning” contradiction.

**Indicator conflict (within-module)**
- Two indicators in the same module with opposite extremes (e.g., “VIX low” and “put/call extremely high”)—flag as “mixed signal.”

**How to implement**
- Define contradiction rules as simple predicates in config (YAML) so you can tune without refactor:
  - `if EquityRisk.score >= 70 and Credit.score <= 40 -> severity=high`
  - `if RatesLiquidity.score <= 35 and EquityRisk.score >= 70 -> severity=med`

Store contradictions in `log_contradiction` with details (which inputs triggered it) for later investigation.

### Aggregation strategy: module weights, stance vector mapping, risk budget

**Module score**
\[
\text{module\_score}_t = \sum_{i \in module} w_i \cdot \text{score}_{i,t}
\]
with \(\sum w_i = 1\). Weights come from `configs/weights.yaml`.

**Stance vector**
For each stance dimension \(d\) (e.g., equity, duration, credit, USD, commodities), map module scores to \([-1, +1]\):
\[
\text{tilt}_t = \text{clip}\left(\frac{\text{module\_score}_t - 50}{50}, -1, +1\right)
\]
Then stance vector is a small dict:
```json
{"equity": 0.4, "duration": -0.2, "credit": 0.1, "usd": 0.3, "commodities": -0.1}
```

**Risk budget (0–100)**
Define risk budget as a weighted blend of “risk-on capacity” modules:
\[
\text{risk\_budget}_t = \sum_m W_m \cdot \text{module\_score}_{m,t}
\]
This replaces traffic lights with a single continuous “how much risk can I run?” scalar.

### Tuning approach without breaking comparability

Key rule: **freeze scoring method + directionality + lookback** for each indicator in registry, and version them.
- If you change bands/lookbacks/weights, bump `scoring_version` or `playbook_version` and store in `params_json`.
- Keep historical comparability by either:
  - recomputing full history under the new version, or
  - storing both versions and switching which one the dashboard uses.

DuckDB’s analytical workflow + SQL transforms make recompute feasible for 60–120 indicators over multi-year weekly history.

---

## Visualization plan

Streamlit multipage is a good fit: define pages with `st.Page` and navigation with `st.navigation`. citeturn0search13turn0search25

### Home

**Goal:** one-screen weekly situation awareness.

**Visuals/widgets**
- “As of” selector (latest vs historical week)  
- Overall Risk Budget gauge (0–100)  
- Confidence gauge (0–100)  
- Stance vector table + small bar chart  
- Top movers list (largest score changes)  
- Contradictions panel (click to drill down)

**Required queries/fields**
- `agg_regime` for selected `as_of_date`: risk_budget, module scores, stance values
- `log_contradiction` for `as_of_date`
- Derived “top movers”: compare `fact_score` vs previous week

**UX**
- One-click “Export snapshot.json”
- One-click “Export report.md”
- Buttons to jump to Modules / Heatmap / Regime Map

### Modules

**Goal:** show module internals and time evolution.

**Visuals/widgets**
- Module selector
- Time series line: module score over time (`st.line_chart` or Altair). citeturn2search2  
- Mini heatmap: indicators in module vs last 12 weeks scores
- Table: indicators sorted by score, confidence, and 12-week delta

**Queries/fields**
- `fact_score` join `dim_series` for module membership
- `fact_feature` for deltas and trend flags

### Indicator Detail

**Goal:** “indicator development over time” (value + score + context) — a core requirement.

**Visuals/widgets**
- Indicator search (by name, tags)
- Dual-axis chart: value (left) + score (right)
- Heat strip: last 52 weeks score as color band
- Distribution view: percentile position in lookback (histogram/vline)
- “Playbook excerpt” panel (only that indicator’s rules)

**Queries/fields**
- `fact_weekly` (value history)
- `fact_score` (score history)
- `fact_feature` (deltas, rolling stats)

**UX**
- Export chart as PNG (Streamlit components or matplotlib save)
- Export “indicator card” markdown for weekly notes

### Heatmap

**Goal:** cross-asset score matrix over time.

**Visuals/widgets**
- Select: modules / asset classes / custom basket
- Heatmap: rows=indicators, cols=weeks, cell=color=score
- Optional sorting: by latest score, by volatility of score, by correlation to risk budget

**Queries/fields**
- `fact_score` filtered by the selected set and time window

### Regime Map with time trail

**Goal:** show regime evolution and “trail.”

**Design**
- Choose a 2D regime space:  
  - X axis = Growth (e.g., ISM/PMI composite, copper, cyclicals)  
  - Y axis = Inflation / financial conditions (e.g., inflation proxies, oil, real yields, credit spreads)  
- Compute regime coordinates weekly from module scores and plot as a moving point with trail (last 26 weeks).

**Queries/fields**
- `agg_regime` stance dims that map into 2D coordinates
- `fact_score` for underlying drivers (for tooltip drilldown)

### What “good” looks like

A good end-state UI lets you:
- start at Home, understand the week in <60 seconds,
- click into a contradiction and see exactly which indicators disagree,
- open any indicator and see value+score over time with a clear “why now” story,
- export a compact snapshot for AI reporting in one click.

Streamlit caching is essential because Streamlit reruns scripts; `st.cache_data` is recommended for cached data results and `st.cache_resource` for shared resources like DB connections. citeturn5search0turn5search12

---

## AI integration

### Snapshot export formats

**Required:** `snapshot.json`  
**Optional:** `snapshot.md` (human-readable) and `report.md` (weekly check-up output)

Design principle: **snapshot-first**: your AI prompt sees:
- the current snapshot (plus optionally last N snapshots), and
- only the relevant Playbook modules for interpretation.

### AI-safe payload (weekly runs)

Minimum fields per indicator (token-efficient, decision-useful):
- `value`, `delta_1w`, `delta_4w`, `delta_12w`
- `trend` (up/down/flat)
- `score` (0–100)
- `confidence` (0–100)

Plus macro-level:
- module aggregates (score/confidence/tilt)
- overall risk budget (0–100)
- stance vector (tilts)
- contradictions list (id/severity/summary)
- top movers (largest score changes)
- key drivers (top 3 contributors to risk budget change)

### Playbook retrieval strategy (token efficient)

**Do not feed the full seminar PDF each run.** Instead:
1. Convert seminar insights + your heuristics into **small Markdown modules** (one per concept/module + optional per-indicator notes).  
2. Each indicator in registry lists `playbook_refs: ["sentiment.md", "AAII.md"]`.  
3. The snapshot builder includes **only the referenced modules** for the indicators that moved, plus modules relevant to active contradictions.

This is deterministic, fast, and avoids embedding/RAG complexity for personal use.

The onvista seminar material itself is naturally modular (Liquidity / Sentiment / Fundamentals) and provides concrete indicator examples (AAII weekly survey, Fear & Greed index, Put/Call ratio, yield-curve inversion). citeturn0file0

### Prompt & token management best practices for long-running systems

This section is intentionally “systems-oriented”: you’re building a workflow that runs every week for years.

**Prompt architecture (layers)**  
Use a stable “prompt contract” that rarely changes:
- **System prompt:** rules (non-negotiables), output constraints, safety constraints, “don’t hallucinate,” response budgeting.
- **Role prompt:** “senior macro allocator / quant interpreter” persona with consistent evaluation criteria.
- **Task prompt:** what to do this run (weekly check-up, suitability, contradiction deep-dive).
- **Structured context blocks:** snapshot JSON, selected Playbook modules, and any user overrides.

OpenAI’s prompt engineering guidance emphasizes clarity, specificity, and providing examples/structure for consistent outputs. citeturn1search0turn1search24

**Chunking / iteration strategies**
- **Progressive summarization:**  
  - Step 1: summarize snapshot into “facts only” bullets  
  - Step 2: interpret with Playbook rules  
  - Step 3: output stance + action notes  
- **Selective retrieval:** only include:
  - indicators with big score change,
  - indicators at extremes (e.g., score < 20 or > 80),
  - indicators tied to contradictions.

For long-form content handling, chunking + iterative summarization is a standard pattern (preprocess → chunk → iterate → refine). citeturn0search11turn0search7turn1search6

**Safe output safeguards**
- **Output budgeting:** fixed max sections + hard cap on bullets per section.
- **Stop conditions:** if the model hits budget, stop at a logical boundary and output:
  - “Checkpoint Summary”
  - “Next Output Plan”
- **Checkpointing/resumable outputs:** include a `report_state` block in `report.md` so a second prompt can continue without rereading everything.

For long-running “agent harnesses,” Anthropic’s guidance emphasizes structuring context and separating initialization vs repeated-run prompts to keep workflows stable and efficient. citeturn1search5turn1search9

**Minimal yet robust output formats**
- Human: Markdown with strict sections and short lists.
- Machine: JSON with a strict schema and stable keys.

**Prompt compression (optional)**
If you ever need to compress rule excerpts or longer histories, prompt compression methods are an active area; research characterizes prompt compression as important for long-context inference at system level. citeturn0search15

### Downstream prompts (templates)

These templates assume you pass:
- `snapshot.json` (required)
- `playbook_excerpt.md` (optional; the selected modules only)

#### Weekly check-up prompt (short, factual)

```text
SYSTEM:
You are an investment process assistant. Be precise. Do not invent data. If a field is missing, say “missing”.

ROLE:
You are a senior macro allocator + risk manager. Your job is to summarize the week from the snapshot and highlight what changed.

TASK:
1) Summarize the snapshot factually.
2) List top movers and contradictions.
3) Identify key drivers of the risk budget.

CONTEXT: SNAPSHOT_JSON
<<<PASTE snapshot.json>>>

CONTEXT: PLAYBOOK_EXCERPT
<<<PASTE only relevant playbook modules>>>

OUTPUT FORMAT (Markdown):
## Facts (as_of: YYYY-MM-DD)
## Top movers
## Contradictions
## Risk budget and stance
## Data quality notes
```

#### Environment suitability prompt (actionable stance + rationale)

```text
SYSTEM:
Be action-oriented but do not produce trade instructions. Focus on risk posture and tilts.
Keep output under 500 words.

ROLE:
You are a portfolio risk overlay designer.

TASK:
Given the snapshot and playbook rules:
- Propose a stance vector (equity/duration/credit/usd/commodities) using -1..+1.
- Explain in 3–5 bullet points which modules/indicators drive it.
- Provide a confidence score and explain what would change your mind.

CONTEXT: SNAPSHOT_JSON
<<<snapshot.json>>>

CONTEXT: PLAYBOOK_EXCERPT
<<<selected rules only>>>

OUTPUT FORMAT (Markdown):
## Proposed stance
## Rationale
## Risks and invalidation triggers
## Confidence
```

#### Contradiction investigation prompt (hypotheses + resolution data)

```text
SYSTEM:
You are a contradiction investigator. Prefer hypotheses that can be tested with data.
Do not exceed 600 words.

ROLE:
You are a senior macro cross-asset strategist.

TASK:
For each contradiction in snapshot.json:
1) Restate the conflict in plain language.
2) Provide 2–3 hypotheses (why both can be true).
3) List the minimum additional data needed to resolve (specific indicators or releases).
4) Propose a near-term monitoring plan (next 1–4 weeks).

CONTEXT: SNAPSHOT_JSON
<<<snapshot.json>>>

CONTEXT: PLAYBOOK_EXCERPT
<<<rules relevant to the conflicting modules only>>>

OUTPUT FORMAT (Markdown):
## Contradiction: <id>
### What conflicts
### Hypotheses
### What resolves it (data/tests)
### Monitoring plan
```

---

## Implementation plan

### MVP milestones (scales 60 → 120 without refactor)

Milestones are registry-driven: adding indicators is adding rows to registry + (optional) playbook modules.

1. **Project scaffold + repo structure** (low)  
2. **Registry schema + loader (YAML → typed objects)** (med)  
3. **DuckDB warehouse init + tables** (med) citeturn0search0turn4search17  
4. **Manual CSV/XLSX ingestion connector** (med)  
5. **API connector skeleton + caching to staging** (med)  
6. **Canonical weekly alignment SQL** (med) citeturn2search16turn2search0  
7. **Feature generation (deltas/trends/z-scores/percentiles)** (high)  
8. **Scoring engine (percentile/zscore/band) + directionality** (high)  
9. **Module aggregation + stance vector + risk budget** (high)  
10. **Contradictions engine + logging table** (med)  
11. **Snapshot exporter (json + optional md)** (med)  
12. **Streamlit app pages + caching + exports** (high) citeturn0search13turn5search0turn2search3  
13. **Windows scheduling scripts (Task Scheduler creation)** (med) citeturn0search2turn3search0turn3search9  
14. **Test suite + regression baselines** (high)

### Recommended libraries and why

- `duckdb`: fast analytical SQL in-process; persistent local DB file. citeturn0search0turn4search17  
- `pyarrow`: Parquet/Arrow interchange; great for staging and exports; DuckDB supports efficient Parquet read/write. citeturn2search1  
- `streamlit`: multipage dashboards; caching; download/export widgets. citeturn0search13turn5search0turn2search3  
- `altair` or `plotly`: richer interactivity than basic charts (`st.altair_chart` is the standard integration point). citeturn2search18turn2search2  
- `pytest`: regression tests; snapshot diffs (very useful when score rules change).

### Testing strategy

**Data tests**
- Integrity: no duplicate `(series_id, as_of_date)` in weekly table.
- Freshness: each critical indicator updated within allowed lag.
- Range sanity: values within plausible bounds (config).

**Scoring tests**
- Monotonicity tests: if `higher_is_better=True`, increasing input should not decrease score (for percentile/band).
- Stability tests: small value changes should not cause massive score jumps (except near thresholds).

**Regression tests**
- Keep a “golden snapshot” set for a fixed historical week; if you change playbook/weights, either:
  - update golden snapshots intentionally with version bump, or
  - fail test to force explicit acknowledgment.

### Performance considerations

- Push heavy transforms into DuckDB SQL (rolling windows, joins). citeturn2search0turn2search16  
- Stage raw pulls as Parquet and let DuckDB scan with predicate/projection pushdown. citeturn2search1turn2search25  
- Streamlit: cache DB queries with `st.cache_data` and cache DB connection with `st.cache_resource`. citeturn5search0turn5search12  
- Keep `snapshot.json` compact and minified for AI calls; include only “last + deltas + score/confidence + module aggregates + contradictions.”

---

## Runnable mock MVP example

This example is intentionally **offline** (no network calls). It demonstrates registry entries, mock observations, feature/scoring, aggregation, and a sample `snapshot.json`.

### Example registry entries (YAML-like)

```yaml
- series_id: SPX
  name: "S&P 500 Index"
  asset_class: Equity
  frequency: W
  unit: index
  source_type: manual_csv
  higher_is_better: true
  scoring_method: percentile
  module_id: EquityRisk
  playbook_refs: [fundamentals.md, sentiment.md]

- series_id: VIX
  name: "CBOE VIX"
  asset_class: Equity
  frequency: W
  unit: index
  source_type: manual_csv
  higher_is_better: false
  scoring_method: percentile
  module_id: EquityRisk
  playbook_refs: [sentiment.md]

- series_id: US10Y
  name: "US 10Y Treasury Yield"
  asset_class: Rates
  frequency: W
  unit: pct
  source_type: manual_csv
  higher_is_better: false
  scoring_method: zscore
  module_id: RatesLiquidity
  playbook_refs: [liquidity.md, rates.md]

- series_id: T10Y2Y
  name: "US 10Y-2Y Yield Curve Spread"
  asset_class: Rates
  frequency: W
  unit: pct
  source_type: manual_csv
  higher_is_better: true
  scoring_method: band
  module_id: GrowthRisk
  playbook_refs: [fundamentals.md, rates.md]

- series_id: HY_OAS
  name: "US High Yield OAS"
  asset_class: Credit
  frequency: W
  unit: pct
  source_type: manual_csv
  higher_is_better: false
  scoring_method: percentile
  module_id: Credit
  playbook_refs: [credit.md]
```

### Mock observations (CSV-like)

(Only a few rows shown; in practice you’d keep 3+ years weekly history.)

```csv
series_id,obs_date,value
SPX,2026-01-30,4675.2369
SPX,2026-02-06,4754.9475
SPX,2026-02-13,4779.6226
VIX,2026-01-30,15.8943
VIX,2026-02-06,15.5238
VIX,2026-02-13,15.3292
US10Y,2026-01-30,4.4107
US10Y,2026-02-06,4.4763
US10Y,2026-02-13,4.5410
T10Y2Y,2026-01-30,-0.3345
T10Y2Y,2026-02-06,-0.1674
T10Y2Y,2026-02-13,-0.2132
HY_OAS,2026-01-30,3.7281
HY_OAS,2026-02-06,3.8954
HY_OAS,2026-02-13,3.9622
```

### Feature computation + scoring (minimal pseudocode)

```python
# For each series and as_of_date:
value = last_value(as_of_date)
delta_1w  = value - value_lag(1)
delta_4w  = value - value_lag(4)
delta_12w = value - value_lag(12)
trend = slope_sign(last_5_values)

if method == "percentile":
    score = pct_rank(value in lookback_window)
    if lower_is_better: score = 100 - score

elif method == "zscore":
    z = (value - rolling_mean) / rolling_std
    z = tanh(z/2)  # damp
    score = 50 + 25*z
    if lower_is_better: score = 100 - score

elif method == "band":
    score = band_map(value)

confidence = quality * stability * coherence  # simplified
```

### Sample `snapshot.json` (compact but readable)

In actual runs you should **minify** JSON for token efficiency; this is formatted for readability.

```json
{
  "schema_version": "1.0",
  "as_of": "2026-02-13",
  "overall": {
    "risk_budget": 53.7,
    "confidence": 77.3,
    "stance_vector": {
      "equity": 0.93,
      "duration": 0.7,
      "credit": -0.93
    }
  },
  "modules": [
    { "module": "EquityRisk", "score": 96.7, "confidence": 80.0, "tilt": 0.93 },
    { "module": "RatesLiquidity", "score": 12.4, "confidence": 80.2, "tilt": -0.75 },
    { "module": "GrowthRisk", "score": 35.0, "confidence": 0.0, "tilt": -0.3 },
    { "module": "Credit", "score": 3.3, "confidence": 71.6, "tilt": -0.93 }
  ],
  "contradictions": [
    {
      "id": "EQ_vs_Credit",
      "severity": "high",
      "summary": "Equity risk is risk-on while credit spreads signal stress."
    },
    {
      "id": "EQ_vs_Rates",
      "severity": "medium",
      "summary": "Equity risk is risk-on while rates/liquidity conditions look tight."
    }
  ],
  "top_movers": [
    { "id": "US10Y", "delta_score_1w": -5.6 },
    { "id": "SPX", "delta_score_1w": 2.2 },
    { "id": "HY_OAS", "delta_score_1w": -1.1 }
  ],
  "indicators": [
    {
      "id": "SPX",
      "module": "EquityRisk",
      "value": 4779.6226,
      "delta_1w": 24.6751,
      "delta_4w": 104.3857,
      "delta_12w": 239.4707,
      "trend": "up",
      "score": 96.7,
      "confidence": 88.0
    },
    {
      "id": "VIX",
      "module": "EquityRisk",
      "value": 15.3292,
      "delta_1w": -0.1946,
      "delta_4w": -0.5651,
      "delta_12w": -1.9831,
      "trend": "down",
      "score": 96.7,
      "confidence": 71.9
    },
    {
      "id": "US10Y",
      "module": "RatesLiquidity",
      "value": 4.541,
      "delta_1w": 0.0647,
      "delta_4w": 0.1324,
      "delta_12w": 0.258,
      "trend": "up",
      "score": 10.6,
      "confidence": 85.3
    },
    {
      "id": "T10Y2Y",
      "module": "GrowthRisk",
      "value": -0.2132,
      "delta_1w": -0.0458,
      "delta_4w": 0.1031,
      "delta_12w": -0.0502,
      "trend": "up",
      "score": 35.0,
      "confidence": 0.0
    },
    {
      "id": "HY_OAS",
      "module": "Credit",
      "value": 3.9622,
      "delta_1w": 0.0668,
      "delta_4w": 0.2882,
      "delta_12w": 0.732,
      "trend": "up",
      "score": 3.3,
      "confidence": 71.6
    }
  ]
}
```

### What charts would plot (axes + overlays)

**Indicator Detail (SPX example)**
- X-axis: `as_of_date` (weekly)
- Left Y-axis: `fact_weekly.value`
- Right Y-axis: `fact_score.score_0_100`
- Overlays:
  - markers on weeks where `log_contradiction` references the module
  - shaded bands for score thresholds (e.g., 20/50/80)

**Heatmap**
- Rows: `series_id`
- Columns: `as_of_date` (last 52 weeks)
- Cell color: `score_0_100`
- Tooltip: value + deltas + confidence

**Regime map (trail)**
- X = “growth coordinate” from `agg_regime` stance dims
- Y = “inflation/conditions coordinate”
- Point per week with line trail (last 26 weeks)

---

**Note on Playbook derivation from the seminar PDF:** the seminar’s structure naturally suggests modular rules (Liquidity, Sentiment, Fundamentals) and provides concrete indicator examples like AAII sentiment, Fear & Greed (0–100), Put/Call ratio, ISM thresholding, and yield curve inversion framing—ideal seeds for Playbook modules that you store once and reuse token-efficiently. fileciteturn0file0