# Workflow Plan 07: Private Coaching Client Lifecycle, Automated Invoicing & Payment Watchdog

**Workflow ID:** WF-07  
**Target Domain:** Private Entrepreneurship & Coaching Bookkeeping  
**Target Repositories:** `MasterOfArts/Coaching/` + WSL2 KI-Basis (`Paperless`, `Firefly`, `OpenProject`)  
**Cognitive Architecture:** Tier 1 CLI Agent (Offer) + Tier 3B KI-Basis (Bookkeeping Engine)

---

## 1. Operational Overview
End-to-end lifecycle for private coaching clients: drafting custom agreements in `MasterOfArts/Coaching/`, generating compliant § 14 UStG PDF invoices into Paperless, matching incoming bank wires in Firefly III, and triggering automated reminder drafts for overdue invoices.

---

## 2. Step-by-Step Execution Procedure

1. **Agreement Formulation**:
   - Custom client package generated in `MasterOfArts/Coaching/Leela Coaching/<ClientName>/`.
2. **Invoice Generation & Archiving**:
   - Python script produces compliant PDF invoice (`INV-2026-XXXX`).
   - Uploads to Paperless-ngx (`http://127.0.0.1:8010`) with tag `COACHING-INVOICE-OUTGOING`.
3. **Ledger Reconciliation in Firefly III**:
   - Firefly III records expected account receivable.
   - Ingested bank transaction matching invoice ID automatically marks invoice settled.
4. **Overdue Payment Reminder**:
   - Daily cron flags unpaid invoices past 14-day terms; drafts reminder for operator approval.

---

## 3. Specific Test Run & Verification Protocol

### Test Command: Query Paperless & Firefly Coaching Accounts
```powershell
python -c "
import urllib.request, json
try:
    req = urllib.request.Request('http://127.0.0.1:8010/api/', headers={'Authorization': 'Token c0b591378103b3328b1bb3269fcf581191864a06'})
    res = urllib.request.urlopen(req)
    print('Paperless API: ONLINE (' + str(res.status) + ')')
except Exception as e:
    print('Paperless API Error:', e)
"
```
*Expected Output*: `Paperless API: ONLINE (200)`.

---

## 4. Pass / Fail Criteria
* **PASS**: Paperless and Firefly accessible; invoices formatted to § 14 UStG standards; zero co-mingling with community accounts.
* **FAIL**: Inability to post to Paperless or failure to match invoice tags.

---

## 5. Operator Interaction Points
* **PAUSE & PROMPT**: Operator must approve any automated overdue payment reminder draft before it is dispatched to the client.
