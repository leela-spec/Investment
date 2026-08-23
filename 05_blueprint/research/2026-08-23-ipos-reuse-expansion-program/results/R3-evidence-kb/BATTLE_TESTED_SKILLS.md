# Battle-Tested Skills and Processing Assets

**Evaluation date:** 2026-08-23.  
**Rule:** an agent prompt is not “battle-tested” merely because it is public. A pass requires inspectable implementation, license, current maintenance, a deterministic useful core, and either tests/fixtures in the upstream project or narrow delegation to a mature tested tool. Agent compatibility is recorded separately from the underlying tool's maturity.

## Findings

Only two agent-facing assets meet a narrow reuse threshold: Docling's first-party packaged skill and Karakeep's first-party MCP server. Neither is a truth/claim pipeline. Mature non-agent processing assets—Zotero translators, Docling, GROBID, Tika, OCRmyPDF/Tesseract and SQLite—are more trustworthy building blocks than the community “financial research skill” repositories inspected.

| Candidate | Public/current implementation | Code and tests/demonstrated use | License | Agents/interfaces | AI required? | Deterministic component | Verdict |
|---|---|---|---|---|---|---|---|
| Docling first-party agent skill | Skill ships in Docling source; HEAD observed `e1cb2b2…` | Skill router/reference files call documented CLI/SDK; main project has extensive tests/examples | MIT | Docs explicitly describe `.agents/skills` for Codex, Cursor and Copilot and `.claude/skills` for Claude | No for standard conversion | Local CLI/SDK conversion to Docling JSON/Markdown/text; optional VLM paths separable | **ADOPT NOW**, but pin version and keep AI enrichments off baseline |
| Karakeep first-party MCP | MCP app ships inside main Karakeep repo; HEAD `7ca5ee2…` | TypeScript server delegates to official API; repository CI/tests cover the application, though MCP-specific durability is less evidenced | AGPL-3.0 | MCP clients; README demonstrates Claude Desktop; other MCP-capable agents can connect | No | Search/read/create/update bookmark/list/tag/asset/highlight operations | **ADOPT NOW** as interface only; never as source-truth extractor |
| Zotero translators | First-party translator repo; HEAD `56eaac3…` | Actual JavaScript translators, per-translator fixtures and automated test runner documented | AGPL-compatible contribution terms; Zotero AGPL-3.0 | Zotero/Connector, not an agent skill | No | Web/import/export/search metadata translation | **ADOPT NOW** when Zotero is used; direct deterministic asset is preferable to an agent wrapper |
| GROBID | Maintained first-party source/docs | Code, service/API, tests and published benchmark/evaluation docs | Apache-2.0 | REST/Java clients; no agent dependency | ML models are internal; no hosted LLM | Repeatable TEI/header/reference extraction with pinned model/version | **TEST FURTHER** for scholarly PDFs only |
| Apache Tika | Maintained Apache project | Broad parser code/tests and release documentation | Apache-2.0 | CLI/server/Java; any agent can invoke tool | No | MIME, metadata and text extraction; OCR optional | **ADOPT LATER** as fallback |
| OCRmyPDF + Tesseract | Maintained public projects | CLI/code/tests/documentation | MPL-2.0 / Apache-2.0 | CLI; agent-independent | No hosted AI/LLM | Pinned OCR pipeline and searchable-PDF artifact | **TEST FURTHER** only on scan corpus |
| `zirui-song/claude-skills` | Public; HEAD `ab1129a…`; small commit history | Actual skill Markdown and some scripts/workflows, but limited repository-level tests and independent production evidence | MIT | Claude-oriented | Varies | Some verification steps can run without AI | **DEFER / TEST FURTHER**; insufficient evidence for canonical ingestion or claim verification |
| `herbertkokholm/zotero-mcp` (renamed Cite Caddy) | Public; HEAD `82ae5cc…` | Implementation exists, but it is a third-party wrapper and lacks maturity evidence comparable with Zotero translators/API | Repository-specific; must be rechecked at chosen release | MCP | Agent needed to use interface, not Zotero itself | Zotero API operations beneath wrapper | **DEFER**; direct Zotero export/API is the lower-risk interface |
| OpenClaw Zotero/finance skills found in catalog/search | Individual skill text was discoverable, but source repository/license/test lineage could not be consistently verified | No adequate end-to-end evidence | Unverified | OpenClaw | Varies | Unverified | **REJECT for adoption** until code, license, version and tests are independently verifiable |
| Generic summarization/claim/contradiction “skills” | Many prompts exist; no candidate inspected demonstrated a durable, licensed, test-backed financial truth pipeline | Prompt demos are not groundedness tests | Varies/unverified | Varies | Usually yes | Source anchoring can be deterministic, extraction cannot be assumed true | **REJECT as evidence authority**; implement bounded optional derived workflow only |

