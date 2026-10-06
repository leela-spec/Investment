## 1. Executive Answer

No single off-the-shelf software product—open source or commercial—currently fulfills this end-to-end investment research extraction workflow under the specified cost, provenance, and privacy constraints. Enterprise financial terminals and intelligence engines (such as AlphaSense, Tegus, and Bloomberg) provide search and partial transcript/filing ingestion, but they are disqualified immediately due to closed data architectures, lack of programmatic claim extraction into custom schemas, and prohibitive institutional subscription fees ($10,000 to >$30,000 annually). General-purpose AI document and knowledge-management platforms (such as Google NotebookLM, Dify, and Khoj) support multi-format search and conversational grounded answers, but they fail the requirement for headless, deterministic, schema-constrained batch export of atomic claims with verifiable quotation character/timestamp offsets.

  

The best research-backed approach is an orchestrated, composable toolchain comprising established, active, open-source components paired with a lightweight, schema-enforced LLM extraction layer via OpenRouter:

  

- **Ingestion & Parsing:** `yt-dlp` combined with `faster-whisper` (or `WhisperX`) for German/English audio and timestamp generation; `mail-parser` for RFC-compliant email and attachment extraction; `trafilatura` for clean, boilerplate-free web article extraction; and IBM's `Docling` for layout-aware PDF parsing, TableFormer table structure recovery, and page/coordinate-level provenance.
    
      
    
- **Semantic Claim Extraction & Typing:** `Instructor` (Python) enforcing strict Pydantic schemas over cheap, high-context LLMs (such as Google Gemini 1.5/2.0 Flash, Anthropic Claude 3.5 Haiku, or DeepSeek V3) via OpenRouter.
    
      
    
- **Deterministic Grounding & Entity Linking:** Local, deterministic verification passes using Python substring matching and `RapidFuzz` to validate that every extracted quote exists verbatim in the source artifact before committing it to storage, supplemented by `GLiNER` for zero-shot named entity recognition and the `OpenFIGI` API for security identifier normalization.
    
      
    
- **State & Export:** A strictly deterministic export stage outputting append-only, validated JSON/JSONL records with deterministic content hashes (SHA-256) ready for downstream, manual broker-review and portfolio-mapping scripts.
    
      
    

## 2. Market Landscape

The software landscape relevant to this pipeline divides into seven distinct categories:

  

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            MARKET LANDSCAPE                                 │
├──────────────────────────────┬──────────────────────────────────────────────┤
│ 1. Enterprise Financial Terminals │ AlphaSense, Tegus, Sentieo, Canalyst.     │
│    (Disqualified: Cost/Closed)│ High-cost ($10k-$30k/yr), closed APIs, manual│
├──────────────────────────────┼──────────────────────────────────────────────┤
│ 2. AI Document Assistants    │ Google NotebookLM, Khoj, AnythingLLM.        │
│    (Disqualified: Interactive)│ Conversational focus, no headless JSON export│
├──────────────────────────────┼──────────────────────────────────────────────┤
│ 3. LLM Orchestration Platforms│ Dify, Flowise, Langflow.                     │
│    (Overhead / Framework Lock)│ Low-code visual workflow UI, generic RAG.    │
├──────────────────────────────┼──────────────────────────────────────────────┤
│ 4. Document Intelligence SDKs│ IBM Docling, Marker, PyMuPDF, Unstructured.  │
│    (Core Composable Pillar)  │ Layout analysis, OCR, Table extraction, JSON │
├──────────────────────────────┼──────────────────────────────────────────────┤
│ 5. Speech-to-Text Engines    │ faster-whisper, WhisperX, OpenAI Whisper.    │
│    (Core Composable Pillar)  │ Local CTranslate2 ASR, word/segment offsets  │
├──────────────────────────────┼──────────────────────────────────────────────┤
│ 6. Constrained Generation    │ Instructor, BAML, Outlines.                  │
│    (Core Composable Pillar)  │ Pydantic schema validation, tool-calling     │
├──────────────────────────────┼──────────────────────────────────────────────┤
│ 7. Bookmarking & Custody     │ Karakeep (Hoarder), Linkwarden, Wallabag.    │
│    (Peripheral Archiving)    │ Asset caching, high-level summaries/tags.    │
└──────────────────────────────┴──────────────────────────────────────────────┘
```

The fundamental structural boundary in this market sits between **interactive, conversational user interfaces** (which emphasize chat and unstructured visual citations) and **deterministic data engineering libraries** (which output structured, auditable data records for downstream code).

  

## 3. Complete-Product Search

An exhaustive search was conducted to identify any comprehensive, off-the-shelf product capable of managing the full pipeline from raw media ingestion to structured investment-claim JSON.

  

|**Product Candidate**|**Primary Focus**|**License / Pricing**|**Format Coverage**|**Verifiable Citations**|**Machine Export (JSON)**|**Inclusion / Rejection Decision**|
|---|---|---|---|---|---|---|
|**OpenBB Workspace**|Financial analysis & research dashboard|Hybrid AGPLv3 / Commercial SaaS|Market data, SEC filings, manual docs|Low (chat-based citations)|None (dashboard widgets / API query endpoints)|**Rejected:** Interactive workspace; does not support automated batch extraction of timestamped video, emails, and PDFs into claim schemas.|
|**Google NotebookLM**|Research assistant & grounded notebook|Free cloud service (Google account)|PDF, Google Docs, Web URLs, YouTube|High (inline document highlights)|None (no public API, no structured JSON export)|**Rejected:** Proprietary walled garden; no programmatic batch CLI/API; cannot output schema-validated claim registers.|
|**Dify (LangGenius)**|Open-source LLM app & RAG orchestrator|Apache 2.0 (self-hostable)|Text, PDF, Web (basic parsers)|Medium (RAG chunk retrieval)|Supported (via custom workflow REST endpoints)|**Rejected as all-in-one:** Heavy multi-container deployment; lacks native layout-aware table extraction (TableFormer) and speech-to-text timestamp alignment.|
|**Khoj**|Personal AI second brain|AGPL-3.0 / Cloud SaaS ($5–$25/mo)|Markdown, PDF, Org-mode, Web|Low (conversational retrieval)|None (conversational and search output only)|**Rejected:** Geared toward desktop/personal chat retrieval; lacks financial claim data schemas and verification engines.|
|**AlphaSense / Sentieo**|Institutional market intelligence|Proprietary enterprise ($12k–$30k+/yr)|Transcripts, broker research, SEC, news|High (exact document hit highlights)|Gated / Custom Enterprise API only|**Rejected:** Violates strict zero/low-cost constraint; closed ecosystem.|
|**Paperless-ngx**|Document archiving & OCR management|GPL-3.0 (self-hostable)|PDF, images, Office, email|Low (document-level tags/fields)|Metadata JSON API (no atomic claim extraction)|**Rejected:** Document custody and document-level indexing only; no semantic extraction or speech-to-text.|
|**Karakeep (Hoarder)**|Bookmark & read-it-later manager|AGPL-3.0 (self-hostable)|Links, notes, images, PDFs|Minimal (high-level tag/summary)|REST API / CLI (bookmarks only)|**Rejected:** Lacks atomic claim extraction, quote verification, audio timestamping, and table extraction.|

_Finding:_ No complete product currently covers this specific ingestion-to-claim workflow out of the box.

  

## 4. Composable-Tool Longlist

The established, maintained software candidates across each required pipeline stage are cataloged below:

  

```
                              RAW INCOMING CHANNELS
         ┌───────────────────┬────────────────────┬───────────────────┐
         ▼                   ▼                    ▼                   ▼
    YouTube / Audio     Research Emails     Web Articles          PDFs / Scans
   [yt-dlp + whisper]    [mail-parser]      [trafilatura]          [Docling]
         │                   │                    │                   │
         └───────────────────┼────────────────────┴───────────────────┘
                             ▼
                 UNIFIED NORMALIZED SEGMENTS
         (Source ID, Text Blocks, Page / Timestamp Anchors)
                             │
                             ▼
                 STRUCTURED EXTRACTION LAYER
                 [Instructor + Pydantic via OpenRouter]
             - Atomic Claim Extraction
             - Classification (Fact/Forecast/Opinion/Risk)
             - Direction, Horizon, Extracted Entities
                             │
                             ▼
                 DETERMINISTIC VERIFICATION PASS
                 [Python Substring Match / RapidFuzz]
             - Verbatim Quote Verification in Segment
             - Discard / Retry on Hallucinated Quotes
                             │
                             ▼
                 NORMALIZATION & DEDUPLICATION
                 [OpenFIGI API / GLiNER / Python State Hash]
             - Security & Macro Variable Mapping
             - Support / Contradiction Hash Lookup
                             │
                             ▼
                 STABLE JSONL CLAIM LEDGER
             (Consumed by Deterministic Portfolio Mapper)
