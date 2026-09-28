# Handover — Guided WEB.DE Research Email Integration

**Purpose:** Give a new chat enough context to guide the operator, step by step, through integrating
approved WEB.DE research emails into the IPOS research-intake pipeline.

**Working directory:** `C:\GitDev\Investment`

**Current boundary:** This handover does not authorize RI-04 execution. The canonical active packet
remains RI-01 until its source mandate is accepted. RI-02 and RI-03 must also pass before RI-04 can
configure a live WEB.DE connection.

---

## 1. What IPOS Is Building

IPOS is a local-first investment research and portfolio-review system. Its research-intake path is
intended to turn information from explicitly approved sources into evidence-linked outcomes:

```text
approved source
    -> bounded discovery
    -> original-source custody
    -> evidence extraction
    -> NO_IMPACT / WATCH / REVIEW / HIGH_PRIORITY_REVIEW
    -> operator review
```

The system does not turn an email recommendation into a trade. All numeric calculations are
performed by deterministic code, LLMs may only classify or narrate, and broker execution remains
manual.

WEB.DE is one source channel within this larger process. The intended path is:

```text
WEB.DE folder "IPOS Research"
    -> Activepieces IMAP trigger
    -> sender/domain allowlist and duplicate check
    -> normalized research event
    -> Karakeep evidence custody
    -> IPOS evidence classification and operator review
```

The point is not to scan an entire mailbox. It is to deliver approved research exactly once while
preserving the original source and a clear audit trail.

---

## 2. Canonical Repository Frontier

At the start of the next chat, read only:

1. `PROJECT_STATE.md`
2. `orchestration/state.yaml`
3. The active packet named by `active_packet` in `orchestration/state.yaml`
4. Only the authority sections explicitly cited by that packet

Do not start RI-04 merely because this handover exists. Do not bulk-read historical handovers,
plans, or `.agents` transcripts.

As of 2026-09-28:

- The reality battery passes: **5 PASSED, 0 FAILED**.
- RI-01 is stopped pending one bounded operator source list.
- The five existing media fixtures have been recovered and identity-verified.
- `IPOS Research` is the proposed bounded WEB.DE folder.
- `IPOS/Research` is the proposed bounded Gmail label.
- RI-02, RI-03, and RI-04 remain blocked.
- Karakeep and Activepieces must not be deployed as part of RI-01.

The dependency chain is:

```text
RI-01  Approve source mandate and representative samples
  |
  +--> RI-02  Prove Karakeep evidence custody
  |
  +--> RI-03  Prove Activepieces routing
          |
          +--> RI-04  Configure and prove bounded WEB.DE email intake
```

---

## 3. How the Next Chat Should Work With the Operator

Guide the operator through one concrete action at a time. Explain what the action accomplishes,
wait for its result, verify it, and only then give the next action.

Use plain language. Do not ask for vague “identifiers” or “stable references.” Ask for the exact
piece of information needed, such as:

- “Which sender email addresses or domains should be allowed?”
- “What is the local path to the relevant `.eml` sample you exported?”
- “Did you create the folder named `IPOS Research` in WEB.DE?”

Never ask the operator to paste or store a password, OAuth token, API key, session cookie, recovery
code, or mailbox credential. When a later packet reaches connection setup, credentials must be
entered by the operator directly in the provider or Activepieces connection UI.

If the operator provides a local sample path, inspect only that named path. Do not search unrelated
directories or scan a mailbox.

---

## 4. Stage One — Complete the WEB.DE Part of RI-01

The immediate goal is to define a bounded source mandate, not to connect the mailbox.

### Step 1 — Confirm the bounded folder

Ask the operator to create or confirm a WEB.DE folder named exactly:

```text
IPOS Research
```

Only messages placed in this folder may be considered by the future automation. Whole-mailbox
semantic scanning is prohibited.

### Step 2 — Build the sender allowlist

Ask the operator which specific research senders should be accepted. Record exact email addresses
or domains and a short reason for each inclusion.

For every approved sender or domain, RI-01 ultimately needs:

- owner: the person responsible for approving or removing it;
- source class: `web_de_email`;
- exact sender address or domain;
- reason for inclusion;
- relevant investment topics;
- priority;
- lookback period;
- detection method: bounded folder plus sender/domain allowlist.

Do not infer approval merely because an address appears in a sample message.

### Step 3 — Recover representative samples

Ask the operator to export messages from WEB.DE as `.eml` files and provide local paths, not message
contents pasted into chat.

The minimum RI-01 WEB.DE pair is:

1. one relevant research email from an approved sender;
2. one irrelevant email that should be rejected.

To prepare for later RI-04 acceptance efficiently, prefer a small bounded fixture set that also
covers:

- a relevant email with an attachment;
- a relevant email containing a video link;
- an analyst BUY, SELL, REDUCE, ADD, HOLD, or WATCH recommendation;
- a duplicate or forwarded copy of a relevant message.

