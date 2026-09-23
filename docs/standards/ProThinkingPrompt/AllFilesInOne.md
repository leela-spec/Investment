## `00_README.md`

```
# Pro Thinking Prompt Design System

## Purpose

This package defines a reusable method for creating high-autonomy,
research-backed prompts for GPT-5.6 Pro or comparable advanced reasoning models.

It is intended for difficult and expensive tasks where the prompt must:

- keep the model focused on one concrete final product;
- provide enough authority and source context to prevent drift;
- require ingestion, research, synthesis, creation, and validation;
- preserve the model’s freedom to determine its internal method;
- avoid instruction overload and procedural micromanagement;
- produce one clearly defined deliverable package;
- return one ZIP rather than duplicating every file in the browser response.

## Central principle

> Give the model a precise destination, trustworthy source boundaries,
> required evidence, a concrete output contract, and freedom over the route.

The target should appear near the beginning and be restated at the end as the
final success condition.

## Package contents

1. `01_PRO_THINKING_PROMPT_DESIGN_STANDARD.md`
   - principles and prompt architecture

2. `02_REUSABLE_MASTER_TEMPLATE.md`
   - fillable prompt template

3. `03_INGESTION_RESEARCH_SYNTHESIS_WORKFLOW.md`
   - source ingestion, research, and synthesis design

4. `04_ANTI_OVERENGINEERING_AND_VALIDATION.md`
   - restraint rules and validation scorecard

5. `05_APEX_PROMPT_CASE_STUDY.md`
   - analysis of the reference APEX prompt

6. `06_ORIGINAL_APEX_PRO_PROMPT.md`
   - original reference prompt

7. `package-manifest.yaml`
   - package index
```

---

## `01_PRO_THINKING_PROMPT_DESIGN_STANDARD.md`

````
# Pro Thinking Prompt Design Standard

## 1. Definition

A Pro Thinking prompt is a high-autonomy task specification for a capable
reasoning model.

It is not a script for the model’s thought process.

Its purpose is to define:

- the exact product to create;
- why the product matters;
- where authoritative information lives;
- what current research is required;
- which boundaries genuinely matter;
- what artifacts must be delivered;
- how the completed work will be validated;
- how the result must be returned.

---

## 2. Primary design principle

> Specify the destination more precisely than the route.

A strong Pro prompt is strict about the result and permissive about the model’s
working method.

### Be strict about

- the exact target;
- source authority;
- scope boundaries;
- required evidence;
- deliverables;
- safety and mutation boundaries;
- validation;
- delivery format;
- success criteria.

### Give freedom over

- internal sequencing;
- research depth;
- grouping of sources;
- working notes;
- internal batching;
- the number of material decisions;
- detailed artifact structure;
- reconciliation method;
- revision cycles.

---

## 3. Target-first architecture

The exact target should appear at both ends of the prompt.

### Opening target

State the task directly:

> Research, synthesize, design, and create `<FINAL PRODUCT>` in one continuous
> run.

Immediately explain:

- what the product is;
- who will use it;
- which problem it solves;
- what should not be substituted for it.

### Closing target

End with:

> The run is successful when `<FINAL PRODUCT>` satisfies `<QUALITY TESTS>` and
> is delivered as `<DELIVERY FORMAT>`.

This prevents the model from returning only research, planning, or an
architecture proposal.

---

## 4. Recommended prompt architecture

Use only sections that materially improve execution.

### A. Role

Define the relevant expertise and responsibility in one short paragraph.

Good:

> You are the research, information-design, and template-architecture lead for
> this task.

Avoid stacking theatrical roles that do not change the work.

---

### B. Objective

Name:

1. the exact final product;
2. its intended user;
3. its practical purpose;
4. its required components;
5. what is not the primary result.

Example:

> Create the complete production-ready template family. The primary result is
> the usable template package, not another architecture proposal.

---

### C. Authority model

Use a short hierarchy.

Example:

1. Live contracts define domain meaning.
2. Accepted design files define presentation intent.
3. Verified user stories define operator value.
4. Research reports provide evidence and design leads.
5. Current web research may improve presentation but cannot override domain
   authority.

Do not treat every source as equally authoritative.

---

### D. Named source set

