# Gaps and Uncertainties

## Unresolved evidence gaps

1. **No production corpus benchmark.** R3 did not install tools or run a parser/search benchmark because the prompt does not request a POC and the launcher forbids production mutation. Docling table fidelity, resource use and deterministic output must be tested on the operator-approved evaluation set before installation.
2. **Karakeep deployment state is intentionally not assumed.** R1 owns Karakeep integration/deployment research. R3 treats documented current capabilities as architecture evidence only.
3. **Rights are artifact/dataset specific.** SEC filing exhibits, FRED series, World Bank third-party datasets, bibliographic abstracts, corporate IR material and central-bank publications may carry rights different from their host portal. The source registry needs a recorded decision for each connector/dataset; this report cannot grant legal permission.
4. **Bulk sizes change.** Most corpus sizes were classified by planning scale rather than fabricated precision. Disk/bandwidth projections require selecting the actual IPOS dataflow/issuer universe.
5. **Search scale threshold is not measured.** SQLite FTS5 is recommended because the likely personal corpus and requirements fit it, but no representative corpus/query-latency target was supplied. Tantivy remains the explicit scale-up candidate after a benchmark failure.
6. **Multilingual retrieval.** FTS5 tokenization/stemming behavior for multilingual European documents was not benchmarked. Metadata/identifier lookup remains robust; a language-specific tokenizer or separate indexes may be needed.
7. **OCR quality.** No scan corpus or target languages were provided. OCRmyPDF/Tesseract is therefore a routed candidate, not a baseline dependency.
8. **Scholarly citation extraction.** GROBID versus Docling/Zotero accuracy was not compared on finance papers. Add GROBID only after a measured improvement.
9. **Agent-skill ecosystem remains immature.** The public community repositories inspected did not provide enough tests, licensing and independent use evidence to call their finance/research skills battle-tested. This can change quickly; recheck only when a specific candidate is proposed.
10. **No semantic-retrieval eval set.** There is no evidence that embeddings improve an actual IPOS research question. They remain disabled until a labeled query/hit benchmark shows a material recall gap.
11. **Annotation round-trip.** Exact mapping of Karakeep highlights and Zotero annotations into neutral page/DOM anchors requires fixture testing because web DOMs and PDF annotation schemas differ.
12. **Private/licensed data policy.** Storage encryption, backup destination, retention and separation for private portfolio or personally licensed artifacts require a human decision. The recommendation excludes them from the general evidence KB by default.

## Important uncertainties in judgments

- MCDA scores are deliberately transparent integers but not empirical measurements. Option E's lead over D is sensitive to the value of Karakeep capture automation; if capture export is unreliable, use D without changing canonical data.
- Maintenance “currentness” was checked at repository/documentation HEAD on 2026-08-23. Dependency versions should be pinned from a tested release, not the observed development HEAD.
- Product documentation describes supported behavior, not preservation guarantees for every dynamic/paywalled site. Capture success and fidelity remain site-specific.
- A content hash proves byte identity, not publisher authenticity or factual truth. Source authority, signature/HTTPS receipt and reviewed metadata are separate controls.
- Deterministic parser execution does not imply accurate parsing. Financial tables/XBRL facts require validation and source anchors.

## Blockers

**None for the R3 research decision.** The unresolved items are pre-implementation tests/human policy decisions, not blockers to recommending the architecture.

## Deterministic next tests

1. Freeze 20–30 lawful fixtures across web, PDF, scan, filing/XBRL, presentation, CSV/SDMX and email; record expected titles/identifiers/table cells and source hashes.
2. Run a pinned Docling standard pipeline twice offline and compare serialized outputs; manually grade text/table/anchor fidelity.
3. Export five accepted Karakeep records, including a changed SingleFile page, into the proposed receipt/object contract; delete/rebuild the SQLite index.
4. Define 30 keyword/phrase/entity/date/source queries with expected hits; benchmark FTS5 index size, ingest time, P50/P95 latency and recall.
5. Run a backup/restore drill on a clean environment and verify every hit opens an original with URL/hash/acquisition receipt.
6. Only after baseline scoring, compare GROBID citation extraction and optional embedding recall on the same fixed fixtures/queries.

## Human gates for later implementation

- Approve storage/encryption/backup location and private/licensed evidence policy.
- Approve source allowlist, rate/disk/network quotas and dataset-specific rights decisions.
- Approve installation/credentials for Karakeep API/MCP and local parser dependencies.
- Approve the evidence-to-operational promotion governance; R3 recommends no automatic path.
