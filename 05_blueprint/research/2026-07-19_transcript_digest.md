# Research Archive — Transcript Deep-Read Digest

**Date:** 2026-07-19 · **Method:** full read of `Everything from this chat.md` (2,757 lines) by a dedicated analysis agent · **Purpose:** verify what the extraction transcript actually contains before planning, so the plan rests on verified facts, not assumptions.

## Critical finding

`Everything from this chat.md` is **not** the IPOS Blueprint request conversation. It is the **extraction pipeline log**: ChatGPT reading the 231-page seminar PDF in 8 chunks through the stages DOC_MAP → ROI_GATE → INDICATOR_EXTRACT → RULE_EXTRACT → PROCESS_EXTRACT → NORMALIZE_MERGE → PLAYBOOK_WRITE.

**Not present in that file** (they live elsewhere): the deliverables-1–9 blueprint request (its *answer* is `Automated Investment Playbook.md`), the constraint labels B1/C2/D2/D3 (they are in `For next chat.md`), token budgets, "no traffic lights"/"stance vector" wording. Only "A2 = macro-first" appears verbatim.

## What it does contain (verified, load-bearing for the plan)

- **Outputs concept:** per-module risk budget 0–100 (posture caps NORMAL 100 / CAUTION 70 / RECOVERY 40 / DEFENSIVE 25), stance/tilt priors, confidence 0–100, explicit "Contradictions to Watch" per module, auditable snapshots ("store policy_selectors … so your report can explain why risk changed").
- **Regime governor:** CHOPPY/TRENDY/MOMENTUM + risk_scaler 0.50/1.00/0.75 (UNCERTAIN 0.40); hysteresis requirement (e.g. 2-weekly-close confirmation on MA200 crossings).
- **Extracted indicator clusters with source hints:** Liquidity (FRED WALCL), Sentiment (AAII xls, NAAIM, CNN F&G composite-only, StockCharts !PCRATCBO put/call > 1.1), Fundamentals (ISM headline >50/<50; 5 subindices with weights 30/25/20/15/10 — deferred; UMich contrarian-at-extremes), Rates (T10Y2Y, T10Y3M pair), Equity Flows (buybacks — all deferred, source unclear), Technical (volume family, MA 50/200 + below-200-negative-filter, Slow Stoch 14-3-3 80/20, RSI 70/30 + weekly Power Zone >70 = momentum confirmation, NOT contrarian).
- **Hard numbers to preserve:** Put/Call >1.1; ISM 50; RSI 70/30, Power Zone >70; Stoch 80/20; choppy retracement 80–100%; momentum initial stop 1–2 ATR; Donchian N=14 (TRENDY) / N=10 (MOMENTUM); CRV ≥ 1.3; max drawdown cap 30%; risk/trade ≈ 1.66–1.67%; ADTV ≥ 400k shares; price ≥ $10.
- **Policies:** composites external-only (never rebuild Fear & Greed / Goersch Trend internals); manual-first for portfolio/exposure data, automate later; "keep only high-impact MVP signals active now" (token/ROI gate).
- **Open items flagged `needs_verification`:** S&P 500 series choice, NAAIM cadence alignment, all ISM subindices, all buyback series, 10Y−3M, MA-cross rules, ~30 rules total.

## Consequence for planning

The knowledge layer is trustworthy and richer than the repo's module set alone; the blueprint constraints come from `For next chat.md` + `Automated Investment Playbook.md`. The plan (00_MASTER_PLAN) therefore treats extraction as **done** and focuses entirely on the unbuilt implementation, seeding configs from `03_extract/*.jsonl` with provenance (`extract_ref`).