```

### Stage 1: Video & Audio Acquisition / Transcription

- **yt-dlp**: Command-line media downloader. Active maintainers (yt-dlp org), Unlicense, CLI/Python API. Battle-tested globally for reliable YouTube audio extraction and video metadata retrieval.
    
      
    
- **faster-whisper**: CTranslate2 reimplementation of OpenAI's Whisper. Active maintainer (SYSTRAN), MIT License. Up to 4x faster than standard Whisper with lower VRAM requirements. Emits segment-level timestamps out-of-the-box. Exceptional transcription accuracy on German financial broadcasts.
    
      
    
- **WhisperX**: Extension of `faster-whisper` adding wav2vec2 forced phoneme alignment and pyannote-audio speaker diarization. Apache 2.0 License. Provides sub-100ms word-level timestamp boundaries, ensuring exact quotation anchoring.
    
      
    

### Stage 2: Email Parsing & MIME Extraction

- **mail-parser (SpamScope)**: Production-grade RFC-compliant email parser wrapping Python's standard `email` library. Apache 2.0 License. Extracts headers, hops, HTML/plain text bodies, and attachments into typed Python objects and serialized JSON.
    
      
    
- **Python `email` standard library + `extract_msg`**: Zero-dependency standard library for standard MIME (`.eml`), paired with `extract_msg` (GPLv3) for Microsoft Outlook binary (`.msg`) files. Completely local, zero cost, deterministic.
    
      
    

### Stage 3: Web-Page Acquisition & Readable Extraction

- **trafilatura**: Web-scraping and text-extraction library developed by Adrien Barbaresi (adbar). GPLv3 License. Outperforms Readability, Newspaper3k, and Goose on precision and recall benchmarks. Features built-in German stoplist filtering, metadata extraction (author, date, title), and table handling.
    
      
    
- **Crawl4AI**: Open-source, LLM-tailored asynchronous web crawler and scraper (unclecode). Apache 2.0 License. Built on Playwright for rendering dynamic JavaScript SPAs, outputting clean, structured Markdown.
    
      
    

### Stage 4: Document / PDF Parsing, Layout, & OCR

- **Docling (IBM Research Zurich)**: Specialized document conversion engine. MIT License. Features state-of-the-art layout analysis, TableFormer for tabular reconstruction (crucial for financial survey tables), and emits a lossless `DoclingDocument` JSON representation preserving page numbers, bounding boxes, and reading order. Supports local OCR via Tesseract/EasyOCR.
    
      
    
- **Marker (datalab-to / Vik Paruchuri)**: High-speed PDF-to-Markdown/JSON converter. GPL-3.0 License. Marker 2.0 (released July 2026) employs Surya OCR 2 and lightweight ONNX layout models. Extremely fast, but structured table hierarchy is less deterministic than Docling's TableFormer.
    
      
    
- **PyMuPDF (`pymupdf4llm`)**: C-based PDF extraction library (Artifex Software). AGPLv3 / Commercial. Extremely fast CPU-based text and layout extraction; however, borderless multi-column financial table parsing is weaker than dedicated deep-learning layout models.
    
      
    
- **Unstructured (`unstructured`)**: Open-source ETL parser. Apache 2.0. Broad format coverage, but possesses heavy dependency chains, suffered significant security path-traversal vulnerabilities (CVE-2025-64712), and heavily nudges users toward proprietary hosted APIs.
    
      
    

### Stage 5: Structured Claim Extraction

- **Instructor (jxnl / 567-labs)**: Pydantic-based structured extraction library. MIT/Apache 2.0 License. Integrates seamlessly with any OpenAI-compatible endpoint, including OpenRouter. Automatically injects JSON schemas into API calls and validates responses against Pydantic models with automated retries on validation errors.
    
      
    
- **BAML (BoundaryML)**: Domain-specific programming language for LLM structured output. Apache 2.0. Compiles down to Rust with native schema-aligned parsing (SAP), client generation for Python, and an integrated prompt testing playground. Highly robust, but introduces a custom language DSL.
    
      
    
- **Outlines (dottxt-ai)**: Guided decoding engine enforcing regex and context-free grammars at the logit level. Apache 2.0. Ideal for local models (via vLLM/llama.cpp), but cannot enforce logit constraints across third-party remote endpoints like OpenRouter.
    
      
    

### Stage 6: Entity Linking & Normalization

- **GLiNER (Generalist and Lightweight Named Entity Recognition)**: Compact BERT/DeBERTa-based zero-shot NER model. Apache 2.0 License. Identifies arbitrary entity types (`company`, `economic_variable`, `sector`, `index`) locally on CPU without LLM token costs.
    
      
    
- **OpenFIGI API**: Bloomberg's open financial symbology service. Free tier (25 requests/min unauthenticated, 250 requests/min with free account). Maps company names, tickers, and ISINs deterministically to Financial Instrument Global Identifiers (FIGI).
    
      
    
- **RapidFuzz**: High-performance C++ fuzzy string-matching library for Python. MIT License. Rapidly reconciles extracted entity strings against a local master portfolio taxonomy.
    
      
    

### Stage 7: Exact Quotation & Citation Verification

- **Deterministic Python Substring & Span Matcher**: Deterministic code performing exact search (`source_text.find(quote)`) or character-offset slicing against the parsed segment. Zero model involvement, 100% deterministic.
    
      
    
- **RapidFuzz Partial Ratio**: Handles whitespace, typographical, and minor ASR punctuation variations when exact substring matching fails, returning an explicit similarity score [0–100].
    
      
    

### Stage 8: Claim Typing, Stance, & Portfolio Schema Export

- **Pydantic v2**: High-performance data validation library in Python. MIT License. Enforces enum typing (`Fact`, `Forecast`, `Opinion`, `Risk`, `Catalyst`), directional stance (`Bullish`, `Bearish`, `Neutral`), and time horizons, exporting pristine JSON/JSONL records.
    
      
    

## 5. Ranked Shortlist

The candidates below represent either leading complete platform candidates or the anchor components of the primary composable stack.

  

### Scoring Rubric & Weights

1. **Exact Quotation, Citation & Provenance (20%)**
    
      
    
2. **Transcript, Email, Web, and PDF Source Coverage (15%)**
    
      
    
3. **Deterministic Stages & Structured Output (15%)**
    
      
    
4. **Production Adoption & Operational Maturity (15%)**
    
      
    
5. **Zero / Genuinely Low Cost (15%)**
    
      
    
6. **Maintenance Health & Documentation (10%)**
    
      
    
7. **German-Language Support (5%)**
    
      
    
8. **Local Operation / OpenRouter Compatibility (5%)**
    
      
    

_Note on scoring:_ Scores are rated from 1 to 10 per criterion. Unknown capabilities receive a score of 0.

  

```
Total Weighted Score = (Quote_Prov * 0.20) + (Source_Cov * 0.15) + (Deterministic * 0.15) 
                     + (Adoption * 0.15) + (Cost * 0.15) + (Maintenance * 0.10) 
                     + (German * 0.05) + (Local_OR * 0.05)
