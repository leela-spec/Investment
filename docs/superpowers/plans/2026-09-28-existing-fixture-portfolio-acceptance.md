# Existing Research Fixture and Portfolio Acceptance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run the existing transcript, research-PDF, broker-ledger, broker-statement, ZERO-portfolio, and macro-snapshot fixtures through one unattended acceptance path that proves evidence grounding, portfolio reconciliation, deterministic decision effects, report output, idempotency, and the manual-broker boundary.

**Architecture:** Add one small fixture manifest, adapters only where an existing artifact format is not currently consumable, and one isolated acceptance runner. The runner reads source fixtures in place, writes only to a temporary run directory under `implementation-runs/fixture-acceptance/`, and never mutates the live warehouse, live action/watch register, source fixtures, or broker files. Transcript-derived WATCH items are tested without trading impact; a separate explicitly simulated operator promotion proves the existing ACTION-to-portfolio path.

**Tech Stack:** Python 3.11+, uv, pytest, PyYAML, Pydantic, pandas, pypdf, existing IPOS evidence/portfolio engines, existing TTK V2 artifacts, DuckDB-free component execution for the acceptance runner.

## Global Constraints

- Code computes every numeric value; LLMs only classify or narrate.
- All broker execution remains manual and operator-controlled.
- The five transcript fixture directories, research PDFs, broker exports, and existing snapshots are read-only inputs.
- Never copy the private Smartbroker activity CSV, broker statement, or portfolio contents into Git.
- Never write credentials, tokens, cookies, mailbox secrets, or broker secrets.
- The acceptance run must not modify `data/action_watch_register.json`, `data/warehouse.duckdb`, or existing `data/exports/` snapshots.
- Test outputs go only to a newly created timestamped directory under `implementation-runs/fixture-acceptance/`.
- Missing optional live services do not block fixture acceptance; Karakeep, Activepieces, Gmail, WEB.DE, and broker portals are out of scope.
- Raw ASR and PDF text are evidence, not automatically verified fact.
- A transcript WATCH has no automatic portfolio effect. Portfolio impact is tested only after an explicit simulated operator promotion to ACTION in the isolated test register.
- Preserve all unrelated dirty-worktree changes and commit only the paths named by each task.

---

## File Structure

- Create `configs/fixture_acceptance.yaml`: stable fixture identities, paths, hashes, expected counts, and non-secret acceptance invariants.
- Create `ipos/evidence/ttk_adapter.py`: read-only TTK V2 transcript/evidence adapter that emits IPOS-compatible segments and selected grounded claim cards.
- Create `ipos/evidence/document_adapter.py`: deterministic PDF extraction and exact-quote/page grounding.
- Create `ipos/fixture_acceptance.py`: isolated orchestration of fixtures, portfolio replay, decision comparison, and result generation.
- Modify `ipos/cli.py`: add the `fixture-acceptance` command only.
- Modify `pyproject.toml`: add `pypdf` and expose `ipos-fixture-acceptance`.
- Create `tests/test_fixture_acceptance_manifest.py`: manifest validation and read-only source guarantees.
- Create `tests/test_ttk_adapter.py`: TTK V2 conversion, grounding, validation, and NO_IMPACT control behavior.
- Create `tests/test_document_adapter.py`: real research-PDF extraction, hashing, and exact page grounding.
- Create `tests/test_fixture_portfolio_replay.py`: real Smartbroker/ZERO reconciliation and 32-holding consolidation.
- Create `tests/test_fixture_acceptance.py`: complete isolated acceptance, idempotency, portfolio delta, and manual-order boundary.
- Create `orchestration/work/RI-10.yaml`: bounded unattended fixture-acceptance packet.
- Modify `orchestration/state.yaml`: make RI-10 the executable fixture-validation frontier without falsely completing RI-01.

---

### Task 1: Pin and Validate the Existing Fixture Inventory

**Files:**
- Create: `configs/fixture_acceptance.yaml`
- Create: `tests/test_fixture_acceptance_manifest.py`

**Interfaces:**
- Consumes: Existing repository and `C:/GitDev/apexai-os-meta` files.
- Produces: `configs/fixture_acceptance.yaml`, loaded with `yaml.safe_load`, containing `transcripts`, `research_documents`, `portfolios`, and `macro_snapshot` mappings.

- [ ] **Step 1: Write the manifest validation test**

