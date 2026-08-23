# Downloadable Financial Corpora

**Evidence date:** 2026-08-23. This is an architecture/licensing screen, not legal advice. “Downloadable” means the provider offers bulk files or a complete enumerated collection; it does not erase third-party rights in filings, abstracts or attachments. Retain each provider's current terms URL and dataset metadata at acquisition time.

## Classification rules

- **FULLY DOWNLOADABLE:** official bulk files or a complete, enumerable public collection can be mirrored under stated terms.
- **INCREMENTALLY ARCHIVABLE:** lawful official items can be captured as published, but no stable complete bulk corpus exists or rights are item-specific.
- **API-ONLY:** programmatic retrieval is supported, but full mirroring is not offered, practical or uniformly licensed.
- **NOT LEGALLY/PRACTICALLY ARCHIVABLE:** a bulk mirror would violate/strain rights, access controls, contracts or proportionality.

Size is planning-scale, not a quota: `tiny` <1 GB, `medium` 1–100 GB, `large` >100 GB, or `unbounded`. Exact size is recorded only where the publisher supplies it.

## FULLY DOWNLOADABLE

| Corpus | Bulk/API mechanism and update | Rights posture | Approx. size / readability | Provenance and IPOS relevance | Decision |
|---|---|---|---|---|---|
| SEC EDGAR submissions + company facts | Nightly `submissions.zip` and `companyfacts.zip`; JSON APIs update throughout the day | SEC site says public information may be copied/distributed; filing exhibits can contain third-party material, so preserve source/terms per artifact; fair-access policy applies | Medium and growing; JSON, XBRL facts | First-party regulator, accession/CIK identity. Very high for issuer fundamentals, events and source linking | **Download selected bulk indexes/facts now**; retrieve filings by tracked issuers/events |
| SEC Financial Statement Data Sets | Quarterly ZIPs from 2009; current page includes 2026 Q1 (81.31 MB) | SEC data terms/disclaimers; flattened data is not a substitute for filing review | Several GB historical; tab-delimited derived XBRL | First-party regulator; high for reproducible statement research, but dimensional detail is flattened | **Download quarterly incrementally** if statement research is in scope |
| CFTC Commitments of Traders historical compressed files | Complete annual ZIPs by report format; new files published on report schedule/year | US government data; preserve CFTC notices and report methodology | Tiny/medium; text/CSV-like files | First-party market-positioning data; high for existing sentiment/positioning playbook | **Download relevant report families now** |
| BIS Data Portal topics | Official bulk-download page offers topic-level ZIPs in CSV and SDMX forms; refresh with portal releases | BIS terms apply; retain terms snapshot and dataset attribution | Medium selected, potentially large all topics; CSV/SDMX | First-party international institution; high for credit, debt, liquidity, FX, property and central-bank series | **Download only selected topics** |
| Eurostat datasets | Data Browser/bulk facility and APIs; datasets are versioned/updated on publication schedules | Commission reuse notice generally permits reuse with attribution, subject to identified third-party exceptions | Medium selected, very large whole estate; TSV/SDMX/CSV/JSON | Official EU statistics with dataset/geo/time IDs; high for Europe macro | **Mirror an allowlist, not everything** |
| ECB Data Portal dataflows | Official bulk downloads by dataflow plus SDMX API | ECB copyright/reuse terms and series metadata apply | Medium selected; CSV/SDMX | First-party central bank; high for euro-area rates, monetary and financial data | **Mirror selected dataflows** |
| Deutsche Bundesbank statistical dataflows | SDMX REST supports full dataflow retrieval and `preparedAfter` incremental filtering; large-data ZIP route documented | Bundesbank data/service terms apply; retain dataflow metadata | Medium selected; CSV/JSON/XML SDMX | First-party national central bank; high for German/euro-area detail | **Mirror selected dataflows and deltas** |
| World Bank open datasets | Dataset pages/API and downloadable archives for many products | Default summary terms use CC BY 4.0 except separately identified/third-party content | Medium selected, very large whole catalog; CSV/JSON | First-party institution and strong dataset metadata; medium/high long-horizon macro relevance | **Download named open datasets only** |
| GLEIF Golden Copy | Daily full LEI Golden Copy plus delta files for shorter windows | Public LEI-data terms must travel with snapshot; no inference to proprietary security IDs | Medium and growing; CSV/XML/JSON/RDF distributions vary by file | First-party GLEIF, LEI/relationship identity; very high for deterministic entity resolution | **Download latest full + daily deltas** |
| DataCite public DOI metadata file | Annual public JSONL-GZIP file plus APIs; 2025 file reports 108,468,906 records, 33 GiB compressed and 615 GiB decompressed | Public metadata file is CC0; some described works remain copyrighted | Large; JSONL | Excellent DOI provenance, but finance is a tiny fraction | **Do not download full file initially**; use targeted API/export; bulk only with demonstrated need |
| RePEc bibliographic metadata | Distributed archive templates and mirrored metadata; provider documents obtaining data rather than scraping IDEAS | RePEc archive terms and provider rights apply; metadata is not a license to hosted full text | Medium metadata; tagged text/ReDIF | Strong economics working-paper coverage, distributed provenance | **Mirror finance/economics metadata selectively**, link to lawful full text |
| GovInfo official publications/bulk data | Official bulk-data directories/APIs for CFR, bills, Congressional and other collections | US government/publication terms; package metadata and rendition status preserved | Medium/large by collection; XML, MODS, PDF, text | Authoritative laws/regulations/publication packages | **Download only market-relevant collections/updates** |
| FIBO ontology | Public versioned Git repository/releases | MIT license | Tiny; OWL/RDF | Curated financial concepts and identifiers; useful vocabulary, not market facts | **Download/version-pin as optional taxonomy input** |

