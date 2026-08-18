# Research — high-impact visualizations for a financial report / status / decision & analysis framework

**Date:** 2026-07-29 · **Asked by:** operator, before continuing the roadmap
**Question:** What are the highest-impact visualizations and dashboard elements for a financial
report/status/decision-and-analysis framework? Has IPOS missed any? Rank every candidate by
build cost, maintenance cost, copycat-ability, free access, value, **evidence** of that value,
and risk.

**Outcome:** Tier 0 + Tier 1 built the same day; Tier 2 deferred; item 19 rejected; item 17
spec'd but not built. Decisions and rationale: `01_DECISION_ANALYSIS.md` amendment 2026-07-29.

---

## 0. Evidence-quality framing (read this before using the ranking)

This domain has **almost no randomized-trial evidence.** Three kinds of support exist, and
each candidate below is graded on which it has:

- **(a) Perception experiments** on encoding accuracy. Real, replicated, narrow in scope.
- **(b) Formal theory** — scoring rules for forecast evaluation (Brier, calibration).
- **(c) Revealed preference** — what regulators and the largest asset managers actually ship
  at scale. Weaker than a trial, much stronger than a blog post.

Explicitly discarded as evidence: "best financial dashboard 2026" listicles (SEO content),
"AI-adaptive dashboard" trend claims (vendor marketing), and — partially — Tufte's data-ink
ratio, which rests on limited qualitative evidence and which a later quantitative study
contradicted by finding some viewers *prefer* lower data-ink.

## 1. Findings

1. **Encoding hierarchy — the one properly-evidenced item.** Cleveland & McGill: position on
   a common scale > length > direction > angle > slope > area > volume > shading/saturation.
   Replicated by Heer & Bostock via crowdsourcing. Later work qualifies it importantly: only
   *position* is robust across tasks; color, size and shape are task- and context-dependent.
   → **Consequence for IPOS:** the shared-0–100 strip and dot-on-scale choices are right; the
   52×22 score heatmap is the weakest encoding in the report and should stay a scanning aid,
   never a reading surface.
2. **Contextualizing a current reading against its own history is the most-copied
   institutional form.** JP Morgan's *Guide to the Markets* — the industry's most widely
   distributed chartbook — builds its valuation pages on percentile-and-range with a current
   marker and a median tick (percentiles computed on monthly data since 2000). The generic
   form is the ranged dot plot: bar = historical range, dot = today. Evidence class (c), at
   very large scale.
3. **Composite indices are published together with their decomposition.** The OFR Financial
   Stress Index (33 variables, five categories: credit, equity valuation, funding, safe
   assets, volatility) ships the index *and* contribution-by-category and by-region, on a
   zero-centered scale with US recession shading and a line/column toggle. A regulator's
   production answer to "why is the number what it is". Evidence class (c).
4. **Waterfall/bridge is the standard finance idiom** for reconciling a start value to an end
   value, including risk-attribution decomposition by asset class and factor. Caveat we hit
   in practice: it only works when the opening balance and the increments share a usable
   scale.
5. **Lead with the diff.** The recurring dashboard arc is *what changed → why → what do we do
   now*, with delta indicators plus trend context — because −10% inside an 8-week uptrend
   means the opposite of the same −10% inside a downtrend. Paired warning from the same
   sources: *"when everything is highlighted, nothing is."*
6. **Forecast self-scoring is founded theory, not fashion.** Brier `BS = 1/N Σ (fₜ − oₜ)²`
   plus a reliability diagram (predicted probability vs. observed frequency per bin).
   Punishes misplaced confidence asymmetrically: 90% and right costs 0.01, 90% and wrong
   costs 0.81. The stated prerequisite is the hard part — *record before the verdict*: dated,
   quantified, fixed horizon, unambiguous resolution criterion. Evidence class (b).
7. **Conditional/analog analysis is real practice but hazardous.** "When this indicator sat
   in this percentile, here is the distribution of what followed" appears in GS-style
   long-horizon return models and in commercial macro-analog tools. The published examples
   also display the failure mode vividly — one write-up reports a "−189% annualized"
   conditional return, which is a thin-conditional-sample artifact, not a finding.
8. **Regime work reduces to persistence.** Markov regime-switching models are summarized by
   the transition matrix (rendered as a heatmap) plus expected duration `1/(1 − P_kk)`;
   published equity estimates put low-volatility regime persistence near 97–98% per period
   (≈125 weeks at 0.992, ≈32 weeks at 0.969) — regimes last months, not weeks.