```python
from hashlib import sha256
from pathlib import Path
import yaml


MANIFEST = Path("configs/fixture_acceptance.yaml")


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def test_fixture_manifest_resolves_and_hashes_match():
    data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    fixtures = (
        data["transcripts"]
        + data["research_documents"]
        + data["portfolios"]
        + [data["macro_snapshot"]]
    )
    for fixture in fixtures:
        path = Path(fixture["evidence_file"])
        assert path.is_file(), fixture["id"]
        assert digest(path) == fixture["sha256"], fixture["id"]
```

- [ ] **Step 2: Run the test to verify it fails because the manifest is absent**

Run: `uv run pytest -q tests/test_fixture_acceptance_manifest.py`

Expected: FAIL with `FileNotFoundError: configs/fixture_acceptance.yaml`.

- [ ] **Step 3: Create the exact manifest**

```yaml
schema_version: 1
mode: offline_read_only
transcripts:
  - id: imf-weo-july-2026
    identity: vzZpKJlpqKo
    root: implementation-runs/E05/20260923-230911
    evidence_file: implementation-runs/E05/20260923-230911/RESEARCH_ARTIFACT.yaml
    transcript_file: implementation-runs/E05/20260923-230911/audio.json
    sha256: 0f9fd85f8d340b065dae7ee5a5e8aeb7983a6b981407a7bebb383fc373e25d76
    expected_outcome: WATCH
  - id: markus-koch-tech-pressure
    identity: vFTuLylvYnA
    root: C:/GitDev/apexai-os-meta/artifacts/transcript_pipeline_v2/corrective-run/raw/p20-four-source/vFTuLylvYnA
    evidence_file: C:/GitDev/apexai-os-meta/artifacts/transcript_pipeline_v2/corrective-run/raw/p20-four-source/vFTuLylvYnA/manifest.json
    transcript_file: C:/GitDev/apexai-os-meta/artifacts/transcript_pipeline_v2/corrective-run/raw/p20-four-source/vFTuLylvYnA/source/transcript.json
    claims_file: C:/GitDev/apexai-os-meta/artifacts/transcript_pipeline_v2/corrective-run/raw/p20-four-source/vFTuLylvYnA/ledger/evidence.json
    validation_file: C:/GitDev/apexai-os-meta/artifacts/transcript_pipeline_v2/corrective-run/raw/p20-four-source/vFTuLylvYnA/validation.json
    sha256: fef5e25f25da395ec83418702a1e466f1e6fe0c97578e41bb5f53779916b1681
    expected_outcome: WATCH
  - id: elliott-wave-technical-market
    identity: CygwqaNg2PY
    root: C:/GitDev/apexai-os-meta/artifacts/transcript_pipeline_v2/corrective-run/raw/p20-four-source/CygwqaNg2PY
    evidence_file: C:/GitDev/apexai-os-meta/artifacts/transcript_pipeline_v2/corrective-run/raw/p20-four-source/CygwqaNg2PY/manifest.json
    transcript_file: C:/GitDev/apexai-os-meta/artifacts/transcript_pipeline_v2/corrective-run/raw/p20-four-source/CygwqaNg2PY/source/transcript.json
    claims_file: C:/GitDev/apexai-os-meta/artifacts/transcript_pipeline_v2/corrective-run/raw/p20-four-source/CygwqaNg2PY/ledger/evidence.json
    validation_file: C:/GitDev/apexai-os-meta/artifacts/transcript_pipeline_v2/corrective-run/raw/p20-four-source/CygwqaNg2PY/validation.json
    sha256: 2da160f244b74ed382d90d62bb358e714eb0f8cf842ebcacd13ec681e4f67f6d
    expected_outcome: WATCH
  - id: market-cycles-watch
    identity: oZIsMX6WgFs
    root: C:/GitDev/apexai-os-meta/artifacts/transcript_pipeline_v2/corrective-run/raw/p20-four-source/oZIsMX6WgFs
    evidence_file: C:/GitDev/apexai-os-meta/artifacts/transcript_pipeline_v2/corrective-run/raw/p20-four-source/oZIsMX6WgFs/manifest.json
    transcript_file: C:/GitDev/apexai-os-meta/artifacts/transcript_pipeline_v2/corrective-run/raw/p20-four-source/oZIsMX6WgFs/source/transcript.json
    claims_file: C:/GitDev/apexai-os-meta/artifacts/transcript_pipeline_v2/corrective-run/raw/p20-four-source/oZIsMX6WgFs/ledger/evidence.json
    validation_file: C:/GitDev/apexai-os-meta/artifacts/transcript_pipeline_v2/corrective-run/raw/p20-four-source/oZIsMX6WgFs/validation.json
    sha256: cc50a79f8d889132c214705cd830f69ff49e92c1b50d88be3bc94188377ccb48
    expected_outcome: WATCH
  - id: emotions-non-investment-control
    identity: P-h5WSQG1Sw
    root: C:/GitDev/apexai-os-meta/artifacts/transcript_pipeline_v2/corrective-run/raw/p20-four-source/P-h5WSQG1Sw
    evidence_file: C:/GitDev/apexai-os-meta/artifacts/transcript_pipeline_v2/corrective-run/raw/p20-four-source/P-h5WSQG1Sw/manifest.json
    transcript_file: C:/GitDev/apexai-os-meta/artifacts/transcript_pipeline_v2/corrective-run/raw/p20-four-source/P-h5WSQG1Sw/source/transcript.json
    claims_file: C:/GitDev/apexai-os-meta/artifacts/transcript_pipeline_v2/corrective-run/raw/p20-four-source/P-h5WSQG1Sw/ledger/evidence.json
    validation_file: C:/GitDev/apexai-os-meta/artifacts/transcript_pipeline_v2/corrective-run/raw/p20-four-source/P-h5WSQG1Sw/validation.json
    sha256: d092cb2793595bd323b910defdb27ae70da862bc0af7a0a4938aac38dc19a0d4
    expected_outcome: NO_IMPACT
research_documents:
  - id: elephant-room-research
    evidence_file: Sources/GER Elephant in The Room Analysis.pdf
    companion_text: Sources/GER Elephant in The Room Analysis.md
    sha256: f2d4b8dab16222893ddef1b039b2cca7a7b8f3ec3aea0b0e63befd15dcf8e39e
    expected_pages: 13
    expected_outcome: REVIEW
portfolios:
  - id: smartbroker-activities
    evidence_file: C:/Users/gehma/Downloads/3370191001-2026-09-24T09-02-24.190Z.csv
    sha256: 4fd36847b400b0e011078f7aec290f5fdde705aaaf551fd709f9c51298d6927a
    expected_activities: 332
    expected_open_positions: 24
  - id: smartbroker-statement
    evidence_file: data/inbox/3370191001-2026-09-25T15-15-35.459Z.pdf
    sha256: dcd3d05d542652fb09ba3c57ec48323db1b33c59fdf90deb42c996a401f30b2c
    expected_open_positions: 24
  - id: zero-positions
    evidence_file: data/inbox/ZERO-pos-25.09.2026.csv
    sha256: b329eb187e3c8a653599b7888d4b6df1209fbb2f0332403ad753fd459b04bd38
    expected_open_positions: 8
macro_snapshot:
  id: macro-2026-09-25
  evidence_file: data/exports/snapshots/2026-09-25/snapshot.json
  sha256: 376fd5814a18e67bf365bbd18e186e9d11ee12cb5974dd6ac72532eb0bceaeba
  expected_as_of: 2026-09-25
```