Name the highest-signal files and folders directly.

This prevents:

- unfocused scanning;
- stale sources dominating;
- token waste;
- project-resource drift.

Allow expansion only when:

- a named source points to another file;
- an owning contract is required;
- a material ambiguity remains;
- the requested product cannot otherwise be completed reliably.

---

### E. Ingestion and understanding

Require the model to understand the system before creating the final result.

State the understanding required, not a mechanical reading procedure.

Example:

> Before settling the design, reconstruct the lifecycle, ownership boundaries,
> user needs, accepted decisions, and known failure modes.

Do not require a long preliminary report unless it is itself a deliverable.

---

### F. Current research

Require research only where current external evidence can improve the result.

Define:

- the questions research must answer;
- preferred source quality;
- how research should influence the product;
- that a generic literature review is not the objective.

Good:

> Research how progressive disclosure, interruption recovery, operator decision
> interfaces, uncertainty presentation, and Markdown scanability should affect
> the final template system.

Weak:

> Research template best practices.

---

### G. Findings and synthesis

Require a substantial synthesis artifact before final creation.

Useful components:

- evidence-backed findings;
- source reconciliation;
- design principles;
- options considered;
- decision matrix;
- selected approaches;
- trade-offs;
- assumptions;
- implications for the final files.

Ask for decisions and evidence, not private chain-of-thought.

---

### H. Creation task

List the artifacts that must exist.

For example:

- findings document;
- design decision matrix;
- final templates;
- example fragments;
- package overview;
- validation report;
- manifest.

Allow the model to improve file names or package organization when this
materially improves coherence.

---

### I. Design freedom

Give explicit freedom over:

- internal research process;
- batching;
- section structure;
- file organization;
- placeholder conventions;
- presentation choices;
- example placement;
- decision-matrix depth;
- reconciliation method.

Preserve only the fundamentals that would cause real damage if changed.

---

### J. Essential boundaries

Keep boundaries compact and material.

Typical examples:

- do not invent domain meaning;
- do not override canonical contracts;
- do not silently mutate durable state;
- do not confuse evidence with interpretation;
- do not treat a recommendation as authorization;
- do not write to external systems without approval;
- do not duplicate information unnecessarily.

State each rule once.

---

### K. Validation

Require a final system-level review.

Check:

- target completeness;
- source fidelity;
- internal consistency;
- naming consistency;
- relationship correctness;
- non-duplication;
- usability;
- scanability;
- example realism;
- appropriate complexity;
- package completeness;
- delivery compliance.

Allow the model to revise the result before packaging it.

---

### L. Delivery

For artifact-heavy browser tasks, prefer:

```yaml
delivery:
  browser_summary: concise
  downloadable_artifacts:
    count: 1
    format: zip
  duplicate_individual_downloads: false
  paste_all_files_into_chat: false
  repository_writes: false
````

The ZIP should contain the detailed work.

The browser response should contain only:

1. what was created;
2. the most important conclusion;
3. a consequential caveat, when needed;
4. one ZIP link.

---

## 5. Ingestion before synthesis, synthesis before creation

The recommended flow is:

```
Target definition
→ source ingestion
→ authority reconciliation
→ current research
→ findings synthesis
→ material design decisions
→ artifact creation
→ cross-artifact validation
→ revision
→ package delivery
```

This is an output architecture, not a mandatory private reasoning script.

The prompt should require these outcomes while allowing the model to determine  
its internal method.

---

## 6. The autonomy equation

```
Prompt quality
=
target precision
+ source quality
+ output clarity
+ validation strength
- redundant instruction
- procedural micromanagement
- irrelevant context
```

Freedom is useful only when the target and authority are clear.

---

## 7. Minimum sufficient Pro prompt

A Pro prompt is complete when it defines:

1. Target
2. Relevant context
3. Source authority
4. Research need
5. Required deliverables
6. Hard boundaries
7. Validation criteria
8. Delivery format

Every additional section must justify its token cost.

---

## 8. When detail is justified

A long prompt is appropriate when the task has:

- many source authorities;
- complex artifact relationships;
- high drift risk;
- important lifecycle distinctions;
- expensive rerun cost;
- substantial research needs;
- a large deliverable package.

Length itself is not the failure.

The failure is low-value instruction density.

A detailed prompt remains lean when every section changes the model’s decisions,  
prevents a known failure, or defines a required product.

---

## 9. Continue through uncertainty

For costly Pro runs, prefer:

- use the best-supported interpretation;
- label consequential assumptions;
- distinguish verified facts from inferences;
- preserve relevant uncertainty;
- complete the most useful coherent package possible.

Do not create blocker-heavy stop rules for ordinary ambiguity.

Use hard stops only when:

- an action would be unsafe;
- a destructive mutation lacks authorization;
- the target cannot be identified;
- proceeding would require fabricating essential domain meaning.

---

## 10. Final axiom

> A great Pro Thinking prompt does not tell the model how to be intelligent.  
> It makes the intended result, evidence base, boundaries, and success standard  
> impossible to misunderstand.

````

---

## `02_REUSABLE_MASTER_TEMPLATE.md`

```markdown
# Reusable GPT-5.6 Pro Research and Creation Prompt