Sources: [SEC EDGAR APIs and nightly bulk archives](https://www.sec.gov/search-filings/edgar-application-programming-interfaces), [SEC Financial Statement Data Sets](https://www.sec.gov/dera/data/financial-statement-data-sets.html), [SEC privacy/copying notice](https://www.sec.gov/about/privacy-information), [SEC fair-access guidance](https://www.sec.gov/about/developer-resources), [CFTC historical compressed COT](https://www.cftc.gov/MarketReports/CommitmentsofTraders/HistoricalCompressed/index.htm), [BIS bulk downloads](https://data.bis.org/bulkdownload), [BIS terms](https://www.bis.org/terms_conditions.htm), [Eurostat copyright/reuse](https://ec.europa.eu/eurostat/en/web/main/help/copyright-notice), [Eurostat database/download](https://ec.europa.eu/eurostat/web/main/data/database), [ECB bulk downloads](https://data.ecb.europa.eu/help/bulk-download), [Bundesbank SDMX service](https://statistiken.bundesbank.de/statistiken-de/hilfe-970224?article=bundesbank-sdmx-web-service-api-991208), [World Bank terms](https://data.worldbank.org/summary-terms-of-use), [GLEIF Golden Copy/deltas](https://www.gleif.org/en/lei-data/gleif-golden-copy/download-the-golden-copy), [DataCite public data file](https://support.datacite.org/docs/datacite-public-data-file), [2025 DataCite file dimensions/checksum](https://datafiles.datacite.org/datafiles/public-2025), [RePEc data acquisition](https://ideas.repec.org/getdata.html), [GovInfo developer/bulk resources](https://www.govinfo.gov/developers), [FIBO repository/license](https://github.com/edmcouncil/fibo/blob/master/LICENSE).

## INCREMENTALLY ARCHIVABLE

| Source family | Mechanism/update | Rights and practical limit | Readability/provenance | IPOS decision |
|---|---|---|---|---|
| Individual SEC filing documents and exhibits | Enumerate from submissions/indexes; retrieve official filing URLs on event/issuer updates | Regulator access is stable, but incorporated exhibits may contain third-party rights; do not republish indiscriminately | HTML, inline XBRL, XML, text, PDF exhibits; accession-level provenance | Archive filings for tracked universe and evidence used in decisions |
| Corporate investor-relations releases and presentations | Official RSS/email/site polling; prefer SEC 8-K Exhibit 99.1 where duplicated | Site terms and presentation/media rights vary; no universal corpus license | HTML/PDF with publisher URL/time/hash | Archive only tracked issuers and cited artifacts |
| Official earnings calls/materials | Company webcast, prepared remarks or transcript when explicitly downloadable | Availability and rights vary; audio transcription does not create redistribution rights | PDF/HTML/audio; strong issuer provenance but speaker/transcript accuracy varies | Capture lawful official materials; prefer filed release and prepared remarks |
| Central-bank publications/research | Official RSS/search/API/site collections, with PDF/HTML downloads | Publication rights/third-party figures differ by institution; bulk crawling is unnecessary | High-provenance PDFs/HTML with publication IDs | Archive documents cited by tracked themes/indicators |
| National statistics releases | RSS/release calendars and dataset APIs | Dataset may be open while release graphics/third-party content differ | HTML/PDF/CSV; official release timestamp | Archive selected releases that explain observed regime changes |
| Federal Register documents | No-key API provides metadata and rendition links; add new/revised documents as published | Federal Register API output is unofficial; cite official PDF/GovInfo rendition for authority | JSON/XML/HTML/PDF, document number | Archive market-relevant final/proposed rules and official rendition |
| Open-access finance/economics papers | DOI/RePEc/DataCite metadata, then publisher/repository open-access URL | Metadata openness does not grant PDF redistribution; verify license per work | PDF/JATS/metadata, DOI/version | Archive only clearly licensed manuscripts; otherwise metadata/link only |
| ESMA instrument-reference files (FIRDS) | Daily downloadable files/register | Very high volume and limited value outside EU instrument mapping; terms and schema changes need monitoring | XML/CSV-style regulator files, official IDs | Archive only required slices/date windows if an EU identifier need exists |

Sources: [Federal Register API](https://www.federalregister.gov/developers/documentation/api/v1), [ESMA registers/FIRDS](https://registers.esma.europa.eu/publication/details?core=esma_registers_firds), [SEC EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces), [DataCite REST guidance](https://support.datacite.org/docs/api).

## API-ONLY

| Corpus/service | API/update | Licensing/practical issue | Readability/provenance | IPOS decision |
|---|---|---|---|---|
| FRED/ALFRED series and releases | Keyed API; series, observations, vintages/releases; FRED API v2 supports full-release histories | FRED explicitly states series can be third-party copyrighted; users must check each series. Notes are copyrighted and API terms apply | JSON/XML; excellent series metadata and provenance | Keep existing IPOS allowlist/connectors; archive only permitted series outputs, not a FRED mirror |
| IMF Data API | SDMX 2.1/3.0 API and portal exports | No single verified open bulk/licensing contract was established for the whole estate; dataset terms vary | SDMX/CSV/JSON; official | Query/download selected datasets after terms review; do not mirror all IMF data |
| OECD Data Explorer API | SDMX API with dataset/dataflow discovery | Whole-platform bulk and redistribution posture is not uniform in the reviewed docs | SDMX/CSV/JSON; official | Query selected dataflows and cache permitted responses |
| Crossref REST metadata | Public REST API with polite pool; public data file also exists but is operationally very large | Most bibliographic metadata is open; abstracts can retain copyright and full dump is disproportionate | JSON; DOI-level provenance | Use DOI lookup incrementally; no whole dump initially |
| filings.xbrl.org / ESEF API | Paginated API for filings metadata/files | Availability depends on source registers and filings can be withdrawn; site/API terms and issuer content rights apply | JSON plus XBRL packages; strong filing/entity links | Query selected EU issuers; do not treat aggregator as immutable authority |
| OpenFIGI | API maps identifiers under service terms/rate limits | Proprietary service terms and usage limits; not a free bulk security master | JSON; useful mapping response provenance | Use only if required and retain mapping receipt; prefer official identifiers |

Sources: [FRED API license guidance](https://fred.stlouisfed.org/docs/api/fred/licenses/series.html), [FRED API terms](https://fred.stlouisfed.org/docs/api/terms_of_use.html), [IMF API](https://data.imf.org/en/Resource-Pages/IMF-API), [OECD API explainer](https://www.oecd.org/en/data/insights/data-explainers/2024/09/api.html), [Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/), [filings.xbrl.org API](https://filings.xbrl.org/docs/api), [OpenFIGI API](https://www.openfigi.com/api).

## NOT LEGALLY/PRACTICALLY ARCHIVABLE

| Source family | Why not | Safe alternative |
|---|---|---|
| Commercial earnings-transcript databases | Subscription/access does not imply bulk-download or redistribution rights; anti-bot/access controls and database rights may apply | Official company prepared remarks/webcast where terms allow; SEC 8-K earnings release; metadata/link-only |
| Paywalled news/newsletters/research | Copyright and subscription terms are item/provider-specific; full mirror has no general legal basis | Save citation metadata, a lawful personal copy only when terms permit, and operator notes/short quotations |
| Social-network firehoses and closed communities | Platform API/retention/display terms, deleted-content rules and privacy make durable general archiving unsafe | Store URL, author/time and operator note; use official licensed API only for bounded need |
| Proprietary real-time exchange feeds and security masters | Contractual entitlements, redistribution restrictions and ongoing fees | Store licensed derived identifiers only as permitted; prefer GLEIF, regulator files and issuer/exchange public reference endpoints |
| “All internet finance PDFs” or shadow-library corpora | Copyright, provenance and malicious-file risk; no controlled update or rights model | Curated allowlisted official/open sources with per-artifact receipts |
| Generated summaries/claims as a corpus of truth | Model output is not a source, can omit/alter facts and has no source preservation value | Keep as rebuildable, labeled derivative linked to exact sources and review status |

## Recommended acquisition set

### Download now (bounded bootstrap)

1. SEC submissions/company-facts bulk archives plus the current tracked-company ticker mapping; do **not** fetch every filing body.
2. CFTC COT historical files for report families used by the sentiment/positioning playbook.
3. Latest GLEIF Golden Copy and subsequent daily deltas for entity identity.
4. The specific BIS, ECB, Eurostat, Bundesbank and World Bank datasets that overlap current IPOS indicators or declared research questions.
5. Version-pinned FIBO only if taxonomy/ontology mapping is actually used; otherwise defer.

### Archive incrementally

- Filings and 8-K exhibits for tracked issuers/events.
- Official central-bank/statistical releases tied to monitored series/regime changes.
- Corporate IR releases/presentations actually reviewed.
- Relevant final/proposed regulations with an official rendition.
- Open-access papers whose license is recorded.

### Query rather than mirror

- FRED/ALFRED, IMF, OECD, Crossref, ESEF and OpenFIGI.
- DataCite's complete public file: it is legally downloadable but disproportionate (33 GiB compressed/615 GiB expanded for the 2025 file). Use targeted metadata until a measured corpus-wide need exists.

### Do not store

- Unauthorized commercial transcripts, paywall copies, proprietary feeds or social firehoses.
- Every version of low-value API responses without a retention reason.
- Duplicate transformed files that can be regenerated from an original plus pinned parser.
- Credentials, private portfolio snapshots or brokerage exports in the general evidence corpus.
- Model-generated text as if it were external evidence.

## Update and provenance controls

Every source connector needs a short declarative policy: base URL/domain allowlist, provider terms URL, user agent/rate limit, collection scope, update cursor, retention class, expected MIME/size, canonical identifier, rights status and checksum behavior. A weekly job may discover candidates, but downloads outside the allowlist or beyond the expected size go to review. For mutable bulk files, store provider checksum when offered plus local SHA-256; record dataset release/vintage, not just download date.
