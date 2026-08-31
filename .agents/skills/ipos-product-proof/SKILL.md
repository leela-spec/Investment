---
name: ipos-product-proof
description: Proves that an IPOS integration with a named external product or library is real rather than a local facade. Use for OpenBB, Wealthfolio, Riskfolio-Lib, TA-Lib, TradingView, Karakeep, Activepieces, Hermes, or any module whose success depends on a third-party product actually executing.
---

# IPOS Product Proof

Use this skill whenever the implementation target is a named external product/library.

## Goal

Prevent facade-completion: code, tests, or reports that mimic the target product without actually exercising it.

## Required control loop

### 1. Establish the target identity

Write a short `TARGET_PROOF.md` in the current module run directory before implementation:

```yaml
target_product: <exact product/library>
expected_version: <resolved current/pinned version>
official_interface_to_use: <package API | CLI | desktop import | REST | MCP | export>
proof_action: <one concrete operation only the real target can perform>
independent_oracle: <how correctness is checked independently>
facade_failure_example: <what would look plausible but not count>
```

### 2. Prove installation separately from use

Installation/import is only an installation proof. It is never functional completion.

Capture:
- installed package/app version;
- official command/API surface discovered at runtime;
- process/package path where useful.

### 3. Exercise the real interface

At least one pass-condition test must cross the actual target boundary.

Examples:
- Riskfolio-Lib: import `riskfolio` and invoke its portfolio/optimization API; capture solver/result diagnostics.
- Wealthfolio: run the actual desktop/local app, import a supported CSV, inspect/export resulting portfolio data, and use the real native MCP endpoint if MCP is claimed.
- OpenBB: call `openbb`/`obb` provider APIs and reconcile selected observations against authoritative provider values.
- TA-Lib: import and call native `talib` functions, then compare selected values with an independently sourced fixture.
- TradingView: use an actual TradingView CSV export or live alert receipt if claiming TradingView reconciliation/integration.

### 4. Build an independent oracle

The expected result must come from a path independent of the implementation output.

Acceptable oracles:
- official upstream source value;
- manually fixed golden fixture derived from documented source material;
- real target-system export after import;
- mathematically independent calculation when it does not reuse the same implementation path;
- operator-provided real-world expected result.

Forbidden oracle patterns:

```python
expected = actual.copy()
expected = implementation_under_test(...)
assert result["success"] is True  # when implementation itself sets success
```

### 5. Add a facade-detection test

Ask: "Could a developer delete the named dependency/product and still make these tests pass?"

If YES, the test suite does not prove the integration.

Where practical, add one of:
- monkeypatch/import denial showing the wrapper fails when the actual dependency is unavailable;
- runtime inspection that proves calls cross into the named dependency;
- real process/API receipt;
- product export generated only by the target system.

### 6. Verify pass conditions one by one

Produce a matrix:

| Pass condition | Real proof | Independent oracle | Verdict |
|---|---|---|---|

No row may cite only prose or an implementation-authored boolean flag.

### 7. Adversarial verification

Invoke the workspace `ipos-proof-verifier` custom agent in a fresh context or use Teamwork `development` integrity gates.

The verifier gets:
- current module authority;
- `TARGET_PROOF.md`;
- module diff;
- raw command/runtime receipts;
- tests;
- official sources.

Do not prime the verifier with "implementation passed". Ask it to falsify the claim.

## Hard stop

If the real target cannot be invoked through a supported interface, classify the module `BLOCKED` or `FAIL`. Never replace it with a home-grown equivalent unless the operator explicitly changes the architecture.
