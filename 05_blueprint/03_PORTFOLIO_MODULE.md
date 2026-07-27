# Portfolio Module — Plan (built 2026-07-27)

**Status:** ✅ **built 2026-07-27**, matches this design closely (one clarification made during build, see §8). This file remains the spec of record — read it before touching the module again. Post-build notes, deviations, and ranked follow-ups: **§8** at the bottom.

**Goal:** compare the operator's *actual* portfolio exposure against IPOS's *suggested* weekly stance vector, so the report answers "am I already positioned the way this week's signal suggests, and by how much am I over/under?" — not just "what does the signal say."

**Origin:** the only prior trace of this idea is one line in `00_MASTER_PLAN.md` Phase 4 ("portfolio/exposure module (manual CSV first, per transcript guidance)") and a prompt template in `Automated Investment Playbook.md` that has the LLM *propose* a stance vector — neither ingests real holdings. This file is the first concrete design.

---

## 1. The automation question (operator asked directly — answered here, verified 2026-07-26)

Operator holds accounts at **Smartbroker** and **finanzen.net zero** (Germany) and asked whether this should be an API integration. Researched before writing this plan, not guessed:

| Broker | Automation available | Cost / access | Verdict |
|---|---|---|---|
| **Smartbroker** | Yes — SMARTBROKER+ has a real REST API (`api-trading`) that can query portfolios/transactions for "evaluations and analyses." | **Free only with "heavy trader" VIP status (≥45 trades/quarter)**; otherwise **€29.90/month**. ([smartbrokerplus.de](https://www.smartbrokerplus.de/de-de/api-trading/)) | Real option, but crosses the project's $0 constraint unless the operator already qualifies as a heavy trader. Needs an explicit decision, same as any other paid-source trigger in `01_DECISION_ANALYSIS.md` D5. |
| **finanzen.net zero** | No public API found. CSV/PDF export only (Depot → Meine Orders → Ausgeführt → export button). Third-party tools (Portfolio Performance, DivvyDiary, Finanzfluss Copilot) all rely on this same manual CSV export — there is no more-automated path today. | Free | CSV export is the ceiling for this broker; nothing to build against beyond that. |
| **PSD2 / open banking aggregator** (FinAPI, Tink, etc.) | Exists, BaFin-regulated, could read *any* German bank/broker account with consent. | These are **B2B products** aimed at companies integrating with banks — not a simple free personal API key like FRED's. Pricing/access would need its own research if pursued. | Noted as the "real" full-automation path if this ever becomes worth paying for; out of scope for a $0 personal project today. |

**Consequence for design:** true one-click automation isn't available for free across both brokers today. The design below targets **maximum automation within the $0 constraint**: not manual data entry, but not a live API pull either — a **drop-a-file, auto-ingest-on-next-run** pattern, identical to the existing `manual_csv` connector already used for HY_OAS/IG_OAS (`ipos/etl/manual_csv.py`: matches `data/inbox/<glob>`, picks the latest file automatically, no manual parsing). Exporting a CSV from either broker's portal and dropping it in `data/inbox/` is the one manual step that remains; everything after that is automatic.

**If Smartbroker's API is wanted later** (operator has/gets heavy-trader status, or accepts €29.90/month): that becomes a second, additional ingestion path feeding the *same* internal portfolio model described below — the aggregation/report logic doesn't change, only how the raw position data arrives. Treat adopting it as its own decision (alternatives + switch trigger), same discipline as D5.

---

## 2. What "done" looks like

A new report section, **"Portfolio vs. Stance"**, showing per module: your actual exposure (% of total portfolio value) next to IPOS's suggested tilt for that module this week, with a simple over/under read (e.g. "Equity: you're 62% weighted; system suggests a +0.60 tilt — roughly aligned" vs "Commodities: you're 0% weighted; system suggests +0.93 — you're not participating in a signal the system currently likes").

## 3. Data model

**`data/inbox/portfolio*.csv`** (operator-exported or hand-maintained; latest file wins, same convention as `manual_csv.py`):

| Column | Example | Notes |
|---|---|---|
| `instrument` | `IE00B4L5Y983` (ISIN) or ticker | Whatever the broker export gives; not interpreted directly |
| `quantity` | `120` | Shares/units held |
| `value_eur` | `18500.00` | Current position value — if the export only gives quantity + price, compute this at import time, don't require the operator to |

**`configs/portfolio_mapping.yaml`** (operator-maintained, one-time setup + occasional additions — mirrors how `registry.yaml` maps series to modules):

```yaml
# instrument -> IPOS module. Add a line whenever a new position is bought.
mappings:
  IE00B4L5Y983: EquityRisk   # e.g. an MSCI World / S&P 500 ETF
  DE000A1EWWW0: Commodities  # e.g. a gold ETC
  ...
unmapped_policy: warn   # warn (default, shows in report) | ignore | error
```

This mirrors the project's existing pattern (registry-driven, explicit config, no magic inference) rather than trying to auto-classify instruments by name/type, which would be fragile and silently wrong.

## 4. Build plan (files, matching existing module conventions)

- `ipos/etl/portfolio_csv.py` — reads `data/inbox/portfolio*.csv` (same "latest file wins" pattern as `manual_csv.py`), validates columns, resolves `value_eur` if only quantity+price given.
- `ipos/aggregate/portfolio.py` — joins parsed positions against `portfolio_mapping.yaml`, sums `value_eur` per module, computes each module's % of total portfolio value; flags unmapped instruments per `unmapped_policy`.
- `ipos/export/snapshot.py` — new `portfolio` block in `snapshot.json`: `{module: {weight_pct, value_eur}}` + `unmapped: [...]`.
- `ipos/report/html.py` + `ipos/report/glossary.py` — new "Portfolio vs. Stance" section, reusing the existing tilt-bar component; add glossary entries for this new section (consistent with the 2026-07-26 explainability pass).
- `ipos/report/report.py` (markdown) — matching plain-text section.
- No portfolio data ever required: if `data/inbox/portfolio*.csv` is absent, this section is simply omitted — fail-degraded, matching every other optional piece of this system (never a hard dependency, per `00_MASTER_PLAN.md` principle 4).

## 5. Definition of Done

- Dropping a portfolio CSV export in `data/inbox/` and running `ipos-weekly` produces a "Portfolio vs. Stance" section with no manual data entry beyond the broker's own export click.
- Absent file → report renders exactly as today, no error, no missing section crash.
- An instrument in the CSV with no entry in `portfolio_mapping.yaml` is surfaced clearly (not silently dropped or silently zero-weighted).
- Tests: a fixture CSV + fixture mapping produce known module weights (unit test, no network — matches every other test in this suite).

## 6. Explicitly out of scope for this plan

- No brokerage login/credential storage of any kind (unofficial scraping libraries for German neobrokers exist in the wild; not used here — ToS risk + credential-handling risk, inconsistent with this project's and the agent's safety posture).
- No automatic instrument classification/mapping — the operator maintains `portfolio_mapping.yaml` explicitly, same philosophy as every other config in this repo.
- No trade execution or rebalancing suggestions of any kind — this stays strictly a read-only comparison, consistent with `00_MASTER_PLAN.md`'s "no trade calls" principle carried through the whole system.

---

## 8. Post-build notes (2026-07-27)

Built as designed in §3–§5, file-for-file, with the markdown report living at its actual path `ipos/export/report.py` (§4 said `ipos/report/report.py` — that path never existed; corrected here, no behavior change). All Definition-of-Done items (§5) are met and covered by `tests/test_portfolio.py` (18 tests): CSV parsing incl. price→value_eur computation, known-weight aggregation, all three `unmapped_policy` branches, the alignment-read classifier, and an integration test proving the section is included/omitted correctly.

**One clarification made during build, not in the original spec:** `unmapped_policy` only controls whether an unmapped instrument is *listed* in the report. `total_value_eur` (the weight-% denominator) always includes every position's value, mapped or not — an unmapped ETF is still real money in the account and must not silently shrink the total. `warn` shows it, `ignore` hides it from the list (but still counts it in the total), `error` aborts the section. `configs/portfolio_mapping.yaml`'s comments spell this out.

**Files added/changed** (exact list, for a future diff-check): `ipos/etl/portfolio_csv.py`, `ipos/aggregate/portfolio.py`, `configs/portfolio_mapping.yaml`, `tests/test_portfolio.py` (new); `ipos/export/snapshot.py`, `ipos/export/report.py`, `ipos/report/html.py`, `configs/glossary.yaml` (extended).

**2026-07-27 follow-up pass (items 1-5 below):** `ipos/etl/portfolio_csv.py` (real-export parsing, currency default, freshness), `ipos/aggregate/portfolio.py` (`convert_to_eur`, `persist_portfolio_weights`), `ipos/aggregate/contradictions.py` (`tilt`/`portfolio_weight` predicates; also fixed a pre-existing gap where negative numeric literals like `-0.2` couldn't compile — `ast.USub`/`ast.UAdd` were never in the safe-evaluator's node whitelist), `configs/contradictions.yaml` (+8 rules), `ipos/run.py` (new "portfolio" stage), `ipos/export/snapshot.py`/`ipos/report/html.py`/`ipos/export/report.py` (currency + freshness wiring/banner), `ipos/warehouse/migrations/004_portfolio.sql` (new), `tests/test_portfolio.py` + `tests/test_contradictions.py` (extended).

### Ranked follow-ups (impact × effort, same ranking function as `00_MASTER_PLAN.md` §2)

1. **✅ Done 2026-07-27 — Verify against a real broker export.** Operator supplied a real finanzen.net Zero CSV export. It did **not** match the invented schema at all: semicolon-delimited, German column names (`Name;ISIN;WKN;Art;Anzahl;...;Kurs;...;Wert;...`), German decimal-comma/thousands-dot numbers (`"10.684,60"`, `"8.849"` meaning 8849). Fixed in `ipos/etl/portfolio_csv.py`: delimiter sniffing (`;` vs `,`), a file-level (not per-column) locale decision — German thousands-only values like `"8.849"` have no comma at all, so per-column comma-detection would have silently misparsed them — candidate-column lists extended with `isin`/`anzahl`/`wert`/`kurs`, and a UTF-8-sig/cp1252 encoding fallback. Verified against the real export by hand: all 5 real positions parsed to the exact instrument/quantity/value shown in the export. Real file never committed (personal financial data) — `tests/test_portfolio.py` covers the same shape with a synthetic fixture.
2. **✅ Done 2026-07-27 — Surface a large weight/tilt mismatch as a first-class contradiction.** New `fact_portfolio_weight` table (migration `004_portfolio.sql`) persists actual weights per module each run (a new `run.py` "portfolio" stage, before `contradictions`); `contradictions.py` gained `tilt()`/`portfolio_weight()` predicate functions; `configs/contradictions.yaml` gained 8 `PORTFOLIO_*_MISMATCH` rules (one per golden module), reusing `stance_alignment`'s existing thresholds (weight 10%, tilt 0.2). Null-safe: a week with no portfolio CSV writes no rows, so `portfolio_weight()` is `None` everywhere and no rule can misfire.
3. **✅ Done 2026-07-27 — Currency handling.** `ipos/aggregate/portfolio.py`'s new `convert_to_eur()` converts non-EUR positions using that week's `EURUSD` rate from `fact_weekly` (nearest at-or-before `as_of`); unsupported/unrated currencies warn-and-skip rather than crash. Not triggered by the real Zero export itself (German brokers already report in EUR), but in place for any future non-EUR export.
4. **✅ Done 2026-07-27 — Log the portfolio stage in `run_log`.** New `run.py` "portfolio" stage always logs (status `OK` in both the CSV-present and no-CSV cases — absence is the documented default mode, not a failure), with `rows_out`/`detail` showing modules-found/unmapped counts.
5. **✅ Done 2026-07-27 — Flag a stale/aging portfolio CSV.** `portfolio_csv.portfolio_freshness()` compares the CSV's file mtime against `as_of` (14-day allowance, mirroring the `W`-frequency indicator staleness window); a `.banner.warn` shows in both report renderers when stale. Uses `as_of`, never wall-clock, to preserve `build_snapshot`'s byte-identical-rerun determinism contract.
6. **★★☆☆☆ / M — An aggregate portfolio-level read, not just per-module.** Right now the comparison is module-by-module only. A single derived number — e.g. a portfolio-weighted average tilt, compared against the system's own `risk_budget` — would answer the plan's opening question ("am I already positioned the way this week's signal suggests") at a glance, before the operator reads eight rows. Deferred because it needs a defensible weighting formula (by value? by risk-budget-weight per module?) that wasn't specified in the original design — needs a small decision, not just code.
7. **★★☆☆☆ / M — Weight-history sparkline.** Every indicator and module already gets a 52-week score sparkline in the HTML report; the portfolio block doesn't get the same treatment even though the data exists implicitly (each week's `snapshot.json` retains that week's portfolio block, the same append-only pattern as everything else). Cosmetic/trend-visibility value only — Phase-4-optional, not urgent.
8. **New, discovered during this build — populate real ISIN→module mappings.** `configs/portfolio_mapping.yaml` ships empty (`mappings: {}`); every real holding is currently `unmapped` (harmless — `unmapped_policy: warn` — but the module compares nothing until this is filled in). This is an investment-categorization judgment call for the operator, not something to invent silently.
9. **New, discovered during this build — Smartbroker PDF ingestion.** The operator also holds a Smartbroker depot (PDF-only "Depotübersicht" statement, not CSV — no export-automation path was found for this broker, only a gated paid API). PDF table extraction is a materially different, larger feature than CSV parsing; not built, flagged here as a possible future follow-up.

None of the above block current use: the module is fully functional and degrades correctly (omitted entirely) with no portfolio file present, per the Definition of Done.