Replace all angle-bracket placeholders.

Delete sections that do not materially help the task.

---

# <PROJECT OR PRODUCT> — GPT-5.6 Pro Research and Creation Prompt

## Role

You are the <RELEVANT EXPERT ROLE> for <PROJECT OR DOMAIN>.

Your task is to research, synthesize, design, and create
**<EXACT FINAL PRODUCT>** in one continuous run.

Use your own judgment and internal working method. Do not ask the operator to
approve intermediate choices. Continue through uncertainty using the
best-supported interpretation, and record consequential assumptions in the
findings.

---

## Objective

Create **<EXACT FINAL PRODUCT>** for <INTENDED USER OR USE>.

The completed package must include:

- <DELIVERABLE 1>;
- <DELIVERABLE 2>;
- <DELIVERABLE 3>;
- <RESEARCH OR FINDINGS DOCUMENT>;
- <DECISION OR SYNTHESIS DOCUMENT>;
- <EXAMPLE OR TEST ARTIFACT>;
- <VALIDATION ARTIFACT>;
- <PACKAGE MANIFEST>.

The primary result is **<EXACT FINAL PRODUCT>**, not merely research,
recommendations, a plan, or another architecture proposal.

---

## Source authority

Use this authority order:

1. <PRIMARY CANONICAL AUTHORITY>
2. <ACCEPTED DESIGN OR POLICY AUTHORITY>
3. <VERIFIED USER STORIES OR DECISIONS>
4. <NAMED RESEARCH REPORTS AND EXAMPLES>
5. Current external research

External research may improve <PRESENTATION, METHOD, OR IMPLEMENTATION>, but it
must not override <DOMAIN AUTHORITY OR ACCEPTED DECISIONS>.

---

## Named sources

Begin with these sources:

```text
<SOURCE OR PATH 1>
<SOURCE OR PATH 2>
<SOURCE OR PATH 3>
<SOURCE OR PATH 4>
````

Use additional sources only when:

- a named source points to them;
- an owning contract is needed;
- a material ambiguity remains;
- the final product cannot otherwise be completed reliably.

Avoid broad, unfocused source scanning.

---

## Ingest and understand before creating

Before settling the final design:

- reconstruct <SYSTEM, LIFECYCLE, OR DOMAIN MODEL>;
- identify source and ownership boundaries;
- identify accepted decisions;
- identify the intended user’s practical needs;
- identify known failure modes;
- distinguish <IMPORTANT CONCEPT A> from <IMPORTANT CONCEPT B>;
- identify what should be shared and what must remain separate.

Use this understanding to improve the final product. Do not turn the ingestion  
phase into an unnecessary standalone report.

---

## Current research

Conduct fresh research on:

- <RESEARCH QUESTION 1>;
- <RESEARCH QUESTION 2>;
- <RESEARCH QUESTION 3>;
- <RESEARCH QUESTION 4>;
- <RESEARCH QUESTION 5>.

Prefer <PRIMARY OR AUTHORITATIVE SOURCE TYPES>.

Translate the research into concrete implications for  
**<EXACT FINAL PRODUCT>**.

Do not produce a generic literature review disconnected from the requested  
result.

---

## Findings and synthesis

Create a substantial findings document that reconciles:

- canonical sources;
- accepted internal decisions;
- user needs;
- existing reports;
- current research;
- known failure patterns.

Create an evidence-backed decision matrix covering every material design  
decision.

Do not impose an arbitrary row limit.

For each material decision, include:

|Field|Meaning|
|---|---|
|Decision|The choice being made|
|Problem|Why the choice matters|
|Options|Serious alternatives considered|
|Evidence|Internal and external support|
|Selected approach|The chosen design|
|Reason|Why it was chosen|
|Trade-off|What is gained and lost|
|Applied to|Where the decision affects the product|

Expose evidence, alternatives, decisions, and trade-offs.

Do not expose private chain-of-thought.

---

## Creation task

Create:

1. <FILE OR ARTIFACT 1>
2. <FILE OR ARTIFACT 2>
3. <FILE OR ARTIFACT 3>
4. <FILE OR ARTIFACT 4>
5. <EXAMPLE OR TEST ARTIFACT>
6. <VALIDATION ARTIFACT>
7. <PACKAGE MANIFEST>

You may improve the internal folder structure or file names when doing so  
materially improves usability and coherence.

---

## Design freedom

You may determine:

- your internal research method;
- internal batching;
- detailed artifact structure;
- heading hierarchy;
- presentation patterns;
- placeholder conventions;
- example placement;
- package organization;
- the number of material findings and decisions;
- how to reconcile consistency with artifact-specific needs;
- how often earlier decisions should be revisited.

Preserve only these fundamentals:

1. <HARD DOMAIN REQUIREMENT 1>
2. <HARD DOMAIN REQUIREMENT 2>
3. <HARD DOMAIN REQUIREMENT 3>
4. Do not invent domain meaning.
5. Do not duplicate information unnecessarily.
6. Do not overengineer the product.

---

## Examples and realism

Use <NAMED EXAMPLE SOURCE> as realistic sample content.

Treat it as a stress test, not as architectural authority.

Create practical example fragments that demonstrate difficult or ambiguous  
parts of the final artifacts.

Keep fictional example content visibly separate from:

- required schema;
- canonical rules;
- current project truth;
- operator-approved state.

---

## Missing or conflicting information

Do not abort the run for ordinary ambiguity or incomplete context.

Instead:

- use the best-supported interpretation;
- label consequential assumptions;
- distinguish verified facts from inferred choices;
- record material unresolved tensions;
- preserve uncertainty where relevant;
- complete the most useful coherent package possible.

---

## Validation

After creation, review the complete package for:

- source fidelity;
- target completeness;
- internal consistency;
- user usefulness;
- non-duplication;
- correct ownership and lifecycle boundaries;
- accessibility and scanability;
- realistic usability;
- appropriate complexity;
- complete links and manifest entries;
- delivery compliance.

Revise the package before final delivery when validation identifies a  
correctable issue.

---

## Delivery

Return the result in the browser conversation as:

1. a concise completion summary;
2. the most important design conclusion;
3. any consequential unresolved assumption;
4. **one downloadable ZIP file** containing the complete package.

Do not:

- return the ZIP plus duplicate standalone files;
- paste all deliverable contents into the browser response;
- create a branch or pull request;
- write to repositories or external systems unless explicitly authorized.

---

## Final success condition

The run is successful when **<EXACT FINAL PRODUCT>** is complete,  
evidence-backed, internally coherent, validated against <SUCCESS TESTS>,  
practical for <INTENDED USER>, and delivered as **one ZIP file**.

````

---

## `03_INGESTION_RESEARCH_SYNTHESIS_WORKFLOW.md`

```markdown
# Ingestion, Research, and Synthesis Workflow

## Purpose

This workflow ensures that the model understands the task and evidence before
creating the final product.

It should be expressed as required outcomes, not as a rigid private reasoning
script.

---

## 1. Ingestion

The model should identify:

- the exact final target;
- intended users;
- authoritative sources;
- accepted decisions;
- source conflicts;
- system or lifecycle structure;
- ownership boundaries;
- known failure modes;
- representative examples;
- existing partial work.

Recommended prompt wording:

> Before settling the final design, reconstruct the system, source authority,
> user needs, ownership boundaries, accepted decisions, and known failure modes.