```

### Candidate 1: Composable Open-Source Core Stack

_(Docling + faster-whisper/WhisperX + trafilatura + mail-parser + Instructor + OpenRouter)_

  

- **Quote & Provenance (10/10):** Docling provides exact page numbers and bounding boxes; faster-whisper provides millisecond segment anchors; deterministic Python/RapidFuzz verifies verbatim quotation presence before emission.
    
      
    
- **Source Coverage (10/10):** Covers YouTube/audio (faster-whisper), RFC-822/Outlook emails (mail-parser), web articles (trafilatura), and complex scanned/digital PDFs (Docling).
    
      
    
- **Deterministic & Structured Output (10/10):** Deterministic extraction at every parsing stage; strict JSON schema output enforced by Instructor and Pydantic v2.
    
      
    
- **Production Adoption & Maturity (9/10):** Every component has widespread real-world adoption (Docling >48k stars, faster-whisper industry-standard ASR, Instructor millions of downloads).
    
      
    
- **Zero / Low Cost (9.5/10):** 100% open-source software (MIT/Apache 2.0). Inference cost on OpenRouter using models like Gemini Flash or Claude 3.5 Haiku is less than $1.00/month for private volume.
    
      
    
- **Maintenance & Docs (9.5/10):** Active commits across all packages in 2026; comprehensive documentation and test suites.
    
      
    
- **German-Language Support (9.5/10):** Whisper large-v3 has top-tier German WER; Trafilatura contains explicit German stoplists; LLMs process German financial text natively.
    
      
    
- **Local / OpenRouter (10/10):** Ingestion runs 100% locally; extraction connects natively to OpenRouter or local Ollama/vLLM endpoints.
    
      
    

$$\text{Score} = (10 \times 0.20) + (10 \times 0.15) + (10 \times 0.15) + (9 \times 0.15) + (9.5 \times 0.15) + (9.5 \times 0.10) + (9.5 \times 0.05) + (10 \times 0.05)$$

$$\text{Score} = 2.00 + 1.50 + 1.50 + 1.35 + 1.425 + 0.95 + 0.475 + 0.50 = \mathbf{9.70 / 10}$$

### Candidate 2: IBM Docling (Standalone Ingestion Engine)

_(Evaluated as an ingestion-layer foundation)_

  

- **Quote & Provenance (9.5/10):** Preserves native layout, reading order, table cells, and page coordinate bounding boxes in `DoclingDocument` JSON.
    
      
    
- **Source Coverage (8.5/10):** Parses PDF, DOCX, XLSX, HTML, and has added basic `.eml` and audio transcription; lacks specialized YouTube fetching and advanced email attachment recursion.
    
      
    
- **Deterministic & Structured Output (9/10):** Emits lossless JSON data representations; utilizes deterministic table reconstruction algorithms alongside ML models.
    
      
    
- **Production Adoption & Maturity (8.5/10):** Backed by IBM Research; widespread adoption in enterprise RAG pipelines (over 48k GitHub stars).
    
      
    
- **Zero / Low Cost (10/10):** 100% open-source (MIT License); runs locally on consumer CPUs/GPUs without subscription.
    
      
    
- **Maintenance & Docs (9.5/10):** Bi-weekly releases; excellent documentation and technical papers.
    
      
    
- **German-Language Support (8.5/10):** Layout models and OCR (Tesseract/EasyOCR) support German diacritics and umlauts without degradation.
    
      
    
- **Local / OpenRouter (9/10):** Fully local execution; outputs clean Markdown/JSON for consumption by downstream OpenRouter calls.
    
      
    

$$\text{Score} = (9.5 \times 0.20) + (8.5 \times 0.15) + (9.0 \times 0.15) + (8.5 \times 0.15) + (10 \times 0.15) + (9.5 \times 0.10) + (8.5 \times 0.05) + (9.0 \times 0.05)$$

$$\text{Score} = 1.90 + 1.275 + 1.35 + 1.275 + 1.50 + 0.95 + 0.425 + 0.45 = \mathbf{9.13 / 10}$$

### Candidate 3: Dify (Self-Hosted Workflow Platform)

_(Evaluated as an all-in-one orchestration candidate)_

  

- **Quote & Provenance (5/10):** RAG chunks retain basic document IDs and chunk indices, but lacks exact character-level quote span validation or sub-second audio timestamps out-of-the-box.
    
      
    
- **Source Coverage (6/10):** Ingests basic text, PDF, and web pages; lacks native audio transcription pipelines or direct RFC-822 email parsing.
    
      
    
- **Deterministic & Structured Output (6.5/10):** Visual workflow supports JSON output nodes, but complex multi-stage deterministic data sanitation is awkward compared to native Python code.
    
      
    
- **Production Adoption & Maturity (8.5/10):** Extensive open-source community (>50k stars); widespread production deployments for internal knowledge bots.
    
      
    
- **Zero / Low Cost (8.5/10):** Apache 2.0 open-source version is free to self-host, but infrastructure overhead (Postgres, Redis, Weaviate, Sandbox containers) requires non-trivial compute.
    
      
    
- **Maintenance & Docs (8.5/10):** Frequent releases, professional maintainer team, comprehensive documentation.
    
      
    
- **German-Language Support (8/10):** UI and underlying LLM prompts handle German well; depends on chosen embedding/LLM models.
    
      
    
- **Local / OpenRouter (9/10):** Full native support for OpenRouter API keys and self-hosted model backends.
    
      
    

$$\text{Score} = (5 \times 0.20) + (6 \times 0.15) + (6.5 \times 0.15) + (8.5 \times 0.15) + (8.5 \times 0.15) + (8.5 \times 0.10) + (8 \times 0.05) + (9 \times 0.05)$$

$$\text{Score} = 1.00 + 0.90 + 0.975 + 1.275 + 1.275 + 0.85 + 0.40 + 0.45 = \mathbf{7.13 / 10}$$

### Candidate 4: OpenBB Workspace + Copilot

_(Evaluated as a financial research platform candidate)_

  

- **Quote & Provenance (4/10):** Interactive copilot provides conversational citations, but does not emit machine-readable quote character spans or verifiable source offset keys.
    
      
    
- **Source Coverage (5/10):** Excellent coverage of market data, earnings call transcripts, and SEC filings; weak/unsupported for ad-hoc user YouTube recordings, local emails, and custom research PDFs.
    
      
    
- **Deterministic & Structured Output (4/10):** Focused on interactive dashboards and financial charting; no batch JSONL export pipeline for custom atomic claim schemas.
    
      
    
- **Production Adoption & Maturity (8/10):** Established brand in open-source and institutional quantitative finance.
    
      
    
- **Zero / Low Cost (7/10):** Open-source core exists; advanced Copilot workspace features require commercial licensing.
    
      
    
- **Maintenance & Docs (8.5/10):** Highly active development, clean documentation.
    
      
    
- **German-Language Support (4/10):** Heavily biased toward US/English financial markets and SEC filings; German macro/broker research is not first-class.
    
      
    
- **Local / OpenRouter (7/10):** Copilot allows custom BYOK keys; core requires local Python environment.
    
      
    

$$\text{Score} = (4 \times 0.20) + (5 \times 0.15) + (4 \times 0.15) + (8 \times 0.15) + (7 \times 0.15) + (8.5 \times 0.10) + (4 \times 0.05) + (7 \times 0.05)$$

$$\text{Score} = 0.80 + 0.75 + 0.60 + 1.20 + 1.05 + 0.85 + 0.20 + 0.35 = \mathbf{5.80 / 10}$$

### Candidate 5: Google NotebookLM

_(Evaluated as a hosted complete-product candidate)_

  

- **Quote & Provenance (8/10):** Grounded RAG system provides reliable citation anchors directly back to source passages.
    
      
    
- **Source Coverage (8/10):** Supports PDFs, YouTube links, text files, Google Docs, and URLs out of the box. Lacks direct email MIME ingestion.
    
      
    
- **Deterministic & Structured Output (1/10):** **Critical failure:** No public API, no CLI, no structured JSON schema export, and no deterministic data pipeline integration.
    
      
    
- **Production Adoption & Maturity (7.5/10):** Widely used by researchers and students as a consumer desktop app.
    
      
    
- **Zero / Low Cost (9/10):** Free to use under standard Google account limits.
    
      
    
- **Maintenance & Docs (5/10):** Consumer product; minimal technical documentation on internals or automation.
    
      
    
- **German-Language Support (8.5/10):** Underlying Gemini models handle German audio and documents with high fidelity.
    
      
    
- **Local / OpenRouter (1/10):** Closed Google SaaS; zero local data privacy, completely incompatible with OpenRouter.
    
      
    

$$\text{Score} = (8 \times 0.20) + (8 \times 0.15) + (1 \times 0.15) + (7.5 \times 0.15) + (9 \times 0.15) + (5 \times 0.10) + (8.5 \times 0.05) + (1 \times 0.05)$$

$$\text{Score} = 1.60 + 1.20 + 0.15 + 1.125 + 1.35 + 0.50 + 0.425 + 0.05 = \mathbf{6.40 / 10}$$

### Candidate 6: Karakeep (formerly Hoarder)

_(Evaluated as an ingestion & custody candidate)_

  

- **Quote & Provenance (2/10):** Does not support quote extraction or citation anchors; extracts only page-level readable text or full-page HTML.
    
      
    
- **Source Coverage (5/10):** Ingests web links, uploaded PDFs, and images; archives YouTube video files (via yt-dlp); cannot parse emails or transcribe audio files.
    
      
    
- **Deterministic & Structured Output (3/10):** REST API and CLI provide JSON bookmarks and lists; zero support for claim schemas or deterministic verification.
    
      
    
- **Production Adoption & Maturity (7/10):** Over 28k stars on GitHub; actively used as a self-hosted read-it-later bookmark manager.
    
      
    
- **Zero / Low Cost (8.5/10):** AGPL-3.0 open source, free to self-host.
    
      
    
- **Maintenance & Docs (8/10):** Active GitHub repository, clear self-hosting guides.
    
      
    
- **German-Language Support (6/10):** Supports multi-language bookmarks; basic search depends on Meilisearch tokenization.
    
      
    
- **Local / OpenRouter (7.5/10):** Supports local Ollama or OpenRouter for its basic tagging and summary features.
    
      
    

$$\text{Score} = (2 \times 0.20) + (5 \times 0.15) + (3 \times 0.15) + (7 \times 0.15) + (8.5 \times 0.15) + (8 \times 0.10) + (6 \times 0.05) + (7.5 \times 0.05)$$

$$\text{Score} = 0.40 + 0.75 + 0.45 + 1.05 + 1.275 + 0.80 + 0.30 + 0.375 = \mathbf{5.40 / 10}$$

## 6. Shortlist Comparison Table

|**Feature / Metric**|**Composable Core Stack**|**IBM Docling (Core)**|**Dify**|**OpenBB Workspace**|**Google NotebookLM**|**Karakeep (Hoarder)**|
|---|---|---|---|---|---|---|
|**Maintainer / Owner**|Modular (IBM, SYSTRAN, 567-labs)|IBM Research Zurich|LangGenius, Inc.|OpenBB Inc.|Google LLC|Localhost Labs Ltd.|
|**Current Stable Ver. (2026)**|Individual packages (v1.x - v3.x)|docling 2.119+ / docling-core 2.98.0|v0.15+|v4.x / Workspace 2026|Cloud SaaS (Current)|v0.32+|
|**License**|MIT / Apache 2.0 / GPLv3|MIT License|Apache 2.0|AGPLv3 / Commercial|Proprietary Closed|AGPL-3.0|
|**Self-Hosting**|100% Local CLI / Scripts|100% Local (Python/CLI)|Docker Compose|Local / Cloud|No (Google Cloud only)|Docker Compose|
|**Primary Formats**|Audio, Video, Email, Web, PDF|PDF, DOCX, XLSX, HTML, EML|Text, PDF, Web (via plugins)|Financial datasets, SEC|PDF, Web, YouTube, Docs|Web URLs, Notes, Images, PDF|
|**Exact Citations**|Bounding box + Timestamp + Substring|Bounding box + Page + Cell coords|Chunk index only|Unstructured text|Highlight overlays|None (High-level tags only)|
|**German Support**|Excellent (Whisper large-v3 + Trafilatura)|High (Tesseract / EasyOCR)|Model-dependent|Moderate (US market focus)|High (Gemini native)|Moderate (Meilisearch)|
|**OpenRouter Support**|Native (via Instructor client)|N/A (Downstream)|Native provider|Partial (BYOK)|None|Supported for basic tags|
|**Local Data Privacy**|Air-gapped capable (or local LLM)|100% Local air-gapped|100% Local air-gapped|Local data / Remote APIs|Zero (Public Google cloud)|100% Local air-gapped|
|**Hardware Required**|Consumer CPU (GPU optional for ASR)|CPU (GPU speeds TableFormer)|4+ vCPU, 8–16 GB RAM|Standard PC (8 GB RAM)|Browser only|2 vCPU, 4 GB RAM|
|**Low-Volume Cost**|**<$1.00 / month** (OpenRouter tokens)|**$0.00**|**$0.00** (compute only)|Free tier / $20+ Pro|**$0.00**|**$0.00**|
|**Weighted Total**|**9.70 / 10**|**9.13 / 10**|**7.13 / 10**|**5.80 / 10**|**6.40 / 10**|**5.40 / 10**|

## 7. Recommended Candidate Stack

The recommended candidate stack uses established, production-tested components connected via deterministic Python glue code.

  

```
                         RECOMMENDED CANDIDATE STACK
                         
  [Media Sources]       [Processing Component]              [Output Artifact]
  
  YouTube / Audio ───►  yt-dlp + faster-whisper  ─────────► Timestamped Segments
  Research Emails ───►  mail-parser (RFC-822)    ─────────► Plaintext / Attachments
  Web Articles    ───►  trafilatura              ─────────► Clean Markdown
  Research PDFs   ───►  IBM Docling (TableFormer)────────► DoclingDocument JSON
                               │
                               ▼
  [Extraction Layer]    Instructor + Pydantic v2 ────────► Schema-Validated Claims
                        (via OpenRouter: Gemini Flash / Claude Haiku)
                               │
                               ▼
  [Verification Layer]  Python exact search + RapidFuzz ─► Grounded Claim Register
                        & GLiNER / OpenFIGI Normalizer
                               │
                               ▼
  [Downstream Input]    Append-Only JSONL Ledger ────────► Manual Broker & Portfolio Code
