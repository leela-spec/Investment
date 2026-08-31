---
alwaysApply: true
description: IPOS execution integrity, anti-facade verification, and definition of done rules.
---

# IPOS execution integrity rule

Activation: ALWAYS ON for this workspace.

## Scope lock

- Repository authority: `leela-spec/Investment`.
- Work only on the operator-selected branch. Never silently switch to `main`.
- One implementation module at a time.
- Do not load or implement future modules unless the current module explicitly depends on one output contract.
- Existing architecture and module authority files outrank implementation convenience.

## Reuse-before-invention invariant

When a module names an external product/library as the implementation target, the named target MUST actually execute.

Examples:
- `Riskfolio-Lib` means code imports and invokes Riskfolio-Lib APIs. Installing Riskfolio-Lib and writing a SciPy substitute is a FAILURE.
- `Wealthfolio POC` means the actual Wealthfolio application/import/export/MCP surface is exercised. A local Python class that imitates Wealthfolio is a FAILURE.
- `TradingView benchmark` means independently exported/observed TradingView values. Copying the implementation output into a variable called `tv_benchmark` is a FAILURE.
- `reconciliation` means independently derived source totals are compared with computed totals. Hard-coding a zero difference is a FAILURE.

Never create a facade, mock, local substitute, invented API, or conceptual equivalent and call the named external product implemented.

## Evidence hierarchy

A completion claim is valid only when supported by the strongest applicable evidence:

1. Actual external product/library execution.
2. Independent authoritative comparison or real import/export round trip.
3. Runtime/code inspection proving the named dependency is invoked.
4. Tests whose expected oracle is independent of implementation output.
5. Reports/documentation.

Reports are never proof by themselves.

A test is INVALID as verification when:
- expected values are copied from the actual values being tested;
- both actual and expected use the same helper/function/library path;
- the test only checks a hard-coded status flag produced by the implementation;
- a fake local API is tested instead of the named upstream product;
- the test asserts metadata such as `is_network_disabled=True` without independently constraining/observing network behavior when that distinction matters.

## Definition of done

Before marking a module PASS, prove every module pass condition individually with an evidence path.

For every required implementation step classify exactly one:
- `DONE_PROVEN`
- `DEFERRED_BY_APPROVED_WAIVER`
- `BLOCKED_HUMAN_GATE`
- `FAILED`

Never mark a step completed merely because scaffolding or a substitute exists.

## Verification separation

The implementation agent may run development tests but may not authoritatively PASS itself.

Final verification must be performed by either:
- the `ipos-proof-verifier` custom agent in a fresh context; or
- Antigravity Teamwork Critic/Challenger/Auditor/Success Auditor gates in `development` integrity mode.

The verifier must actively try to disprove completion and inspect whether the named external product actually participated.

A verifier must not fix implementation defects while verifying.

## Anti-drift behavior

If the approved target cannot be implemented through a documented supported interface:
1. STOP that module.
2. Write exact blocker evidence.
3. State what supported interface is missing.
4. Propose alternatives separately.
5. Do NOT silently implement an alternative.

Do not add new databases, orchestration frameworks, UIs, vector stores, queues, graph stores, or abstraction layers unless the current module authority explicitly requires them.

## User questions

Do not ask routine implementation questions. Ask only for genuine human gates such as:
- missing real broker/source file;
- login/credential/license action;
- destructive or externally consequential action;
- architecture decision required because official interface is unavailable.

## Commit discipline

- One module per commit where practical.
- Commit only after verifier verdict is recorded.
- Never commit secrets, private broker statements, virtual environments, caches, or product databases.
- A PASS commit must contain real implementation evidence, not only reports/tests.