Avoid prescribing an exact file-by-file reading ceremony unless ordering itself
is required for correctness.

---

## 2. Source triage

Use a compact classification:

```yaml
source_classes:
  canonical:
    purpose: defines domain truth

  accepted_design:
    purpose: defines approved interpretation or presentation

  user_verified:
    purpose: defines desired value and operator decisions

  research_guidance:
    purpose: provides patterns, findings, and source leads

  examples:
    purpose: tests usability and realism

  current_external_research:
    purpose: updates external best practice
````

### Named-source-first rule

Start with explicitly named, high-signal sources.

Expand only when:

- a named source references another authority;
- an owning contract is required;
- sources conflict materially;
- required information remains missing;
- validation requires another file.

This avoids unrestricted project-resource scanning.

---

## 3. System reconstruction

Before creating the final product, reconstruct:

- inputs;
- outputs;
- lifecycle;
- ownership;
- user decisions;
- state transitions;
- handoffs;
- failure points;
- areas where information must not be duplicated.

The reconstruction is a working model, not necessarily a large deliverable.

---

## 4. External research

Research must answer concrete design questions.

Weak instruction:

> Research current best practices.

Strong instruction:

> Research how progressive disclosure, uncertainty presentation, interruption  
> recovery, human review, accessible Markdown, and operator decision interfaces  
> should affect the final product.

Research should result in:

- findings;
- implications;
- options;
- decisions;
- trade-offs;
- applied design rules.

---

## 5. Synthesis

Synthesis combines internal authority with external evidence.

Recommended structure:

|Element|Purpose|
|---|---|
|Finding|What the evidence indicates|
|Internal relevance|Why it matters to this project|
|Options|Serious alternatives|
|Decision|Selected approach|
|Reason|Why it best fits|
|Trade-off|What is lost or constrained|
|Application|Which files or artifacts use it|

Do not cap the number of material decisions arbitrarily.

The complexity of the task should determine the depth.

---

## 6. Creation

Creation begins after enough understanding exists to prevent structural drift.

The prompt should make clear:

- research is not the final product;
- findings support the final design;
- examples demonstrate usage;
- validation may require revision;
- the complete package must stand alone.

---

## 7. Validation and revision

Validate the package across:

```
validation_dimensions:
  target_completion:
    question: Do all requested deliverables exist?

  authority_fidelity:
    question: Was canonical meaning preserved?

  internal_coherence:
    question: Do files use consistent names, terms, and relationships?

  usability:
    question: Can the intended user act without reconstructing hidden context?

  non_duplication:
    question: Is information owned once and referenced elsewhere?

  realism:
    question: Do examples expose practical weaknesses?

  restraint:
    question: Does every major section improve comprehension or execution?

  delivery:
    question: Does one ZIP contain the complete package?
```

Correct problems before packaging the final result.

---

## 8. Final browser delivery

The browser response should remain small:

- what was created;
- one key conclusion;
- one material caveat when needed;
- one ZIP link.

All detailed work belongs inside the ZIP.

````

---

## `04_ANTI_OVERENGINEERING_AND_VALIDATION.md`

```markdown
# Anti-Overengineering and Validation Guide

## 1. Main failure mode

The largest failure in advanced prompt design is often not missing guidance.

It is burying the target under excessive guidance.

Common symptoms:

- repeated instructions;
- excessive internal process rules;
- arbitrary limits on findings or decisions;
- blocker logic for ordinary uncertainty;
- duplicated output requirements;
- too many examples;
- entire project-resource scans;
- ZIP plus duplicated individual files;
- research that becomes the product.

---

## 2. Instruction value test

For every instruction, ask:

1. Does it materially change the final product?
2. Does it prevent a known, likely, costly failure?
3. Does it define authority, safety, or delivery?
4. Would a capable reasoning model infer it correctly without being told?

Delete the instruction when:

- the first three answers are no; and
- the fourth answer is yes.

---

## 3. Freedom test

Do not dictate:

- how many internal reasoning passes to perform;
- how many sources to read;
- how many material decisions to record;
- the exact order of every analytical action;
- the exact heading structure of every file;
- how long the model should think;
- chain-of-thought disclosure;
- several alternative answers merely because Pro mode is being used.

