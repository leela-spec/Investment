# External-product integration specification

**Status:** product interfaces verified against primary documentation; deployment and real-data acceptance pending. Pin the selected release, Python/runtime, model artifacts and solver versions in the existing dependency mechanism after host compatibility checks. Do not overwrite an unseen lockfile or claim the documented version is already installed.

## 1. Product selections and intentional exclusions

| Need | Selected integration | Reuse / limit |
|---|---|---|
| Speech and alignment | WhisperX CLI with its faster-whisper backend | Actual ASR/alignment product, not a claim-truth engine. [E6] |
| Source-grounded candidate cards | LlamaIndex `PydanticProgramExtractor` and supported Pydantic program/provider | Framework supplies extraction; domain schema and quote validation are integration code, not a replacement TTK framework. [E7] |
| Documents and custody | Retain R3 Docling and R1 Karakeep choices | Do not add Unstructured as a competing default without a demonstrated format gap. [R4] [R5] |
| Statistical clusters and risk diagnostics | Riskfolio `plot_clusters`, `plot_dendrogram`, `plot_risk_con` | These do not supply sector taxonomy or determine macro effects. [E8] |
| Sector/industry display | Plotly treemap, supplementary to numerical table/bar | Offline companion HTML; leave the established core renderer intact. [R3] [E10] [E11] |
| Broker PDF parsing | Portfolio Performance's actual desktop importer and CSV export | No copied Java parsers, invented headless CLI, paid broker API, or cloud PDF transmission. [E12] [E13] |
| Cross-OS transfer | OpenSSH SFTP | Existing transport; no shared database, custom transport server or extra queue framework. [E4] [E21] |

## 2. M08: media in WSL2/ext4

Retain the original video, acquisition metadata and audio. An `.m4a` alone cannot satisfy slide extraction. Hash originals separately from derivatives; record the common media timeline and any trim offset. Never remove introductions/ad segments without preserving a time mapping.

With the approved WSL environment already installed and `IPOS_MEDIA_URL` set to one authorized source, these are real product commands, not commands executed in this audit:

```bash
set -euo pipefail
: "${IPOS_MEDIA_URL:?Set one authorized media URL}"
: "${IPOS_MEDIA_DIR:?Set an ext4 output directory}"
cd "$IPOS_MEDIA_DIR"
yt-dlp --ignore-config --no-playlist --write-info-json \
  -f 'bv*+ba/b' --merge-output-format mkv --remux-video mkv \
  -o 'source.%(ext)s' "$IPOS_MEDIA_URL"
ffmpeg -nostdin -n -i source.mkv -vn -c:a aac audio.m4a
whisperx audio.m4a --language de --device cpu --compute_type int8 \
  --output_format json --output_dir aligned
scenedetect -i source.mkv -o slides detect-content list-scenes save-images
```

Select language from the source; `de` is an explicit example, not an autodetected fact. The CPU path avoids inventing CUDA compatibility. A GPU profile is enabled only after its actual driver/model test. Freeze the chosen model name explicitly after the first compatibility run; the illustrative CLI uses the installed default and is not a production lock. [E6] [E19] [E20]

WhisperX alignment is derived evidence: some tokens can lack trustworthy word timing or be interpolated. Keep segment-level anchors and alignment status. "Exact quote" below means exact bytes/text of the retained transcript, not independently verified audio transcription. Check quoted financial numbers against audio before consequential promotion.

## 3. M09: bind to LlamaIndex, not a bespoke prompt pipeline

Use the framework's extractor template and a domain output schema. No custom multi-agent TTK runner, vector database or hosted parsing service is required. This is the verified OpenAI-program adapter example; `llm` must be an explicitly configured, compatible provider object with authorized credentials. An AI subscription must not be assumed to grant API access. An approved local/provider adapter may replace it only after the same acceptance tests. [E7]

