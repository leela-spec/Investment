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

### Ranked follow-ups (impact × effort, same ranking function as `00_MASTER_PLAN.md` §2)

1. **★★★★★ / S — Verify against a real broker export.** `portfolio_csv.py`'s column-name guessing (`value_eur`/`price_eur`/etc.) was designed from the *plan's* assumed schema, never checked against an actual Smartbroker or finanzen.net zero CSV export. This is the single most likely near-term blocker to real use — a real export's headers (language, decimal separator, currency column) may not match. **Action:** operator exports one real CSV, drops it in `data/inbox/`, runs `ipos-weekly`, and we adjust `VALUE_COL_CANDIDATES`/`PRICE_COL_CANDIDATES`/decimal parsing to match reality.
2. **★★★★☆ / S — Surface a large weight/tilt mismatch as a first-class contradiction**, not just a table row. The contradictions engine (`ipos/aggregate/contradictions.py`, `configs/contradictions.yaml`) already exists and is the report's designated "don't miss this" mechanism (top of report, card UI). A portfolio row like "Commodities: 0% weighted vs. +0.93 tilt" is exactly the kind of thing that mechanism was built for, but today it's buried in a table below the fold. Cheap to add: one more predicate class operating on `(weight_pct, tilt)` pairs instead of indicator scores.
3. **★★★☆☆ / S — Currency handling.** `value_eur` is trusted as-is; a US-listed ETF held in EUR-quoting-but-USD-denominated form, or a raw USD cash position, isn't converted. The registry already carries a live `EURUSD` series — a `currency` column + conversion using that week's rate would close this gap. Likely low real-world impact for a German-broker CSV (exports are typically already EUR-valued) but worth confirming against the real export from item 1 before deciding whether to build it.
4. **★★★☆☆ / S — Log the portfolio stage in `run_log`.** Every other stage in `run.py` (`pull`, `canonical`, `score`, `regime`, `aggregate`, `contradictions`, `export`) writes a `_log_stage` row; the portfolio block is built silently inside `build_snapshot` with no audit trail entry. Low cost to add a `portfolio` stage log line (found file? mapped how many? how many unmapped?) — matches the project's "everything scripted/auditable" principle.
5. **★★☆☆☆ / S — Flag a stale/aging portfolio CSV.** There's no equivalent of the indicator staleness system for the portfolio file itself — if the operator drops one CSV and then forgets to update it for months, the report will keep comparing an old snapshot of holdings against fresh signals with no warning. A simple "portfolio last updated N days ago, based on file mtime" banner (reusing the existing `.banner.warn` CSS class) would close this without adding real complexity.
6. **★★☆☆☆ / M — An aggregate portfolio-level read, not just per-module.** Right now the comparison is module-by-module only. A single derived number — e.g. a portfolio-weighted average tilt, compared against the system's own `risk_budget` — would answer the plan's opening question ("am I already positioned the way this week's signal suggests") at a glance, before the operator reads eight rows. Deferred because it needs a defensible weighting formula (by value? by risk-budget-weight per module?) that wasn't specified in the original design — needs a small decision, not just code.
7. **★★☆☆☆ / M — Weight-history sparkline.** Every indicator and module already gets a 52-week score sparkline in the HTML report; the portfolio block doesn't get the same treatment even though the data exists implicitly (each week's `snapshot.json` retains that week's portfolio block, the same append-only pattern as everything else). Cosmetic/trend-visibility value only — Phase-4-optional, not urgent.

None of the above block current use: the module is fully functional and degrades correctly (omitted entirely) with no portfolio file present, per the Definition of Done.