One message may cover several cases. Do not manufacture messages when authentic, non-sensitive
examples are available. Do not commit mailbox exports to Git unless an active packet explicitly
authorizes their destination and handling.

### Step 4 — Check sample suitability

For each named `.eml` path, verify only what RI-01 requires:

- the file exists and is readable;
- sender, subject, timestamp, and message identity are present;
- its expected classification is stated by the operator;
- no password, token, cookie, or connection secret is present;
- the sample is relevant to the approved source mandate.

Do not silently rewrite the original evidence. If personal information requires special handling,
stop and agree on a safe storage location before proceeding.

### Step 5 — Finish the complete RI-01 mandate

WEB.DE alone is not the whole RI-01 source mandate. The active packet also requires the approved
Gmail senders/domains, YouTube channels, public sites/feeds, and representative PDF/article samples.
Keep RI-01 active until its complete acceptance criteria pass and `configs/research_sources.yaml`
can be written without invented sources or unresolved placeholders.

---

## 5. Stages Two and Three — Release RI-04 Safely

After RI-01 is accepted, the orchestration frontier must complete:

- **RI-02:** deploy and prove Karakeep custody;
- **RI-03:** deploy and prove Activepieces routing.

Do not treat a service being reachable as acceptance. Each packet must record its own evidence and
update `orchestration/state.yaml` before the next dependency is released.

Only after RI-01, RI-02, and RI-03 are accepted may the chat open and execute
`orchestration/work/RI-04.yaml`.

---

## 6. Stage Four — What RI-04 Will Configure

When RI-04 becomes active, the next chat should follow its packet exactly. The expected WEB.DE flow
is narrow:

1. Run the required reality battery.
2. Confirm all three dependencies are accepted.
3. Perform one bounded health check of Activepieces and Karakeep.
4. Snapshot or export the empty target flow before changing it.
5. Have the operator enter the WEB.DE connection secret directly in the Activepieces UI.
6. Configure IMAP using current WEB.DE provider documentation.
7. Restrict discovery to the `IPOS Research` folder.
8. Apply the approved sender/domain allowlist from `configs/research_sources.yaml`.
9. Normalize an accepted message to the shared event contract.
10. Deduplicate using provider plus stable source message ID.
11. Preserve the original evidence in Karakeep or create an explicit custody-failure record.
12. Emit safe-retry SYSTEM records for material authentication, routing, or custody failures.
13. Exercise the approved relevant, attachment, video, action, duplicate, and irrelevant fixtures.
14. Export only non-secret flow definitions and acceptance evidence.
15. Stop as soon as RI-04 acceptance passes.

The normalized event must include:

```text
event_id
source
source_message_id
sender
subject
received_at
body_ref
attachment_refs
urls
classification_hint
ingested_at
```

The idempotency key is:

```text
provider + stable source_message_id
```

A duplicate delivery must not create a second event or Action/Watch item.

---

## 7. Safety and Stop Conditions

Stop and explain the issue plainly if:

- the approved folder, sender allowlist, or fixture messages are missing;
- RI-01, RI-02, or RI-03 is incomplete;
- a provider requires unrestricted mailbox access;
- the requested action would expose a password, token, cookie, or mailbox credential;
- Activepieces or Karakeep is unavailable after the packet's single bounded health check;
- completion would require product-code changes, a new framework, or unrelated refactoring;
- an email recommendation would be converted into an automatic broker action.

Never bypass mailbox security, paywalls, authentication, or provider controls. Never send or stage a
broker order from email content.

---

## 8. Definition of Success

The WEB.DE integration is complete only when RI-04 proves that:

- only the `IPOS Research` folder is consumed;
- only approved senders/domains pass;
- accepted messages emit the normalized event exactly once;
- irrelevant messages are rejected;
- duplicates create no second event or action;
- original evidence receives a stable Karakeep ID or an explicit custody failure;
- material failures create safe-retry SYSTEM records;
- no secret appears in Git, logs, chat, or evidence artifacts;
- no broker action is sent or executed.

---

## 9. Suggested Opening Prompt for the Next Chat

```text
You are guiding me through the WEB.DE research-email integration for IPOS in
C:\GitDev\Investment.

Read HANDOVER_WEB_DE_EMAIL_INTEGRATION.md first. Then follow the canonical frontier in
PROJECT_STATE.md and orchestration/state.yaml. Work on only the active packet; do not start RI-04
until RI-01, RI-02, and RI-03 are accepted.

Guide me through one concrete operator action at a time. Begin with the current RI-01 blocker.
Use "IPOS Research" as the bounded WEB.DE folder. Ask only for information that cannot be recovered
from the repository. Never ask me to paste passwords, OAuth tokens, API keys, cookies, or mailbox
credentials. Do not scan my whole mailbox, deploy blocked services, alter portfolio arithmetic, or
automate broker execution.
```