- [ ] **Step 4: Extend the test to reject writable output paths inside source fixtures**

Assert that no manifest entry contains `output_path`, and that every runner-created path is rooted under a pytest `tmp_path` or `implementation-runs/fixture-acceptance/`.

- [ ] **Step 5: Run the manifest test**

Run: `uv run pytest -q tests/test_fixture_acceptance_manifest.py`

Expected: PASS.

- [ ] **Step 6: Commit**

```powershell
git add configs/fixture_acceptance.yaml tests/test_fixture_acceptance_manifest.py
git commit -m "test: pin existing research and portfolio fixtures"
```

---

### Task 2: Adapt TTK V2 Transcripts Without Rewriting TTK

**Files:**
- Create: `ipos/evidence/ttk_adapter.py`
- Create: `tests/test_ttk_adapter.py`

**Interfaces:**
- Consumes: `manifest.json`, `source/transcript.json`, `ledger/evidence.json`, and `validation.json` from one TTK V2 fixture root.
- Produces: `load_ttk_fixture(root: Path) -> TTKFixture` and `build_watch_drop(fixture: TTKFixture, claim_index: int, topic: str) -> dict[str, Any]`.

- [ ] **Step 1: Write failing tests for TTK validation and segment normalization**

```python
from pathlib import Path
from ipos.evidence.ttk_adapter import load_ttk_fixture


ROOT = Path("C:/GitDev/apexai-os-meta/artifacts/transcript_pipeline_v2/corrective-run/raw/p20-four-source/vFTuLylvYnA")


def test_load_ttk_fixture_normalizes_string_segment_ids():
    fixture = load_ttk_fixture(ROOT)
    assert fixture.identity == "vFTuLylvYnA"
    assert fixture.validation["ok"] is True
    assert len(fixture.segments) == 178
    assert fixture.segments[0].id == 0
    assert fixture.original_segment_ids[0] == "seg-000001"
```

