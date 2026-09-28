# Repository-Backed Orchestration Design

**Status:** Approved by the operator; linked for orchestration bootstrap
**Date:** 2026-09-28
**Scope:** Investment Process OS (IPOS) planning and execution coordination

This control-layer specification does not replace the product plan. The canonical process, value
map, RI-01–RI-07 sequence, source fixtures, and architecture corrections remain in
[`HANDOVER_RESEARCH_INTAKE_BOOTSTRAP.md`](../../../HANDOVER_RESEARCH_INTAKE_BOOTSTRAP.md). The
authoritative behavioral requirements remain in the existing
[`IPOS user stories`](../../../05_blueprint/research/2026-08-28-modular-rebuild/08_USER_STORIES_AND_INTEGRATION_WORKFLOWS.md).
The current machine-readable entrypoint is [`orchestration/state.yaml`](../../../orchestration/state.yaml),
which names the single active work packet and its bounded authority references.

## 1. Purpose

Create a product-first orchestration model in which chats are disposable execution surfaces and the
repository preserves all durable context. The model must let a new agent continue without relying on
conversation memory while avoiding duplicate plans, activity-log sprawl, speculative infrastructure,
and isolated features that do not compose into practitioner value.

The primary product outcome is an evidence-linked investment decision queue that answers:

1. What new information arrived?
2. What did the source actually claim?
3. Which holding, thesis, risk factor, or scenario might it affect?
4. Is the result `NO_IMPACT`, `WATCH`, `REVIEW`, or `HIGH_PRIORITY_REVIEW`?

Research custody, transcription, automation, messaging, and project management are supporting
capabilities. They are not substitutes for this outcome. No automated broker execution is authorized.

## 2. Authority Model

| Surface | Canonical responsibility | Explicit exclusion |
|---|---|---|
| Repository | Product intent, contracts, decisions, work packets, implementation state, evidence, and continuation context | Conversational transcripts and duplicated historical explanations |
| OpenProject | Human-facing ownership, priority, status, dependency, and links to canonical repository records | Architecture, schemas, complete handovers, or independent technical truth |
| Orchestration chat | Select the next valuable outcome, create bounded packets, manage gates and dependencies, and review evidence | Product implementation and permanent memory |
| Execution chat | Deliver one bounded, independently verifiable outcome | Program redesign, unrelated cleanup, and silent shared-contract changes |

The repository is authoritative. OpenProject is a thin management projection. When the two disagree,
the repository record wins and the OpenProject projection is corrected.

## 3. Minimal Control Surfaces

The target structure is deliberately small:

```text
PROJECT_STATE.md
orchestration/
|-- state.yaml
`-- work/
    `-- RI-02A.yaml
```

### `PROJECT_STATE.md`

The short human restart page. It identifies the current product-value target, active phase, next gate,
and links to the machine-readable state. It does not reproduce detailed work packets or evidence.

### `orchestration/state.yaml`

The canonical machine-readable program index. It records the active phase, active packet, ready and
blocked packets, dependency edges, completed evidence references, relevant OpenProject identifiers,
and exact paths to authoritative contracts. It references information rather than copying it.

### `orchestration/work/RI-02A.yaml` and subsequent packet files

One bounded execution contract, updated in place with its result. A packet contains:

- practitioner value and observable output;
- required inputs and exact authority references;
- dependencies and readiness conditions;
- permitted paths and explicitly forbidden scope;
- minimum acceptance evidence and stop conditions;
- concise result, artifacts, deviations, and next action.

Existing plans remain authoritative where still valid. The orchestrator resolves conflicts before
dispatch and gives an executor only the packet plus explicitly cited source sections.

## 4. Work-Packet Schema

The initial logical schema is:

```yaml
id: RI-02A
status: ready
product_value: Preserve a real research source for a later investment decision.
practitioner_output: Searchable evidence with verified source identity and timestamps.

inputs:
  - path: implementation-runs/E05/20260923-230911/
    purpose: Proven real-media fixture
  - path: 05_blueprint/research/2026-08-28-modular-rebuild/implementation-plans/M07_KARAKEEP.yaml
    purpose: Applicable custody contract

output:
  - One retained source object
  - One immutable IPOS evidence event
  - Proof that repeated synchronization creates no duplicate

dependencies:
  - Live Karakeep API identity established

allowed_paths:
  - ipos/etl/karakeep.py
  - tests/test_karakeep.py
  - orchestration/work/RI-02A.yaml

forbidden_scope:
  - Activepieces configuration
  - Telegram implementation
  - Portfolio arithmetic
  - New orchestration frameworks
  - Unrelated refactoring

acceptance:
  - Real source identifier recorded
  - Source hash preserved
  - Second synchronization is a no-op
  - Service outage preserves prior evidence and fails visibly

stop_when:
  - Live API contradicts the approved contract
  - A required credential is unavailable
  - A shared contract would need to change

result:
  state: pending
  artifacts: []
  evidence: []
  deviations: []
  next_action: null
```

Exact field validation belongs to the later implementation plan. The design requirement is a compact,
human-readable, machine-readable record—not a new workflow platform.

## 5. Orchestration Flow

1. The orchestrator reads `PROJECT_STATE.md`, `orchestration/state.yaml`, and only the authorities
   needed to resolve the next dependency gate.
2. It selects the smallest vertical outcome that creates observable practitioner value.
3. It creates or activates one bounded packet with explicit scope, acceptance, and stop conditions.
4. An executor reads that packet and only its explicit authority references.
5. The executor updates the packet at meaningful checkpoints and returns either verified evidence or
   a structured escalation.
