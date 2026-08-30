# Antigravity Handover — Execute M10–M14 Bootstrap Slice

Status: `READY_FOR_ANTIGRAVITY`
Date: `2026-08-30`
Repository: `leela-spec/Investment`
Required branch: `ipos-modular-rebuild-2026-08-28`

## 1. Mission

Execute only the bounded implementation slice `M10 → M11 → M12 → M13 → M14` from the modular IPOS rebuild.

This is intentionally allowed before M01–M09 because these modules primarily establish local deterministic market data, portfolio normalization, portfolio visualization, optimization, and technical computation. Do **not** broaden the task into messaging, Hermes integration, Karakeep, Activepieces, TradingView webhooks, or weekly orchestration.

The authoritative exception contract is:

`05_blueprint/research/2026-08-28-modular-rebuild/implementation-plans/05_ANTIGRAVITY_M10_M14_SLICE.yaml`

## 2. Why this slice can run now

- `M11` has no dependency.
- `M12` and `M13` depend only on `M11`.
- `M14` depends on `M10`.
- `M10` normally depends on `M01` only because its final step exposes a narrow data surface to Hermes. The local OpenBB data POC can run now; Hermes exposure is explicitly deferred.
- `M12P` is **not** part of this slice. IPOS policy integration waits until M10/M11/M14 are verified.

Do not reinterpret these waivers. Read `05_ANTIGRAVITY_M10_M14_SLICE.yaml` exactly.

## 3. Antigravity operating mode

Use Antigravity in **Planning Mode** for this task.

Preferred CLI launch:

```bash
agy --mode=plan
```

If using the Antigravity IDE/2.0 instead:

- use `Planning Mode`;
- set Artifact Review to `Request Review`;
- work in **Local Mode** on a checkout already on `ipos-modular-rebuild-2026-08-28`;
- do not let Antigravity create a different implementation branch/worktree for this run.

Rationale: this repository's execution contract requires one exact branch. Antigravity New Worktree Mode is useful in general for isolation, but a new Antigravity worktree would create/operate on another branch and would violate this slice's branch identity contract.

## 4. First prompt to Antigravity

Paste this as the initial task:

```text
Execute the IPOS M10–M14 bootstrap slice in this repository.

First verify that the workspace is leela-spec/Investment and the checked-out branch is exactly ipos-modular-rebuild-2026-08-28. Stop if either is wrong.

Use Planning Mode. Do not implement immediately.

Read, in this order, and treat them as authority:
1. @AGENTS.md
2. @05_blueprint/research/2026-08-28-modular-rebuild/implementation-plans/05_ANTIGRAVITY_M10_M14_SLICE.yaml
3. @05_blueprint/research/2026-08-28-modular-rebuild/implementation-plans/01_EXECUTOR_CONTRACT.yaml
4. @05_blueprint/research/2026-08-28-modular-rebuild/implementation-plans/03_REPORT_SCHEMAS.yaml
5. @05_blueprint/research/2026-08-28-modular-rebuild/implementation-plans/M10_OPENBB_ODP.yaml

Do not preload M11–M14 yet.

Before editing:
- inspect only the files explicitly required by M10;
- reopen every current official source marked verify_before_execution;
- use a research subagent if useful to independently check current install/version/platform gotchas;
- write the M10 preflight artifact required by the executor contract;
- produce an Antigravity implementation-plan artifact for M10 only;
- request review before making changes.

After approval, execute M10 using the exact implementation loop in 01_EXECUTOR_CONTRACT.yaml.

M10 special rule: implement/test the local OpenBB data POC but defer M10-S06 Hermes API/MCP exposure. The verifier may issue PASS_WITH_LIMITATIONS if the only limitation is that deliberate Hermes deferral.

After implementation, use a fresh verifier subagent/context that is explicitly forbidden to modify files. It must inspect the diff and receipts, rerun safe acceptance tests, and write VERIFICATION_REPORT.md.

Only if M10 is PASS or PASS_WITH_LIMITATIONS with a non-blocking limitation from the slice contract, checkpoint/reset the primary context and load M11. Repeat the same module-isolated process for M11, then M12, M13, and M14.

Do not execute M12P or any other module.
Do not merge to main.
Do not execute broker trades.
Do not add frameworks, databases, UIs, queues, or services not required by the module plan.
Do not guess broker schemas.
Do not mark tests passed without command/output evidence.

At the end, write the slice-level reports required by 05_ANTIGRAVITY_M10_M14_SLICE.yaml and stop.
```

