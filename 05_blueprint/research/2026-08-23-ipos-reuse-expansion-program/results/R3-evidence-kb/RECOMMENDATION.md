# Recommendation

## Decision

**Adopt architecture E: a neutral immutable evidence store plus local SQLite FTS5, with Karakeep as the primary capture/review interface and Zotero only as an optional scholarly workspace.** Use Docling for default local parsing after an isolated compatibility test. Keep GROBID, Tika and OCRmyPDF routed fallbacks rather than permanent baseline services. Do not add embeddings, a vector database, Meilisearch/Typesense, or an autonomous claim pipeline now.

This is a research recommendation, not an implementation. No production component was installed or changed.

## Why it fits current IPOS

The pinned IPOS repository is already a deterministic operational system: facts enter the DuckDB warehouse through governed connectors, scoring/rules are code/configuration, the playbook is explicitly retrieved without RAG, and AI narration is optional. The evidence KB should extend the system's memory without weakening that boundary. A sidecar can preserve documents and support research; it must not become an alternate numeric data path or silently edit `03_extract/`, `04_playbook/`, `configs/`, scoring or governors.

Option E scored 97/100 under the prompt's weights. The runner-up, a pure filesystem/Markdown/index design, scored 92 and is the safe degradation path if capture integrations disappoint. The five-point benefit comes from reusing Karakeep's human capture/API and optional Zotero citation workflow without letting either own canonical evidence.

## What to reuse

### ADOPT NOW in the design

1. **Content-addressed filesystem objects and JSON evidence receipts** as canonical truth.
2. **SQLite FTS5** for unified BM25 full-text retrieval plus relational metadata, identifier, tag, entity and relationship tables.
3. **Karakeep** for web/PDF capture, triage, notes, highlights and review. Export accepted artifacts to the neutral store; do not rely only on its database/backups.
4. **Docling standard local conversion** for broad documents into lossless JSON and Markdown/text, with version/configuration recorded and remote/VLM paths disabled by default.
5. **Zotero translators and citation workflow** when academic finance research is used. Zotero remains optional and references neutral evidence IDs.
6. **Provider identifiers and metadata:** SEC accession/CIK, DOI metadata through DataCite/Crossref, GLEIF LEI, official dataset/series IDs and FIBO only as a vocabulary aid.

### TEST FURTHER

- Docling on a fixed evaluation set: text PDF, complex 10-K table, inline XBRL filing, presentation, scanned PDF and malformed file. Measure text/table fidelity, runtime, dependencies and determinism.
- Karakeep → neutral export round-trip, including SingleFile asset, PDF, changed page/version, tags/notes/highlights and backup restoration.
- Zotero interoperability on ten open papers: translator metadata, attachment hash, neutral ID, note/citation export and duplicate behavior.
- GROBID only if citation/reference extraction accuracy is materially better on the academic set.
- OCRmyPDF/Tesseract only for image-only PDFs, with language packs pinned.
- Tantivy only if a representative SQLite query benchmark fails an agreed target.

### DEFER

- ArchiveBox/WARC-grade capture until replay fidelity or scheduled crawl coverage is a measured requirement.
- Apache Tika until Docling format/error coverage leaves a real gap.
- DuckDB evidence analytics until cross-document aggregation is needed; never use DuckDB FTS as the incremental primary index because its documented index does not auto-update.
- Embeddings/rerankers until a fixed retrieval evaluation proves an FTS/metadata recall gap.
- Paperless-ngx unless scanned administrative documents become a substantial independent corpus.

### REJECT for the baseline

- Meilisearch/Typesense/vector-database services and an always-on RAG stack.
- Dual-canonical Karakeep+Zotero synchronization.
- Community agent skills without verified license, tests and production evidence.
- LLM summaries, extracted claims or contradictions as evidence truth.
- Any automatic evidence-to-operational-IPOS promotion.

## What to download

Use a bounded, relevance-first bootstrap—not a data-hoarding project:

- SEC nightly submissions/company-facts archives and selected Financial Statement Data Set quarters.
- CFTC COT historical files for report families used by IPOS.
- Latest GLEIF Golden Copy plus daily deltas.
- Only the BIS, ECB, Eurostat, Bundesbank and World Bank dataflows overlapping monitored indicators or explicit research questions.
- GovInfo market-relevant regulation collections and FIBO only when a concrete taxonomy use exists.

