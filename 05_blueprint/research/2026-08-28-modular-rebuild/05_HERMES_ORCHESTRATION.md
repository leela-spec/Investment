# Hermes Orchestration — Candidate Decision

## Decision

Use **Hermes Agent** as the default orchestrator candidate for the modular IPOS rebuild.

This replaces the previous OpenClaw + LangGraph proposal. LangGraph is not required by default.

## Why Hermes fits

Current Hermes Agent documentation verifies:
- MCP client support is built into the standard install;
- local `stdio` and remote HTTP MCP servers are supported;
- MCP tools are discovered automatically;
- per-server include/exclude filtering can constrain the tool surface;
- built-in terminal, process, file, web/browser, memory, skills, delegation and cron tools exist;
- Tool Search can progressively disclose MCP/plugin tools rather than placing all schemas in context;
- Hermes can itself run as an MCP server for inter-agent/channel scenarios.

This directly supports the architecture principle: **connect proven products through supported interfaces instead of inventing another integration framework.**

## Proposed tool exposure

### Initial read-only toolsets

1. `mcp-karakeep-read`
   - search bookmarks/evidence;
   - read content/highlights/tags;
   - no delete/mutation by default.

2. `mcp-openbb-read`
   - retrieve approved market/macro/fundamental endpoints;
   - no dynamic package installation;
   - no credential output.

3. `mcp-wealthfolio-read` if POC passes
   - portfolio holdings/value/performance/activity reads;
   - no Connect;
   - no mutation by default.

4. local deterministic command wrappers
   - portfolio normalize/validate;
   - IPOS policy evaluation;
   - Riskfolio optimization;
   - TA-Lib snapshot generation;
   - output validation.

## Agent contract

Hermes may:
- choose which approved deterministic tool to invoke;
- retrieve evidence;
- sequence the weekly review;
- compare deterministic outputs;
- detect missing inputs;
- narrate contradictions;
- generate decision options;
- request human approval.

Hermes may not:
- invent missing market values;
- silently change policy thresholds;
- alter raw portfolio files;
- treat LLM calculations as authoritative;
- execute broker orders in v0.1;
- write to evidence/portfolio systems unless the exact mutating capability has later been approved.

## Numeric authority hierarchy

1. Raw source file / upstream provider response
2. Deterministic normalization/validation
3. Deterministic local calculation library
4. IPOS policy/rule engine
5. Hermes narrative

If level 5 conflicts with levels 1-4, levels 1-4 win.

## Privacy implication

Hermes itself runs locally, but inference may be provided by a cloud model. Therefore local orchestration does **not** automatically mean local data privacy.

Required configuration decision before production:
- which inference provider(s) may receive portfolio context;
- whether sensitive portfolio details are redacted/aggregated before model calls;
- whether a local model is used for restricted-data tasks;
- which MCP outputs are allowed into the model context.

## Token-efficiency posture

Use Hermes Tool Search/progressive disclosure when the MCP tool surface becomes large. Avoid exposing all OpenBB/Karakeep/portfolio tools on every turn.

Preferred pattern:
- one narrow toolset per task;
- read-only first;
- deterministic outputs returned in compact schemas;
- source evidence linked rather than pasted wholesale;
- use the IPOS Playbook modules by relevance rather than loading the whole corpus.

## POC gate

Hermes is not frozen as production orchestrator until it completes one end-to-end read-only weekly review with:
1. canonical portfolio snapshot;
2. market/macro data from approved local provider layer;
3. relevant IPOS rules;
4. Karakeep evidence retrieval;
5. deterministic Riskfolio output;
6. no hallucinated numeric values;
7. auditable record of tool inputs/outputs.