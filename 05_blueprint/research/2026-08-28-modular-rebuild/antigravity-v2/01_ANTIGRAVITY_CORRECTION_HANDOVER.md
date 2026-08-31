# Antigravity V2 — IPOS correction handover

Status: `READY_FOR_OPERATOR_EXECUTION`
Branch: `ipos-modular-rebuild-2026-08-28`

## Purpose

Repair the failed M10-M14 bootstrap slice without repeating the facade-completion failure pattern.

Do NOT execute the whole correction set in one campaign.

Each correction is one independent Antigravity campaign with one plan artifact, one implementation context, one adversarial verifier context, one commit, then STOP.

## Native controls already installed in this workspace

Antigravity should discover/use:
- `.agents/rules/ipos-execution-integrity.md`
- `.agents/skills/ipos-product-proof/SKILL.md`
- `.agents/agents/ipos-proof-verifier/agent.md`
- `.agents/hooks.json`
- `.agents/workflows/ipos-correction-module.md`

Operator setup check in Antigravity IDE:
1. Open Customizations -> Rules and ensure `ipos-execution-integrity` is activated `Always On` for the workspace.
2. Open `/hooks` and confirm `ipos-module-stop-gate` is loaded/enabled.
3. Open `/agents` and confirm `ipos-proof-verifier` is discoverable.
4. Confirm the repo is checked out on `ipos-modular-rebuild-2026-08-28`.

Do not proceed if these controls are not visible.

## Correction dependency order

```text
C11 normalizer -----> C13 Riskfolio
       |
       +------------> C12 Wealthfolio

C10 OpenBB ---------> C14 TA-Lib validation/integration
```

Recommended order:
1. `C11_NORMALIZER_CORRECTION.yaml`
2. `C13_RISKFOLIO_CORRECTION.yaml`
3. `C12_WEALTHFOLIO_CORRECTION.yaml`
4. `C10_OPENBB_CORRECTION.yaml`
5. `C14_TALIB_CORRECTION.yaml`

Reason: C11 and C13 contain the most consequential false-positive implementations and should be repaired before portfolio UX work.

## Preferred execution method — Teamwork if available

Antigravity's Teamwork `development` integrity mode is especially appropriate because it allows external libraries/pre-built systems while explicitly auditing fabricated output and facade implementations.

Start a fresh conversation for ONE correction only:

```text
/teamwork-preview Repair exactly one IPOS module using the correction authority at @05_blueprint/research/2026-08-28-modular-rebuild/antigravity-v2/C11_NORMALIZER_CORRECTION.yaml.

Repository: leela-spec/Investment
Required branch: ipos-modular-rebuild-2026-08-28

Read @AGENTS.md, @.agents/rules/ipos-execution-integrity.md, @.agents/skills/ipos-product-proof/SKILL.md, the correction card, and the original M11 module plan. Do not load future correction cards.

Use DEVELOPMENT integrity mode. Code reuse and proven external libraries are desired. Facade implementations, fake local substitutes, fabricated outputs, self-referential test oracles, and reports presented as proof are forbidden.

Before implementation the prompt/plan artifact must explicitly state:
1. the exact named target or deterministic behavior being proven;
2. the real interface/action that constitutes proof;
3. an independent oracle;
4. an example of a facade implementation that would NOT count;
5. all human gates;
6. pass conditions and negative/anti-facade tests.

After I approve the prompt artifact, execute autonomously through real implementation and all Teamwork Critic, Challenger, Auditor, and Success Auditor gates. Do not start another correction module. Commit only after the current correction has an accepted verifier verdict, then stop.
```

During Teamwork's integrity interview choose/insist on:
- `development` integrity;
- libraries/pre-built products are allowed and preferred;
- fabricated outputs are forbidden;
- facade implementations are forbidden;
- mock-only proof is insufficient when a real target product is available.

Do NOT choose benchmark mode because it conflicts with reuse-before-invention.

## Fallback execution method — normal Antigravity

Use a fresh Antigravity conversation for one correction card.

### Phase A — plan

Invoke the workspace workflow if available:

```text
/ipos-correction-module @05_blueprint/research/2026-08-28-modular-rebuild/antigravity-v2/C11_NORMALIZER_CORRECTION.yaml
```