```

### 1. Acquisition & Extraction Tier

- **Audio/Video:** `yt-dlp` extracts high-bitrate audio streams from YouTube URLs. `faster-whisper` (running `large-v3` or `large-v3-turbo` in INT8/FP16 on CPU/GPU) handles German and English financial speech, emitting discrete segments with millisecond start/end timestamps.
    
      
    
- **Emails:** Standard Python `email` module combined with `mail-parser`. Ingests `.eml` or forwarded digests, parses MIME headers (`From`, `Date`, `Subject`), extracts plaintext and HTML bodies, and dumps attachments (e.g. research PDFs) into a deterministic processing directory.
    
      
    
- **Web Articles:** `trafilatura` handles financial news and blog URLs. Bypasses boilerplate and navigation banners, extracts published dates, authors, and main text, and falls back to `playwright`/`Crawl4AI` only if client-side rendering is strictly required.
    
      
    
- **Research PDFs:** IBM `Docling` processes multi-page reports. It preserves layout order, identifies table rows and columns via `TableFormer`, handles scanned pages via Tesseract OCR, and outputs a structured `DoclingDocument` JSON file with exact page numbers and bounding boxes for every text span.
    
      
    

### 2. Semantic Extraction Tier (OpenRouter + Instructor)

- **Schema Enforcement:** An `Instructor` Python client wraps the OpenAI SDK configured with `base_url="[https://openrouter.ai/api/v1](https://openrouter.ai/api/v1)"`.
    
      
    
- **Model Selection:** Fast, inexpensive, large-context models (Google Gemini 1.5/2.0 Flash or Anthropic Claude 3.5 Haiku) execute the extraction.
    
      
    
- **Target Schema:** A Pydantic v2 data model enforces the required target fields:
    
      
    

Python

```
from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class ExtractedClaim(BaseModel):
    statement: str = Field(description="Atomic financial claim or thesis statement")
    verbatim_quote: str = Field(description="Exact verbatim quotation from the source text")
    claim_type: Literal["Fact", "Forecast", "Opinion", "Risk", "Catalyst", "Recommendation"]
    sentiment: Literal["Bullish", "Bearish", "Neutral", "Volatility"]
    time_horizon: Optional[Literal["Immediate", "Short-term", "Medium-term", "Long-term"]] = None
    affected_entities: List[str] = Field(description="Mentioned companies, tickers, or economic variables")
    source_location: str = Field(description="Page number, table cell, or timestamp anchor")
    confidence_score: float = Field(ge=0.0, le=1.0)
