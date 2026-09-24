# Target-first execution reporting design

## Purpose

Keep target-product execution focused on operator value and decisions. Detailed
receipts remain available without dominating conversational reports or driving
work toward proxy completion.

## Scope

Apply this rule only to the active target-product execution handover. Do not
change the project-wide `AGENTS.md` contract.

## Reporting contract

Routine progress and final reports lead with:

1. target;
2. intended value;
3. current verdict;
4. remaining material gap;
5. one next value-producing action.

Each item should normally be one concise line. Hashes, row-level calculations,
schemas, command output, and other audit detail belong in the relevant
`implementation-runs/` evidence files. Surface them conversationally only when
the user requests them or when a material failure cannot be understood without
them.

## Investigation stop rule

Before continuing an investigation, ask whether the result can change the
current product decision or next action. If not, stop and record any necessary
detail in evidence rather than expanding the conversation.

Tests, receipts, files, and schemas remain evidence rather than completion.
Product-native behavior and operator value remain the acceptance criteria.

## E02 application

E02 remains fail-closed because Wealthfolio's computed holdings and cash do not
reconcile. The only active action is the bounded EUR custom-asset probe for NDA
and PSYC. Do not pursue broader Wealthfolio internals, additional abstractions,
or E03 until that probe determines the product decision.