Specify these only when they are genuine product requirements.

---

## 4. Constraint test

Keep a constraint when violating it would:

- change domain meaning;
- cause unsafe or unauthorized action;
- make the product unusable;
- cause known project drift;
- violate delivery requirements;
- make validation impossible;
- silently mutate accepted state.

Combine related constraints into one section.

State each once.

---

## 5. Target visibility test

The exact final target should appear in:

- the opening;
- the objective;
- the creation task;
- the closing success condition.

Avoid targets such as:

- “improve the system”;
- “analyze the project”;
- “research templates”;
- “provide recommendations.”

Replace them with a concrete product.

---

## 6. Output contract test

A complete output contract identifies:

- final artifact classes;
- research and findings documents;
- decision or synthesis documents;
- examples or tests;
- validation output;
- manifest;
- package structure;
- browser delivery behavior.

Preferred pattern:

```yaml
delivery:
  browser_summary: concise
  downloadable_artifacts:
    count: 1
    format: zip
  duplicate_standalone_files: false
  paste_full_contents_into_chat: false
  repository_writes: false
````

---

## 7. Pro Thinking Prompt Scorecard

Score each dimension from 0 to 2.

|Dimension|0|1|2|
|---|---|---|---|
|Target precision|Vague|Partly defined|Exact product and user|
|Authority|Missing|Sources listed|Ranked authority model|
|Source scope|Uncontrolled|Named sources|Named-first expansion rule|
|Research|Generic|Topics listed|Questions tied to decisions|
|Synthesis|Missing|Summary requested|Findings, options, decisions, trade-offs|
|Deliverables|Vague|Partial list|Complete package contract|
|Autonomy|Micromanaged|Mixed|Outcome control with method freedom|
|Boundaries|Missing or repeated|Usable|Compact and material|
|Validation|Generic|Checklist|System review and revision|
|Delivery|Unclear|Multiple files|One ZIP and concise response|
|Target restatement|Missing|Appears once|Beginning and end|
|Restraint|Missing|Implied|Explicit anti-overengineering rule|

### Interpretation

- **21–24:** Ready for an expensive Pro run
- **17–20:** Strong, but simplify or clarify
- **12–16:** Significant drift risk
- **0–11:** Rewrite before execution

---

## 8. Red flags

Revise prompts containing:

- “Think step by step.”
- “Show all your reasoning.”
- “Follow exactly these 47 internal steps.”
- repeated prohibition sections;
- arbitrary decision-count limits;
- mandatory exhaustive source scans;
- hard blockers for ordinary missing information;
- repository writes when browser artifacts are sufficient;
- ZIP plus all files individually;
- generic research unrelated to the final product;
- a target that appears only implicitly.

---

## 9. Final preflight

```
preflight:
  exact_target_named_at_start: true
  primary_result_distinguished_from_research: true
  named_sources_prioritized: true
  authority_hierarchy_defined: true
  current_research_questions_defined: true
  ingestion_required: true
  synthesis_required: true
  model_controls_internal_method: true
  material_constraints_stated_once: true
  ordinary_uncertainty_does_not_abort_run: true
  complete_deliverable_package_defined: true
  final_validation_required: true
  one_zip_only: true
  exact_target_repeated_at_end: true
```

````

---

## `05_APEX_PROMPT_CASE_STUDY.md`

```markdown
# APEX Pro Prompt Case Study

## Reference task

The reference prompt asks GPT-5.6 Pro to research, design, and create the complete
APEX operator template family for J1–J12 plus a conditional Skip Marker.

The required package includes:

- research findings;
- an evidence-backed decision matrix;
- complete blank templates;
- practical example fragments;
- a family overview;
- a package manifest;
- cross-template validation.

---

## Why it works

### 1. The target is unmistakable

The opening names the production-ready template family as the target.

The objective enumerates every artifact.

The model cannot easily substitute a research report for the product.

---

### 2. Research is subordinate to creation

The prompt requires substantial research and synthesis, but explicitly states:

> The primary result is the ready-to-use template package—not another
> architecture proposal.

This protects the run from becoming research-only.

---

### 3. Authority is ranked

The prompt distinguishes:

1. live contracts;
2. accepted design files;
3. user stories;
4. research reports and examples;
5. current web research.

