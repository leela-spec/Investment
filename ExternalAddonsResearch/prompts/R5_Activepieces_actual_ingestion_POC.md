<system_instruction>
Evaluate Activepieces as a deterministic research-ingestion sidecar for IPOS.

This is a research + proof-of-concept task.

The current IPOS architecture deliberately rejected an orchestrator for its weekly
core pipeline. Therefore Activepieces must NOT be silently inserted into that core.

Test it as a separate intake automation layer and determine whether the added value
justifies formally changing or refining the existing architecture decision.
</system_instruction>

<objective>
Test this target flow:

YouTube channel
Email/newsletter
RSS/web publication
alert/webhook
        ↓
Activepieces
        ↓
source metadata + artifact
        ↓
Karakeep and/or deterministic research inbox
        ↓
existing transcription/extraction system where applicable
        ↓
IPOS research_event candidate

No investment scoring occurs here.
</objective>

<research>
Verify:
- current license
- community/self-host limitations
- Windows/Docker compatibility
- local deployment
- Gmail connector
- IMAP alternative
- RSS
- webhook
- HTTP
- filesystem/data outputs
- scheduling
- retries
- idempotency
- deduplication
- secrets
- logging
- backup/export
- flow portability
- failure notifications
- API/MCP characteristics
</research>

<alternatives>
Benchmark against:
- n8n
- Node-RED
- plain Python + Windows Task Scheduler
- PowerShell + Task Scheduler
- Huginn if still relevant

Do not compare feature counts alone.
</alternatives>

<poc>
Actually implement a disposable proof of concept.

Flow A — YouTube:
YouTube channel RSS/Atom
→ detect unseen video
→ structured metadata
→ hand off URL to transcription inbox or mock
→ create research_event fixture.

Flow B — email:
test mailbox/fixture
→ detect labelled research email
→ save metadata/body/attachment reference
→ research_event.

Flow C — RSS:
feed item
→ dedupe
→ Karakeep or local evidence-inbox entry
→ research_event.

Test:
- first event
- duplicate event
- malformed event
- source unavailable
- destination unavailable
- restart/retry
- secret not available
- rerun/idempotency

Do not commit credentials.
Use fixtures where live credentials are unavailable.
</poc>

<mcda>
determinism/resilience 20
IPOS fit 20
local/free 15
connector maturity 10
observability 10
failure recovery 10
operator simplicity 10
portability 5
</mcda>

<deliverables>
1. ACTIVEPIECES_RESEARCH.md
2. ALTERNATIVES_MCDA.md
3. POC_RUNBOOK.md
4. POC_RESULTS.md
5. FLOW_EXPORTS/ if legally/technically exportable
6. ADOPTION_DECISION.md

ADOPTION_DECISION must explicitly say one of:
- ADOPT_SIDE_CAR
- STAY_TASK_SCHEDULER_ONLY
- ADOPT_N8N_INSTEAD
- ADOPT_NODE_RED_INSTEAD
- OTHER

If ADOPT_SIDE_CAR:
state which existing IPOS architecture decision must be amended and why.
</deliverables>
