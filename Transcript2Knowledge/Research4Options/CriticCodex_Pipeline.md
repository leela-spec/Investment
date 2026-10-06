criticed documetn: C:\GitDev\Investment\Transcript2Knowledge\Research4Options\Gemini Deep Research Prompt — Proven Source-to-Investment-Claim Toolchain.md

The research is directionally right: there is no cheap, proven single product that turns every video, email, PDF, and article into trustworthy portfolio-relevant investment claims. Karakeep should remain out of the core design.

But Gemini’s “9.7/10” stack ranking is not evidence. It combines unrelated tools into a hypothetical system and then scores the result as if it had been tested end-to-end. It has not proven the hard part: extracting correct financial claims from imperfect sources and grounding each claim precisely enough to trust.

The important correction is this:

```
Source acquisition
→ deterministic text / PDF extraction and stable source anchors
→ LLM proposes structured claim candidates
→ deterministic evidence validation
→ operator review / acceptance
→ portfolio exposure and thesis comparison
→ manual trading decision
```

Only the following can be deterministic:

- Source hashes, timestamps, PDF page references, and transcript segment IDs
- Whether a quoted passage exactly exists in the source
- Schema validity, duplicate detection, portfolio weights, exposure calculations
- The link from an approved claim to a holding, sector, or thesis rule

An LLM cannot deterministically decide that “liquidity is deteriorating” is true, important, or relevant to a holding. It can propose that claim, classify it, and explain why—but the system must label it as a candidate until its quotation, context, and portfolio mapping pass checks.

The research’s strongest practical recommendation is a small composable stack, but with a sharper division of responsibility:

|Need|Sensible candidate|What it actually gives IPOS|
|---|---|---|
|Existing transcript|Your existing normalized Markdown transcript|Immediate source text with stable segment anchors; bypass ASR while testing the real claim pipeline|
|YouTube transcription later|`yt-dlp` + `faster-whisper` / WhisperX|Audio and timed transcript; not validated investment knowledge|
|PDFs|Docling, compared empirically with Marker|Text, reading order, pages, tables, and provenance candidates|
|Emails|Standard Python `email` parser for `.eml` first|Deterministic body/attachment extraction; acquisition from Gmail/Web.de is separate|
|Articles|trafilatura|Clean text from ordinary static pages; not reliable for paywalls or JavaScript-heavy sites|
|Structured claim output|Instructor/Pydantic + an OpenRouter model|Enforces claim JSON shape, not truth or grounding|
|Quote validation|Exact normalized substring/anchor matching|Proves the quoted evidence exists in the supplied source|
|Instrument identifiers|OpenFIGI, only after known identifiers exist|Identifier lookup; not general company-name resolution|

Two parts of the Gemini proposal need explicit downgrading:

- `RapidFuzz ≥95%` is not a sufficient evidence gate. Fuzzy matching can “validate” a materially altered quote. Use exact matching first; fuzzy matching may only suggest a recovery location for human review.
- GLiNER and OpenFIGI do not solve entity-to-portfolio mapping. GLiNER is an ML candidate generator, and OpenFIGI maps known identifiers—not arbitrary mentions such as “European banks” or “AI infrastructure.”

The real bottleneck is not PDF parsing, YouTube downloading, or JSON schemas. It is this question:

> Can the system produce a short list of atomic, source-grounded claims that an operator can actually use to inspect portfolio risk or opportunity?

So I would reject both extremes:

- Do not build another broad “IPOS pipeline.”
- Do not buy or install a pile of tools because a research table ranked them highly.

The next valid work item is a narrow empirical validation using the existing normalized Markus Koch Markdown transcript and the existing PDF:

1. Feed the transcript directly into a structured-claim prompt.
2. Require every claim to cite exact transcript segment IDs and quotes.
3. Reject claims whose quotes cannot be exactly found.
4. Do the same for a small selected section of the PDF, including page references.
5. Have the system map only approved claims against the existing portfolio/thesis data.
6. Produce an operator report that clearly separates:
    - source fact / speaker claim,
    - extracted candidate claim,
    - validated evidence,
    - portfolio implication,
    - uncertainty and required human decision.

Only if that produces useful, grounded findings should we add ingestion automation for YouTube, Web.de, Gmail, PDFs, and articles.