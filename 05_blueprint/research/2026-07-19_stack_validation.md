# Research Archive — Local-First Stack Validation (July 2026)

**Date:** 2026-07-19 · **Method:** web research agent (primary sources cited) · **Question:** is the Blueprint stack (DuckDB + Python + Streamlit + Task Scheduler + pandera + pytest) still 2026 best practice for a single-user weekly system on Windows? · **Feeds:** decisions A1–A6, A9–A10; meso plans C1, C7, C8.

## Verdict

Stack is sound. **Two changes adopted:** (1) static HTML report replaces always-on Streamlit as primary UI; (2) uv manages the toolchain. Everything else validated.

## Findings

1. **DuckDB — validated.** v1.5.x stable (1.5.3, 05/2026), storage format stable since 1.0, MIT, ~37M downloads/month; 2026 surveys (Kestra embedded-DB) recommend it as default for exactly this workload. chDB = ClickHouse-niche; SQLite lacks OLAP; Parquet+Polars-only loses SQL transforms + single-file warehouse. **Caveat adopted:** single-writer → weekly job is sole writer, report/dashboard opens read-only or reads Parquet marts.
2. **Dashboard — the one place to change the Blueprint.** Streamlit = always-on server, reruns script per interaction; for weekly batch, "**batch job emits static HTML**" is a recognized 2026 pattern (more resilient, archivable, diffable):
   - Quarto dashboards — static, no server, Python-native; best upgrade path.
   - Observable Framework — static data-app SSG, but JS toolchain.
   - Evidence.dev — DuckDB-native but 6-person seed-stage company = longevity risk.
   - **Datapane — dead** (unmaintained).
   - marimo — strong Streamlit alternative; can export static/WASM HTML.
   **Adopted:** self-contained Plotly HTML per week; Streamlit demoted to optional on-demand explorer.
3. **Orchestration — validated: plain script + Task Scheduler.** 2026 comparisons call Prefect/Dagster/Airflow overkill for single-machine weekly jobs. Best practice adopted: one idempotent entrypoint, structured file logging, non-zero exit codes, Task Scheduler with "run whether user is logged on" + "run ASAP after missed start" (laptop-off case).
4. **Validation — pandera validated** (v0.32.1, 06/2026; light, pandas+polars, schema-as-code fits pytest). Great Expectations = 100+ deps, rejected. Pointblank (posit-dev) = credible alternative with HTML reports — optional later.
5. **pandas vs polars — irrelevant at 60–120 weekly series.** SQL does the transforms; pandas at presentation edges (ecosystem/plotting friction lower).
6. **uv — strongly validated.** 2026 default Python toolchain (replaces pip/poetry/pyenv/venv), first-class Windows, ~75M downloads/month. Task Scheduler invokes `uv run …` — no venv-activation fragility; `uv.lock` = reproducibility.
7. **Projects to imitate:** OpenBB Platform (free, AGPL, local-first, provider-registry pattern) — validates our registry design; usable later as extra connector layer, not adopted wholesale.

Key URLs: github.com/duckdb/duckdb/releases · kestra.io/blogs/embedded-databases · quarto.org/docs/dashboards · github.com/observablehq/framework · docs.datapane.com · docs.marimo.io/guides/exporting/static_html · datastackx.com/insights/airflow-vs-prefect-vs-dagster · pypi.org/project/pandera · databricks.com/blog/polars-vs-pandas · docs.astral.sh/uv · github.com/OpenBB-finance/OpenBB
