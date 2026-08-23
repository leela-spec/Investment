<system_instruction>
You are researching the best evidence architecture for a serious personal
financial research system.

The goal is NOT "chat with PDFs".

The goal is a downloadable, auditable, source-preserving financial evidence base
that can support human research, deterministic IPOS processes and optional AI
analysis without making the AI the source of truth.
</system_instruction>

<repo_context>
Inspect leela-spec/Investment main.

Understand the distinction between:

1. IPOS operational knowledge:
   03_extract/*.jsonl
   04_playbook/modules/*
   configs/*
   scoring/rules/governors

and

2. external evidence:
   filings, macro releases, PDFs, articles, transcripts, newsletters,
   posts, alerts, official documentation and datasets.

Do not collapse these two layers.
</repo_context>

<objective>
Determine the best FREE architecture for a general financial evidence KB.

Research three separate things:

A. storage/indexing software;
B. extraction/processing skills/tools;
C. downloadable financial corpora/knowledge sources.
</objective>

<software_landscape>
Research mature existing systems including, but not limited to relevant candidates:

- Karakeep
- Zotero
- Paperless-ngx
- Obsidian/local Markdown approaches
- SQLite/DuckDB FTS
- Tantivy/Meilisearch/Typesense where appropriate
- Docling
- GROBID
- Apache Tika
- OCR/document parsers only if actually needed
- existing MCP/agent skills
- existing OpenClaw/Codex/Claude Code/Gemini skills

Do not reward a tool because it contains the word "AI".
</software_landscape>

<skill_requirements>
Search specifically for existing battle-tested:

- document parsing skills
- PDF extraction
- web archiving
- metadata extraction
- citation extraction
- entity/ticker extraction
- deduplication
- source classification
- research ingestion
- summarization
- claim extraction
- contradiction checking
- provenance/citation management

For each AI/agent skill verify:
- public implementation exists;
- recent maintenance;
- actual code;
- supported agents;
- tests or demonstrated use;
- license;
- whether AI is required;
- whether deterministic components can run without AI.

Reject vaporware and toy skill repositories.
</skill_requirements>

<downloadable_knowledge>
Research legally downloadable or programmatically obtainable financial evidence corpora.

Examples of categories to investigate:
- company filings
- regulatory filings
- central-bank research/publications
- national statistics
- macro databases
- international institutions
- earnings documents/transcripts where legally available
- corporate investor-relations releases
- academic finance research
- economic working papers
- legislation/regulations relevant to markets
- financial dictionaries/taxonomies/ontologies
- security/instrument reference data
- public historical datasets

Determine for each:
- full-download possibility;
- API/bulk mechanism;
- licensing;
- update mechanism;
- approximate size;
- machine readability;
- provenance quality;
- practical IPOS relevance.

Separate:
FULLY DOWNLOADABLE
INCREMENTALLY ARCHIVABLE
API-ONLY
NOT LEGALLY/PRACTICALLY ARCHIVABLE
</downloadable_knowledge>

<architecture_options>
Compare at least:

A. Karakeep-centric evidence library
B. Zotero-centric evidence library
C. Karakeep + Zotero
D. filesystem/Markdown + deterministic search
E. hybrid evidence store + local search index

Do not assume embeddings/RAG are necessary.

Compare:
- FTS/BM25
- metadata filtering
- deterministic tag/entity lookup
- embeddings only as an optional additional retrieval method
</architecture_options>

<mcda>
Weights:
- evidence provenance: 20
- source preservation/export: 15
- retrieval quality: 15
- local/free: 10
- deterministic operation: 10
- breadth of supported evidence: 10
- automation interfaces: 10
- maturity: 5
- maintenance simplicity: 5
</mcda>

<deliverables>
1. EVIDENCE_KB_REQUIREMENTS.md
2. TOOL_LANDSCAPE.md
3. BATTLE_TESTED_SKILLS.md
4. DOWNLOADABLE_FINANCIAL_CORPORA.md
5. KB_ARCHITECTURE_OPTIONS.md
6. MCDA.json
7. RECOMMENDATION.md
8. INSTALLATION_COMPONENT_MAP.json

The recommendation must identify:
- what to reuse;
- what to download;
- what to archive incrementally;
- what NOT to store;
- what IPOS-specific glue is still actually necessary.
</deliverables>
