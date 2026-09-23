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