- [ ] **Step 2: Run the focused test and verify import failure**

Run: `uv run pytest -q tests/test_ttk_adapter.py::test_load_ttk_fixture_normalizes_string_segment_ids`

Expected: FAIL with `ModuleNotFoundError: ipos.evidence.ttk_adapter`.

- [ ] **Step 3: Implement the minimal read-only adapter**

```python
@dataclass(frozen=True)
class TTKFixture:
    identity: str
    transcript_sha256: str
    segments: list[TranscriptSegment]
    original_segment_ids: list[str]
    candidate_claims: list[dict[str, Any]]
    validation: dict[str, Any]


def load_ttk_fixture(root: Path) -> TTKFixture:
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    transcript_path = root / "source" / "transcript.json"
    transcript_bytes = transcript_path.read_bytes()
    transcript = json.loads(transcript_bytes.decode("utf-8"))
    evidence = json.loads((root / "ledger" / "evidence.json").read_text(encoding="utf-8"))
    validation = json.loads((root / "validation.json").read_text(encoding="utf-8"))
    if not validation.get("ok") or not validation.get("complete"):
        raise ValueError(f"TTK fixture is not complete: {root}")
    original_ids = [str(s["id"]) for s in transcript["segments"]]
    segments = [
        TranscriptSegment(
            id=index,
            start=float(segment["start"]),
            end=float(segment["end"]),
            text=str(segment["text"]),
            words=[],
        )
        for index, segment in enumerate(transcript["segments"])
    ]
    return TTKFixture(
        identity=root.name,
        transcript_sha256=hashlib.sha256(transcript_bytes).hexdigest(),
        segments=segments,
        original_segment_ids=original_ids,
        candidate_claims=list(evidence.get("candidate_claims") or []),
        validation=validation,
    )
```

- [ ] **Step 4: Write failing grounding tests for the three investment fixtures**

Select these exact `candidate_claims` quotes and preserve their cited source segment IDs:

- Markus Koch: `Wir haben die Renditen der 10-jährigen Staatsanleihen heute`
- Elliott Wave: `which is a common pattern and the market did the exact opposite because that was actually part`
- Market Cycles: `It's pure math everyone could do that so now the trap is for sure those cycles are not stable.`

Assert that each produces one grounded WATCH through `process_research_drop`, with timestamps derived from its cited transcript segment. For the IMF WhisperX fixture, use the already-tested exact quote `Trade fragmentation could accelerate, and a correction in technology-driven expectations is another downside risk`.

- [ ] **Step 5: Implement `build_watch_drop`**

The function must embed normalized segments, preserve `source_id`, use `item_class: WATCH`, and preserve the exact candidate quote. It must reject a candidate whose cited segment ID is absent from `original_segment_ids`.

- [ ] **Step 6: Add the non-investment control test**

Load `P-h5WSQG1Sw`, verify its TTK validation and transcript hash, classify its fixture result as `NO_IMPACT`, and assert that no drop is passed to `ActionWatchRegister`. Record the validation receipt only.

- [ ] **Step 7: Run adapter and existing evidence tests**

Run: `uv run pytest -q tests/test_ttk_adapter.py tests/test_evidence_claims.py tests/test_evidence_ingest.py`

Expected: all tests PASS.

- [ ] **Step 8: Commit**

```powershell
git add ipos/evidence/ttk_adapter.py tests/test_ttk_adapter.py
git commit -m "feat: adapt validated TTK fixtures for IPOS evidence tests"
```

---

### Task 3: Add Page-Grounded Research-PDF Evidence

**Files:**
- Modify: `pyproject.toml`
- Modify: `uv.lock`
- Create: `ipos/evidence/document_adapter.py`
- Create: `tests/test_document_adapter.py`

**Interfaces:**
- Consumes: `Sources/GER Elephant in The Room Analysis.pdf`.
- Produces: `extract_pdf(path: Path) -> DocumentEvidence` and `verify_pdf_quote(document: DocumentEvidence, quote: str) -> PageGrounding`.

