# Validation scope

Executed in this conversation's Linux container, not on the operator's Windows/WSL host.

- Python: 3.13.5. pandas: 2.2.3.
- Both baseline source files were reconstructed from GitHub connector text and their complete bytes matched the returned Git blob IDs.
- `git apply --check --whitespace=error-all` passed on that two-file baseline.
- Patched Python and the new test file compiled.
- The 22 delivered regression cases were executed with their test bodies unchanged, except imports were bound to isolated source modules. The module AST retained every function body and constant; only imports of unavailable `duckdb` and `ipos.config.load` were excluded. `REPO_ROOT` was a temporary empty directory. Real pandas, pytest and Python arithmetic were used.
- FX lookup was explicitly stubbed by the relevant delivered tests. There was no SQL/real DuckDB, broker, model, GUI or network integration test.
- Original: 18 failures, 4 passes. Patched: 22 passes. `before.xml` and `after.xml` preserve the actual JUnit results. `result.json` contains extracted counts.
- Full-repository tests and native-host acceptance remain required. These results do not establish correctness of the unseen modern normalizer/optimizer or a sub-15-second production SLA.

Baseline Git blobs:

```text
ipos/etl/portfolio_csv.py 1ceec565aa070d9a03a5c49cdeaff12c204110e8
ipos/aggregate/portfolio.py f294f551281e36536250486416c8b24a157c1e07
```

Run the included normal regression file through the real project's pytest after applying the patch, as specified in artifact 04. No substitute runtime package or fake external product is included in the delivery.