```python
from pydantic import BaseModel, Field
from llama_index.core.schema import TextNode
from llama_index.core.extractors import PydanticProgramExtractor
from llama_index.program.openai import OpenAIPydanticProgram

class Candidate(BaseModel):
    claim: str = Field(description="One proposition stated in this segment.")
    quote: str = Field(min_length=1, description="Exact contiguous source wording.")
    falsifier: str | None = Field(
        default=None, description="Explicit source-stated invalidation condition, else null."
    )

class CandidateBatch(BaseModel):
    claims: list[Candidate]

def extract_segment(segment: dict, transcript_sha256: str, llm) -> list[dict]:
    text = segment["text"]
    program = OpenAIPydanticProgram.from_defaults(
        output_cls=CandidateBatch, prompt_template_str="{input}", llm=llm
    )
    extractor = PydanticProgramExtractor(program=program, input_key="input")
    node = TextNode(text=text, id_=str(segment["id"]))
    raw = extractor.extract([node])[0]
    batch = CandidateBatch.model_validate(raw)
    accepted = []
    for item in batch.claims:
        start = text.find(item.quote)
        # Repeated quotations require a reviewed occurrence, not a guessed anchor.
        if start < 0 or text.find(item.quote, start + 1) >= 0:
            raise ValueError("Unmatched or ambiguous source quote; retain for review")
        accepted.append({
            **item.model_dump(), "status": "CANDIDATE",
            "transcript_sha256": transcript_sha256,
            "segment_id": segment["id"], "char_start": start,
            "char_end": start + len(item.quote),
            "segment_start_s": segment["start"],
            "segment_end_s": segment["end"],
        })
    return accepted
```

Inputs must already have unique segment IDs, finite ordered timestamps and the verified transcript hash. Offsets are relative to that immutable segment. Reject an entire failed extraction attempt without discarding its diagnostic record. To cover propositions spanning segments, assemble bounded neighboring segments with explicit offset mapping; do not concatenate silently or claim this one-segment binding solves all context loss.

**Promotion contract:** record source URL/acquisition ID, media and transcript hashes, extraction product/model/version, source language, quote offsets and review outcome outside the LLM response. A nullable falsifier is deliberate: the model must not invent a condition the source never stated. A reviewer can separately author a testable hypothesis. Deterministic code then evaluates approved conditions against typed observations with units, dates and missing-data handling. No automatic assertion of truth follows from schema or quote matching.

**Axiom resolution:** extraction is bounded evidence annotation, not numeric portfolio authority. It cannot set target weights, order quantities, tax basis, thresholds, stop prices or active rules. Strictly banning all upstream model use would conflict with the requested semantic extraction itself; this limited role is the interpretation adopted here.

## 4. C13/WF07: actual Riskfolio and Plotly calls

The following integration accepts **real already-normalized inputs**, not downloaded or fabricated sample returns. `returns_eur` contains a declared, complete, adjusted-return investment sleeve; `weights` is its approved allocation. `holdings` is a separate full-account valuation table. Cash/excluded assets and sleeve coverage must be stated in the report; do not silently renormalize or pretend the cluster represents the whole portfolio. Missing history blocks the statistical view, not the holdings table.

```python
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import riskfolio as rp
import plotly.express as px

def render_portfolio_views(returns_eur, weights, holdings, out_dir,
                           as_of, min_observations, scope_label):
    R = returns_eur.sort_index()
    if (not isinstance(R.index, pd.DatetimeIndex) or R.index.has_duplicates
            or R.columns.has_duplicates or weights.index.has_duplicates):
        raise ValueError("Ambiguous return or weight identity")
    if R.empty or R.shape[1] < 2 or len(R) < max(2, min_observations):
        raise ValueError("Insufficient declared-sleeve history")
    if R.index.max() > pd.Timestamp(as_of):
        raise ValueError("Future return observation")
    if set(R.columns) != set(weights.index):
        raise ValueError("Return/weight universe mismatch")
    w = weights.reindex(R.columns).astype(float)
    if (not np.isfinite(R.to_numpy(dtype=float)).all()
            or not np.isfinite(w).all() or (R.std() <= 0).any()
            or (w < 0).any() or not np.isclose(w.sum(), 1.0, atol=1e-8, rtol=0)):
        raise ValueError("Invalid long-only sleeve returns or weights")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for name, function in [("clusters", rp.plot_clusters),
                           ("dendrogram", rp.plot_dendrogram)]:
        ax = function(returns=R, codependence="pearson", linkage="ward")
        ax.set_title(f"{scope_label}: {name}; through {as_of}")
        ax.figure.savefig(out / f"{name}.svg", bbox_inches="tight")
        plt.close(ax.figure)
    ax = rp.plot_risk_con(w=w.to_frame("weights"), returns=R,
                          cov=R.cov(), rm="MV", percentage=True)
    ax.figure.savefig(out / "risk-contribution.svg", bbox_inches="tight")
    plt.close(ax.figure)
    H = holdings.copy()
    needed = ["sector", "industry", "instrument", "value_eur", "macro_score"]
    if H[needed].isna().any().any():
        raise ValueError("Missing valuation or approved sector/macro mapping")
    if (not np.isfinite(H[["value_eur", "macro_score"]].to_numpy()).all()
            or (H["value_eur"] <= 0).any()):
        raise ValueError("Treemap requires positive, finite positions")
    fig = px.treemap(H, path=["sector", "industry", "instrument"],
                     values="value_eur", color="macro_score",
                     hover_data=["value_eur", "macro_score"])
    fig.write_html(out / "sector-exposure.html",
                   include_plotlyjs=True, full_html=True)
```