- [ ] **Step 1: Add the PDF dependency**

Add `pypdf>=5.0` to project dependencies and run `uv lock`.

- [ ] **Step 2: Write the failing real-PDF extraction test**

```python
from pathlib import Path
from ipos.evidence.document_adapter import extract_pdf


PDF = Path("Sources/GER Elephant in The Room Analysis.pdf")


def test_real_research_pdf_is_hashed_and_page_addressable():
    document = extract_pdf(PDF)
    assert document.sha256 == "f2d4b8dab16222893ddef1b039b2cca7a7b8f3ec3aea0b0e63befd15dcf8e39e"
    assert len(document.pages) == 13
    assert all(page.page_number >= 1 for page in document.pages)
    assert sum(len(page.text.strip()) for page in document.pages) > 1000
```

- [ ] **Step 3: Run the test and verify import failure**

Run: `uv run pytest -q tests/test_document_adapter.py::test_real_research_pdf_is_hashed_and_page_addressable`

Expected: FAIL with `ModuleNotFoundError: ipos.evidence.document_adapter`.

- [ ] **Step 4: Implement deterministic PDF extraction**

```python
@dataclass(frozen=True)
class DocumentPage:
    page_number: int
    text: str


@dataclass(frozen=True)
class DocumentEvidence:
    source_path: str
    sha256: str
    pages: list[DocumentPage]


def extract_pdf(path: Path) -> DocumentEvidence:
    raw = path.read_bytes()
    reader = PdfReader(io.BytesIO(raw))
    pages = [
        DocumentPage(page_number=index + 1, text=page.extract_text() or "")
        for index, page in enumerate(reader.pages)
    ]
    return DocumentEvidence(
        source_path=str(path),
        sha256=hashlib.sha256(raw).hexdigest(),
        pages=pages,
    )
```

- [ ] **Step 5: Add exact quote/page grounding tests**

Use this exact page-1 sentence as the test constant: `Die Welt ist nicht schwach genug für einen klassischen Deflations- oder Krisenmodus, aber auch nicht gesund genug für ein echtes, breites Risikoumfeld.` Assert `verify_pdf_quote` returns page 1 and exact character offsets. Also assert the fabricated sentence `The source guarantees a risk-free return of 25 percent.` raises `ValueError` and produces no register item.

- [ ] **Step 6: Implement quote grounding without fuzzy matching**

Normalize whitespace only. Do not correct numbers, translate text, or use OCR/LLM inference. Return `PageGrounding(page_number, start_char, end_char, quote_exact)` for an exact normalized match.

- [ ] **Step 7: Verify the companion Markdown is not substituted for the PDF**

Hash `Sources/GER Elephant in The Room Analysis.md` as `157feb8d8d1bf014857a4bef80b1c1cff0698153c3b2dd2e633b1822c2f2cf13`. Treat it as a comparison artifact only; the accepted quote must ground in the extracted PDF page text.

- [ ] **Step 8: Run the document tests**

Run: `uv run pytest -q tests/test_document_adapter.py`

Expected: all tests PASS.

- [ ] **Step 9: Commit**

```powershell
git add pyproject.toml uv.lock ipos/evidence/document_adapter.py tests/test_document_adapter.py
git commit -m "feat: add exact page grounding for research PDFs"
```

---

### Task 4: Replay and Reconcile the Existing Portfolios

**Files:**
- Create: `tests/test_fixture_portfolio_replay.py`

**Interfaces:**
- Consumes: Smartbroker activities CSV, Smartbroker statement PDF, ZERO positions CSV.
- Produces: A consolidated positions DataFrame with 32 holdings for later acceptance tasks.

- [ ] **Step 1: Write the real-fixture replay test with no skip**

```python
def test_real_broker_fixtures_reconcile_and_consolidate():
    activities = PortfolioPerformanceAdapter(
        default_account="SMARTBROKER"
    ).parse_smartbroker_activities(SMARTBROKER_ACTIVITIES)
    assert len(activities) == 332

    ledger = PortfolioLedger(account_name="SMARTBROKER")
    ledger.replay_activities(activities)
    ledger_positions = ledger.get_open_positions()
    assert len(ledger_positions) == 24
    assert ledger_positions["CA64073L1013"].quantity == 1000.0
    assert ledger_positions["CA74447P1009"].quantity == 10000.0

    statement = _parse_smartbroker_pdf(SMARTBROKER_STATEMENT)
    report = ledger.reconciliation_report(
        external_holdings_control=dict(zip(statement.instrument, statement.quantity))
    )
    assert report["reconciliation_status"] == "MATCH"
    assert report["holdings_discrepancies"] == []

    zero = load_positions(path=ZERO_POSITIONS)
    assert len(zero) == 8
    assert len(statement) + len(zero) == 32
```