6. The orchestrator compares actual evidence with the packet contract, updates canonical state, and
   only then releases downstream work.
7. OpenProject receives a concise projection: packet ID, outcome-oriented title, owner, status,
   dependency, practitioner-value sentence, and repository/evidence links.

The first vertical slice reuses the committed IMF E05 fixture and proves source custody through
evidence normalization and practitioner review output. The Markus Koch fixture is the second media
case for German-language semantic and numerical-preservation behavior. Live email follows after
custody and idempotency are proven, reducing simultaneous authentication, privacy, filtering, and
schema variables.

## 6. Continuity and Checkpoints

Durable state is written when:

- work starts (`ready` to `active`), including the base commit and exact scope;
- an observable artifact or live identifier is produced;
- observed reality contradicts the approved packet;
- acceptance completes (`active` to `complete`); or
- a successor requires a concrete continuation instruction.

The repository must not contain internal reasoning, routine progress narration, copied conversation,
repeated plan text, speculative improvements, or exhaustive command logs. Preserve decisions, facts,
evidence, deviations, and next actions—not the full process that generated them.

At a valid checkpoint, a successor needs only:

1. `PROJECT_STATE.md`;
2. `orchestration/state.yaml`;
3. the single active packet; and
4. authority sections explicitly referenced by that packet.

## 7. Product-First and Drift Guards

Before dispatch, the orchestrator must answer:

1. What can the investment practitioner do afterward that they cannot do now?
2. Which observable output demonstrates that value?
3. What is the smallest vertical change that produces it?
4. Which existing component, contract, plan, or fixture is reused?
5. What is intentionally excluded?
6. What evidence is sufficient, and when must work stop?

Mandatory execution constraints:

- No new file unless the packet requires it.
- No new framework for a problem already handled by the repository.
- No broad rewrite where a surgical edit is sufficient.
- No changing historical facts to make documentation appear consistent.
- No silent shared-schema adaptation.
- No opportunistic refactoring or unrelated cleanup.
- No testing expansion beyond product acceptance or a material regression risk.
- Stop when acceptance passes; additional hardening requires a separately justified packet.
- Preserve zero LLM arithmetic: code computes numeric outputs and LLMs only classify or narrate.
- Keep core Python and DuckDB native on Windows NTFS; supporting containers remain on WSL2 ext4.
- Keep Wealthfolio desktop/manual and broker execution human-controlled.

Infrastructure work is permitted only when it is the minimum dependency for the current vertical
product output. Tests are evidence, not the product.

## 8. Reality Mismatch and Escalation

An executor does not improvise when live reality contradicts a packet. It changes the packet state to
`blocked` and records:

- expected behavior;
- observed behavior with stable evidence;
- affected contract and downstream packets;
- two or three bounded alternatives;
- its recommendation and risk assessment.

The orchestrator resolves the conflict and updates canonical contracts before execution resumes.
Credentials, source mandates, structural OpenProject writes, production enablement, and architecture
changes remain operator-gated.

## 9. Acceptance Evidence

Completion requires a fixed evidence packet containing:

- actual input identity;
- changed files or live configuration scope;
- output artifact paths and stable identifiers or hashes;
- proportionate automated test results;
- at least one relevant failure or degraded-mode result;
- comparison of intended and observed behavior;
- remaining limitations and the next justified action.

A demonstration, narrative summary, or green unit test suite alone is insufficient for a live
integration. Conversely, unrelated verification and generalized infrastructure are not required.

## 10. OpenProject Projection

The appropriate destination is a dedicated private top-level `Investment / IPOS` project, separate
from unrelated projects. A projected work package contains only:

- packet ID and outcome-oriented title;
- owner, status, priority, and dependencies;
- one practitioner-value sentence;
- link to the canonical repository packet;
- link to final evidence when complete.

OpenProject descriptions do not duplicate architecture or handovers. Repository-to-OpenProject is a
one-way projection for management visibility. Project creation and subsequent work-package writes
remain subject to the OpenProject skill's preview, explicit confirmation, and reread gates.

## 11. Orchestration Lifetime

An orchestration chat persists only through a coherent phase. Every accepted decision and result is
externalized as it occurs. At a major phase gate—or when context becomes noisy—a successor chat starts
from the canonical repository checkpoint. No chat is treated as permanent memory.

For the initial phase, the scope is Research Intake RI-01 through RI-07. Broader portfolio automation
or later operational phases receive a successor orchestration context after this phase is accepted.

## 12. Approved Design Decisions

The operator approved the following choices:

1. Orchestrator as control plane only.
2. Repository authority with a thin OpenProject delivery projection.
3. Repository-backed bounded context for every agent.
4. One independently verifiable outcome per handover.
5. Orchestrator-owned versioned integration contracts.
6. Thin vertical slices before broad subsystem completion.
7. Existing real video fixture as the first slice.
8. Fixture proof followed by one live sample per source class.
9. Operator gates for mandate, credentials, structural writes, and production acceptance.
10. Fixed evidence packets for completion.
11. Structured escalation instead of local contract improvisation.
12. Dedicated top-level `Investment / IPOS` OpenProject project.
13. Phase-bounded orchestration chats with durable checkpoints.
14. Standard completion and escalation returns.
15. Baseline control contract and first source mandate before implementation dispatch.
16. Evidence-linked investment decision queue as the governing practitioner value.

## 13. Design Completion Criteria

This design is ready for implementation planning when the operator confirms that:

- the authority split prevents duplicate truth;
- the work-packet schema contains sufficient continuation context;
- product-first and drift guards are strict enough;
- OpenProject remains a thin projection; and
- the initial vertical-slice direction is correct.
