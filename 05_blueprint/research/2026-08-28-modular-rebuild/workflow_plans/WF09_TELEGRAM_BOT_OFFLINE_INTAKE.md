# Workflow Plan 09: Social Initiative Telegram Bot Intake & Offline Backlog Catch-Up Bridge

**Workflow ID:** WF-09  
**Target Domain:** Community Engagement & Mobile Expense Intake  
**Target Repositories:** `apexai-os-meta/ki-basis/`  
**Cognitive Architecture:** Hermes Telegram Bridge (`hermes_telegram_intake.py`) + Telegram Cloud API

---

## 1. Operational Overview
Enables community volunteers to post event ideas and upload receipt photos via Telegram. Solves the offline laptop problem by utilizing Telegram Cloud update offsets: messages sent while the laptop was sleeping are pulled in chronological sequence upon reconnection, staged in Paperless (`STAGED-FOR-REVIEW`), and filed as tasks in OpenProject.

---

## 2. Step-by-Step Execution Procedure

1. **Telegram Ingestion Trigger**:
   - Volunteer posts `/receipt [caption]` with photo, or `/task [description]`.
2. **Offline Catch-Up Processing**:
   - `hermes_telegram_intake.py` queries `getUpdates(offset=last_id)`.
   - Downloads pending media and captions.
3. **Paperless & OpenProject Staging**:
   - Uploads receipt image/PDF to Paperless-ngx.
   - Creates OpenProject task in Project 3 (Equinox 2026) with checklist for treasurer review.

---

## 3. Specific Test Run & Verification Protocol

### Test Command: Test Receipt Staging Simulation
```powershell
python C:\GitDevpexai-os-meta\ki-basis\scripts\hermes_telegram_intake.py --help
```
*Expected Output*: Displays intake options for staging receipts (`--receipt`), filing community tasks (`--task`), and managing OpenProject projects.

---

## 4. Pass / Fail Criteria
* **PASS**: CLI options validated; receipt uploaded with `STAGED-FOR-REVIEW`; OpenProject work package created with document backlink.
* **FAIL**: Direct autonomous mutation of Firefly ledger (violates Tiered Autonomy model).

---

## 5. Operator Interaction Points
* **PAUSE & PROMPT**: Requires Operator to supply Telegram Bot Token (`@BotFather`) and private Group ID if running live polling.