Primary sources: [Docling agent-skill docs](https://docling-project.github.io/docling/usage/agent_skills/), [Docling skill source](https://github.com/docling-project/docling/blob/main/docling/.agents/skills/docling/SKILL.md), [Docling license](https://github.com/docling-project/docling/blob/main/LICENSE), [Karakeep MCP README](https://github.com/karakeep-app/karakeep/blob/main/apps/mcp/README.md), [Karakeep license](https://github.com/karakeep-app/karakeep/blob/main/LICENSE), [Zotero translator docs](https://www.zotero.org/support/dev/translators), [Zotero translators](https://github.com/zotero/translators), [GROBID docs](https://grobid.readthedocs.io/en/latest/), [Tika formats](https://tika.apache.org/3.3.0/formats.html), [OCRmyPDF docs](https://ocrmypdf.readthedocs.io/en/latest/).

## Capability-by-capability answer

| Requested capability | Reusable mature asset | What it safely provides | Residual control required |
|---|---|---|---|
| Document/PDF parsing | Docling; Tika fallback | Structured/text derivatives from local inputs | Preserve original; pin tool/config; validate tables/pages |
| Web archiving | Karakeep + SingleFile; optional ArchiveBox | Captures and attachments with human inbox | Neutral export, hashes, HTTP/acquisition receipt and version policy |
| Metadata extraction | Tika/Docling; Zotero translators | File metadata and bibliographic fields | Source precedence, field normalization, confidence/review |
| Citation extraction | Zotero translators; GROBID; Crossref/DataCite lookup | DOI/bibliography/TEI references | Store exact document/page anchor; avoid fuzzy auto-linking |
| Entity/ticker extraction | No agent skill accepted | — | SEC/GLEIF/reference joins, regex and versioned alias table; human review |
| Deduplication | No skill needed | — | SHA-256 plus DOI/accession/LEI constraints; fuzzy only creates candidates |
| Source classification | No agent skill accepted | — | Allowlisted domain/connector/MIME rules with test fixtures |
| Research ingestion | Karakeep MCP and direct APIs | Queue/capture/search/update operations | Idempotent neutral ingest receipt and allowlist |
| Summarization | No evidence-authoritative skill | Optional convenience text | Label derived; retain model/prompt/source anchors; never overwrite source |
| Claim extraction | No accepted battle-tested skill | Candidate structured claims only | Schema validation and human confirmation before use |
| Contradiction checking | Existing IPOS deterministic contradiction logic applies only to operational typed data | Operational rule evaluation | Evidence contradiction candidates require normalized reviewed claims; LLM cannot adjudicate truth |
| Provenance/citation management | Neutral manifest + Zotero for papers | Traceable IDs, citations, exports | Hashes/acquisition data must remain outside a single app |

## Why the accepted assets are bounded

### Docling skill

The skill is useful because it teaches agents to call a real local parser and to select documented input/output paths. The standard conversion path does not need an LLM or embeddings. It does **not** prove that every PDF table is correct; the source PDF and page references remain authoritative. Do not enable remote services, ASR or VLM enrichment merely because examples exist.

### Karakeep MCP

The MCP is useful because it exposes the same concrete bookmark/list/tag/asset/highlight operations as the official API. It makes an agent a UI client; it does not turn model-generated tags/summaries into evidence. Destructive bookmark operations must remain outside autonomous evidence export, and accepted items must be materialized into the neutral object/record contract.

### Zotero translators

These are not branded as an agent skill, which is a virtue: they are mature deterministic adapters with site-specific code and fixtures. Use them directly through Zotero rather than wrapping them in a less-tested autonomous skill.

## Minimum safe optional-AI contract

If later work adds a summary, claim or contradiction skill, require every output to contain:

```json
{
  "derived_kind": "summary|claim_candidate|contradiction_candidate",
  "source_evidence_ids": ["..."],
  "source_anchors": [{"evidence_id":"...","page":12,"quote_hash":"..."}],
  "model": "provider/model/version",
  "prompt_version": "...",
  "generated_at": "...",
  "review_status": "unreviewed",
  "may_drive_ipos": false
}
```

The model output is discarded/rebuilt independently of originals. There is no automatic path from this record into `03_extract/`, `04_playbook/`, `configs/`, scoring or governors.

## Rejection criteria applied

- README-only, catalog-only or prompt-only entries without inspectable implementation.
- No license or ambiguous reuse rights.
- No current source or release lineage.
- “Works with Claude/Codex” without tests, fixtures or demonstrated deterministic tool calls.
- Agent requires cloud AI for basic parse/index/search.
- Claims to verify facts/contradictions without evidence anchors and measurable tests.
- Duplicates a mature direct API/CLI while adding autonomy and another failure surface.
