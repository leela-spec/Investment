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
