# Gemini Deep Research Prompt — Proven Source-to-Investment-Claim Toolchain

## Reference files to attach before starting

These files are representative input context only. Gemini must not claim to have run candidate
software against them.

1. `transcript.md` — the existing Markus Koch normalized, timestamped transcript with stable
   segment anchors.
2. `GER Elephant in The Room Analysis.pdf` — a representative investment-research PDF.

Optional provenance context:

3. `manifest.json` — describes the transcript segmentation artifact. Use it only for source
   metadata and integrity context, not as proof that the extraction is correct.

Do **not** attach the existing IPOS `evidence.json`, action/watch register, fixture-acceptance
results, or generated `report.html` as expected answers. Those are outputs of the untrusted
custom process being replaced and would bias the evaluation.

No representative email file currently exists. Do not invent one. Evaluate email support only from
the tools' documented capabilities and identify what a later human-run validation would need.

Do not upload raw broker statements or transaction exports during this research. Any later
human-run portfolio-mapping validation should use a sanitized holdings table containing only instrument identifier,
instrument name, quantity or current value, and sector/theme. Exclude account numbers, customer
identifiers, addresses, transaction history, and credentials.

---

## Prompt for Gemini Deep Research

Act as an independent technology researcher selecting a production-proven, inexpensive
source-intelligence toolchain for a private investment workflow. You have no access to the user's
local repository or previous conversations. Everything necessary for the research is contained in
this prompt and the attached source fixtures.

### The actual problem

The user receives investment-relevant information through:

- YouTube videos and local audio/video recordings.
- Research emails and email attachments.
- Web articles and saved pages.
- Text PDFs, scanned PDFs, tables, and research papers.

The required system must transform those sources into structured, evidence-linked statements that
can later be compared with a real investment portfolio and investment thesis.

Example desired outcomes include:

- "US Treasury yields are rising and are creating valuation pressure for technology shares."
- "Fund-manager cash levels are unusually low, which may indicate crowded risk positioning."
- "Semiconductor long positioning remains crowded despite declining from the prior survey."
- "A named company reduced guidance, creating a possible negative catalyst for directly exposed
  holdings."

Each useful statement should preserve as much of the following as the source actually supports:

- An atomic claim or statement.
- The exact supporting quotation.
- Timestamp, page, paragraph, email part, table cell, or another stable source location.
- Stable source identity and retrieval date.
- Mentioned companies, instruments, industries, countries, and economic variables.
- Direction or sentiment when supported by the source.
- Time horizon when stated or safely classifiable.
- Claim type such as fact, forecast, opinion, risk, catalyst, or recommendation.
- Extraction method and confidence/provenance.
- Supporting or contradicting statements.

This is a target schema, not a rule that every field must always be present. Missing fields must be
reported as missing rather than inferred without evidence.

### Critical constraints

1. Do not trust or recommend the user's existing custom IPOS extraction process. Treat the attached
   transcript and PDF as raw evaluation inputs, not as evidence that prior claims were correct.
2. Prioritize established deterministic software for downloading, parsing, OCR, segmentation,
   citation anchoring, validation, deduplication, and numerical work.
3. Where semantic interpretation requires an LLM, prioritize maintained structured-output tools or
   reusable skills that can use inexpensive models through OpenRouter.
4. LLMs may classify, normalize, and narrate text. They must not calculate portfolio weights,
   exposure, risk, or trade sizes; deterministic code must perform those calculations.
5. Exact quotation and source-location preservation are mandatory for serious candidates.
6. Broker execution must remain completely manual.
7. Prefer zero-cost, open-source, locally runnable components. Consider only very-cheap hosted or
   model usage. Exclude products with material mandatory subscriptions, enterprise-only pricing,
   or high per-document costs.
8. Do not propose building a new framework. A recommendation may compose a small number of
   established tools, but every component must already exist, be maintained, documented, and used
   outside this project.
9. Investigate whether a credible complete software product already performs most or all of this
   workflow. Do not assume that no such product exists.
10. Karakeep is currently considered most likely irrelevant. Reconsider it only if evidence shows
    that it contributes unique value beyond bookmarking, custody, archiving, generic summaries,
    and search.

### What "battle-proven" means

A GitHub repository, marketing page, or agent demonstration is insufficient. For every shortlisted
candidate, investigate:

- Active maintainer or commercial owner.
- Current stable version and latest release date.
- Release cadence and unresolved critical issues.
- License and self-hosting availability.
- Documented APIs, CLI, or reproducible batch interface.
- Evidence of production adoption, package usage, credible case studies, or independent evaluation.
- Supported source formats and languages, including German.
- Structured-output and citation/provenance capabilities.
- Deterministic and model-dependent stages.
- OpenRouter compatibility or required inference provider.
- Local-data and privacy implications.
- CPU/GPU requirements.
- Mandatory fees and a realistic low-volume monthly cost estimate.
- Failure handling, validation, and observability.