This prevents external UX advice from rewriting accepted domain meaning.

---

### 4. Sources are named

The prompt names the relevant repository files and project sources directly.

The model is allowed to expand only when a material question requires it.

This reduces drift and token waste.

---

### 5. Ingestion precedes creation

The model must understand:

- the operating loop;
- artifact ownership;
- planning versus execution;
- evidence versus interpretation;
- candidate versus approved state;
- durable writing versus accepted truth;
- recommendation versus authorization.

These distinctions determine the product’s correctness.

---

### 6. Research questions affect design

The prompt focuses research on:

- human-AI interfaces;
- progressive disclosure;
- operator dashboards;
- interruption recovery;
- uncertainty and provenance;
- accessible Markdown;
- cognitive load;
- reusable template systems.

This gives research a direct design function.

---

### 7. Findings are a real deliverable

The decision matrix is not artificially limited.

The model can document every material decision while ignoring trivial formatting
choices.

This preserves the value of the expensive Pro run.

---

### 8. The model receives design freedom

The prompt allows the model to decide:

- research process;
- batching;
- template structure;
- heading hierarchy;
- placeholders;
- presentation forms;
- example placement;
- package structure;
- matrix depth.

The prompt protects domain fundamentals without trying to perform the design
itself.

---

### 9. Missing information does not waste the run

The model is instructed to:

- continue with the best-supported interpretation;
- label consequential assumptions;
- distinguish verified and inferred choices;
- preserve uncertainty;
- complete the package.

This prevents an expensive run from ending in a blocker-only response.

---

### 10. Validation happens across the family

The prompt validates:

- names;
- lifecycle;
- ownership;
- handoffs;
- duplication;
- state distinctions;
- artifact-specific depth;
- example correctness;
- package usability;
- unnecessary complexity.

The model may revise before delivery.

---

### 11. Delivery is economical

The result is:

- a concise browser summary;
- one ZIP file.

It does not duplicate every file in the browser response.

---

## Reusable pattern

```text
Exact final target
→ ranked authority
→ named source set
→ required system understanding
→ focused current research
→ substantial findings and decisions
→ final artifact creation
→ cross-artifact validation
→ one-ZIP delivery
→ target restated as success condition
````

---

## Final case-study conclusion

The APEX prompt is detailed about:

- the product;
- the evidence;
- domain boundaries;
- deliverables;
- validation.

It is intentionally not detailed about the model’s private reasoning route.

That is the core pattern future Pro Thinking prompts should preserve.

````

---

## `package-manifest.yaml`

```yaml
package:
  name: Pro Thinking Prompt Design System
  version: "1.0"
  purpose: >
    Create high-autonomy, research-backed, anti-overengineered prompts for
    GPT-5.6 Pro and comparable advanced reasoning modes.

  delivery:
    artifact: single_zip
    duplicate_standalone_files: false

files:
  - path: 00_README.md
    role: Package orientation

  - path: 01_PRO_THINKING_PROMPT_DESIGN_STANDARD.md
    role: Principles and design standard

  - path: 02_REUSABLE_MASTER_TEMPLATE.md
    role: Fillable Pro Thinking prompt template

  - path: 03_INGESTION_RESEARCH_SYNTHESIS_WORKFLOW.md
    role: Pre-creation ingestion, research, and synthesis design

  - path: 04_ANTI_OVERENGINEERING_AND_VALIDATION.md
    role: Restraint rules and quality validation

  - path: 05_APEX_PROMPT_CASE_STUDY.md
    role: Analysis of the successful reference prompt

  - path: 06_ORIGINAL_APEX_PRO_PROMPT.md
    role: Original attached APEX reference prompt

  - path: package-manifest.yaml
    role: Machine-readable package index

core_principles:
  - Name the exact target at the beginning.
  - Distinguish the final product from research and analysis.
  - Rank source authority.
  - Name high-signal sources directly.
  - Require ingestion before synthesis.
  - Require synthesis before final creation.
  - Give the model freedom over its internal method.
  - State each material constraint once.
  - Continue through ordinary uncertainty.
  - Validate the complete package before delivery.
  - Return one ZIP rather than duplicate files.
  - Restate the target at the end as the success condition.
````