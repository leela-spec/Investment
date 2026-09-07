# Workflow Plan 08: Equinox 2026 Pretix Ticketing Settlement & Non-Profit Tax Accounting

**Workflow ID:** WF-08  
**Target Domain:** Community Operations (Safer Space e.V. / Equinox 2026)  
**Target Host / Stack:** Windows Alpine Docker Desktop (100% Core Quarantined)  
**Cognitive Architecture:** Alpine KI-Basis Stack + `ki-basis/scripts/pretix_adapter.py`

---

## 1. Operational Overview
Settles Pretix ticketing intake for the Equinox Hamburg 2026 fundraiser. Splits gross revenue into platform fees, payment gateway costs, and net payouts; uploads official payout documentation into Paperless; logs German non-profit tax bookings (Zweckbetrieb) into Firefly III; and syncs door capacity to OpenProject.

---

## 2. Step-by-Step Execution Procedure

1. **Pretix Order Data Ingestion**:
   - Connects to Pretix API v1 via `pretix_adapter.py`.
2. **Fee Calculation & Deduction**:
   - Computes: Gross (€11,300), Pretix fee (€282.50), Stripe/Gateway (€183.60), Net Payout (€10,833.90).
3. **Multi-Service Booking**:
   - Ingests payout summary PDF to Paperless with tag `PRETIX`.
   - Commits double-entry transactions in Firefly III under Safer Space e.V. GLS bank account.
   - Updates OpenProject work package attendance figures.

---

## 3. Specific Test Run & Verification Protocol

### Test Command: Execute Full Fundraiser Verification Audit
```powershell
python C:\GitDevpexai-os-meta\ki-basis\scriptserify_fundraiser_stack.py
```
*Expected Output*:
`ALL AUDIT VERIFICATIONS PASSED WITH ZERO ERRORS!` (Pretix, Paperless, Firefly, and OpenProject verified).

---

## 4. Pass / Fail Criteria
* **PASS**: 100% audit verification passed. Data strictly confined to Windows Alpine Docker environment.
* **FAIL**: Any discrepancies in net payout calculations or port collisions with WSL2.

---

## 5. Operator Interaction Points
* **PAUSE & PROMPT**: Operator and club treasurer must verify the actual bank payout transfer against the generated settlement receipt.