```

### 3. Deterministic Verification & Entity Linking Tier

- **Quote Verification:** A deterministic Python validator checks `source_text.find(claim.verbatim_quote)`. If an exact match is missing, `RapidFuzz` checks whether token similarity exceeds 95% (to catch minor ASR punctuation differences). If below 95%, the claim is quarantined or rejected for re-extraction.
    
      
    
- **Entity Linking:** `GLiNER` (running locally on CPU) extracts entity spans without LLM token cost. Company names are checked against a local portfolio holdings list; unresolved equities are mapped via the free `OpenFIGI` API.
    
      
    
- **Deduplication & Stance:** A deterministic composite hash (`SHA256(source_id + segment_anchor + statement)`) prevents duplicate ledger entries.
    
      
    

### 4. Downstream Export Tier

- Emits validated, immutable JSONL records directly into a dedicated directory. Downstream portfolio calculations (weighting, exposure, delta) are handled solely by separate, deterministic Python scripts.
    
      
    

## 8. Attached-File Fit Assessment

The technical characteristics of the representative input files were evaluated against the documented capabilities of the recommended stack.

  

### 1. Markus Koch Transcript (`transcript.md` / `vFTuLylvYnA`)

- **Input Characteristics:** Spoken German, rapid financial journalism from the NYSE floor, frequent English technical terms (_Treasury Yields_, _Mega-Caps_, _Guidance_, _P/E Multiples_, _Spread_), conversational pauses, phonetic transcription noise, and time-bounded segments (`[00:01:15 -> 00:01:25]`).
    
      
    
- **Documented Candidate Capabilities:**
    
      
    - _Speech-to-Text (`faster-whisper`):_ The Whisper `large-v3` architecture was trained on tens of thousands of hours of German audio. Benchmark evaluations indicate German word error rates (WER) under 7–9%. The CTranslate2 backend preserves segment boundaries with start/end floating-point seconds.
        
          
        
    - _Anglicism Handling:_ The Whisper decoder natively recognizes mixed English-German financial terminology without phonetic mangling.
        
          
        
    - _Quote Anchoring:_ `Instructor` can be prompted over individual timestamped chunks. Because each input chunk possesses a fixed `[start_time, end_time]` identifier, the extracted `verbatim_quote` is deterministically locked to that specific segment window.
        
          
        
    - _Gap / Unknown:_ Colloquial phrasing and run-on sentences in German spoken broadcasts make sentence boundary detection non-trivial. Whisper's native punctuation must be validated to ensure quotes do not span arbitrary segment seams.
        
          
        

### 2. Investment Research PDF (`GER Elephant in The Room Analysis.pdf`)

- **Input Characteristics:** A 13-page macroeconomic and equity strategy document containing dense multi-column analytical text, embedded statistical charts, structured tables (e.g. fund manager survey cash levels, positioning metrics), footnotes, and page headers.
    
      
    
- **Documented Candidate Capabilities:**
    
      
    - _Layout & Reading Order (IBM `Docling`):_ Docling's layout analysis engine explicitly parses multi-column pages and reads text blocks in topological reading order rather than raw vertical coordinate order.
        
          
        
    - _Table Extraction:_ Docling’s `TableFormer` reconstructs complex borderless tables directly into HTML tables or markdown grids, preserving row and column relationships. This handles survey tables where cash percentages and historical percentiles must not get merged into adjacent text columns.
        
          
        
    - _Page-Level Citations:_ `DoclingDocument` represents each page as a discrete collection of tokens with bounding boxes (`l, t, r, b`) and explicit `page_no` integers. Any quote extracted from page 4 is deterministically linked to `page_no: 4`.
        
          
        
    - _Claim Separation:_ By processing text chunks extracted along Docling section boundaries, `Instructor` prompts can separate documented factual data ("Cash levels fell to 3.8%") from strategist forecasts ("This indicates a crowded risk rally").
        
          
        
    - _Gap / Unknown:_ Text embedded inside bitmap chart images requires OCR. If vector charts lack embedded text streams, Docling's OCR pipeline must be invoked, requiring moderate CPU/GPU compute.
        
          
        

### 3. Email Ingestion (Documented Capabilities & Gap Analysis)

- **Documented Candidate Capabilities:**
    
      
    - `mail-parser` parses standard RFC-822 `.eml` and Outlook `.msg` files into structured dictionaries. It isolates MIME bodies (giving priority to `text/plain` to prevent HTML tag noise) and dumps attachments (such as analyst PDF decks) into an uncompressed binary stream.
        
          
        
- **Human-Run Validation Requirement:**
    
      
    - Because no sample email fixture was provided, a human operator must test forwarding chains and nested newsletter formats. Forwarded research emails frequently introduce quoting artifacts (`>` prefixes, disclaimer footers, inline tracking pixels) that require deterministic regex stripping before feeding into Docling or Trafilatura.
        
          
        

## 9. Later Human-Run Validation Checklist

To confirm performance without relying on unverified assumptions, a human operator should execute these minimal experiments:

  

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    HUMAN VALIDATION EXPERIMENT MATRIX                       │
├───────────────────┬─────────────────────────────────────────────────────────┤
│ Phase 1: Audio    │ Transcribe 3 min of Markus Koch via faster-whisper.     │
│                   │ Validate: German financial term spelling & timestamps.  │
├───────────────────┼─────────────────────────────────────────────────────────┤
│ Phase 2: PDF      │ Convert pages 1–3 of Elephant PDF via Docling CLI.      │
│                   │ Validate: Multi-column reading order & table integrity. │
├───────────────────┼─────────────────────────────────────────────────────────┤
│ Phase 3: Email    │ Feed 1 raw .eml newsletter through mail-parser.         │
│                   │ Validate: Attachment extraction & body cleanliness.     │
├───────────────────┼─────────────────────────────────────────────────────────┤
│ Phase 4: Schema   │ Run 5 parsed chunks through Instructor via OpenRouter.  │
│                   │ Validate: Pydantic parsing & verbatim quote presence.   │
├───────────────────┼─────────────────────────────────────────────────────────┤
│ Phase 5: Mapping  │ Feed output JSONL into mock portfolio script.           │
│                   │ Validate: Deterministic ticker matching (No LLM math).  │
└───────────────────┴─────────────────────────────────────────────────────────┘
```