The caller enforces a single timezone convention, approved observation frequency/window and corporate-action treatment. `min_observations` is an explicit policy input, not an invented statistical guarantee. Unknown sector or macro mapping must be displayed as unknown in the main table, not turned into a neutral zero to satisfy this supplemental renderer. Output is published only after every selected view succeeds. [E8] [E10] [E11]

**Optimization is separate.** A real supported binding is `rp.Portfolio(returns=R)`, followed by `assets_stats(method_mu="hist", method_cov="hist")` and `rp_optimization(model="Classic", rm="MV", b=b, hist=True)`, with positive, normalized risk budgets `b` aligned to assets. This identifies the product interface, not a replacement implementation of missing C13. Preserve its actual constraints when recovered. Verify returned weights, solver result, budget/constraint residuals and cash feasibility independently. HRP is not synonymous with this convex risk-budgeting solve. [E9]

Sector taxonomy comes from an approved instrument master with source/date; correlation clusters remain statistical labels. Macro headwinds/tailwinds come from versioned approved rules. A Plotly color or LLM opinion must not become an optimizer parameter without that explicit mapping.

## 5. Smartbroker PDFs and finanzen.net zero

Use **Portfolio Performance locally**: create/select the appropriate account, use its PDF bank-document import, inspect the preview, then export the relevant securities-account and cash-account transactions to CSV. Preserve issuing bank, document type, statement hash and account identity. DAB/BNP and Baader have real Java extractor classes; support is based on document patterns, not merely the Smartbroker brand. [E12] [E13] [E14] [E15]

No supported standalone PDF-to-JSON CLI was established in this audit. Therefore this path intentionally retains the import/review/export clicks instead of proposing a fake Python wrapper or new Java service. A `Depotuebersicht` holdings PDF is **not proven supported for the operator's exact format**. If it fails, retain R3 Docling as human-reviewed table extraction or use a manual normalized holdings snapshot; do not invent transactions. [R2] [R5]

The already supported zero holdings CSV remains a snapshot input. Transaction exports require a separate typed adapter: account, source event ID, ISIN/instrument, date/time, event type, quantity, native amount, currency, fees/taxes and FX convention. Cross-document duplicates, cancellations, transfers and corporate actions must reconcile before FIFO. Pairing the cash leg and securities leg of one trade must not double-count it.

## 6. C12 Wealthfolio and custody boundaries

Current documentation distinguishes holdings mode from transaction mode. A holdings-mode CSV uses `date,symbol,quantity,avgCost,currency`; date/symbol/quantity are required, and `$CASH` denotes cash. Use only known cost, never zero for unknown basis. Transaction-mode schemas are version-specific and need explicit fee, amount and FX reconciliation. Verify the installed desktop release before choosing the import mapping. [E16] [E22]