9. **Anti-patterns to keep avoiding:** circular gauges, pie charts beyond ~4 slices, 3D
   effects, dual-axis charts ("almost always misleading"), truncated y-axes, traffic lights
   (already banned by IPOS's own locked constraints), and metric overload — the recurring
   advice is 5–8 headline KPIs. One line worth quoting for this project specifically:
   *"errors in visualized data are more dangerous than errors in spreadsheets because they
   are more convincing"* — precisely the failure class of the three synthetic-data incidents
   of 2026-07-26/27 and the `fx_warnings` silent drop found in this audit.

## 2. What IPOS already had (so nothing was rebuilt)

Bullet-style risk track with qualitative zones at 20/50/80, score and stance sparklines, a 2D
dated growth×inflation regime map with arrowhead and quadrant key, a regime ribbon, a
multi-horizon Δscore strip, a member-disagreement strip on a shared 0–100 axis, tilt bars, a
52×22 module-grouped score heatmap, contradiction cards, events, top movers, a portfolio
table, ~149 CSS-only glossary popovers, and a CVD-validated single RdBu diverging scale.

Two of the research's own recommendations were therefore **already satisfied**: Few's
bullet-graph-over-circular-gauge, and Tufte's sparklines-in-tables.

## 3. The actual gap

Not chart types — **rendering**. See the `01_DECISION_ANALYSIS.md` amendment for the itemized
list of fields the pipeline computed and stored but no renderer drew (`pctile_156w`, `z_104w`,
risk-budget/confidence history, `base_risk_budget`, `regime_features`, `fx_warnings`,
stale/missing series names, `n_high_severity`, `delta_4w/12w`, `playbook_selection`), plus the
scale problem: ~3,847 weeks of scored history existed and 52 were charted.

## 4. Ranked candidates

Cost is for *this* codebase (deterministic inline SVG, no JS, no CDN, no `src=`).
Copycat = can a known-good design be lifted instead of invented. All candidates are free.

### Tier 0 — already computed, never rendered · **BUILT 2026-07-29**

| # | Candidate | Build | Maint | Copycat | Value | Evidence | Risk |
|---|---|---|---|---|---|---|---|
| 1 | Level-percentile strip per indicator | XS–S | XS | Easy (JPM GTTM) | High | **Strong** (c) + (a) | Low |
| 2 | Risk-budget & confidence history line | XS | XS | Easy | High | Strong | Very low |
| 3 | "Why this regime" — base → ×scaler → headline bridge + classifier measurements | S | XS | Easy (OFR) | High | **Strong** (c) | Low |
| 4 | HTML/markdown parity: stale-series names, Δ4w/12w, `n_high_severity` | XS | XS | n/a | Med–High | Med | Very low |
| 5 | `fx_warnings` surfaced (**correctness bug**) | XS | XS | n/a | Med–High | n/a | Very low — *leaving it was the risk* |
| 6 | `playbook_selection` audit line | XS | XS | Easy | Med | Med | Very low |

### Tier 1 — cheap new computation over existing tables · **BUILT 2026-07-29**

| # | Candidate | Build | Maint | Copycat | Value | Evidence | Risk |
|---|---|---|---|---|---|---|---|
| 7 | "What changed this week" panel above the fold | S | XS | Easy | High | Med (design consensus) | Very low |
| 8 | Breadth / diffusion index (% above 50, % improving) | XS | XS | Easy | Med–High | Med | Very low |
| 9 | Per-module contribution decomposition | S–M | XS | Easy (OFR) | High | **Strong** | Low — arithmetic must close |
| 10 | Contradiction recurrence ("fired N of last M weeks") | S | XS | Easy | Med–High | Med | Low |

### Tier 2 — genuinely new work / new history spend · **DEFERRED**

| # | Candidate | Build | Maint | Copycat | Value | Evidence | Risk |
|---|---|---|---|---|---|---|---|
| 11 | Long-history level charts + US recession shading (FRED `USREC`, free) | M | S | Easy (Fed/OFR) | **High** | **Strong** | Low–Med — 1970 epoch floor is a known trap |
| 12 | Regime persistence & transition stats (needs a deep `ipos-replay`) | M | S | Easy (Markov) | Med–High | Med–Strong | Med — small-sample counts must be shown |
| 13 | Drawdown / underwater plot | S | XS | Easy | Med | Med–Strong | Low |
| 14 | `run_log` observability panel | S | XS | Easy | Med (ops) | Med | Very low |
| 15 | Portfolio aggregate read + over/under-weight bars | S | XS | Easy | Med–High | Med | Med — needs the weighting-formula decision |
| 16 | Rolling correlation matrix | M | S | Easy | Med | Med | Low–Med — weakest encoding |

### Tier 3 — needs its own written decision

| # | Candidate | Build | Maint | Copycat | Value | Evidence | Risk | Status |
|---|---|---|---|---|---|---|---|---|
| 17 | Brier score + reliability diagram on the framework's own past stance | L | M | Med | **Highest — the only thing that says whether any of this works** | **Strong theory** (b) | **High** — needs record-before-the-verdict; retro-scoring is self-serving | **Spec'd, not built** |
| 18 | Falsification / trigger panel ("what would change my mind") | S–M | M | Hard — no standard form | High for decisions | **Weak** | Med — reads as a signal to act on | Open |
| 19 | Conditional analogs ("what happened next") | L | M | Med | High if honest | Med, with documented failure modes | **Highest** — thin samples, overfitting, slides toward advice | **Rejected for now** |

### Rejected outright

Circular gauges, pie charts, dual-axis, 3D, traffic lights, "AI-adaptive" widgets, and
small-multiples-of-module-history (the heatmap already covers it, and the data-ink evidence
behind it is the weakest in the set).

## 5. Sources

- [Perception and Visualization — Cleveland & McGill hierarchy (U. Iowa)](https://homepage.divms.uiowa.edu/~luke/classes/STAT4580/percep.html)
- [A Review and Collation of Graphical Perception Knowledge for Visualization Recommendation (arXiv)](https://arxiv.org/pdf/2109.01271)
- [The Risks of Ranking: Revisiting Graphical Perception (Northwestern)](https://mucollective.northwestern.edu/files/2022-perception-individual-differences.pdf)
- [How William Cleveland Turned Data Visualization Into a Science](https://priceonomics.com/how-william-cleveland-turned-data-visualization/)
- [JP Morgan Guide to the Markets (US)](https://cdn.jpmorganfunds.com/content/dam/jpm-am-aem/global/en/insights/market-insights/guide-to-the-markets/mi-guide-to-the-markets-us.pdf)
- [How to make ranged dot plots](https://playfairdata.com/how-to-make-ranged-dot-plots-in-tableau/)
- [OFR Financial Stress Index](https://www.financialresearch.gov/financial-stress-index/)
- [The OFR Financial Stress Index — working paper](https://www.financialresearch.gov/working-papers/files/OFRwp-17-04_The-OFR-Financial-Stress-Index.pdf)
- [Waterfall charts in wealth management](https://www.finticx.com/en/insights/waterfall-charts)
- [Drawdowns — Portfolio Charts](https://portfoliocharts.com/charts/drawdowns/)
- [Brier score: measuring the reliability of investment forecasts](https://www.verdoso.com/en/notes/brier-score-investment-forecasts/)
- [Scoring a risk forecast — calibration and reliability diagrams](https://magoo.medium.com/scoring-a-risk-forecast-58673bb6a05e)
- [A Markov Regime Switching Approach to Characterizing Financial Time Series](https://medium.com/@cemalozturk/a-markov-regime-switching-approach-to-characterizing-financial-time-series-a5226298f8e1)
- [Goldman Sachs — Forecasting long-term S&P 500 returns](https://www.gspublishing.com/content/research/en/reports/2024/10/18/29e68989-0d2c-4960-bd4b-010a101f711e.html)
- [Bullet graphs for not-to-exceed targets — Perceptual Edge (Stephen Few)](https://www.perceptualedge.com/blog/?p=217)
- [Bullet graph (Wikipedia)](https://en.wikipedia.org/wiki/Bullet_graph)
- [Sparkline theory and practice — Edward Tufte](https://www.edwardtufte.com/notebook/sparkline-theory-and-practice-edward-tufte/)
- [Tufte's Principles of Data-Ink — including the counter-evidence caveat](https://jtr13.github.io/cc19/tuftes-principles-of-data-ink.html)
- [Top 10 dashboard design mistakes](https://www.domo.com/learn/article/top-10-dashboard-design-mistakes-and-what-to-do-about-them)
- [10 Dashboard Design Errors](https://www.fusioncharts.com/blog/10-dashboard-design-mistakes/)
- [Why less data often leads to better decisions](https://www.sigmacomputing.com/blog/data-analysis-less-more)
- [From Data To Decisions: UX Strategies For Real-Time Dashboards — Smashing Magazine](https://www.smashingmagazine.com/2025/09/ux-strategies-real-time-dashboards/)
- [Risk dashboard features checklist for financial institutions](https://www.riskinmind.ai/blogs/risk-dashboard-features-checklist-for-financial-institutions)
- [MacroDashboard — open-source Python macro dashboard (reference only)](https://github.com/SunFish98/MacroDashboard)

**Could not be retrieved:** BlackRock's Market Risk Monitor PDF returned HTTP 403 to
automated fetch. If a future session wants an additional institutional reference for
cross-asset percentile presentation, that document is worth opening manually.
