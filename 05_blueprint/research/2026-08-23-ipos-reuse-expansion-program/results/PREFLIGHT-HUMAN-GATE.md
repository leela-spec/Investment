# Preflight Human Gate — Missing Authoritative Track Prompts

**Status:** `HUMAN_GATE_REQUIRED`  
**Pinned main:** `79bbcda3fe211785084fc9fb9025675954786c14`  
**Opened:** 2026-08-23T15:26:58.033Z

## Finding

The complete recursive tree of live `main` was inspected and was not truncated. The research-program directory contains exactly:

- `AUTONOMOUS-PROGRAM-LAUNCHER.md` — `705d7bb4f4aad240f3451d2c5794e3c8d146e254`
- `METHOD-BASIS.md` — `146725254888cf9182228493e45c08e346dece0a`
- `START-CHATGPT-WORK.md` — `8ae7717047642ad059a075453755997f17071235`

No authoritative prompt file for R1, R2, R3, R4, R5, R6, R7, R8, or R9 exists anywhere in the pinned repository tree. Repository code searches for the distinctive objectives (Karakeep/IPOS, Activepieces ingestion, Ghostfolio POC, Zotero, and thin-glue implementation) return only the launcher or general project prose, not track contracts.

## Gate basis

Launcher §2.2 states that if any R1–R8 prompt is missing or ambiguous, the controller must not improvise it and must ask the operator. Because all R1–R9 contracts are missing, no research track can be launched and no valid `PROGRAM-PLAN.md` can be completed.

## Required operator action

Commit the authoritative R1–R9 prompt files to `main`, then provide the resulting commit SHA. If the files already exist under unexpected paths, provide those exact paths instead. After that, the controller can re-run prompt discovery, update the pin/re-grounding record, build the program plan, and continue autonomously.
