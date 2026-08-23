# Method Basis — IPOS Reuse Expansion Research Program

**Date:** 2026-08-23
**Purpose:** Record the external workflow evidence used to design the ChatGPT Work research program. This file is methodological evidence, not IPOS investment evidence.

## Primary guidance consulted

### OpenAI — ChatGPT Work
Source: https://openai.com/chatgpt-work/

Relevant guidance:
- Work is intended for longer, multi-step tasks across connected tools, files, and the web.
- It gathers context, proposes/plans an approach, takes actions, and allows the operator to review or redirect.
- Plan mode is explicitly designed so the approach can be reviewed before work begins.

Program implication:
- Use one lead Work run as the program controller.
- Start with a preflight/context pass and a visible execution plan before the research wave begins.
- Keep operator intervention for genuine decision/permission gates, not routine research choices.

### OpenAI Academy — ChatGPT Work Reimagine Guide
Source: https://academy.openai.com/public/clubs/champions-ecqup/resources/chatgpt-work-reimagine-guide-for-team-activators-2026-07-08

Relevant guidance:
- Choose/narrow a meaningful workflow.
- Map trusted inputs, current steps, handoffs, outputs, friction, and standards.
- Design and test the smallest useful version.
- Package the workflow for reuse and measure evidence before scaling.

Program implication:
- Preserve explicit input/output contracts per research track.
- Do not convert research directly into implementation.
- Require POCs only where the track explicitly asks for them and keep them disposable/non-production.

### OpenAI Help — Deep Research
Source: https://help.openai.com/en/articles/10500283-deep-research

Relevant guidance:
- Define the desired outcome and constraints.
- Choose sources deliberately, including connected apps and specific sites.
- Review the research plan.
- Produce documented results with citations/source links and inspect the sources before relying on conclusions.

Program implication:
- Primary-source-first source strategy.
- Every consequential external claim must be traceable to a cited source.
- Repo facts must be traced to current `main`, not conversation memory.

### OpenAI Academy — ChatGPT for Research
Source: https://openai.com/academy/research/

Relevant guidance:
- Start with a research outline containing sub-questions, source strategy, and evaluation criteria.
- Require citations for key claims and perform source-quality checks.
- Explicitly surface missing information, disputed areas, and limitations.

Program implication:
- Every track writes its plan before browsing deeply.
- Every track contains a `GAPS_AND_UNCERTAINTIES` section.
- Review evaluates source quality separately from conclusion quality.

### OpenAI — A practical guide to building agents
Source: https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/

Relevant guidance:
- Prefer incremental complexity; a single agent can remain the controller while specialized agents/tools are added as needed.
- Instructions should use existing procedures, decompose dense work into smaller actions, define clear outputs, and capture edge cases.
- Human intervention should be reserved for failure thresholds and high-risk/irreversible actions.
- Guardrails should be layered rather than relying on a single control.

Program implication:
- One lead controller owns sequencing and synthesis.
- Track prompts are authoritative routines rather than being paraphrased by the controller.
- Retry/re-review is bounded.
- Production writes, credential use, or high-risk installation remain human gates; normal source selection does not.

### Anthropic Engineering — How we built our multi-agent research system
Source: https://www.anthropic.com/engineering/multi-agent-research-system

Relevant guidance:
- Breadth-heavy research benefits from an orchestrator-worker architecture with independent specialized research branches.
- The orchestrator must give each worker a precise objective, output format, source/tool guidance, and task boundaries to avoid duplication and gaps.
- Parallelization is most useful for independent research directions; Anthropic reports 3–5 subagents as a useful pattern and large speedups from parallel search.
- Search should begin broad and progressively narrow based on evidence.
- Persist the plan/context in structured memory/artifacts for long runs.
- Citation processing/verification should occur after research rather than assuming citations are correct.

Program implication:
- Execute only genuinely independent IPOS tracks in parallel waves.
- Do not have multiple tracks research the same question unless intentional independent verification is required.
- Persist track status and outputs to the repository after each accepted track.
- Run a separate reviewer pass before a track is accepted.

### Anthropic Engineering — Demystifying evals for AI agents
Source: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents

Relevant guidance:
- Research-agent outputs should be evaluated using groundedness, coverage, and source-quality checks rather than requiring one exact reasoning path.
- Evals should judge outcomes and evidence quality.

Program implication:
- The reviewer grades: factual/source groundedness, citation accuracy, completeness, source quality, repo alignment, and efficiency.
- A track fails review if a consequential recommendation rests on weak/uncited evidence even if the prose is persuasive.

### Anthropic Engineering — Harness design for long-running application development
Source: https://www.anthropic.com/engineering/harness-design-long-running-apps

Relevant guidance:
- Decompose long-running work into tractable chunks.
- Use structured artifacts to hand off context between sessions/agents.
- Separate generation from evaluation.

Program implication:
- Research outputs, reviews, state, and synthesis are persisted as files.
- The program is restartable from repository state rather than chat memory.

## Derived program principles

1. **Repository-first preflight.** Current `main` is the project source. Conversation memory is non-authoritative.
2. **One controller, specialized tracks.** One Work agent owns the DAG; research tracks remain narrowly scoped.
3. **Parallelize independence, serialize dependencies.** Parallel work is used only where outputs do not depend on each other.
4. **Prompt files are contracts.** The controller executes the research prompt files; it does not rewrite their objectives from memory.
5. **Primary-source-first.** Official docs, repositories, licenses, APIs, regulatory/public bodies, and current release information are preferred for consequential claims.
6. **Evidence before recommendation.** Every consequential claim must be traceable; uncertainty is explicit.
7. **Researcher/reviewer separation.** Every track receives an independent review before being marked accepted.
8. **Bounded correction.** One targeted correction/re-review cycle is allowed automatically. Persistent failure is escalated.
9. **POCs are disposable.** Tests may install/run tools only where a research prompt explicitly asks for a POC, must not use production secrets/data, and must not silently modify IPOS production behavior.
10. **Structured handoffs.** State is persisted in machine-readable artifacts after every track so the program can resume without conversation history.
11. **Synthesis is downstream.** Final implementation planning starts only after all prerequisite research tracks are accepted.
12. **No implementation by enthusiasm.** Final synthesis must distinguish ADOPT NOW / TEST FURTHER / DEFER / REJECT.

## Reviewer rubric

Each completed track is graded 0–2 on each dimension:

- `repo_grounding`: uses current `main` and distinguishes stale/conflicting documents.
- `factual_grounding`: consequential claims are supported by evidence.
- `citation_accuracy`: cited sources actually support the claim made.
- `source_quality`: primary/authoritative sources are preferred where available.
- `coverage`: all required questions and deliverables in the authoritative prompt are addressed.
- `uncertainty`: gaps, disputed findings, and unavailable evidence are explicit.
- `target_alignment`: no drift into redesigning unrelated IPOS subsystems.
- `reuse_first`: existing systems are evaluated before custom implementation.
- `poc_integrity`: where required, the POC is reproducible, isolated, and honestly reports blockers/failures.
- `efficiency`: no obvious duplicate/redundant research or uncontrolled tool loops.

**Pass:** >= 17/20 AND no zero in `repo_grounding`, `factual_grounding`, `citation_accuracy`, or `coverage`.

A failed track receives one targeted correction pass against the failed rubric items. If it still fails, set status `HUMAN_GATE_REQUIRED` and continue only with tracks that do not depend on it.