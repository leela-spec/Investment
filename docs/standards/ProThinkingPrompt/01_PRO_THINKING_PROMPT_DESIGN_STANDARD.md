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
