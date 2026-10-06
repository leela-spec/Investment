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
Write a short `TARGET_PROOF.md` in the current module run directory before implementation.

### 2. Prove installation separately from use
Installation/import is only an installation proof. It is never functional completion.

### 3. Exercise the real interface
At least one pass-condition test must cross the actual target boundary.

### 4. Build an independent oracle
The expected result must come from a path independent of the implementation output.

### 5. Add a facade-detection test
Ask: "Could a developer delete the named dependency/product and still make these tests pass?"

### 6. Verify pass conditions one by one
Produce a matrix of Pass condition | Real proof | Independent oracle | Verdict.

### 7. Adversarial verification
Falsify claims.