## 5. Required module order

### M10 — OpenBB ODP local/free data POC

Read only when M10 starts:

`@05_blueprint/research/2026-08-28-modular-rebuild/implementation-plans/M10_OPENBB_ODP.yaml`

Key interpretation:

- local Python/data POC is authorized now;
- Hermes MCP/API exposure is deferred;
- paid OpenBB Workspace is forbidden;
- test representative free data;
- compare OpenBB values with upstream authoritative provider values;
- **reject OpenBB cleanly** if direct official-provider adapters are materially simpler for the actual small IPOS series set.

Do not defend OpenBB merely because it was selected as a candidate.

### M11 — Deterministic portfolio normalizer

Load only after M10 verification is complete and context has been compacted/reset:

`@05_blueprint/research/2026-08-28-modular-rebuild/implementation-plans/M11_PORTFOLIO_NORMALIZER.yaml`

Critical gate:

- search approved workspace/source locations for representative finanzen.net ZERO / Smartbroker exports;
- if none exist, do **not** infer their schemas from memory or the web;
- implement/test only the canonical schema, validation, reconciliation framework, deterministic CLI, and synthetic fixtures;
- mark the real broker adapter blocked/limited until a representative export is supplied.

Synthetic-fixture completion is allowed to unblock M12/M13 inside this slice, but the limitation must remain explicit.

### M12 — Wealthfolio local UI POC

Load only after M11 verifier verdict:

`@05_blueprint/research/2026-08-28-modular-rebuild/implementation-plans/M12_WEALTHFOLIO.yaml`

Rules:

- local/desktop app only;
- Connect remains disabled;
- import through officially supported surfaces;
- never write directly to Wealthfolio's internal DB;
- test backup/restore;
- test read-only MCP only if the installed current version officially supports it;
- fail the candidate if meaningful use would require reverse engineering or custom internal integration.

### M13 — Riskfolio-Lib deterministic optimizer

Load only after M12 verifier verdict:

`@05_blueprint/research/2026-08-28-modular-rebuild/implementation-plans/M13_RISKFOLIO.yaml`

Rules:

- isolated environment;
- pinned versions/solver settings;
- synthetic deterministic return/constraint fixtures first;
- wrapper must emit weights + solver/constraint diagnostics;
- no AI-generated arithmetic;
- infeasible constraints must fail explicitly;
- network-disabled execution must pass.

Do not implement Black-Litterman unless explicit views are supplied by deterministic upstream policy/fixture.

### M14 — TA-Lib deterministic technical engine

Load only after M13 verifier verdict:

`@05_blueprint/research/2026-08-28-modular-rebuild/implementation-plans/M14_TALIB_TECHNICAL_ENGINE.yaml`

Rules:

- narrow indicator set only: actually used MA/RSI/Stochastic/ATR/volume concepts;
- use official wheels/native installation guidance;
- fixed OHLCV fixture first;
- if M10 OpenBB passed, test integration with representative M10 OHLCV output;
- if OpenBB was rejected, M14 may still pass core computation with runtime data integration explicitly deferred;
- TradingView CSV is validation evidence only, never a runtime dependency.

## 6. Context-management contract for Antigravity

The primary Antigravity conversation is the orchestrator, not the place to accumulate every detail.

For each module:

1. Load only the shared authority files + current module.
2. Use exact `@file` references rather than repo-wide browsing.
3. Use a research subagent only for current official-source/version verification or a narrowly defined technical question.
4. Keep long command/test output in run artifacts; bring only compact receipts into context.
5. Before context becomes bloated, write/update `state.json`.
6. After verification, start a fresh/compacted context for the next module.
7. Never use conversational memory as implementation state.

Do not assign two writing subagents to the same checkout concurrently.

Subagents are preferred for:

- official-document freshness check;
- independent test/verification;
- narrow comparison questions.

Subagents are **not** preferred for concurrent implementation of M10–M14 because all modules share one checkout and have sequential dependencies.

## 7. Antigravity artifact policy

For every module, Antigravity should create/review its own implementation-plan artifact before mutation.

The Antigravity artifact is subordinate to the repository YAML plan. If Antigravity proposes a different product, architecture, data model, or scope, it must explain a concrete blocker against the authoritative module plan and stop for operator review rather than silently changing direction.

