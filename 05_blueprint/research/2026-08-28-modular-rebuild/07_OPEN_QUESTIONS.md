# Open Questions for Operator

These questions are intentionally separated from implementation so work can continue without guessing.

## Resolved operator decisions — 2026-08-28

- Hermes may receive portfolio/private investment context for now; do not impose a new privacy restriction at this stage.
- Raw transactions are not categorically local-only.
- Karakeep may use Hermes for semantic analysis where appropriate instead of requiring a separate Karakeep inference policy.
- TradingView may contain cost-basis information if useful; necessity remains to be evaluated.
- Reuse the Hermes installation already being established as the system-wide orchestrator; do not deploy a separate Hermes runtime for Investment by default.
- Wealthfolio desktop/local application is sufficient for the current portfolio UX.
- Required review outputs are all four: dashboard review, investment memo, ranked actions, and proposed target weights.
- Whether approved decisions may produce deterministic broker order CSVs remains unresolved.

## A. Privacy / data egress

1. **Portfolio-to-LLM boundary:** May Hermes send exact holdings, quantities, market values and P/L to the configured cloud LLM, or should it receive only redacted/aggregated portfolio facts?
2. **Transaction history:** Is raw transaction history categorically local-only?
3. **Research evidence:** May full private Karakeep articles/PDF text be sent to a cloud LLM for synthesis, or should sensitive research use local inference only?
4. **TradingView:** Are you comfortable storing watchlists/technical alerts/symbol lists in TradingView cloud, while keeping actual broker transactions/cost basis outside it?
5. **Cloud exception policy:** What specific categories of investment information are a hard no-go for any third-party cloud?

## B. Hermes

6. Which exact Hermes deployment are we standardizing on: the existing Hermes Agent installation already being established elsewhere, or a separate Investment-specific Hermes instance/config?
7. Which inference route is preferred for investment work: Nous subscription, ChatGPT/Codex subscription, Anthropic subscription, OpenRouter/API, or a local model for restricted tasks?
8. Should investment tools be isolated into a dedicated Hermes project/profile with a minimal read-only MCP surface?
9. Should Hermes be allowed to write notes/tags back to Karakeep later, or remain read-only permanently?

## C. Portfolio UX

10. What is the primary desired portfolio screen: current allocation, P/L/performance, risk exposures, target-vs-current drift, scenario impact, or a combination?
11. Is a desktop-local app acceptable, or do you require browser access from multiple devices?
12. Do you want Wealthfolio only as a visualization layer, or also as the human rebalancing/planning UI if its supported target-allocation features pass the POC?
13. Do you need tax-lot or German tax reporting in this architecture, or is that explicitly out of scope?

## D. TradingView

14. Which TradingView plan do you currently have exactly (current plan names/features have changed over time)?
15. Which technical analyses are genuinely used for decisions today: MA50/200, RSI, Stochastic, volume confirmation, ATR/momentum, trend breaks, support/resistance, others?
16. Do you want webhook alerts only for high-impact exceptions, or a broader event stream into Hermes?
17. Is it acceptable that TradingView remains cloud-based because the data sent there is market/symbol-level rather than sensitive portfolio data?

## E. Market/macro data

18. Is the target still **free wherever realistically possible**, with new paid data capped around EUR 20-30/month unless exceptional?
19. Which paid data do you already have indirectly through TradingView, broker subscriptions, newsletters or other services that we should avoid buying twice?
20. Do you require real-time market data locally, or is end-of-day/weekly data sufficient for the IPOS decision layer?
21. Which asset classes are mandatory in v1: equities/ETFs, bonds/rates, commodities, FX, crypto, options?

## F. Decision/output workflow

22. What should the weekly output ultimately be: a dashboard review, a written investment memo, a ranked action list, proposed target weights, or all four?
23. Should Hermes only recommend, or may it prepare deterministic rebalance/order CSVs for manual broker entry after approval?
24. Do you want current holdings to be scored against IPOS rules instrument-by-instrument, or only at portfolio/asset-class level?
25. Should scenario analysis from the existing debt-cycle/AI/USD-rotation work become a formal deterministic overlay, or remain research context for narration until separately validated?

## Provisional assumptions used until answered

- No automatic broker connections.
- No broker execution.
- Raw portfolio files stay local.
- Wealthfolio Connect disabled.
- OpenBB paid Workspace rejected.
- TradingView used for market/technical information, not private canonical portfolio state.
- Hermes receives only data necessary for a task and starts with read-only integrations.
- Free/local sources preferred; paid services require explicit approval.