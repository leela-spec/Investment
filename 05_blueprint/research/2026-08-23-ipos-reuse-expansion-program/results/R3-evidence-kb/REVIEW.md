# Independent Review — R3 General Financial Evidence Knowledge Base

**Review date:** 2026-08-23  
**Reviewer role:** independent of the R3 researcher  
**Repository authority:** `leela-spec/Investment@6353c1acb768d61a7be83477e1cc4fee55653d97`  
**Prompt:** `ExternalAddonsResearch/prompts/R3_General_Financial_Evidence_Knowledge_Base.md` (`bc0ce869817804b6cc1622792b1d04e043027668`)  
**Method:** launcher §7 and `METHOD-BASIS.md`

## Score

| Dimension | Score (0–2) | Review finding |
|---|---:|---|
| Repo grounding | 2 | Correctly pins the repository, distinguishes the 34 extracted indicator records from 22 live indicators, and preserves the operational/evidence boundary shown by `PROJECT_STATE.md`, `configs/ai.yaml`, the no-RAG master-plan decision, DuckDB runtime, contradiction rules, and golden-test governance. |
| Factual grounding | 1 | Most consequential product, corpus, API, size, and license claims were confirmed. Two qualifications are important: Docling's standard PDF path uses local ML layout/table models even when VLM/remote paths are disabled, and FRED's API/service terms are more restrictive about storing/archiving API content than the series-rights shorthand conveys. |
| Citation accuracy | 1 | Spot-checked citations generally support their claims. The cited FRED series-license URL currently renders as the general API page; the API terms/legal pages are the direct support for the third-party-rights and anti-archiving qualifications. The Docling formats page supports inputs/outputs but the model catalog is the direct source for its local ML stages. |
| Source quality | 2 | Consequential claims rely overwhelmingly on official documentation, first-party repositories/licenses, regulators, central banks, and public institutions. Community repositories are appropriately used only to evaluate themselves. |
| Coverage | 1 | All eight required deliverables plus launcher artifacts exist, all five architectures and exact MCDA weights are covered, and corpus classifications address mechanism/rights/update/scale/readability/provenance/relevance. The OpenClaw/Gemini-specific skill search is reported only at a high level and lacks a reproducible candidate/source inventory, so that sub-landscape is thinner than the prompt requests. |
| Uncertainty | 2 | `GAPS_AND_UNCERTAINTIES.md` is unusually explicit about rights, untested parser/capture behavior, scale, multilingual retrieval, OCR, annotation round-trip, and the lack of a semantic-retrieval benchmark. |
| Target alignment | 2 | Stays within evidence architecture research, makes no production change, and does not collapse external evidence into operational extracts, configs, scoring, governors, or AI narration. |
| Reuse-first discipline | 2 | Evaluates mature capture, citation, document-management, parsing, OCR, and search components before narrowing custom work to receipts, export/router/index contracts, rights rules, and a read-only query boundary. |
| POC integrity | 2 | Explicitly N/A: R3 does not require a POC. No installation or implementation is claimed, and later fixture/benchmark/restore tests are deterministic and appropriately deferred. |
| Efficiency | 2 | Deliverables are decision-oriented tables/JSON with little duplicated landscape prose; search stops at primary evidence and explicit uncertainty rather than over-researching speculative RAG. |
| **Total** | **17/20** | Passes the launcher threshold; no zero occurs in repo grounding, factual grounding, citation accuracy, or coverage. |

## Major claims spot-checked

