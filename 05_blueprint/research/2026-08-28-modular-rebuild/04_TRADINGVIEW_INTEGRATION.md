# TradingView Pro Integration — v0.1

## Decision

Promote the existing TradingView Pro subscription to a first-class **market/technical workbench and event source**.

Do not treat TradingView as the canonical private portfolio database, a general-purpose data API, or the numeric policy engine.

## Supported capabilities to exploit

### 1. Interactive technical analysis
Use TradingView for:
- multi-timeframe chart review;
- market structure;
- trend/support/resistance validation;
- volume/oscillator overlays;
- cross-asset comparisons;
- watchlists and screeners;
- economic/yield-curve context available in the platform.

### 2. CSV export
TradingView officially supports exporting the data loaded on a chart to CSV, including displayed indicators.

Potential uses:
- operator-selected technical evidence export;
- validating TA-Lib calculations against visible TradingView indicator values;
- supplying bounded chart-series inputs to a local deterministic analysis notebook/script.

Constraint: exported history is the chart data currently loaded. Do not treat this as an unrestricted automated historical-data API.

### 3. Webhook alerts
TradingView can POST alert messages to a configured endpoint; valid JSON messages are sent as JSON.

Potential architecture:

```text
TradingView alert
      |
      | HTTPS webhook, non-sensitive JSON
      v
Activepieces self-hosted
      |
      | validate / normalize / deduplicate / HMAC-sign
      v
Hermes authenticated webhook route
      |
      v
"re-run review" / "inspect symbol" workflow
      |
      v
Hermes investment communication channel
```

Activepieces is used here as an existing event-routing product, not as an investment engine. It also provides the common intake layer for WEB.DE IMAP and Gmail research workflows.

Good alert payloads:
- symbol;
- timeframe;
- condition identifier;
- market price/indicator values exposed by TradingView placeholders;
- timestamp;
- non-secret correlation ID.

Never include:
- passwords;
- API keys;
- broker credentials;
- account IDs;
- private holdings unless explicitly approved.

### 4. Pine logic
Pine can be used for TradingView-native deterministic alert conditions and visual studies.

Boundary:
- Pine scripts are a platform-specific view/alert layer.
- Canonical IPOS policy must stay in the local repository, not become a hidden Pine-only implementation.

## Alert scaling strategy

TradingView alert capacity is treated as scarce.

Use TradingView-native alerts for capabilities that depend on TradingView state:
- manually drawn support/resistance and trendlines;
- TradingView-only/Pine conditions;
- selected time-critical symbol-specific events.

Prefer TradingView Watchlist Alerts where one common condition should apply to many symbols.

Use a separate local deterministic scanner for broad recurring conditions that do not need TradingView-specific state, for example:
- price move thresholds;
- MA50/MA200 conditions;
- RSI/Stochastic;
- ATR/momentum;
- volume conditions;
- canonical locally stored support/resistance levels.

Both TradingView and local scanner events should normalize into the same market-event contract before Hermes sees them.

Do not assume that manually drawn TradingView support/resistance levels can be automatically synchronized into the local system. This remains a POC gate.

## Relationship with TA-Lib

TradingView and TA-Lib are complementary:

| Need | Owner |
|---|---|
| visual exploration and manual chart review | TradingView |
| cloud alerts | TradingView |
| screeners | TradingView |
| deterministic local batch computation | TA-Lib |
| reproducible numeric snapshot feeding IPOS | TA-Lib/local scripts |
| operator validation of computed signals | TradingView |

## POC questions

1. Which existing IPOS technical indicators already exist identically in TradingView?
2. Can the user export those indicator values cleanly enough to serve as validation evidence?
3. Which recurring technical events are worth webhook alerts instead of weekly polling?
4. Does TradingView portfolio functionality add any useful visualization beyond Wealthfolio without requiring private transaction data?
5. Which symbol mappings differ between TradingView and the canonical portfolio schema?

## Current recommendation

Use TradingView heavily for **human-facing technical intelligence** and selectively for deterministic alert events. Keep batch computation, policy rules, portfolio state, and optimization local.