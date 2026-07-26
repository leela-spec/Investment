# Portfolio Module — Plan (not yet built)

**Status:** planned 2026-07-26, **zero code written yet**. This is the concrete design to build from when this phase is picked up — do not start coding without re-reading this file first (per `HANDOVER.md` §5, plan-repair before code).

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