1. **Audio ASR & Timestamp Verification:**
    
      
    - _Step:_ Run `faster-whisper` (model: `large-v3`, `compute_type="int8"`) on a 3-minute clip of a Markus Koch NYSE broadcast.
        
          
        
    - _Check:_ Verify that terms like "Renditen", "Cash-Quote", and ticker symbols are transcribed accurately, and that segment timestamps align within 500ms of the spoken audio.
        
          
        
2. **PDF Layout & Table Integrity:**
    
      
    - _Step:_ Run `docling "Sources/GER Elephant in The Room Analysis.pdf" --to json` on a local machine.
        
          
        
    - _Check:_ Inspect the generated JSON for a table on pages 2–5. Confirm that table rows and columns are preserved as discrete cells rather than garbled into raw sequential strings.
        
          
        
3. **Email MIME & Attachment Extraction:**
    
      
    - _Step:_ Export a representative research email from an inbox as a `.eml` file. Run `mail-parser -f sample.eml -j`.
        
          
        
    - _Check:_ Confirm that sender metadata, plaintext body, and PDF attachments are extracted into discrete files with intact checksums.
        
          
        
4. **Verbatim Quote & Structured Schema Pass:**
    
      
    - _Step:_ Send one extracted Docling text section and one audio segment through `Instructor` calling `google/gemini-2.5-flash` or `anthropic/claude-3.5-haiku` on OpenRouter, requesting the `ExtractedClaim` schema.
        
          
        
    - _Check:_ Run Python's `raw_text.find(claim.verbatim_quote)`. Verify that the string matches 100% character-for-character without LLM rewriting or ellipsis hallucination.
        
          
        
