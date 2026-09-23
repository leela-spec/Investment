# Reconciled decision matrix

**Status:** proposed, evidence-backed amendments to the accessible decision analysis; not remotely applied. The August-28 revised matrix is absent at `cec42be2aaf922c74ea6b13dc44fe11adfdd618f`, so its individual choices remain **UNRECONCILED**, not silently superseded. `Applied to` means the intended landing location; only the safety changes listed in artifact 05 are delivered as executable patches.

| Decision | Problem | Options | Evidence | Selected approach | Reason | Trade-off | Applied to |
|---|---|---|---|---|---|---|---|
| D1/D8: restore source alignment | Newer modules described but absent on main | Guess replacements; switch branches; reconcile exact references | [R0] [R1] | Reconcile local main and remote main; preserve both evidence histories | Prevents patching the wrong generation | Later integration certification blocked meanwhile | `05_blueprint/01_DECISION_ANALYSIS.md`; unseen rebuild matrix |
| D2: retain DuckDB, correct ownership | "Writer + read-only readers" interpreted across processes | Shared file; server migration; export boundary | [R1] [E1] | One host writer process; all outside consumers use artifacts | Resolves locking without new database infrastructure | Readers see committed batches, not live state | Decision D2; `ipos/run.py`; `ipos/export/snapshot.py` |
| D4: native host quantitative task | WSL/Docker/media/AI incorrectly become Saturday dependencies | Synchronous mega-flow; separate lanes | [R1] [R8] [E2] | Separate acquisition/transport; host consumes validated cached inputs | Preserves zero-container compute path | Freshness and queue state must be explicit | Decision D4; missing WF05/WF06/WF07 |
| D6: narrow AI authority | Claim suggestions can become portfolio instructions | Ban AI; unconstrained agent; candidate extraction | [R1] [R5] [E7] | LlamaIndex candidate extraction, exact quote check, reviewed promotion; narrator cannot change numbers | High semantic value without numeric prompt leakage | Review remains for consequential claims; provider access must be verified | Decision D6; missing M09/M06/M12P plans |
| R1/R3: preserve custody choices | More tools could duplicate evidence truth | Karakeep-only; new stack; neutral mirror | [R4] [R5] | Karakeep capture, retained Docling, immutable manifests and ext4 index | Extends existing research instead of restarting it | Capture service availability differs from durable custody | Existing R1/R3 documents; missing WF06 |
| M08: replace internal ASR assumptions | Audio-only cannot produce slides; word times are fallible | Internal TTK; WhisperX; generic PDF extraction | [E6] [E19] [E20] | WhisperX plus retained video and PySceneDetect | Actual supported products with separable outputs | Model/slide/timing acceptance still required | Missing `implementation-plans/M08_MEDIA_PIPELINE.yaml` and M09 plan |
| C11: reject incorrect totals | Dropped rows and failed FX contaminate valuation | Ignore; drop unknown money; reject incomplete input | [R6] [R7] [R10] | Delivered surgical validation and FX-label patch | Directly fixes demonstrated arithmetic boundary | Invalid inputs abort current attempt; graceful quarantine is follow-up | `ipos/etl/portfolio_csv.py`; `ipos/aggregate/portfolio.py`; new regression tests |
| C11: snapshot is not ledger | FIFO claimed from holdings-only inputs | Fabricated buys; verified events; explicit opening state | [R2] [E12] [E13] | Portfolio Performance local import/export plus typed event reconciliation | Reuses maintained parsers and preserves lot semantics | Supported GUI steps remain; unknown historic basis stays unknown | `05_blueprint/03_PORTFOLIO_MODULE.md`; missing normalizer and tests |
| C13: risk clusters are not sectors | Statistical grouping mistaken for economic classification | Cluster labels as sectors; explicit taxonomy | [E8] [E9] | Explicit instrument/sector master, approved macro policy, existing solver preserved | Separates measurement, interpretation and allocation | Sector/factor data and policy remain prerequisites | Missing `ipos/portfolio/optimizer.py`; M12P; existing portfolio spec |
| D3: reuse visualization | Redundant dashboard rebuild; misleading area encoding | Core renderer rewrite; optional native views | [R3] [E8] [E10] [E11] | Riskfolio SVG diagnostics and optional standalone Plotly HTML, with exact table | Preserves prior rendering decisions and shows real exposures | Additional files; no proven improvement in investment returns | Decision D3; `ipos/report/html.py` integration seam; missing C13 |
| C12: independent desktop parity | GUI imports can manufacture trades or validate themselves circularly | Synthetic buys; native holdings mode; actual transactions | [E16] [E17] | Correct native mode, original broker control, exported local backup | Preserves economic meaning and checks a different representation | Installed version/schema and valuation times must match | Missing C12 sources; `05_blueprint/03_PORTFOLIO_MODULE.md` |
| US10-12: isolate community | Global orchestrator/Docker access crosses privacy and ownership | One global credential; per-domain access | User contract; [E3] | Preserve community stack; separate credentials, paths, volumes and publication channels | No IPOS enhancement needs a community migration | Same daemon is not strong security isolation | Future infrastructure handover; no community file edits |