The plan artifact must state:

- exact files expected to change;
- packages/apps expected to install;
- exact tests to run;
- external state that will be mutated;
- rollback;
- secrets/data that must not be committed;
- known deferred steps from the slice contract.

## 8. Verification discipline

Google Antigravity guidance emphasizes local verification loops; apply that literally here.

For each module:

- tests should exist before or alongside consequential changes;
- run smoke tests;
- run positive acceptance tests;
- run at least one negative/failure test;
- run deterministic/reproducibility tests where applicable;
- rerun tests after integration;
- capture command/output evidence;
- independent verifier reruns safe tests from a fresh context.

The verifier is prohibited from editing implementation files.

Allowed verdicts:

- `PASS`
- `PASS_WITH_LIMITATIONS`
- `FAIL`

Do not translate `BLOCKED` into `PASS_WITH_LIMITATIONS` unless `05_ANTIGRAVITY_M10_M14_SLICE.yaml` explicitly authorizes the limitation.

## 9. Stop conditions

Stop immediately and write the required blocked artifact if any of the following occurs:

- wrong repo or branch;
- official documentation materially contradicts the module plan;
- installation would require undocumented reverse engineering;
- a real broker schema is needed but no representative export exists;
- a paid product becomes required where the approved architecture expects free/local operation;
- a secret would need to be committed;
- changes to main/production would be required;
- a module's acceptance tests fail after no more than two materially different remediation attempts;
- the task starts drifting into M01–M09, M12P, M15+, or M90.

## 10. Git discipline

Before each module commit:

```bash
git status
git diff --check
```

Inspect the actual diff.

Prefer one module per commit:

- `M10: ...`
- `M11: ...`
- `M12: ...`
- `M13: ...`
- `M14: ...`

Never commit:

- private broker statements;
- credentials/tokens;
- `.env` secrets;
- virtual environments;
- Wealthfolio application DB/state;
- downloaded caches/large market datasets unless explicitly approved as fixtures.

## 11. Slice completion report

At the end, write:

`implementation-runs/AGY-IPOS-M10-M14-BOOTSTRAP/SLICE_STATE.json`

and

`implementation-runs/AGY-IPOS-M10-M14-BOOTSTRAP/SLICE_REPORT.md`

The report must answer:

1. M10 verdict and whether OpenBB actually justified itself versus direct providers.
2. M11 verdict and whether real broker exports or only synthetic fixtures were tested.
3. M12 verdict and whether Wealthfolio materially improved portfolio UX without unsupported integration.
4. M13 verdict and reproducibility/constraint status.
5. M14 verdict and independent indicator reconciliation status.
6. Every deliberate limitation caused by skipping M01–M09.
7. Installed versions and recurring costs.
8. Exact commits created.
9. Exact rollback route for every installed component.
10. The next dependency-ready module, but **do not start it**.

## 12. Antigravity-specific research basis

This handover follows current Google Antigravity guidance checked 2026-08-30:

- Planning Mode is intended for complex multi-file/architectural tasks and presents a structured execution plan before writes.
- Artifact Review `Request Review` is Google's recommended review policy for planned changes.
- Antigravity CLI best practices recommend workspace rules (`AGENTS.md`/`GEMINI.md`), verification loops, and an explore → plan → execute flow.
- Antigravity automatically consults workspace `AGENTS.md`/`GEMINI.md` context.
- Subagents provide isolated context windows and are suitable for specialist research/review tasks.
- Project Local Mode works directly in an existing checkout; New Worktree Mode is normally useful for isolated concurrent agents, but is not used here because the repository contract requires the exact existing branch.

Official references:

- https://antigravity.google/docs/cli/modes/
- https://antigravity.google/docs/artifact-review/
- https://antigravity.google/docs/cli/best-practices/
- https://antigravity.google/docs/cli/subagents/
- https://antigravity.google/docs/projects/
- https://antigravity.google/docs/ide/rules/

## 13. Operator interaction expectation

Do not ask routine implementation questions already answered by authority files.

Ask only for a genuine human gate such as:

- supplying a missing representative broker export;
- approving an Antigravity implementation-plan artifact when Request Review is enabled;
- completing an unavoidable account/login action;
- resolving a documented architecture conflict.

Everything else should be executed autonomously inside the bounded module contract.
