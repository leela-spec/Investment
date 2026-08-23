# Evidence KB Requirements

## Boundary: evidence is not operational IPOS knowledge

At the pinned commit, IPOS already has an operational knowledge/runtime layer: 34 indicator records, 126 rules and 44 process records in `03_extract/`; ten playbook modules in `04_playbook/modules/`; a DuckDB warehouse; deterministic scoring, aggregation and reporting; and a bounded narration layer. `PROJECT_STATE.md` records 22 live indicators and 141 tests. `configs/ai.yaml` states the prime directive explicitly: code computes, the LLM narrates, and the system remains functional without a live model. The existing blueprint also deliberately uses deterministic playbook references rather than RAG.

The new evidence KB must therefore be a **read-only sidecar from IPOS's point of view**. Filings, releases, PDFs, web captures and datasets are evidence. They do not become indicator values, scoring rules, governors or playbook guidance merely because they were captured or summarized. Promotion into operational knowledge is a separate, reviewed process outside R3.

Repository evidence:

- [`PROJECT_STATE.md` at the pinned commit](https://github.com/leela-spec/Investment/blob/6353c1acb768d61a7be83477e1cc4fee55653d97/PROJECT_STATE.md)
- [`configs/ai.yaml`](https://github.com/leela-spec/Investment/blob/6353c1acb768d61a7be83477e1cc4fee55653d97/configs/ai.yaml)
- [`03_extract/`](https://github.com/leela-spec/Investment/tree/6353c1acb768d61a7be83477e1cc4fee55653d97/03_extract)
- [`04_playbook/modules/`](https://github.com/leela-spec/Investment/tree/6353c1acb768d61a7be83477e1cc4fee55653d97/04_playbook/modules)

## Required invariants

### R1. Source truth and preservation

- Preserve every acquired original byte-for-byte when the terms permit it.
- Address originals by SHA-256 and never overwrite them. A changed URL creates a new capture/version.
- Record the original URL, canonical URL, publisher, retrieval time, publication time when known, HTTP validators, MIME type, byte count, checksum and rights status.
- Retain parser output separately with parser name/version/configuration and its own checksum.
- Keep the source artifact authoritative. Parsed text, OCR, normalized tables, summaries, extracted claims and embeddings are rebuildable derivatives.
- Export must work without Karakeep, Zotero, an LLM or a proprietary database.

### R2. Deterministic identity, lineage and deduplication

- Exact deduplication uses SHA-256.
- Logical identity uses authoritative identifiers where available: SEC accession/CIK, DOI, LEI, dataset/series ID, regulation/document number and source URL.
- Normalized-URL or fuzzy fingerprints may propose duplicates; they must not silently merge different editions or filing amendments.
- Each derived record points to its exact source hash and toolchain version.
- A citation must resolve to the captured source, the live source URL and an exact page/section/row anchor when available.

### R3. Retrieval without AI

- Full-text search must provide FTS/BM25, phrase/prefix/Boolean queries and snippets.
- Metadata filters must cover publisher, evidence type, entity, identifier, publication/capture dates, jurisdiction, language, rights status and parser status.
- Deterministic tag/entity lookup must use versioned alias tables. An LLM/NER model may suggest additions but cannot mutate canonical mappings automatically.
- Embeddings are an optional secondary index only. Disabling or rebuilding them must not remove any source, metadata, citation or baseline retrieval function.

SQLite FTS5 directly provides full-text virtual tables, Boolean/phrase/NEAR/column queries, BM25 ranking and snippets. [SQLite FTS5 documentation](https://www.sqlite.org/fts5.html)

### R4. Evidence breadth

The KB must accept:

- web pages and archived snapshots;
- PDFs, office documents, email/newsletters and images;
- SEC/XBRL and other structured filings;
- CSV, JSON, JSONL, XML/SDMX and Parquet datasets;
- citations/DOIs and scholarly metadata;
- official releases, regulations and investor-relations materials.

Binary media transcription is optional and must retain the original media. Paywalled content may be referenced with metadata only unless the operator has lawful download rights.

### R5. Local, free and recoverable

- Baseline operation uses free/open-source components and local files/indexes.
- No always-on cloud service, paid vector database or per-query LLM cost is required.
- Backups contain originals, manifests, annotations and configuration; indexes and model-generated derivatives may be rebuilt.
- Restoration is testable from a documented directory/export contract.

### R6. Rights-aware acquisition

- Every source has `rights_status`: `open`, `public-domain`, `source-terms`, `personal-use`, `unknown`, or `do-not-archive`.
- Downloader rules enforce publisher rate limits, user agents, robots/terms where applicable and per-source retention policy.
- The system never circumvents authentication, DRM or access controls.
- Third-party FRED series, commercial transcripts, paywalled newsletters and social-network feeds default to metadata/link-only until rights are verified.

### R7. Safe automation and AI boundary

Deterministic automation may download an allowlisted resource, hash it, validate size/type, parse it, extract explicit identifiers, index it and emit a receipt. AI may optionally propose tags, summaries, claims or contradiction candidates. Such outputs must be labeled `derived`, contain prompt/model/version/source references and remain untrusted until reviewed. Numeric facts used by IPOS must continue to come through existing validated connectors and deterministic computation, not an evidence summary.

### R8. Operational qualities

- Idempotent ingestion for the same source bytes and acquisition event.
- Transactional manifest/index updates; a failed parser does not lose the original.
- Quarantine for malformed, unexpectedly large or unsupported inputs.
- Structured logs and machine-readable receipts.
- Parser and schema migrations are versioned; old derivatives remain traceable.
- Search/index integrity checks and restoration drills are defined.

## Minimal evidence record

| Field group | Required content |
|---|---|
| Identity | `evidence_id`, `sha256`, byte size, MIME type, immutable object path |
| Source | requested URL, final/canonical URL, publisher, source class, captured/retrieved timestamp, HTTP ETag/Last-Modified |
| Document | title, document type, published/effective date, language, jurisdiction |
| Rights | rights status, license/terms URL, permitted operation, review note |
| Financial IDs | CIK, accession, DOI, LEI, ISIN/FIGI/ticker only when source-backed, dataset/series ID |
| Lineage | prior/superseding evidence ID, attachment/parent relation, acquisition job/connector version |
| Derivative | parser/OCR name and version, config hash, output hash/path, status/confidence |
| Retrieval | deterministic tags/entities, normalized citation anchors, index version |
| Governance | review status, promotion status, retention class; operational promotion defaults to `none` |

## Acceptance tests for a later implementation

1. Re-ingesting identical bytes returns the same object hash and does not create a second object.
2. Capturing a changed page preserves both versions and their timestamps.
3. Deleting and rebuilding `evidence.sqlite` from manifests reproduces the searchable inventory.
4. A search for an exact phrase and a CIK/LEI works with networking and AI disabled.
5. Every search hit can open the original and report source URL, hash and acquisition time.
6. Parser failure leaves the original and a failure receipt intact.
7. The backup/restore test succeeds on a clean host without Karakeep/Zotero state.
8. AI-derived content is never returned as an original source or imported into IPOS operational JSONL/configs automatically.

## Non-requirements

- “Chat with PDFs,” autonomous research agents, semantic/vector search and automatic truth adjudication.
- A new operational indicator warehouse or a replacement for the existing DuckDB pipeline.
- A bespoke capture UI, citation manager, crawler, OCR engine or search server.
- Mirroring the whole internet, all Crossref/DataCite metadata or every financial timeseries merely because bulk access exists.
