# Workflow Plan 03: "Transcendents" Workshop Concept & Curriculum Generator

**Workflow ID:** WF-03  
**Target Domain:** Educational Masterclasses & Immersive Seminars  
**Target Repositories:** `acim-secular` -> `MasterOfArts/workshops/`  
**Cognitive Architecture:** Tier 2 Hermes CLI (`workshop-designer` profile)

---

## 1. Operational Overview
Translates dense, secularized non-dual ontology from `acim-secular` into a practical, modular 8-stage weekend workshop curriculum titled *"The Transcendents: Radical Non-Dual Inquiry & Creative Embodiment"*.

---

## 2. Step-by-Step Execution Procedure

1. **Curriculum Concept Extraction**:
   - Hermes accesses `/root/workspaces/acim-secular/` to extract core lessons on perception, projection, and release.
2. **Pedagogical Structuring**:
   - Adopts `workshop-designer` profile.
   - Formulates 8 distinct modules: 4 on Saturday (Foundation, Deconstruction), 4 on Sunday (Integration, Creative Expression).
   - Designs interactive partner exercises, somatic check-ins, and meditation prompts.
3. **Deliverable Production**:
   - Outputs complete facilitator guide and student syllabus into `MasterOfArts/workshops/transcendents_2026/`.

---

## 3. Specific Test Run & Verification Protocol

### Test Command: Generate Workshop Module Structure
```bash
wsl.exe -d Ubuntu -u root -e bash -c "
mkdir -p /root/workspaces/MasterOfArts/workshops/transcendents_2026
/usr/local/bin/hermes --profile workshop-designer --eval '
Create Module 1 (The Lens of Perception) and Module 2 (Undoing Projection) for the Transcendents Workshop. Include timing (90 min each), exercise instructions, and facilitator guidance. Save to /root/workspaces/MasterOfArts/workshops/transcendents_2026/modules_1_2.md.
'
"
```
*Expected Output*: File `modules_1_2.md` created with professional workshop layout, time blocks, and somatic inquiry steps.

---

## 4. Pass / Fail Criteria
* **PASS**: File created, contains exact timing breakdowns, somatic prompts, and pedagogical structure.
* **FAIL**: Fails to access `acim-secular`, generates superficial text, or writes to wrong directory.

---

## 5. Operator Interaction Points
* **PAUSE & PROMPT**: Operator reviews module pacing, ticket pricing tier suggestions, and venue requirements.
