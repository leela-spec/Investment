# R1 Track Plan — Karakeep → IPOS

**Pinned project state:** `leela-spec/Investment@6353c1acb768d61a7be83477e1cc4fee55653d97`  
**Karakeep verification target:** release `v0.33.2` (latest observed 2026-08-23)

## Questions

1. Which current IPOS capability gap, if any, is solved by Karakeep?
2. Which Karakeep functions are stable, local/free, portable and deterministic enough for IPOS?
3. Which system owns raw evidence, human curation, derived evidence views, operational Playbook rules and scoring?
4. What is the smallest reversible interface, and how does it fail?
5. Can ingest, retrieval, search, deduplication, export and recovery be demonstrated in this environment?

## Repository evidence

- Read the pinned authority documents, all 10 Playbook modules, all three extraction JSONL files, all configs, and the relevant `ipos/etl`, `ipos/export`, `ipos/report`, `ipos/ai` implementation and tests.
- Prefer executable code and tests over historical plans; explicitly record stale/conflicting documents.
- Verify that no current production research/bookmark/evidence connector exists before declaring a gap.

## Source strategy

`broad product scan → official docs/release/license → tagged source/OpenAPI/CLI schemas → failure/adversarial evidence → conclusion`

Primary targets: Karakeep official docs, `karakeep-app/karakeep` release/tagged source and OpenAPI; Docker's official Windows documentation. Community issues are used only to identify unresolved edge cases.

## POC plan

- First check Docker/Podman and a writable Karakeep instance.
- If unavailable, run the official packaged CLI locally far enough to verify version, command surface and process failure behavior.
- Do not install a production service or use private data.
- Document a deterministic full Docker test for: article, PDF, YouTube + transcript note, research note, RSS item, duplicate URL, search, content retrieval, dump and migration/restore.

## Decision method

- Capability classification: `ADOPT`, `ADOPT_AS_OPTIONAL`, `IPOS_ALREADY_HAS_THIS`, `NOT_NEEDED`, `CONFLICTS_WITH_IPOS`, `REQUIRES_OPERATOR_DECISION`.
- MCDA: prompt-specified nine weighted criteria, Karakeep vs current-repo-only baseline.
- Recommendation threshold: no production adoption without a successful writable-instance POC and restore test.

## Outputs

The seven prompt deliverables plus `SOURCES.md`, `GAPS_AND_UNCERTAINTIES.md`, `TRACK-MANIFEST.json`, this plan, and POC command/configuration details.