Use current primary sources for technical capabilities, releases, licenses, pricing, and API
behavior. Use credible independent sources only for adoption and operational experience. Clearly
separate verified facts from your inferences.

### Required search scope

Research both complete products and composable tools across these stages:

1. Video/audio acquisition and transcript generation, including timestamps and German support.
2. Email parsing, MIME/attachment preservation, and Gmail/IMAP or workflow-system handoff.
3. Web-page acquisition and readable-content extraction.
4. PDF parsing, layout extraction, tables, scanned pages, and OCR.
5. Atomic claim or event extraction with constrained structured output.
6. Entity linking for companies, securities, industries, countries, and macro variables.
7. Exact quote/page/timestamp citation validation.
8. Contradiction, support, novelty, and confidence classification.
9. Export to stable JSON or JSONL for a separate deterministic portfolio-mapping program.
10. Optional end-to-end research-intelligence products that already cover most stages.

Potentially relevant categories include mature speech-to-text engines, document-intelligence
systems, scientific-paper parsers, information-extraction libraries, constrained-generation
libraries, knowledge-graph tools, and financial research platforms. Treat examples as search leads,
not endorsements. Search beyond the best-known names.

### Research-only use-case fit assessment

Inspect the attached Markus Koch transcript and research PDF only to understand the real input
characteristics: timestamped German transcript segments, transcription errors, a multi-page research
document, page citations, and possible tables. Do not run tools, simulate tool output, extract a
supposed gold-standard answer, or claim that any candidate processed these files.

For each shortlisted candidate, determine from official documentation and credible published
evidence whether it appears capable of handling timestamped German transcript segments,
transcription noise, exact quotation preservation, entity extraction, and source-location output.
Record unsupported or unclear capabilities as unknown rather than inferring that they work.

For the PDF use case, research whether each candidate documents support for:

- Text and layout recovery.
- Page-level citations.
- Table handling where applicable.
- Atomic claim extraction.
- Separation of source facts, author opinions, forecasts, and recommendations.

For email, research documented support for MIME headers, plain text, HTML, attachments, forwarded
messages, and attachment provenance. State when a separate email parser or workflow connector would
be required.

For later portfolio mapping, assess whether candidates can export stable structured data suitable
for a separate deterministic program. Do not design or claim to validate the portfolio mapper.

### Ranking method

Rank candidates using documented evidence, not hypothetical performance. Use this weighted rubric:

- 20%: exact quotation, citation, and provenance capabilities.
- 15%: transcript, email, web, and PDF source coverage.
- 15%: deterministic/reproducible stages and structured output.
- 15%: evidence of production adoption and operational maturity.
- 15%: zero or genuinely low cost.
- 10%: maintenance health and documentation quality.
- 5%: German-language support.
- 5%: local operation or inexpensive OpenRouter compatibility.

For every score, provide the supporting source or mark it `unknown`. Penalize unknowns rather than
turning them into assumed capabilities. Do not label a candidate "validated," "passing," or
"battle-tested for this use case" solely from the ranking.

### Required final report

Return the report in this exact structure:

1. **Executive answer** — whether a plausible complete product exists and the best research-backed
   approach.
2. **Market landscape** — the relevant product and tool categories.
3. **Complete-product search** — candidates, evidence, costs, and reasons for inclusion or rejection.
4. **Composable-tool longlist** — grouped by pipeline stage.
5. **Ranked shortlist** — weighted scores with a citation or `unknown` for every material capability.
6. **Shortlist comparison table** — maintenance, adoption, formats, citations, German support,
   OpenRouter support, privacy, hardware, and low-volume cost.
7. **Recommended candidate stack** — components worth validating later and why; do not describe it
   as proven for this workflow.
8. **Attached-file fit assessment** — documented ability to handle the characteristics of the
   Markus Koch transcript and research PDF, without claiming that either file was processed.
9. **Later human-run validation checklist** — the smallest experiments needed to verify the major
   unknowns. Do not execute or fabricate their results.
10. **Karakeep decision** — retain, optional, or remove, based on researched capabilities.
11. **Cost and privacy assessment** — realistic low-volume scenario; reject materially expensive
    options.
12. **Risks, unknowns, and operator decisions** — do not conceal missing evidence.
13. **Sources** — direct links placed next to supported claims, prioritizing official sources.

Do not install software, create accounts, request credentials, run candidate tools, simulate their
outputs, or claim empirical validation. This assignment is limited to current web research,
evidence-backed comparison, ranking, and identification of what must be tested later by an operator
or execution-capable agent.