DataCite's full metadata file is legally downloadable but operationally disproportionate: the publisher reports the 2025 file as 33 GiB compressed and 615 GiB decompressed. Query targeted DOI metadata instead. [DataCite public file dimensions](https://datafiles.datacite.org/datafiles/public-2025)

## What to archive incrementally

- Official filings and 8-K exhibits for the tracked issuer/event universe.
- Corporate IR releases, presentations and lawful prepared remarks actually reviewed.
- Central-bank/statistics releases linked to watched series or regime changes.
- Relevant Federal Register/GovInfo rules with the official rendition.
- Open-access finance/economics papers only after recording the work-level license.

Each connector requires an allowlist, rights/terms URL, rate limit, expected format/size, update cursor, identity rule and retention policy. Store a new immutable version when bytes change.

## What not to store

- Unauthorized commercial transcripts, subscription research/newsletters, social firehoses or proprietary feed/security-master mirrors.
- FRED's entire estate: series licensing is item-specific. Continue the existing curated connector model and preserve only outputs whose series terms permit it.
- Credentials, brokerage exports or private portfolio snapshots in the general evidence library.
- Unbounded corpora with no stated IPOS question, such as all DataCite/Crossref metadata.
- Redundant regenerated derivatives when the original plus parser version/config is enough.
- AI-generated summaries/claims as external sources.

## Minimal IPOS-specific glue actually necessary

No new UI, parser, crawler, citation engine or search engine is justified. The thin custom layer is:

1. **Evidence schema/receipt:** validate the fields in `EVIDENCE_KB_REQUIREMENTS.md`; assign evidence/version IDs; record rights and lineage.
2. **Object writer:** stream bytes, enforce limits/type, compute SHA-256, atomically store immutable objects and quarantine failures.
3. **Karakeep exporter:** read accepted bookmark/assets/metadata through official API; materialize them idempotently; write back/reference neutral ID only if safe.
4. **Parser router:** choose Docling, OCR, GROBID or Tika using deterministic MIME/document rules; record version/config/output hash; never discard the original.
5. **Normalizer:** canonicalize URLs/DOIs/accessions/CIKs/LEIs/dataset IDs; exact dedupe; fuzzy candidates only.
6. **Entity/tag mapper:** join authoritative IDs and a reviewed/versioned alias table; source classification by allowlisted rules.
7. **SQLite indexer/query CLI:** transactional metadata/relationship tables and FTS5/BM25; rebuild index entirely from receipts/derivatives.
8. **Rights/source registry:** one declarative policy per source/connector.
9. **Read-only IPOS evidence query contract:** return evidence IDs, source URLs, hashes, dates, snippets/anchors and rights/review status. It cannot write operational facts/rules.

Approximate custom scope is a small package/CLI plus schemas/tests, not a platform. Later implementation should start with one source family, one document type and the acceptance tests before expanding.

## Canonical ownership rules

| Data | Owner | Rebuildable? |
|---|---|---:|
| Original bytes and acquisition receipt | Neutral evidence store | No—back up |
| Rights decision and reviewed metadata/aliases | Neutral records | No—back up/version |
| Parsed text/tables/Markdown | Derived store | Yes from original + pinned toolchain |
| SQLite FTS/metadata index | Local index | Yes from records/derivatives |
| Karakeep notes/highlights before acceptance | Karakeep inbox | Export on acceptance/backup |
| Zotero collections/annotations | Zotero workspace | Back up separately; link by neutral ID |
| Embeddings/summaries/claim candidates | Optional derived store | Yes; never source truth |
| IPOS numeric facts, rules, scoring, playbook | Existing operational repository/warehouse | Governed separately |

## Decision gates for implementation planning

Before installation or code changes, approve:

1. storage location/encryption/backup and whether private/licensed evidence may enter it;
2. initial source allowlist and disk/network quotas;
3. whether Karakeep is already deployed and whether Zotero is genuinely needed;
4. the isolated parser/capture evaluation set and pass thresholds;
5. the evidence-to-IPOS read-only interface and separate promotion governance.

No architecture decision depends on selecting an LLM.