## Tensions resolved, without hiding the remainder

**Zero containers versus Docker:** zero required containers applies to the host numerical task, not a ban on separately running Karakeep or existing community services.

**Main-only versus different operating systems:** use native OS checkouts/deployments of the same approved main commit, never one working tree or virtual environment mounted into both runtimes. Main-only does not mean copying database state between clones.

**No custom prototypes versus integration:** actual product calls, schemas, adapters and acceptance tests are permitted integration work; rebuilding their extraction, parser, clustering, solver or transport internals is not.

**Manual execution versus older "no trade calls":** the current request authorizes a prospective manual Action Matrix, while the old portfolio specification only permits comparison. Record this scope extension before implementing it; do not claim old code already satisfies it. Broker execution remains prohibited. [R2]

**Cheap AI versus existing subscriptions:** reuse an authorized provider, but do not invent API entitlements. Failure of narration cannot block the deterministic report; failure of source validation must block promotion of that claim, not erase existing approved policy.

**Still unresolved:** the absent rebuilt matrix, actual host deployment, precise macro-to-sector policy, return universe/history, broker document variants and independently tested C12 mapping. There are no invented resolutions for these unknowns.

## Source links

[R0]: https://github.com/leela-spec/Investment/commit/cec42be2aaf922c74ea6b13dc44fe11adfdd618f "Observed main reference"
[R1]: https://github.com/leela-spec/Investment/blob/cec42be2aaf922c74ea6b13dc44fe11adfdd618f/05_blueprint/01_DECISION_ANALYSIS.md "Existing decisions"
[E1]: https://duckdb.org/docs/current/connect/concurrency "DuckDB concurrency"
[R8]: https://github.com/leela-spec/Investment/blob/cec42be2aaf922c74ea6b13dc44fe11adfdd618f/ipos/run.py "Live weekly runner"
[E2]: https://learn.microsoft.com/en-us/windows/wsl/filesystems "Microsoft WSL filesystem guidance"
[R5]: https://github.com/leela-spec/Investment/blob/cec42be2aaf922c74ea6b13dc44fe11adfdd618f/05_blueprint/research/2026-08-23-ipos-reuse-expansion-program/results/R3-evidence-kb/TOOL_LANDSCAPE.md "Existing evidence-KB landscape"
[E7]: https://developers.llamaindex.ai/python/examples/metadata_extraction/pydanticextractor/ "LlamaIndex Pydantic extraction"
[R4]: https://github.com/leela-spec/Investment/blob/cec42be2aaf922c74ea6b13dc44fe11adfdd618f/05_blueprint/research/2026-08-23-ipos-reuse-expansion-program/results/R1-karakeep-ipos/CURRENT_IPOS_GAP_MAP.md "Existing Karakeep gap map"
[E6]: https://github.com/m-bain/whisperX "WhisperX official project"
[E19]: https://github.com/yt-dlp/yt-dlp "yt-dlp official project"
[E20]: https://www.scenedetect.com/cli/ "PySceneDetect CLI"
[R6]: https://github.com/leela-spec/Investment/blob/cec42be2aaf922c74ea6b13dc44fe11adfdd618f/ipos/etl/portfolio_csv.py "Live portfolio CSV reader"
[R7]: https://github.com/leela-spec/Investment/blob/cec42be2aaf922c74ea6b13dc44fe11adfdd618f/ipos/aggregate/portfolio.py "Live portfolio aggregation and FX"
[R10]: https://github.com/leela-spec/Investment/blob/cec42be2aaf922c74ea6b13dc44fe11adfdd618f/tests/test_portfolio.py "Existing portfolio tests, inspected first 230 lines"
[R2]: https://github.com/leela-spec/Investment/blob/cec42be2aaf922c74ea6b13dc44fe11adfdd618f/05_blueprint/03_PORTFOLIO_MODULE.md "Built portfolio comparison specification"
[E12]: https://help.portfolio-performance.info/en/reference/file/import/pdf-import/ "Portfolio Performance PDF import"
[E13]: https://help.portfolio-performance.info/en/reference/file/export/ "Portfolio Performance CSV export"
[E8]: https://riskfolio-lib.readthedocs.io/en/latest/riskfoliolib/plot.html "Riskfolio plotting API"
[E9]: https://riskfolio-lib.readthedocs.io/en/latest/riskfoliolib/portfolio.html "Riskfolio convex portfolio API"
[R3]: https://github.com/leela-spec/Investment/blob/cec42be2aaf922c74ea6b13dc44fe11adfdd618f/05_blueprint/research/2026-07-29_dashboard_visualization_audit.md "Existing visualization audit, especially sections 0-2"
[E10]: https://plotly.com/python/treemaps/ "Plotly treemap API"
[E11]: https://plotly.com/python/interactive-html-export/ "Plotly self-contained HTML export"
[E16]: https://wealthfolio.app/docs/guide/csv-import/ "Wealthfolio CSV and holdings-mode import"
[E17]: https://wealthfolio.app/docs/guide/data-export/ "Wealthfolio export and backup"
[E3]: https://docs.docker.com/desktop/features/wsl/best-practices/ "Docker Desktop WSL best practices"
