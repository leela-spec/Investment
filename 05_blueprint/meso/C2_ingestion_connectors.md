# C2 — Ingestion & Connectors (Meso Plan)

**Owns:** `ipos/etl/` — connector interface, per-source connectors, fallback chains, raw archiving, pre-DB validation.
**Depends on:** C1. **Feeds:** C3.

## Source strategy (2026-validated, all free)

| Category | Primary | Fallback | Notes |
|----------|---------|----------|-------|
| Rates / curve / financial conditions | **FRED** (DGS*, T10Y2Y, T10Y3M, NFCI, ANFCI) | ECB (euro rates) | Free key, ~120 req/min, rock-solid |
| Credit spreads (HY/IG OAS) | **FRED** (BAMLH0A0HYM2, BAMLC0A0CM) | NFCI credit subindex | ⚠️ FRED truncated ICE BofA history to rolling 3y (Apr 2026) → **backfill + archive immediately** |
| Volatility | FRED VIXCLS | Stooq ^VIX, CBOE CSV | |
| Equity indices / sector ETFs | **Stooq** (no key, CSV endpoint) | yfinance → Tiingo | yfinance = fragile (recurring rate-limit waves) ⇒ never primary, never sole |
| FX | FRED DTWEXBGS | ECB EXR (no key), Stooq | |
| Commodities | FRED (WTI) + Stooq futures | Alpha Vantage (25 req/day free — fine weekly) | |
| Put/Call | CBOE daily stats scrape | — (accumulate own history) | Old totalpc archive is gone |
| Sentiment surveys | AAII headline scrape, NAAIM page, CNN F&G JSON endpoint | — | All unofficial → isolated, optional, accumulate locally |
| Macro cycle (ISM, UMich, CLI) | FRED (UMich), **DBnomics** (ISM), OECD API (CLI) | ISM press-release scrape | ISM subindices stay `deferred` |
| Rejected | investing.com/investpy (dead, Cloudflare), pandas-datareader (unmaintained), Quandl free (sunset) | | |

## Decisions

1. **Connector protocol** (Blueprint, sharpened): `pull(entry: RegistryEntry, start, end) -> DataFrame[obs_date, value, vintage_id]`. One module per source type: `fred.py`, `stooq.py`, `yfinance_.py`, `tiingo.py`, `ecb.py`, `dbnomics_.py`, `scrape_cboe.py`, `scrape_aaii.py`, `scrape_naaim.py`, `scrape_cnn_fg.py`, `manual_csv.py`. Each ≤ ~60 lines; scrapes ≤ ~30 lines; zero shared state.
2. **Fallback chain per registry entry** (ordered `sources` list): try primary → on failure try next → on total failure use last archived pull → else mark **stale** (staleness feeds confidence in C3; `critical: true` series trigger the fail-safe in C8). Every failure is logged, never raised past the series level.
3. **Archive-everything policy (rank-2 feature):** every successful pull is written verbatim to `data/archive/{source}/{series_id}/{pull_date}.parquet` *before* any transformation. Append-only, never pruned. This is the insurance against FRED windowing and endpoint death. A one-time `scripts/backfill_seed.py` pulls maximum available history for all registry series **now**.
4. **Politeness/robustness:** requests with retry+exponential backoff (3 tries), 10s timeout, browser User-Agent for scrapes, ≤1 req/s per host; weekly cadence keeps us far inside all rate limits (incl. Alpha Vantage 25/day, Tiingo 1k/day).
5. **Manual inbox stays** (Blueprint): `data/inbox/*.csv|xlsx` → validated → archived to `data/inbox/processed/`. Covers anything unautomatable (e.g. broker exports later).
6. **Pre-DB validation (pandera):** per-source schema (columns, dtypes, date monotonic, value bounds from registry `sanity_range`), duplicate handling via PK upsert (`INSERT OR REPLACE` raw; `MERGE` weekly). Outliers (MAD on delta_1w) flag, don't fail.

## Implementation steps

1. `ipos/etl/base.py` — protocol + fallback executor + archive writer.
2. `ipos/etl/fred.py`, `stooq.py` (Phase 1) → covers ~20 golden indicators.
3. `scripts/backfill_seed.py` — immediate history seed (esp. OAS series).
4. `ipos/etl/validators.py` — pandera schemas + sanity ranges.
5. Load path: archive parquet → `fact_observation` upsert (vintage_id = pull timestamp for market data; provider vintage where offered).
6. Phase 3: remaining connectors + scrapes, each with its own tiny pytest using recorded fixtures (no live calls in tests).

## Definition of done
- `uv run ipos-pull` fills `fact_observation` for all active registry entries with zero unhandled exceptions on: happy path, dead primary source, fully offline (uses archive, marks stale). Archive directory grows monotonically. Fixture-based tests green.

**Effort:** Phase-1 slice M; full coverage +M (spread). **Recurring tokens:** 0.
