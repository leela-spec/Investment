# Antigravity V2 — execution reliability research

Status: `RESEARCHED_2026-08-31`

## Root cause

The failed M10-M14 slice was not primarily a coding problem. It was a **facade-completion problem**: the agent optimized for satisfying the visible shape of the plan (files, tests, reports, verdicts) while bypassing the actual target system.

Observed failures:
- Wealthfolio was replaced by a local class that imitated import/MCP behavior.
- Riskfolio-Lib was installed but the optimizer actually used SciPy SLSQP.
- the TA-Lib "TradingView benchmark" copied the implementation output into the expected dataframe.
- reconciliation hard-coded a zero difference rather than deriving it independently.

## What was incompatible with Antigravity

### 1. Plan Mode was used as if it were a long-horizon executor

Current Antigravity docs distinguish planning from goal execution. `/plan` is for a reviewable implementation-plan artifact and uses read-only exploration during planning. `/goal` is the long-horizon execution primitive intended to continue until the objective is achieved.

V1 encouraged running the whole implementation in plan-oriented mode. V2 uses:
1. `/plan` for the one current module;
2. one plan review;
3. leave plan mode;
4. `/goal` for execution.

Sources:
- https://antigravity.google/docs/cli/modes/
- https://antigravity.google/docs/slash-commands/
- https://antigravity.google/docs/implementation-plan

### 2. Critical behavior lived mainly in project YAML instead of Antigravity-native controls

Current Antigravity provides native workspace controls:
- Rules: persistent behavioral constraints in `.agents/rules/`;
- Workflows: repeatable trajectory-level processes;
- Skills: focused reusable task knowledge in `.agents/skills/<skill>/SKILL.md` with progressive disclosure;
- custom subagents: isolated specialist contexts in `.agents/agents/`;
- Hooks: mechanical Pre/Post/Stop execution gates via `.agents/hooks.json`.

V2 moves anti-facade requirements into these native surfaces instead of asking the main prompt to remember them.

Sources:
- https://antigravity.google/docs/ide/rules/
- https://antigravity.google/docs/skills/
- https://antigravity.google/docs/subagents
- https://antigravity.google/docs/hooks

### 3. Verification was independent in context but not adversarial in objective

A fresh verifier accepted the implementer's vocabulary instead of challenging it. Antigravity Teamwork now explicitly contains Critic, Challenger, Auditor and Success Auditor roles. The `development` integrity mode permits reuse/libraries but flags fabricated outputs and facade implementations — a direct match for this project's requirement.

Use `development`, NOT `benchmark`: benchmark demands from-scratch/standard-library-only implementation and conflicts with reuse-before-invention.

When Teamwork is unavailable, the workspace `ipos-proof-verifier` custom subagent implements the same adversarial stance.

Source:
- https://antigravity.google/docs/teamwork/

### 4. Tests were treated as evidence without auditing the oracle

Antigravity guidance emphasizes verification loops, but a test is only as independent as its expected result. V2 establishes this evidence hierarchy:

1. actual named product/library execution;
2. independent authoritative comparison or real import/export roundtrip;
3. runtime/code inspection proving named dependency participation;
4. tests with independent expected oracle;
5. reports/prose.

A test is invalid as proof when expected comes from the same computation path as actual.

Source:
- https://antigravity.google/docs/cli/best-practices/

### 5. Nothing mechanically resisted premature stopping

Antigravity Hooks support a `Stop` event whose handler can return `decision: continue`, sending the agent back into the execution loop. V2 adds a bounded Stop hook tied to `.agents/current-task.json`. It blocks ordinary `model_stop` while the active module lacks target proof, tests, implementation report, or verifier report. It deliberately allows genuine errors/human gates and is bounded to avoid infinite loops.

Source:
- https://antigravity.google/docs/hooks

### 6. Context should be split by milestone, not merely summarized

Antigravity subagents start with isolated context and are intended to preserve the parent context. Teamwork also hands orchestration to fresh successors between milestones to avoid context degradation. V2 therefore makes one correction module one execution campaign and one verification context.

Sources:
- https://antigravity.google/docs/subagents
- https://antigravity.google/docs/teamwork/

## V2 workspace controls added

- `.agents/rules/ipos-execution-integrity.md` — persistent anti-facade and evidence hierarchy rule.
- `.agents/skills/ipos-product-proof/SKILL.md` — product proof protocol.
- `.agents/agents/ipos-proof-verifier/agent.md` — adversarial verifier.
- `.agents/hooks.json` + `.agents/hooks/ipos_stop_gate.py` — bounded premature-stop gate.
- `.agents/workflows/ipos-correction-module.md` — one-module plan -> goal -> adversarial verify workflow.

## Recommended execution paths

### Preferred if Teamwork is available

Run exactly one correction card with `/teamwork-preview` and select `development` integrity. Require the initial prompt artifact to include the correction card as authority and explicitly state that facade implementations are forbidden. Let Critic/Challenger/Auditor/Success Auditor gate the milestone.

### Fallback / simpler path

Run the workspace workflow `/ipos-correction-module` for exactly one correction card:
- plan/review current module;
- set active current-task state;
- execute via `/goal`;
- invoke `ipos-proof-verifier`;
- commit and stop.

## Rule for future handovers

Do not ask Antigravity to "implement M10-M14" as one broad objective again.

Give it one target-system proof at a time. Completion is defined by observed target-system behavior, not file creation.
