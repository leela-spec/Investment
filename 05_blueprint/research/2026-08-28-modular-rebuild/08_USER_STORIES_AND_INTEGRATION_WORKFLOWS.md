# IPOS Modular Rebuild — User Stories and Integration Workflows

Status: WORKFLOW_CANDIDATE_V0_1

## Purpose

Define the intended operator experience before implementation and expose every technical dependency between existing products.

The architecture must prefer existing supported integrations and proven tools over custom platform development.

## Common integration backbone

```text
WEB.DE IMAP ----\
Gmail -----------+--> Activepieces --> normalized event --> Hermes
TradingView ----/          |                               |
                           +--> Karakeep                    +--> shared operator channel
```

Activepieces owns deterministic external-event intake and routing only.  
Hermes owns semantic analysis, orchestration and operator communication.  
Karakeep owns source/evidence custody.  
Transcript-to-Knowledge owns structured transcript knowledge transformation.  
IPOS owns unique investment policy.  
Riskfolio owns portfolio optimization.

## Event classes

Every external event should normalize into one of:

- EMAIL_RESEARCH
- EMAIL_ANALYST_SIGNAL
- ACTION
- VIDEO_RESEARCH
- DOCUMENT_RESEARCH
- MARKET_ALERT
- PORTFOLIO_UPDATE
- PIPELINE_FAILURE

An event must preserve:

- source system;
- source identifier;
- source timestamp;
- ingestion timestamp;
- source URL where applicable;
- deduplication/idempotency identifier;
- raw-evidence reference;
- semantic classification;
- processing status.

## US-COMM-01 — Shared operator communication

As either portfolio operator, I want Hermes to post important investment events into one shared communication space so both operators can see the same evidence, ask follow-up questions and reach decisions from shared context.

Preferred candidate:

- private Telegram group;
- both operators allowlisted;
- Hermes bot;
- topics such as Alerts, Research and Weekly Review.

No automatic trading is triggered by chat alone.

## US-EMAIL-01 — WEB.DE analyst email ingestion

Trigger:

- new email in the designated WEB.DE mailbox.

Flow:

1. Activepieces IMAP trigger detects the message.
2. Preserve sender, subject, timestamp and message identity.
3. Apply sender/source filters and duplicate protection.
4. Create a normalized email event.
5. Store source/evidence in Karakeep where appropriate.
6. Send the normalized event to Hermes.
7. Hermes classifies the content and selects the required downstream workflow.

## US-EMAIL-02 — Gmail research ingestion

Trigger:

- new or newly labelled Gmail message.

Preferred scoping:

- Gmail filters/labels identify approved investment sources before downstream AI processing.

Downstream processing is identical to WEB.DE after normalization.

## US-EMAIL-03 — Analyst action signal

When an approved source explicitly issues a BUY, SELL, REDUCE, ADD, HOLD or WATCH recommendation:

1. Preserve/link the original source.
2. Extract the instrument, action, source and short stated reason.
3. Immediately send an `ACTION` message through Hermes to the shared operator channel.
4. Add the recommendation to the open Action/Watch register.

Default processing stops here.

A deeper portfolio/IPOS analysis runs only when:
- an operator requests `analyze`;
- Hermes identifies an exceptional high-impact case;
- or the item remains relevant for the periodic portfolio review.

A source recommendation is never automatically converted into a trade.

## US-VIDEO-01 — Video research acquisition

When an approved email contains a relevant video URL:

1. Preserve the email and URL.
2. Create/update the Karakeep source record.
3. Obtain media/audio with the approved existing media tooling.
4. Produce a timestamped transcript.
5. Preserve the transcript as immutable evidence.
6. hand the transcript to the Transcript-to-Knowledge pipeline.

## US-VIDEO-02 — Chart extraction

For a research video containing charts, tables or diagrams:

1. Detect scene changes with an existing scene-detection tool.
2. Export representative timestamped frames.
3. Use Hermes vision only to classify which candidate frames contain decision-relevant charts/tables/diagrams.
4. Preserve selected frames with their video timestamps and source reference.
5. Attach/link them to the corresponding knowledge output.

Do not fabricate chart values that cannot be read reliably.

## US-KB-01 — Transcript to structured knowledge

Transcript-to-Knowledge transforms the immutable transcript into:

- Macro synthesis;
- semantic Meso modules;
- Micro atomic claims;
- exact quote anchors;
- concept/entity pages;
- verification queue where appropriate.

Karakeep is not responsible for this transformation.

## US-EVIDENCE-01 — Karakeep evidence custody

Karakeep stores/searches:

- source URLs;
- web pages;
- PDFs/images;
- research text;
- video references/archives;
- highlights;
- tags;
- notes;
- evidence metadata.

Karakeep does not become:

- the portfolio database;
- the deterministic numeric engine;
- the IPOS rule engine;
- the Macro/Meso/Micro knowledge compiler.

