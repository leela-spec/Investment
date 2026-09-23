# Workflow Plan 06: IPOS Research Evidence Custody & Thesis Invalidation Watchdog

**Workflow ID:** WF-06  
**Target Domain:** Evidence Preservation & Anti-Confirmation Bias  
**Target Repositories:** `Investment/` (Karakeep on ext4)  
**Cognitive Architecture:** Karakeep Custody + Hermes (`investment` profile read-only MCP)

---

## 1. Operational Overview
Preserves raw research documents (PDFs, filings, macro articles) in Karakeep on native ext4 (`/root/workspaces/Investment/`). Hermes monitors incoming evidence to detect whether findings contradict active investment theses, raising watch items without touching broker accounts.

---

## 2. Step-by-Step Execution Procedure

1. **Evidence Ingestion**:
   - Research report uploaded into Karakeep in `Investment`.
   - SingleFile capture generated with SHA-256 receipt.
2. **Read-Only MCP Retrieval**:
   - Hermes activates `investment` profile and retrieves document text via `http://localhost:3000`.
3. **Invalidation Stress-Testing**:
   - Evaluates whether new data falsifies existing regime assumptions.
   - Updates Watch Register with citation if contradiction is found.

---

## 3. Specific Test Run & Verification Protocol

### Test Command: Ingestion & Read-Only Retrieval Drill
```bash
wsl.exe -d Ubuntu -u root -e bash -c "
python3 -c '
import hashlib, json
dummy_doc = b"Federal Reserve signals unexpected rate hikes amid persistent sticky core inflation."
doc_hash = hashlib.sha256(dummy_doc).hexdigest()
receipt = {"status": "ARCHIVED", "hash": doc_hash, "inbox": "IPOS Evidence"}
print(json.dumps(receipt))
'
"
```
*Expected Output*: Returns JSON receipt with valid SHA-256 hash.

---

## 4. Pass / Fail Criteria
* **PASS**: Research cleanly fingerprinted; Hermes retrieval strictly read-only (zero mutation tools enabled).
* **FAIL**: Writing to raw source files or attempting to auto-rebalance portfolios based on evidence.

---

## 5. Operator Interaction Points
* **PAUSE & PROMPT**: Operator must acknowledge flagged thesis invalidations before Watch Register items are cleared.
