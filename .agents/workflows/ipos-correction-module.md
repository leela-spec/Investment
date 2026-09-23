# IPOS Correction Module

Description: Execute exactly one IPOS correction module with real-product proof, adversarial verification, and no facade substitutions.

## Step 1 — Scope

Require one correction card path such as:
`05_blueprint/research/2026-08-28-modular-rebuild/antigravity-v2/C13_RISKFOLIO_CORRECTION.yaml`

Confirm:
- repository `leela-spec/Investment`;
- branch `ipos-modular-rebuild-2026-08-28`;
- only one correction module is active;
- prerequisites listed on the correction card are satisfied.

Do not read future correction cards.

## Step 2 — Activate project controls

Read:
- `AGENTS.md`;
- `.agents/rules/ipos-execution-integrity.md`;
- `.agents/skills/ipos-product-proof/SKILL.md`;
- the selected correction card;
- the original module authority it repairs;
- `implementation-plans/01_EXECUTOR_CONTRACT.yaml`;
- `implementation-plans/03_REPORT_SCHEMAS.yaml`.

Do not treat the previous implementation/verification verdict as truth.

## Step 3 — Plan only

Use `/plan` behavior to create a compact plan for the selected correction only.

The plan MUST identify before implementation:
- exact named external product/library;
- exact official interface that will be exercised;
- concrete real-product proof action;
- independent oracle;
- explicit facade implementation that would NOT count;
- human gates, if any;
- acceptance tests and anti-facade test.

Request artifact review. Do not implement until the plan is approved.

## Step 4 — Begin execution state

After plan approval, leave plan mode.

Create a fresh run directory and `TARGET_PROOF.md` using the `ipos-product-proof` skill.

Set `.agents/current-task.json`:
- `active: true`;
- `module_id: <correction id>`;
- `run_dir: <current run directory>`.

## Step 5 — Execute as a goal

Use `/goal` semantics: continue autonomously until the selected correction is either genuinely verified or reaches a real human/blocker gate.

Do not stop after scaffolding, tests, a report, or package installation.

Implementation order:
1. re-check official docs;
2. capture before state;
3. execute the smallest real target-system interaction first;
4. prove that interaction before writing wrappers around it;
5. implement only required glue;
6. run independent-oracle acceptance tests;
7. run negative/facade detection test;
8. run regression tests;
9. write implementation report.

## Step 6 — Adversarial verifier

Invoke `ipos-proof-verifier` as a fresh subagent/context.

Prompt it neutrally:
`Attempt to falsify completion of <correction id>. Do not trust prior verdicts. Verify named-product execution, independent test oracles, every required step, and every pass condition. Do not edit files.`

If Teamwork is available, use its Critic, Challenger, Auditor, and Success Auditor gates with `development` integrity mode instead of weakening verification.

A verifier FAIL is a real FAIL. The implementation agent may repair in the current module only, then must invoke a fresh verifier again.

## Step 7 — Finish safely

Only after verifier PASS or authorized PASS_WITH_LIMITATIONS:
- restore `.agents/current-task.json` to `active: false`;
- write final run state;
- inspect `git diff --check` and `git status`;
- commit the correction as one module-scoped commit;
- STOP.

Do not start another correction module automatically.

If BLOCKED_HUMAN_GATE:
- restore `active: false`;
- write the exact smallest operator action needed;
- STOP without substituting another architecture.
