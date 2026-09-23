# IPOS Research-to-Portfolio Gap Analysis — NON-BINDING RESEARCH EVIDENCE

<!-- Retrievability Markers: IPOS research-to-portfolio gap analysis non-binding research evidence modular rebuild ipos-modular-rebuild-2026-08-28 M08 M09 M11 C11 M13 C13 Riskfolio Wealthfolio Karakeep Portfolio Performance WhisperX yt-dlp PySceneDetect DuckDB broker reconciliation cross-OS WSL -->

Date: 2026-09-23

Status:

**NON-BINDING / RESEARCH EVIDENCE / REQUIRES RE-GROUNDING**

This folder preserves a ChatGPT research run so its evidence, external-product research,
reasoning, identified risks, and proposed corrections remain retrievable.

It is NOT:

- current IPOS SSOT;
- an approved architecture;
- an accepted decision matrix;
- an implementation authority;
- proof of current repository state;
- authorization to overwrite newer work;
- authorization to apply the included patch.

## Important provenance limitation

The original research run inspected `main` first and incorrectly concluded that several
important modular-rebuild files were absent.

Afterwards, the branch:

`ipos-modular-rebuild-2026-08-28`

was inspected and confirmed to contain important later work, including the revised
decision matrix, candidate architecture, M08/M09 plans, M11 normalizer, M13 optimizer,
and their tests.

Therefore any conclusion in this package that depends on those files being absent,
unimplemented, or unreconciled must be re-evaluated against the actual branch history
and current implementation.

## Correct use

Future agents MAY use this folder for:

- external product research;
- identified integration risks;
- candidate failure modes;
- validation ideas;
- proposed numerical invariants;
- cross-OS architecture considerations;
- broker / Wealthfolio / Riskfolio / Karakeep / media-tool research;
- historical reasoning;
- comparison against later implementation.

Future agents MUST:

1. inspect all relevant branches and commits first;
2. prefer live implementation and current accepted repository authority;
3. compare this package against the modular-rebuild branch and any later landed work;
4. explicitly classify each retained conclusion as confirmed, corrected, superseded,
   unresolved, or still useful;
5. never promote this package wholesale into current authority.

## Patch warning

`05_SURGICAL_PATCHES.diff` is preserved only as historical research output.

DO NOT APPLY IT until its target files have been re-grounded against the actual current
implementation.

If equivalent or stronger corrections already exist in later work, preserve the newer
implementation instead.

## Intended follow-up

A new research run should:

- inspect `main`;
- inspect `ipos-modular-rebuild-2026-08-28`;
- inspect relevant commit history and merged descendants;
- determine where each module actually landed;
- compare live code/tests against this research;
- retain useful findings;
- discard or correct stale conclusions;
- produce an updated decision-ready package.