If the workflow is not auto-discovered, use this prompt in normal mode and explicitly ask for `/plan`:

```text
Plan ONLY correction C11 from @05_blueprint/research/2026-08-28-modular-rebuild/antigravity-v2/C11_NORMALIZER_CORRECTION.yaml.
Follow @AGENTS.md, @.agents/rules/ipos-execution-integrity.md and @.agents/skills/ipos-product-proof/SKILL.md.
Do not implement yet.
The plan must define the real proof action, independent oracle, facade failure example, negative test, pass conditions and human gates.
```

Review the plan artifact once.

### Phase B — execute

After approving the plan, LEAVE plan mode and use `/goal`:

```text
/goal Execute the approved C11 correction completely. Use the approved plan and correction card as authority. Create TARGET_PROOF.md before code mutation. Continue until real implementation evidence exists and the independent ipos-proof-verifier has issued a verdict. A test/report alone is not completion. Do not begin any other correction module.
```

Do NOT launch the whole session with `agy --mode=plan` and expect implementation.

## Completion proof required for every correction

Every correction run must contain:
- `TARGET_PROOF.md`
- before/preflight evidence
- raw command/runtime receipts
- tests with independent oracle
- one anti-facade/negative test
- `IMPLEMENTATION_REPORT.md`
- fresh `VERIFICATION_REPORT.md`

The verifier must answer this exact question:

> If I removed the named external dependency/product, could this implementation and its acceptance tests still appear to pass?

If YES, the correction is not complete.

## Correction-specific ground truth

### C11 — Normalizer

Do not accept:
- hard-coded `reconciliation_difference = 0`;
- transaction gross values summed without sign semantics;
- expected balances generated by `PortfolioNormalizer` itself.

Must prove:
- fixed independent source ledger;
- correct buy/sell/dividend/fee/tax cash direction;
- deliberate mismatch yields non-zero/failed reconciliation;
- truthful real-broker coverage state.

### C13 — Riskfolio

Do not accept:
- SciPy optimizer described as "Riskfolio concepts";
- merely installing Riskfolio-Lib;
- decorative `rm/model` parameters.

Must prove:
- runtime imports/calls Riskfolio-Lib;
- actual MV MinRisk + risk-budget/parity + CVaR pathways;
- denying Riskfolio makes wrapper fail rather than silently use a substitute.

### C12 — Wealthfolio

Do not accept:
- local Python `WealthfolioAdapter` as product proof;
- invented MCP methods;
- tests that never run Wealthfolio itself.

Must prove:
- actual local Wealthfolio app run;
- actual supported CSV import;
- actual displayed/exported holdings reconcile with C11 expected values;
- real native MCP only if it is genuinely enabled/tested.

If Antigravity cannot complete desktop interaction, it must ask for the smallest human action and stop — not fake it.

### C10 — OpenBB

Keep real OpenBB code. Correct:
- missing T10Y3M;
- missing non-US macro series;
- unsupported generic metadata claims;
- insufficient cross-provider independent validation.

### C14 — TA-Lib

Keep direct TA-Lib runtime calls. Reject:
- `expected = actual.copy()`;
- any fake TradingView benchmark.

Must prove:
- M10 -> M14 real OHLCV seam;
- independent indicator oracle;
- actual TradingView CSV if claiming TradingView reconciliation.

If no TradingView CSV is available, explicitly request it or downgrade that one proof; never synthesize a fake TV benchmark.

## When to ask the operator

Only ask for:
- representative real broker exports;
- actual TradingView CSV export;
- Wealthfolio desktop interaction/login if Antigravity cannot perform it;
- unavoidable credential/license action;
- a real architecture decision after a supported interface proves unavailable.

Everything else should be handled autonomously.

## Final state after all corrections

Do not recreate a slice-level `COMPLETED` verdict until all five corrected module verdicts are independently re-audited.

Expected target state:

```text
C11  PASS or PASS_WITH_LIMITATIONS(real broker exports only)
C13  PASS
C12  PASS or approved MCP-only limitation
C10  PASS or narrow documented data-source limitation
C14  PASS or TradingView-export human-gate limitation
```

Only then update the bootstrap slice state and dependency readiness.
