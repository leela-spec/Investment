# Workflow Plan 04: MasterOfArts Multi-Variant Business Website Pipeline

**Workflow ID:** WF-04  
**Target Domain:** Digital Presence & Portfolio Staging  
**Target Repositories:** `MasterOfArts/WEbsite/`  
**Cognitive Architecture:** Python Web Engine (`build_all_websites.py`) + Nginx Edge Gateway

---

## 1. Operational Overview
Builds, tests, and stages three full design variations ("Zen Minimalist", "Vibrant", "Modern") of the Master of Arts personal brand portfolio, complete with an interactive switchboard and subpages for ACIM, Dance Fusion, Lika, Workshops, and Coaching.

---

## 2. Step-by-Step Execution Procedure

1. **Website Code Compilation**:
   - Executes `build_all_websites.py` in `C:\GitDev\MasterOfArts\WEbsite`.
2. **Design System Artifact Validation**:
   - Verifies `index.html` (switchboard) and variation folders (`variation-a-zen`, `variation-b-vibrant`, `variation-c-modern`).
3. **Nginx Edge Preview Staging**:
   - Mounts or copies website bundle to the local edge gateway (`http://127.0.0.1:8084/moa/`) for operator review.

---

## 3. Specific Test Run & Verification Protocol

### Test Command: Execute Website Build Script
```powershell
cd C:\GitDev\MasterOfArts\WEbsite
python build_all_websites.py
Test-Path index.html, variation-a-zen/index.html, variation-b-vibrant/index.html, variation-c-modern/index.html
```
*Expected Output*: Returns `True, True, True, True`. All variants successfully compiled.

---

## 4. Pass / Fail Criteria
* **PASS**: All 4 index pages generated, responsive Tailwind CSS scripts embedded, subpages linked correctly.
* **FAIL**: Python syntax error, missing template, or broken relative links.

---

## 5. Operator Interaction Points
* **PAUSE & PROMPT**: Operator selects preferred design variant ("Zen", "Vibrant", or "Modern") for production domain mapping.