- [ ] **Step 2: Make the private activity path configurable without weakening the default**

Resolve `IPOS_SMARTBROKER_ACTIVITIES` when present; otherwise use the exact manifest path. A missing path is a hard acceptance failure, not a pytest skip.

- [ ] **Step 3: Assert market-value controls separately from cost-basis replay**

Assert Smartbroker statement market value is `36411.09` EUR and ZERO market value is `3837.21` EUR. Do not compare these market values with the ledger's economic-cost value (`41508.65` EUR).

- [ ] **Step 4: Run portfolio tests**

Run: `uv run pytest -q tests/test_fixture_portfolio_replay.py tests/test_pp_adapter.py tests/test_portfolio.py`

Expected: all tests PASS and the real Smartbroker test does not skip on this machine.

- [ ] **Step 5: Commit**

```powershell
git add tests/test_fixture_portfolio_replay.py
git commit -m "test: replay and reconcile existing broker portfolios"
```

---

### Task 5: Prove Evidence-to-Portfolio Effects and the Manual Action Boundary

**Files:**
- Create: `tests/test_fixture_acceptance.py`

**Interfaces:**
- Consumes: TTK WATCH drops, PDF REVIEW receipt, consolidated 32-holding portfolio, isolated `ActionWatchRegister`, and the 2026-09-25 macro snapshot.
- Produces: Baseline and promoted-action `MacroPortfolioDecision` objects plus staged manual order tickets.

- [ ] **Step 1: Write the baseline isolation test**

Create the register under `tmp_path`, ingest the three investment transcript fixtures as WATCH items, record the PDF as REVIEW-only evidence, and record the emotions lecture as NO_IMPACT. Assert `MacroPortfolioDecisionEngine.load_open_register_actions()` returns an empty list and baseline sector allocations do not contain research penalties.

- [ ] **Step 2: Run the baseline test and confirm it fails until fixture orchestration exists**

Run: `uv run pytest -q tests/test_fixture_acceptance.py::test_watch_and_review_evidence_cannot_change_portfolio`

Expected: FAIL because the fixture builder is not yet wired.

- [ ] **Step 3: Implement the test fixture builder**

Use the existing 2026-09-25 snapshot values exactly:

```python
regime = snapshot["regime"]
overall = snapshot["overall"]
engine = MacroPortfolioDecisionEngine(register_path=temp_register_path)
baseline = engine.evaluate_decision(
    positions=positions,
    regime_info=regime,
    overall_info=overall,
    contradictions=snapshot.get("contradictions") or [],
    as_of=snapshot["as_of"],
)
```

- [ ] **Step 4: Write the explicit operator-promotion test**

Copy one grounded Markus Koch WATCH into a new temp-register item with `item_class: ACTION`, `instrument_or_topic: TECHNOLOGY_AI`, a new `item_id` prefixed `SIMULATED-OPERATOR-APPROVAL-`, and the original evidence reference. This is the only step allowed to create portfolio impact.

- [ ] **Step 5: Assert deterministic portfolio differences**

Evaluate the decision again and assert:

```python
assert promoted.gating.register_action_gate == "ACTIVE_ALERTS"
assert promoted.gating.allow_sells is True
assert promoted.gating.allow_trims is True
assert tech_promoted.macro_tilt_multiplier == pytest.approx(
    tech_baseline.macro_tilt_multiplier * 0.80
)
assert "SIMULATED-OPERATOR-APPROVAL-" in " ".join(tech_promoted.active_register_items)
```

Assert non-target sectors do not receive that simulated item.

- [ ] **Step 6: Build and stage the action matrix**

Call `build_action_matrix` with the consolidated positions, promoted decision, and existing mapping/names. Pass the result to `stage_orders_from_action_matrix` and assert every ticket is `LIMIT`, broker routing is `ZERO` or `SMARTBROKER`, and the summary contains `Zero automated trade execution.`

- [ ] **Step 7: Prove zero execution leakage**

Retain the existing `tests/test_order_staging.py::test_05_zero_execution_leak` scan and add an acceptance assertion that the runner imports no HTTP, socket, Selenium, broker SDK, or credential module.

- [ ] **Step 8: Run the decision boundary tests**