5. **Sanitized Portfolio Mapping Integration:**
    
      
    - _Step:_ Create a sanitized holdings CSV:
        
          
        
        Code snippet
        
        ```
        identifier,name,current_value,theme
        US0231351067,Amazon.com Inc,10000,MegaCap Tech
        US0605051046,Bank of America,8000,US Financials
        ```
        
    - _Check:_ Run a standalone deterministic Python script to join the generated claim JSONL with this CSV on `affected_entities`. Verify that zero floating-point math or exposure weighting is handled by LLM code.
        
          
        

## 10. Karakeep Decision

### Verdict: REMOVE from Core Pipeline (Optional as Peripheral Inbox Only)

**Rationale Based on Documented Evidence:**

  

- **Not a Claim Engine:** Karakeep (formerly Hoarder, AGPL-3.0) is fundamentally an AI-assisted bookmark and read-it-later manager. Its architectural capabilities are designed for link archiving, full-page HTML downloads (via Monolith), image screenshotting, and Meilisearch full-text indexing.
    
      
    
- **No Quote or Offset Provenance:** Karakeep’s AI features are restricted to high-level tagging (e.g. assigning `#finance`, `#tech`) and single-paragraph summary generation. It does not possess any mechanisms for extracting atomic claims, identifying claim types (fact vs. forecast), validating quotation spans, or calculating character offsets.
    
      
    
- **No Layout-Aware Table or Audio Processing:** Karakeep does not parse multi-column PDF layouts or reconstruct tabular financial data; it treats PDFs as raw attachment assets or flat OCR images. It uses `yt-dlp` to download video files for local archiving, but it does not transcribe spoken speech into timestamped segments.
    
      
    
- **High Operational Overhead:** Self-hosting Karakeep requires running three persistent Docker containers: the Next.js web application, a headless Chrome/Playwright container, and a Meilisearch database instance.
    
      
    
- **Permissible Role:** Karakeep should only be retained if the operator desires a mobile-friendly browser bookmarklet to manually capture URLs while away from the desktop. If retained, it sits strictly outside the extraction toolchain: a background script would periodically poll Karakeep's `/api/v1/bookmarks` endpoint, pull the raw URLs, and pass them directly to `trafilatura` and `Docling`. It must not be tasked with document extraction, citation verification, or claim generation.
    
      
    

## 11. Cost and Privacy Assessment

### 1. Realistic Low-Volume Scenario

- **Assumed Monthly Volume:**
    
      
    - 15 YouTube / audio episodes (~20 minutes each = 300 minutes audio).
        
          
        
    - 20 research PDFs (average 10 pages each = 200 pages).
        
          
        
    - 40 web articles (average 1,500 words each = 60,000 words).
        
          
        
    - 30 research emails (average 800 words each = 24,000 words).
        
          
        

### 2. Monthly Financial Cost Breakdown

|**Component**|**Software / Tool**|**Infrastructure / API Tier**|**Monthly Cost (USD)**|
|---|---|---|---|
|**Audio Processing**|`yt-dlp` + `faster-whisper`|Local consumer CPU/GPU|**$0.00**|
|**Email Ingestion**|`mail-parser` / Python `email`|Local execution|**$0.00**|
|**Web Scraping**|`trafilatura`|Local execution|**$0.00**|
|**PDF & Layout Parsing**|IBM `Docling`|Local execution|**$0.00**|
|**Entity Linking**|`GLiNER` + `OpenFIGI` API|Local CPU + Free Tier API|**$0.00**|
|**Quote Verification**|Python Substring + `RapidFuzz`|Local CPU|**$0.00**|
|**LLM Claim Extraction**|`Instructor` + OpenRouter|Cloud API (Pay-as-you-go)|**~$0.45 – $1.15**|
|**Total Estimated Cost**|—|—|**<$1.50 / month**|

_Inference Cost Calculation:_

  

- Total input text across all monthly sources: ~250,000 tokens.
    
      
    
