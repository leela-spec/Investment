# Sources

All external sources were accessed or rechecked on 2026-08-23. Primary/official sources support consequential facts; community repositories are used only to evaluate their own implementation maturity. Direct URLs are preserved below.

## Repository truth

| ID | Source | Supports |
|---|---|---|
| REP-01 | [Pinned repository tree](https://github.com/leela-spec/Investment/tree/6353c1acb768d61a7be83477e1cc4fee55653d97) | Effective project state at commit `6353c1a…` |
| REP-02 | [PROJECT_STATE.md](https://github.com/leela-spec/Investment/blob/6353c1acb768d61a7be83477e1cc4fee55653d97/PROJECT_STATE.md) | Current pipeline, indicators/tests, deterministic architecture and known data-source constraints |
| REP-03 | [03_extract](https://github.com/leela-spec/Investment/tree/6353c1acb768d61a7be83477e1cc4fee55653d97/03_extract) | Operational indicator/rule/process layer |
| REP-04 | [04_playbook/modules](https://github.com/leela-spec/Investment/tree/6353c1acb768d61a7be83477e1cc4fee55653d97/04_playbook/modules) | Operational playbook modules |
| REP-05 | [configs/ai.yaml](https://github.com/leela-spec/Investment/blob/6353c1acb768d61a7be83477e1cc4fee55653d97/configs/ai.yaml) | AI is optional narration; deterministic report remains complete |
| REP-06 | [MASTER_PLAN](https://github.com/leela-spec/Investment/blob/6353c1acb768d61a7be83477e1cc4fee55653d97/05_blueprint/00_MASTER_PLAN.md) | No-RAG/simplicity and deterministic computation design |
| REP-07 | [R3 prompt](https://github.com/leela-spec/Investment/blob/6353c1acb768d61a7be83477e1cc4fee55653d97/ExternalAddonsResearch/prompts/R3_General_Financial_Evidence_Knowledge_Base.md) | Authoritative track requirements, options, weights and outputs |
| REP-08 | [Program launcher](https://github.com/leela-spec/Investment/blob/6353c1acb768d61a7be83477e1cc4fee55653d97/05_blueprint/research/2026-08-23-ipos-reuse-expansion-program/AUTONOMOUS-PROGRAM-LAUNCHER.md) | Program boundaries and review/source rules |
| REP-09 | [METHOD-BASIS](https://github.com/leela-spec/Investment/blob/6353c1acb768d61a7be83477e1cc4fee55653d97/05_blueprint/research/2026-08-23-ipos-reuse-expansion-program/METHOD-BASIS.md) | Primary-source-first method and reviewer rubric |

## Capture, library and search tools

| ID | Source | Type | Supports |
|---|---|---|---|
| TOOL-01 | [Karakeep bookmarking](https://docs.karakeep.app/using-karakeep/bookmarking/) | Official docs, v0.33.0 | Link/media capture, archives/screenshots, extracted searchable PDFs/media, notes/highlights/attachments |
| TOOL-02 | [Karakeep API](https://docs.karakeep.app/api/karakeep-api/) | Official API | Bookmark/list/tag/highlight/asset/backup interfaces |
| TOOL-03 | [Karakeep search](https://docs.karakeep.app/api/search-bookmarks/) | Official API | Full-text query scope |
| TOOL-04 | [Karakeep SingleFile](https://docs.karakeep.app/integrations/singlefile/) | Official docs | Client-side page capture and append/overwrite behavior |
| TOOL-05 | [Karakeep backup API](https://docs.karakeep.app/api/list-backups/) | Official API | Backup listing/download workflow |
| TOOL-06 | [Karakeep license](https://github.com/karakeep-app/karakeep/blob/main/LICENSE) | First-party source | AGPL-3.0 |
| TOOL-07 | [Karakeep MCP README](https://github.com/karakeep-app/karakeep/blob/main/apps/mcp/README.md) | First-party source | MCP tools and client example |
| TOOL-08 | [Zotero translators](https://www.zotero.org/support/dev/translators) | Official docs | Translator types, implementation and automated tests |
| TOOL-09 | [Zotero search](https://www.zotero.org/support/preferences/search) | Official docs, updated 2026-06-08 | Supported indexed formats and character default |
| TOOL-10 | [Zotero export](https://www.zotero.org/support/kb/exporting) | Official docs | Export/round-trip limits and warning that export is not backup |
| TOOL-11 | [Zotero data directory](https://www.zotero.org/support/zotero_data) | Official docs | Local backup/restore posture |
| TOOL-12 | [Zotero license](https://github.com/zotero/zotero/blob/main/COPYING) | First-party source | AGPL-3.0 |
| TOOL-13 | [Zotero translator source](https://github.com/zotero/translators) | First-party source | Actual translator code/test fixtures |
| TOOL-14 | [Paperless-ngx API](https://docs.paperless-ngx.com/api/) | Official docs | REST interface |
| TOOL-15 | [Paperless-ngx administration](https://docs.paperless-ngx.com/administration/) | Official docs | Export/backup and operations |
| TOOL-16 | [Paperless-ngx license](https://github.com/paperless-ngx/paperless-ngx/blob/dev/LICENSE) | First-party source | GPL-3.0 |
| TOOL-17 | [ArchiveBox docs](https://docs.archivebox.io/latest/) | Official docs | Multi-format web preservation |
| TOOL-18 | [ArchiveBox API](https://docs.archivebox.io/dev/apidocs/) | Official docs | Automation interface |
| TOOL-19 | [ArchiveBox license](https://github.com/ArchiveBox/ArchiveBox/blob/dev/LICENSE) | First-party source | MIT |
| TOOL-20 | [SQLite FTS5](https://www.sqlite.org/fts5.html) | Official docs | FTS syntax, BM25, snippets, update/index mechanics |
| TOOL-21 | [SQLite copyright](https://sqlite.org/copyright.html) | Official statement | Public-domain posture |
| TOOL-22 | [DuckDB FTS](https://duckdb.org/docs/stable/core_extensions/full_text_search) | Official docs | BM25/stemming and non-auto-updating index warning |
| TOOL-23 | [Tantivy](https://github.com/quickwit-oss/tantivy) | First-party source | Embedded Rust search and MIT license |
| TOOL-24 | [Meilisearch license](https://github.com/meilisearch/meilisearch/blob/main/LICENSE) | First-party source | Current mixed MIT/BUSL-1.1 license |
| TOOL-25 | [Typesense](https://github.com/typesense/typesense) | First-party source | Search-server implementation/license surface |
| TOOL-26 | [Obsidian local files](https://help.obsidian.md/Files+and+folders/How+Obsidian+stores+data) | Official docs | Local vault/file behavior |
| TOOL-27 | [Obsidian license](https://obsidian.md/license) | Official terms | Proprietary application/free-use terms |

## Parsing, OCR, metadata and skills

| ID | Source | Type | Supports |
|---|---|---|---|
| PARSE-01 | [Docling supported formats](https://docling-project.github.io/docling/usage/supported_formats/) | Official docs | Inputs, unified representation and JSON/Markdown/text outputs |
| PARSE-02 | [Docling agent skills](https://docling-project.github.io/docling/usage/agent_skills/) | Official docs | Packaged skill locations and supported agent conventions |
| PARSE-03 | [Docling skill source](https://github.com/docling-project/docling/blob/main/docling/.agents/skills/docling/SKILL.md) | First-party code | Actual skill instructions/router reference |
| PARSE-04 | [Docling license](https://github.com/docling-project/docling/blob/main/LICENSE) | First-party source | MIT |
| PARSE-05 | [GROBID docs](https://grobid.readthedocs.io/en/latest/) | Official docs | TEI, references/citation contexts, service and evaluation |
| PARSE-06 | [GROBID license](https://github.com/grobidOrg/grobid/blob/master/LICENSE) | First-party source | Apache-2.0 |
| PARSE-07 | [Apache Tika formats](https://tika.apache.org/3.3.0/formats.html) | Official docs | Broad parser, metadata, PDF/OCR and WARC/WACZ support |
| PARSE-08 | [Apache Tika license](https://github.com/apache/tika/blob/main/LICENSE.txt) | First-party source | Apache-2.0 |
| PARSE-09 | [OCRmyPDF docs](https://ocrmypdf.readthedocs.io/en/latest/) | Official docs | Searchable scanned-PDF workflow and operational constraints |
| PARSE-10 | [OCRmyPDF license](https://github.com/ocrmypdf/OCRmyPDF/blob/main/LICENSE) | First-party source | MPL-2.0 |
| PARSE-11 | [Tesseract](https://github.com/tesseract-ocr/tesseract) | First-party source | OCR code and Apache-2.0 license |
| SKILL-01 | [zirui-song/claude-skills](https://github.com/zirui-song/claude-skills) | Community source | Evaluated only for own code/license/maturity; not used for external claims |
| SKILL-02 | [third-party Zotero MCP / Cite Caddy](https://github.com/herbertkokholm/zotero-mcp) | Community source | Evaluated only as an agent wrapper candidate |

Repository HEADs observed with `git ls-remote` on 2026-08-23: Docling `e1cb2b234c48ff29746b0f2f843d07f8e23905a0`; Karakeep `7ca5ee236b96cd659096b1530c5be3fdcd8e4470`; Zotero translators `56eaac33b15494b35dc3dbf86039350e4e1a9166`; `zirui-song/claude-skills` `ab1129a886287aa6c19e544c9f218cb4214816a3`; third-party Zotero MCP `82ae5cc0b1b6ed5fec373724b8ef2ff38e8d8421`. These are observation pins, not recommended dependency versions.

## Financial corpora and metadata

| ID | Source | Authority | Supports |
|---|---|---|---|
| DATA-01 | [SEC EDGAR APIs/bulk ZIPs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) | SEC | No-key APIs, real-time updates and nightly bulk submissions/company facts |
| DATA-02 | [SEC Financial Statement Data Sets](https://www.sec.gov/dera/data/financial-statement-data-sets.html) | SEC DERA | Quarterly flattened XBRL datasets and historical range |
| DATA-03 | [SEC privacy/copying notice](https://www.sec.gov/about/privacy-information) | SEC | Public information copying statement and cautions |
| DATA-04 | [SEC developer/fair-access resources](https://www.sec.gov/about/developer-resources) | SEC | Automated access policy |
| DATA-05 | [CFTC historical compressed COT](https://www.cftc.gov/MarketReports/CommitmentsofTraders/HistoricalCompressed/index.htm) | CFTC | Complete annual compressed historical report files |
| DATA-06 | [BIS bulk downloads](https://data.bis.org/bulkdownload) | BIS | Topic-level CSV/SDMX bulk files |
| DATA-07 | [BIS terms](https://www.bis.org/terms_conditions.htm) | BIS | Use/attribution terms |
| DATA-08 | [Eurostat copyright/reuse](https://ec.europa.eu/eurostat/en/web/main/help/copyright-notice) | European Commission/Eurostat | Reuse posture and third-party exceptions |
| DATA-09 | [Eurostat database](https://ec.europa.eu/eurostat/web/main/data/database) | Eurostat | Dataset/bulk access |
| DATA-10 | [ECB bulk downloads](https://data.ecb.europa.eu/help/bulk-download) | ECB | Dataflow bulk mechanism |
| DATA-11 | [Bundesbank SDMX API](https://statistiken.bundesbank.de/statistiken-de/hilfe-970224?article=bundesbank-sdmx-web-service-api-991208) | Deutsche Bundesbank | Full and `preparedAfter` incremental dataflow access |
| DATA-12 | [Destatis Open Data](https://www.destatis.de/EN/Service/OpenData/api-webservice.html) | Destatis | German official-statistics APIs |
| DATA-13 | [World Bank terms](https://data.worldbank.org/summary-terms-of-use) | World Bank | CC BY default plus exceptions |
| DATA-14 | [GLEIF Golden Copy](https://www.gleif.org/en/lei-data/gleif-golden-copy/download-the-golden-copy) | GLEIF | Full LEI files and delta schedules |
| DATA-15 | [DataCite public data file](https://support.datacite.org/docs/datacite-public-data-file) | DataCite | Annual CC0 metadata file mechanism |
| DATA-16 | [DataCite 2025 public file](https://datafiles.datacite.org/datafiles/public-2025) | DataCite | Exact record count, compressed/expanded size and checksum |
| DATA-17 | [Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/) | Crossref | Public DOI metadata API and usage guidance |
| DATA-18 | [RePEc data acquisition](https://ideas.repec.org/getdata.html) | RePEc | Distributed metadata access and anti-scraping guidance |
| DATA-19 | [GovInfo developers](https://www.govinfo.gov/developers) | US GPO | Official APIs/bulk collections |
| DATA-20 | [Federal Register API](https://www.federalregister.gov/developers/documentation/api/v1) | Office of the Federal Register | No-key document metadata/rendition links and official/unofficial distinction |
| DATA-21 | [FIBO license/repository](https://github.com/edmcouncil/fibo/blob/master/LICENSE) | EDM Council | MIT-licensed ontology distribution |
| DATA-22 | [FRED series license guidance](https://fred.stlouisfed.org/docs/api/fred/licenses/series.html) | Federal Reserve Bank of St. Louis | Series-specific third-party licensing warning |
| DATA-23 | [FRED API terms](https://fred.stlouisfed.org/docs/api/terms_of_use.html) | Federal Reserve Bank of St. Louis | API/key/use/copyright terms |
| DATA-24 | [IMF API](https://data.imf.org/en/Resource-Pages/IMF-API) | IMF | SDMX API access |
| DATA-25 | [OECD API](https://www.oecd.org/en/data/insights/data-explainers/2024/09/api.html) | OECD | SDMX data API mechanism |
| DATA-26 | [filings.xbrl.org API](https://filings.xbrl.org/docs/api) | XBRL International platform docs | ESEF filing API behavior and limitations |
| DATA-27 | [ESMA registers/FIRDS](https://registers.esma.europa.eu/publication/details?core=esma_registers_firds) | ESMA | Instrument-reference file access |
| DATA-28 | [OpenFIGI API](https://www.openfigi.com/api) | Bloomberg/OpenFIGI | Identifier-mapping API and terms surface |

## Citation verification notes

- Consequential feature claims were tied to official docs or first-party source/license pages, not search-result snippets.
- GitHub branch URLs are intentionally live for current license/code inspection; observed HEAD hashes above make the evidence date explicit.
- Dataset licensing statements are conservative. Where one portal aggregates third-party content (SEC exhibits, FRED series, World Bank datasets, abstracts), the deliverables preserve the exception instead of asserting a blanket license.
- Size statements are qualitative unless the official provider supplies an exact figure. DataCite and SEC 2026 Q1 are the only exact file-size examples used.
- Architecture scores are labeled judgments rather than facts and point to `TOOL_LANDSCAPE.md`/`DOWNLOADABLE_FINANCIAL_CORPORA.md` for their evidence basis.