Use the native backup/export function and compare a **Windows-local exported SQLite backup**, not the open application DB across WSL. The documented Windows directory is `%APPDATA%\com.teymz.wealthfolio\`; verify installation rather than hard-code a database schema. Integrity checks precede version-specific table inspection. A backup is not proof of numeric parity: compare original broker controls, the normalized IBOR, and exported Wealthfolio results using identical dates, prices and cost methods. [E17]

Karakeep's API is the integration boundary, never direct access to its database. Follow pagination and export original assets plus metadata. A client labelled "read-only MCP" is not automatically a server-enforced read-only credential. When scoped authorization cannot be demonstrated, give the narrator a read-only exported evidence bundle rather than a write-capable API secret. [R4] [R5] [E18]

If Hermes runs in WSL, a second Windows-initiated SFTP transfer publishes the committed host report into a dedicated WSL staging inbox. Its report-drop credential is distinct from the read-only evidence-pull credential. Neither role may open databases or alter active rules. The WSL receiver verifies the report bundle before narration; delivery failure leaves numerical output valid. See phase 1 of artifact 04 for the two-direction contract. [E4] [E5] [E21]

## 7. Expected return on integration effort

Highest immediate value is preventing wrong portfolio totals and recovering authoritative sources. Next is supported broker import plus independent reconciliation, then the aligned-transcript/quote-review flow. Riskfolio diagnostics reuse an already selected product; Plotly is an optional presentation layer. No paid broker API, new vector service, extra workflow framework or global Docker migration is justified by the inspected gaps. Monetary savings and investment performance improvements have not been measured and are not claimed.

## Source links

[E6]: https://github.com/m-bain/whisperX "WhisperX official project"
[E7]: https://developers.llamaindex.ai/python/examples/metadata_extraction/pydanticextractor/ "LlamaIndex Pydantic extraction"
[R4]: https://github.com/leela-spec/Investment/blob/cec42be2aaf922c74ea6b13dc44fe11adfdd618f/05_blueprint/research/2026-08-23-ipos-reuse-expansion-program/results/R1-karakeep-ipos/CURRENT_IPOS_GAP_MAP.md "Existing Karakeep gap map"
[R5]: https://github.com/leela-spec/Investment/blob/cec42be2aaf922c74ea6b13dc44fe11adfdd618f/05_blueprint/research/2026-08-23-ipos-reuse-expansion-program/results/R3-evidence-kb/TOOL_LANDSCAPE.md "Existing evidence-KB landscape"
[E8]: https://riskfolio-lib.readthedocs.io/en/latest/riskfoliolib/plot.html "Riskfolio plotting API"
[R3]: https://github.com/leela-spec/Investment/blob/cec42be2aaf922c74ea6b13dc44fe11adfdd618f/05_blueprint/research/2026-07-29_dashboard_visualization_audit.md "Existing visualization audit, especially sections 0-2"
[E10]: https://plotly.com/python/treemaps/ "Plotly treemap API"
[E11]: https://plotly.com/python/interactive-html-export/ "Plotly self-contained HTML export"
[E12]: https://help.portfolio-performance.info/en/reference/file/import/pdf-import/ "Portfolio Performance PDF import"
[E13]: https://help.portfolio-performance.info/en/reference/file/export/ "Portfolio Performance CSV export"
[E4]: https://learn.microsoft.com/en-us/windows-server/administration/OpenSSH/openssh-overview "Windows OpenSSH"
[E21]: https://man.openbsd.org/sftp-server.8 "OpenSSH read-only SFTP server"
[E19]: https://github.com/yt-dlp/yt-dlp "yt-dlp official project"
[E20]: https://www.scenedetect.com/cli/ "PySceneDetect CLI"
[E9]: https://riskfolio-lib.readthedocs.io/en/latest/riskfoliolib/portfolio.html "Riskfolio convex portfolio API"
[E14]: https://github.com/portfolio-performance/portfolio/blob/master/name.abuchen.portfolio/src/name/abuchen/portfolio/datatransfer/pdf/DABPDFExtractor.java "Actual DAB PDF extractor"
[E15]: https://github.com/portfolio-performance/portfolio/blob/master/name.abuchen.portfolio/src/name/abuchen/portfolio/datatransfer/pdf/BaaderBankPDFExtractor.java "Actual Baader PDF extractor"
[R2]: https://github.com/leela-spec/Investment/blob/cec42be2aaf922c74ea6b13dc44fe11adfdd618f/05_blueprint/03_PORTFOLIO_MODULE.md "Built portfolio comparison specification"
[E16]: https://wealthfolio.app/docs/guide/csv-import/ "Wealthfolio CSV and holdings-mode import"
[E22]: https://wealthfolio.app/docs/concepts/tracking-modes/ "Wealthfolio tracking modes"
[E17]: https://wealthfolio.app/docs/guide/data-export/ "Wealthfolio export and backup"
[E18]: https://docs.karakeep.app/api/karakeep-api/ "Karakeep API"
[E5]: https://learn.microsoft.com/en-us/windows/wsl/networking "Microsoft WSL networking"