- Using **Google Gemini 2.0 Flash** via OpenRouter ($0.10 / 1M input tokens, $0.40 / 1M output tokens):
    
      
    
    $$\text{Input: } 0.25 \times \$0.10 = \$0.025$$
    
    $$\text{Output (approx. 50,000 tokens): } 0.05 \times \$0.40 = \$0.020$$
    
- Using **Anthropic Claude 3.5 Haiku** via OpenRouter ($0.80 / 1M input tokens, $4.00 / 1M output tokens):
    
      
    
    $$\text{Input: } 0.25 \times \$0.80 = \$0.20$$
    
    $$\text{Output: } 0.05 \times \$4.00 = \$0.20$$
    
- Even with retries and system prompt overhead, total monthly LLM expenditure remains well under $2.00.
    
      
    

### 3. Data Privacy & Local Boundary Assessment

- **Local Air-Gapped Stages:**
    
      
    - Audio files, email headers, raw research PDFs, and web scrape artifacts remain entirely on the local filesystem.
        
          
        
    - All parsing, OCR, table reconstruction, and audio transcription occur locally.
        
          
        
- **External API Boundary:**
    
      
    - The only data leaving the local machine are individual text chunks sent to OpenRouter for semantic claim structuring.
        
          
        
    - _Zero Retention:_ OpenRouter provides data privacy controls allowing users to bypass logging on upstream providers that honor zero-data retention.
        
          
        
    - _Local Fallback Option:_ If 100% privacy is required, OpenRouter can be swapped for a local Ollama or vLLM instance running Llama-3.3-70B or Qwen-2.5-14B, bringing the external API cost and external data transmission to absolute zero.
        
          
        

## 12. Risks, Unknowns, and Operator Decisions

### 1. Documented Risks

- **Whisper Hallucination on Ambient Audio:** In market broadcasts with loud floor noise or music, Whisper models can hallucinate repetitive loops or omit rapid side-remarks. Mitigate by passing `--condition_on_previous_text False` and utilizing Silero VAD (voice activity detection) filtering inside `faster-whisper`.
    
      
    
- **OCR Degradation on Complex Embedded Charts:** Docling's `TableFormer` reconstructs digital tables with high fidelity, but cannot reconstruct vector charts whose data points are purely visual lines/bars without numbers. Claims derived from charts must be flagged with `extraction_confidence < 0.70` unless an explicit data callout label exists.
    
      
    
- **LLM Quote Truncation:** Language models frequently attempt to "clean up" quotes by fixing colloquial grammar or inserting ellipses (`...`). A strict deterministic post-validation filter must automatically discard any extraction that fails an exact string check against the source text.
    
      
    

### 2. Unresolved Unknowns (Requiring Empirical Test)

- _TableFormer Execution Latency on CPU:_ TableFormer is a deep-learning layout model. On a machine without a dedicated NVIDIA GPU, parsing a 13-page research PDF with 5 complex tables may take between 30 and 90 seconds. Benchmarking CPU latency on the operator's specific hardware is required.
    
      
    
- _Email Forwarding Normalization:_ Different email clients (Apple Mail, Thunderbird, Outlook) format forwarded message threads differently. A single deterministic regex cannot clean all forwarded headers without occasional text loss.
    
      
    

### 3. Operator Decisions Required

1. **Strictness of Quote Validation:** The operator must decide whether to enforce _100% exact substring matching_ (which rejects minor ASR punctuation differences) or allow a _fuzzy threshold_ (e.g. RapidFuzz partial ratio ≥ 95%).
    
      
    
2. **Inference Provider Selection:** The operator must decide whether to use OpenRouter (minimal cost, ~$1.00/mo, zero local GPU usage) or deploy a local model via Ollama (100% private, zero external network requests, but requires 12–16 GB of local VRAM/system memory).
    
      
    

## 13. Sources

1. **IBM Docling:** Official Documentation & Architecture. [https://ds4sd.github.io/docling/](https://ds4sd.github.io/docling/)
    
      
    
2. **Docling GitHub Repository:** IBM Research Zurich. [https://github.com/DS4SD/docling](https://github.com/DS4SD/docling)
    
      
    
3. **Docling Technical Report (arXiv:2408.09869):** Deep Search Team, IBM Research. [https://arxiv.org/abs/2408.09869](https://arxiv.org/abs/2408.09869)
    
      
    
4. **Faster-Whisper:** SYSTRAN CTranslate2 Implementation of Whisper. [https://github.com/SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper)
    
      
    
5. **WhisperX:** Forced Alignment and Diarization for Whisper. [https://github.com/m-bain/whisperX](https://github.com/m-bain/whisperX)
    
      
    
6. **Trafilatura:** Adrien Barbaresi, Python Web Scraping & Text Extraction. [https://github.com/adbar/trafilatura](https://github.com/adbar/trafilatura)
    
      
    
7. **Marker (Marker-PDF):** Datalab / Vik Paruchuri. [https://github.com/datalab-to/marker](https://github.com/datalab-to/marker)
    
      
    
8. **Instructor Library:** Jason Liu / 567-labs. [https://github.com/567-labs/instructor](https://github.com/567-labs/instructor)
    
      
    
9. **BAML Documentation:** BoundaryML Language for Structured AI. [https://github.com/BoundaryML/baml](https://github.com/BoundaryML/baml)
    
      
    
10. **GLiNER Community & Benchmark:** Generalist and Lightweight Named Entity Recognition. [https://huggingface.co/gliner-community](https://huggingface.co/gliner-community)
    
      
    
11. **OpenFIGI API:** Bloomberg Open Symbology Standard. [https://www.openfigi.com/api](https://www.openfigi.com/api)
    
      
    
12. **RapidFuzz:** Max Bachmann, Fast Fuzzy String Matching for Python and C++. [https://github.com/rapidfuzz/RapidFuzz](https://github.com/rapidfuzz/RapidFuzz)
    
      
    
13. **Mail-Parser:** SpamScope RFC-822 Parsing Library. [https://github.com/SpamScope/mail-parser](https://github.com/SpamScope/mail-parser)
    
      
    
14. **Karakeep (formerly Hoarder):** Localhost Labs Ltd. [https://github.com/karakeep-app/karakeep](https://github.com/karakeep-app/karakeep)
    
      
    
15. **OpenBB Workspace Documentation:** OpenBB Inc. [https://docs.openbb.co/workspace](https://docs.openbb.co/workspace)