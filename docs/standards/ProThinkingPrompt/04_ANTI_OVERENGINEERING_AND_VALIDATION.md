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