Run: `uv run pytest -q tests/test_fixture_acceptance.py tests/test_portfolio_decision.py tests/test_action_matrix.py tests/test_order_staging.py`

Expected: all tests PASS.

- [ ] **Step 9: Commit**

```powershell
git add tests/test_fixture_acceptance.py
git commit -m "test: prove research effects preserve manual portfolio control"
```

---

### Task 6: Add One Unattended Acceptance Command and Evidence Report

**Files:**
- Create: `ipos/fixture_acceptance.py`
- Modify: `ipos/cli.py`
- Modify: `pyproject.toml`
- Create: `tests/test_fixture_acceptance_cli.py`

**Interfaces:**
- Consumes: `configs/fixture_acceptance.yaml` and an optional output root.
- Produces: `run_fixture_acceptance(manifest_path: Path, output_root: Path) -> dict[str, Any]`, `result.json`, and `VERIFICATION_REPORT.md`.

- [ ] **Step 1: Write the failing CLI test**

```python
def test_fixture_acceptance_cli_writes_complete_receipt(tmp_path):
    rc = cmd_fixture_acceptance([
        "--manifest", "configs/fixture_acceptance.yaml",
        "--output", str(tmp_path),
    ])
    assert rc == 0
    result = json.loads((tmp_path / "result.json").read_text(encoding="utf-8"))
    assert result["status"] == "PASS"
    assert result["transcripts"]["passed"] == 5
    assert result["documents"]["passed"] == 1
    assert result["portfolio"]["holdings"] == 32
    assert result["portfolio"]["reconciliation"] == "MATCH"
    assert result["manual_execution_only"] is True
```

- [ ] **Step 2: Run it and verify the command is absent**

Run: `uv run pytest -q tests/test_fixture_acceptance_cli.py`

Expected: FAIL importing `cmd_fixture_acceptance`.

- [ ] **Step 3: Implement the isolated runner**

The runner must:

1. Validate fixture paths and hashes before processing.
2. Create a temporary register inside the new output directory.
3. Validate all five transcript fixtures.
4. Ingest three WATCH fixtures, record one IMF WATCH, and record one NO_IMPACT control.
5. Extract and page-ground the research PDF.
6. Replay 332 Smartbroker activities and reconcile 24 positions against the statement.
7. Load eight ZERO positions and build the 32-holding consolidated portfolio.
8. Load the existing macro snapshot without modifying it.
9. Compare baseline and simulated-operator-promotion decisions.
10. Build action matrix and manual-only staged tickets.
11. Re-run ingestion to prove receipt-based idempotency.
12. Write BOM-free UTF-8 `result.json` and `VERIFICATION_REPORT.md`.

- [ ] **Step 4: Add CLI arguments**

```text
ipos fixture-acceptance
  --manifest configs/fixture_acceptance.yaml
  --output implementation-runs/fixture-acceptance/YYYYMMDD-HHMMSS
```

When `--output` is omitted, create the timestamped directory automatically. Never overwrite an existing run directory.

- [ ] **Step 5: Add the project script**

```toml
ipos-fixture-acceptance = "ipos.cli:cmd_fixture_acceptance"
```

- [ ] **Step 6: Add failure and idempotency tests**

Use copies under `tmp_path` to prove: altered hashes fail closed; an ungrounded quote fails; a second run produces no duplicate register item; missing private portfolio input reports the exact missing path; and an existing output directory is never overwritten.

- [ ] **Step 7: Run the CLI tests**

Run: `uv run pytest -q tests/test_fixture_acceptance_cli.py tests/test_fixture_acceptance.py`

Expected: all tests PASS.

- [ ] **Step 8: Commit**

```powershell
git add ipos/fixture_acceptance.py ipos/cli.py pyproject.toml tests/test_fixture_acceptance_cli.py
git commit -m "feat: add unattended research portfolio fixture acceptance"
```

---

### Task 7: Make Fixture Acceptance the Next Runnable Orchestration Packet

**Files:**
- Create: `orchestration/work/RI-10.yaml`
- Modify: `orchestration/state.yaml`
- Modify: `PROJECT_STATE.md`

**Interfaces:**
- Consumes: The `ipos fixture-acceptance` command.
- Produces: A dependency-free, unattended work packet that does not claim live-source activation.

- [ ] **Step 1: Create RI-10 with no live-service dependencies**

Set:

```yaml
id: RI-10
title: Replay existing research and portfolio fixtures
status: ready_for_execution
dependencies: []
executor_instruction: >-
  Run the existing transcript, research-PDF, Smartbroker, ZERO, and macro fixtures through
  ipos fixture-acceptance. Do not deploy services, request credentials, modify source fixtures,
  or execute broker orders. Stop when the acceptance receipt reports PASS or a fixture-integrity
  failure occurs.
```

Allowed paths are limited to the implementation files in this plan, the new timestamped acceptance run, RI-10, state, and PROJECT_STATE.

- [ ] **Step 2: Update orchestration state without falsifying RI-01**

Keep RI-01 as `stopped_pending_operator_source_mandate`. Add RI-10 and set `active_packet: RI-10`, because offline fixture acceptance is independent of live source approval.

- [ ] **Step 3: Update PROJECT_STATE**

Record only that fixture acceptance is runnable and that Gmail, WEB.DE, Karakeep, and Activepieces live activation remain separate.

- [ ] **Step 4: Validate all YAML**

Run:

```powershell
uv run python -c "import pathlib,yaml; [yaml.safe_load(p.read_text(encoding='utf-8')) for p in pathlib.Path('orchestration').rglob('*.yaml')]; print('VALID YAML')"
```

Expected: `VALID YAML`.

- [ ] **Step 5: Commit**

```powershell
git add orchestration/work/RI-10.yaml orchestration/state.yaml PROJECT_STATE.md
git commit -m "docs: add unattended fixture acceptance packet"
```

---

### Task 8: Run the Full Acceptance Battery

**Files:**
- Create at runtime only: `implementation-runs/fixture-acceptance/YYYYMMDD-HHMMSS/result.json`
- Create at runtime only: `implementation-runs/fixture-acceptance/YYYYMMDD-HHMMSS/VERIFICATION_REPORT.md`

**Interfaces:**
- Consumes: All completed tasks.
- Produces: Final machine-readable and practitioner-readable acceptance evidence.

- [ ] **Step 1: Run the anti-facade battery**

Run: `uv run python 06_modular_pipeline_alignment/audit/verify_reality_battery.py`

Expected: `5 PASSED, 0 FAILED`.

- [ ] **Step 2: Run the focused research and portfolio tests**

```powershell
uv run pytest -q tests/test_evidence_claims.py tests/test_evidence_ingest.py tests/test_ttk_adapter.py tests/test_document_adapter.py tests/test_fixture_portfolio_replay.py tests/test_fixture_acceptance.py tests/test_fixture_acceptance_cli.py tests/test_pp_adapter.py tests/test_portfolio.py tests/test_portfolio_decision.py tests/test_action_matrix.py tests/test_order_staging.py
```

Expected: all tests PASS with zero skips for the real Smartbroker/ZERO fixtures on this machine.

- [ ] **Step 3: Run the complete repository test suite**

Run: `uv run pytest -q`

Expected: all tests PASS.

- [ ] **Step 4: Execute the unattended acceptance command**

Run: `uv run ipos fixture-acceptance`

Expected: exit code 0 and a new timestamped run directory.

- [ ] **Step 5: Validate the final receipt**

Require:

- five transcript fixtures passed integrity/validation;
- one research PDF passed hash, page-count, extraction, and exact grounding;
- 332 activities replayed;
- 24 Smartbroker positions reconciled with zero quantity discrepancies;
- eight ZERO positions loaded;
- 32 total holdings evaluated;
- WATCH and REVIEW inputs caused no portfolio mutation;
- one simulated operator-approved ACTION produced the expected 0.80 targeted-sector multiplier;
- non-investment control produced NO_IMPACT;
- duplicate ingestion produced no duplicate register item;
- staged tickets remained manual-only;
- no source fixture, live register, live warehouse, or prior export changed hash.

- [ ] **Step 6: Run repository hygiene checks**

```powershell
git diff --check
git status --short
```

Confirm no private broker source, credential, temporary register, or extracted PDF full text is staged.

- [ ] **Step 7: Commit only the accepted evidence summary if repository policy requires it**

Do not commit the private register or copied source data. Commit only `result.json` and `VERIFICATION_REPORT.md` when their content contains hashes, counts, paths, and outcomes rather than private transaction rows or copyrighted full text.

---

## Completion Criteria

The plan is complete only when one unattended command proves the full existing-fixture path and produces a PASS receipt. Live Gmail OAuth, WEB.DE credentials, Karakeep deployment, Activepieces deployment, and real broker execution are explicitly not required for this acceptance run and must remain separate future activation gates.