1. **Pinned IPOS boundary — confirmed.** The pinned repository contains 34 `indicators.jsonl` records, 126 rules, and 44 process records, while `PROJECT_STATE.md` distinguishes 22 live runtime indicators. `configs/ai.yaml` says the system remains functional without a live model; `05_blueprint/00_MASTER_PLAN.md` explicitly chooses deterministic `playbook_refs`, no RAG/embeddings, artifacts over servers, and DuckDB for the operational warehouse. The R3 sidecar/read-only boundary is therefore well grounded.
2. **Karakeep capabilities/currentness — confirmed.** Current official v0.33.0 documentation says link capture can include metadata, previews, screenshots and archives; PDFs/media are content-extracted and searchable; notes, highlights and attachments are searchable. The API lists bookmarks, lists, tags, highlights, assets and backups. The observed repository HEAD `7ca5ee236b96cd659096b1530c5be3fdcd8e4470` was rechecked, and the first-party license is AGPL-3.0. Sources: [bookmarking](https://docs.karakeep.app/using-karakeep/bookmarking/), [API](https://docs.karakeep.app/api/karakeep-api/), [license](https://github.com/karakeep-app/karakeep/blob/main/LICENSE).
3. **Zotero indexing limit — confirmed.** Official documentation updated 2026-06-08 supports PDF/EPUB/HTML/plain-text indexing, excludes DOCX/ODT, and gives the default 500,000-character cap. The report's warning that export is not backup is linked to Zotero's official export guidance. Source: [Zotero search preferences](https://www.zotero.org/support/preferences/search).
4. **Docling format/local execution claim — confirmed with qualification.** Official docs support the broad listed input formats, XBRL XML, email, and lossless JSON/Markdown/text output; the first-party agent skill is public and the MIT license is current. However, the standard PDF path is not equivalent to “no AI/ML”: Docling's official model catalog documents RT-DETR layout detection and TableFormer table recognition. The safe claim is “no hosted or generative model is required; local learned parser models may run, and output determinism/accuracy must be tested.” Sources: [supported formats](https://docling-project.github.io/docling/usage/supported_formats/), [model catalog](https://docling-project.github.io/docling/usage/model_catalog/), [agent skill](https://docling-project.github.io/docling/usage/agent_skills/), [MIT license](https://github.com/docling-project/docling/blob/main/LICENSE).
5. **Search-engine licensing — confirmed.** Meilisearch's repository declares `MIT AND BUSL-1.1`; Typesense Server is GPL-3.0. The outputs distinguish Meilisearch's mixed license and do not call either an unqualified permissive baseline. Sources: [Meilisearch license](https://github.com/meilisearch/meilisearch/blob/main/LICENSE), [Typesense repository](https://github.com/typesense/typesense).
6. **SEC bulk/API claims — confirmed.** The SEC says the APIs require no authentication/key, update through the day, and the submissions/company-facts bulk ZIPs are rebuilt nightly. The 2026 Q1 Financial Statement Data Set is listed at 81.31 MB. Sources: [EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces), [Financial Statement Data Sets](https://www.sec.gov/dera/data/financial-statement-data-sets.html).
7. **DataCite scale — confirmed.** The 2025 official file reports 108,468,906 records, 33 GiB compressed and 615 GiB decompressed. This directly supports the “legally downloadable but disproportionate” decision. Source: [DataCite 2025 public file](https://datafiles.datacite.org/datafiles/public-2025).
8. **Institutional corpus mechanisms — confirmed on a sample.** BIS offers full topics as zipped CSV or SDMX; GLEIF publishes three Golden Copy sets daily with 8-hour/24-hour/7-day/31-day deltas; World Bank defaults to CC BY 4.0 while preserving third-party exceptions. Sources: [BIS bulk downloads](https://data.bis.org/bulkdownload), [GLEIF Golden Copy](https://www.gleif.org/en/lei-data/gleif-golden-copy/download-the-golden-copy), [World Bank terms](https://data.worldbank.org/summary-terms-of-use).
9. **FRED rights posture — direction confirmed, wording needs care.** Official API terms say series may be third-party-owned and that API access does not override those rights. The broader legal terms also restrict storing/caching/archiving FRED service/API content without consent. R3's classification as API-only and its “do not mirror FRED” recommendation are correct; later source-policy work should prefer underlying providers or obtain an explicit terms basis before retaining FRED responses. Sources: [FRED API terms](https://fred.stlouisfed.org/docs/api/terms_of_use.html), [FRED legal terms](https://fred.stlouisfed.org/legal/).
10. **Machine-readable validation — confirmed.** `MCDA.json`, `INSTALLATION_COMPONENT_MAP.json`, and `TRACK-MANIFEST.json` parse successfully. MCDA weights sum to 100; each option total recalculates exactly (A 80, B 84, C 89, D 92, E 97). Every output listed in the manifest exists and its SHA-256 matches.

## Weak or unsupported claims

- **Docling “AI required: No” is too broad.** It is accurate only if “AI” means hosted/generative AI. Standard PDF conversion can use local learned models. This does not invalidate the recommendation because originals remain canonical and the report already requires an isolated repeatability/fidelity test, but R9 should use the narrower wording.
- **FRED retention requires a source-by-source and service-terms decision, not only a series-license decision.** The existing wording “archive only permitted series outputs” should not be read as permission. Prefer the original issuing agency for durable archiving; treat FRED as an access layer unless counsel/terms provide a clear retention basis.
- **OpenClaw/Gemini ecosystem rejection is not reproducible at candidate level.** No source IDs or named candidates accompany the high-level catalog/search result. The conservative `REJECT until verified` outcome is safe, but it is not evidence that no qualifying skill exists.
- **Current test count is internally time-layered in `PROJECT_STATE.md`.** R3 cites the Phase-3 paragraph's 141 tests while the same pinned file later records 150 tests. This does not affect the architecture, but future synthesis should call the current executable baseline 150 tests or avoid a count.
- **MCDA precision is judgmental.** The 97 versus 92 ranking is transparent and arithmetically correct but not benchmark evidence. The report acknowledges this and supplies a safe D fallback, so no correction gate is warranted.

## Missing requirements

No required deliverable is missing. The only substantive coverage weakness is the thin, non-reproducible OpenClaw/Gemini-specific candidate inventory noted above. Because the recommendation does not adopt those candidates and explicitly requires future candidates to prove code/license/tests/currentness, the omission does not create an unsafe adoption decision.

## Drift and overengineering

- No production IPOS implementation or scoring redesign is proposed.
- The neutral object/receipt store is custom infrastructure, but it directly supplies provenance and application-independent export that the evaluated products do not provide alone. The proposed boundary is narrow enough to remain “thin glue,” provided later work does not expand it into a crawler, UI, autonomous truth engine, or second operational warehouse.
- Option E should be implemented only after the specified capture/parser/search/restore fixtures; absent successful Karakeep export testing, option D is the documented lower-complexity fallback.

## Verdict

**ACCEPT**

The track meets the launcher gate at 17/20 with no mandatory-dimension zero. The qualifications above must be carried into cross-track review/R9, especially the distinction between no hosted/generative AI and Docling's local ML parsing, and FRED service-term restrictions on retention.
