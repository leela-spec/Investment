# Cost, Privacy and Data-Boundary Matrix

Date checked: 2026-08-28

## Egress classes

- `LOCAL_ONLY` — no portfolio/research payload must leave operator-controlled infrastructure for core operation.
- `LOCAL_WITH_OPTIONAL_EXTERNAL_DATA_CALLS` — application runs locally, but requests to explicitly selected market/data providers leave the host.
- `LLM_EGRESS_CONDITIONAL` — local agent/app may send selected context to the configured external LLM provider; can potentially be avoided with a local model.
- `CLOUD_SERVICE` — data entered into the product is processed/stored by a third-party cloud service according to that provider's terms.

## Component matrix

| Component | Core cost | Hosting | Egress class | What may leave our environment? | Current privacy posture |
|---|---:|---|---|---|---|
| **Hermes Agent** | Open-source agent; inference cost depends on selected provider/subscription | Local | `LLM_EGRESS_CONDITIONAL` | Prompts/tool results/context sent to configured cloud model; tool calls may contact configured services | Accept only with explicit model/provider policy and minimum-context discipline |
| **Karakeep self-hosted** | Free/open source | Local Docker/self-host | `LOCAL_ONLY` if local AI/no AI; otherwise `LLM_EGRESS_CONDITIONAL` | Saved content only leaves if external AI provider or other external integration is enabled | Prefer self-host + local Ollama or no AI for sensitive evidence |
| **OpenBB ODP** | Free/open source under AGPL | Local Python/Docker | `LOCAL_WITH_OPTIONAL_EXTERNAL_DATA_CALLS` | Tickers/query parameters/credentials as required by selected upstream data provider | ODP itself advertises local-first/no telemetry; evaluate each provider separately |
| **OpenBB Workspace Community** | Free | OpenBB cloud | `CLOUD_SERVICE` | Workspace content/data integrated into hosted service | Not default; use only after explicit cloud/privacy approval |
| **OpenBB Workspace Lite** | USD 2,400/year list; promotional USD 1,200/year through 2026-08-31 | Self-host/VPC | Local deployment but high cost | Depends on configured data/LLM providers | Reject default on cost; not required for ODP |
| **Wealthfolio core app** | Core local app free | Local | `LOCAL_ONLY` if Connect/AI disabled | Limited operational network traffic; financial DB remains local per privacy policy | Strong candidate |
| **Wealthfolio Connect** | Optional paid/cloud service | Cloud-assisted | `CLOUD_SERVICE`/hybrid | Brokerage data transits service; sync-related data | Disable by default; unnecessary for our manual deterministic import model |
| **Riskfolio-Lib** | Free, BSD-3-Clause | Local Python | `LOCAL_ONLY` | Nothing inherent | Strong fit |
| **TA-Lib** | Free/BSD-style | Local | `LOCAL_ONLY` | Nothing inherent | Strong fit when needed |
| **TradingView Pro** | Existing subscription | TradingView cloud | `CLOUD_SERVICE` | Watchlists, alerts, scripts/layouts, portfolio data entered into TradingView; webhook payloads leave TradingView to configured endpoint | Use for market/technical workbench; do not make it canonical private portfolio store |
| **Activepieces Community** | Open-source/self-hostable | Local if self-hosted | Depends on connectors | Payloads sent to whichever connected services flows use | Do not install until a concrete intake gap is proven |

## Cost policy

### Default ceiling
Prefer zero marginal subscription cost.

A new paid component should normally stay within approximately **EUR 20-30/month** unless it produces exceptional, measurable value that cannot be obtained through the existing free/local stack.

### Explicit exclusions at v0.1
- OpenBB Workspace Lite: too expensive for current requirement.
- Any data vendor requiring institutional pricing before free sources are exhausted.
- Wealthfolio Connect: no need while operator-controlled CSV/PDF import is the chosen ingestion model.
- Additional workflow SaaS: no need until a real missing seam is identified.

## Sensitive data policy candidate

Treat as `RESTRICTED` by default:
- actual positions and quantities;
- transaction history;
- account/broker identifiers;
- cash balances;
- cost basis;
- tax documents;
- unpublished investment theses/notes;
- private research archives.

### Default rules
1. Restricted broker/portfolio files remain local.
2. Never put broker credentials into Hermes, Karakeep, TradingView alerts, or webhooks.
3. Hermes receives only the minimum portfolio facts needed for narration; raw documents should remain behind deterministic extractors.
4. Cloud LLM calls should use redacted/aggregated portfolio context unless the operator explicitly approves otherwise.
5. TradingView should receive market symbols/technical logic, not unnecessary private transaction history.
6. All optional cloud-sync features stay off until separately approved.

## Source facts

- OpenBB ODP: local-first, no telemetry/usage collection; AGPL; works independently from Workspace.
- OpenBB Workspace Community: free but OpenBB-hosted. Lite: self-hosted, USD 2,400/year list.
- Wealthfolio privacy policy: accounts, holdings, transactions and performance history remain in local DB; Connect is separate optional cloud service.
- Karakeep: self-host-first; optional OpenAI-compatible providers or local Ollama for AI tagging/summarization/embeddings.
- Riskfolio-Lib: BSD-3-Clause local Python library.
- TradingView: cloud service with supported CSV export and webhook alerts.