## US-IMPACT-01 — New research portfolio impact

After new knowledge is compiled:

Hermes asks:

1. Which instruments/assets/scenarios are affected?
2. Do we currently hold relevant exposures?
3. Does the evidence reinforce or contradict current IPOS state?
4. Does it create a WATCH or REVIEW condition?
5. Is immediate operator notification justified?

Outputs:

- NO_IMPACT
- WATCH
- REVIEW
- HIGH_PRIORITY_REVIEW

No automatic policy mutation.

## US-TV-01 — Critical TradingView alert

TradingView alert  
→ Activepieces webhook  
→ validate/deduplicate  
→ HMAC-sign  
→ Hermes webhook  
→ portfolio-context lookup  
→ shared operator notification.

## US-TV-02 — TradingView Watchlist Alert

Use Watchlist Alerts where the same deterministic condition applies across many symbols.

Goal:  
reduce consumption of individual TradingView alert slots while retaining TradingView's own market/indicator environment.

## US-TV-03 — Local scalable technical alerts

Use local deterministic calculation for broad recurring conditions that do not require TradingView-specific state.

Examples:

- large percentage moves;
- MA conditions;
- RSI/Stochastic;
- ATR/momentum;
- volume conditions;
- portfolio drawdown triggers.

Events use the same normalized MARKET_ALERT contract as TradingView alerts.

## US-TV-04 — Manual chart-level monitoring

TradingView remains the primary human chart-analysis environment.

Standard indicators and generic price conditions should be monitored locally where possible.

For manually created chart geometry:

### Horizontal support/resistance
Store the exact price level in a small local chart-level registry and monitor:
- approaching threshold;
- touch;
- crossing up;
- crossing down.

### Fibonacci
Store the confirmed anchor points and required Fibonacci levels. Calculate and monitor the resulting prices locally.

### Trendline/channel
Store the confirmed time/price anchor coordinates required to reproduce the line geometry and monitor the calculated current line value locally.

TradingView-native drawing alerts remain available for a small number of critical drawings, but the architecture must not depend on purchasing enough TradingView alert capacity to cover the complete portfolio.

Do not assume that TradingView drawing objects can currently be exported through a supported machine-readable API.

## US-ACTION-01 — Open Action / Watch register

Maintain one minimal durable view of unresolved investment items.

Two primary classes:

- `ACTION` — something may require an operator decision, such as BUY, SELL, REDUCE, ADD or REBALANCE;
- `WATCH` — something should remain under observation but currently requires no action.

Minimum fields:
- instrument/topic;
- action or watch condition;
- source;
- created_at;
- short reason;
- status: OPEN | DONE | DISMISSED | EXPIRED;
- source/evidence reference where applicable.

The register is not a new analytical platform.

Hermes uses it to answer questions such as:
- "What do we need to do?"
- "What are we watching?"
- "Which analyst recommendations remain unresolved?"

Open items are also summarized in the periodic portfolio review.

## US-PORT-01 — Portfolio refresh

Broker CSV/PDF  
→ immutable raw input  
→ deterministic normalization  
→ canonical portfolio  
→ Wealthfolio  
→ IPOS  
→ Riskfolio  
→ Hermes.

## US-OPT-01 — Portfolio optimization

Riskfolio receives:

- canonical portfolio data;
- deterministic return/risk inputs;
- explicit IPOS constraints.

It returns:

- candidate target weights;
- diagnostics;
- constraint status.

Hermes explains the output but does not calculate replacement weights itself.

## US-REVIEW-01 — Weekly investment review

Required outputs:

1. portfolio/dashboard review;
2. written investment memo;
3. ranked action list;
4. proposed target weights.

Inputs:

- canonical current portfolio;
- market/macro data;
- IPOS policy;
- Riskfolio results;
- material new knowledge/evidence;
- TradingView/local technical events.

Hermes delivers the review to the shared operator channel and links the underlying artifacts.

## US-CHAT-01 — Follow-up question

Either operator may reply to a Hermes notification.

Hermes should retrieve the original event, evidence, current portfolio and deterministic IPOS outputs so the explanation remains source-grounded.

## US-HEALTH-01 — Pipeline failure

Material failures must themselves create operator events.

Examples:

- mailbox authentication failure;
- TradingView webhook not delivered;
- failed video download;
- transcription failure;
- invalid TTK run;
- Karakeep unavailable;
- market-data source unavailable;
- portfolio normalization mismatch.

The notification states:

- failed component;
- affected event;
- whether data was lost;
- whether retry is safe;
- whether operator intervention is required.

## US-DECISION-01 — Approved portfolio action

Open decision.

The system currently stops at human approval.

Still unresolved:

- whether an approved proposal may generate a deterministic order CSV for manual broker entry.

No broker order submission is authorized.
