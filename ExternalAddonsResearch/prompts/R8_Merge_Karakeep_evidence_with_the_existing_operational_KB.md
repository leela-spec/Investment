<system_instruction>
Design the evidence-to-operational-knowledge bridge for IPOS.

The core safety principle is:

EXTERNAL EVIDENCE IS NOT AUTOMATICALLY AN IPOS RULE.

Karakeep may preserve and organize evidence.
The existing IPOS Playbook/configuration controls operational behavior.
Your task is to design the bridge between those layers.
</system_instruction>

<input_layers>
Layer A — raw evidence:
articles
papers
videos/transcripts
emails
filings
official releases
data-source documentation

Layer B — candidate knowledge:
claims
mechanisms
indicator proposals
contradictions
rule proposals
source updates

Layer C — operational IPOS knowledge:
03_extract
04_playbook
configs
scoring
governors
contradiction rules

Layer C is authoritative for runtime.
</input_layers>

<objective>
Design a provenance-preserving lifecycle:

source
→ evidence object
→ extracted candidate claim
→ corroboration/contradiction
→ review
→ accepted/rejected/deferred
→ optional operational promotion
→ versioned IPOS change

Determine what should be deterministic and what may use AI.
</objective>

<research>
Investigate existing proven patterns/software for:

- provenance graphs
- evidence ledgers
- claim/evidence stores
- citation graphs
- research review queues
- data lineage
- content-addressed storage
- Git-based review
- knowledge promotion workflows
- Zotero/Karakeep IDs
- W3C PROV or similar standards where useful
- JSON-LD only if it materially helps
- simple relational alternatives

Prefer simpler proven schemas over ontology engineering.
</research>

<data_contracts>
Design:

1. research_event
2. evidence_source
3. candidate_claim
4. claim_evidence_link
5. review_decision
6. operational_promotion

Each needs:
- stable ID
- source system ID
- canonical URL where applicable
- retrieved_at
- published_at
- content hash/version if useful
- provenance
- status
- confidence where appropriate
- citations
- supersession/retraction handling
</data_contracts>

<state_machine>
Research and propose states such as:

INGESTED
PARSED
CANDIDATE
CORROBORATED
CONTRADICTED
REVIEW_REQUIRED
ACCEPTED_AS_RESEARCH
REJECTED
PROMOTED_TO_OPERATIONAL
SUPERSEDED

Do not assume these exact labels are optimal.
</state_machine>

<governance>
Explicitly define what happens when:

- two sources contradict;
- a source changes;
- an article is corrected;
- duplicate evidence arrives;
- an AI extracts a false claim;
- a research claim is later invalidated;
- an existing Playbook rule conflicts with new evidence;
- an operational numeric threshold changes.

Any operational scoring-behavior change must respect current IPOS versioning/golden-test governance.
</governance>

<retrieval>
Determine whether IPOS needs:

- deterministic metadata/tag retrieval
- full-text/BM25
- optional semantic retrieval
- no retrieval integration at all for weekly scoring

Do not introduce RAG merely because a research KB exists.
</retrieval>

<deliverables>
1. KNOWLEDGE_LAYER_BOUNDARIES.md
2. EVIDENCE_TO_RULE_LIFECYCLE.md
3. DATA_CONTRACTS.json
4. PROVENANCE_MODEL.md
5. GOVERNANCE.md
6. FAILURE_CASES.md
7. MINIMUM_BRIDGE_RECOMMENDATION.md
</deliverables>

<definition_of_done>
An operator must be able to point at any future IPOS rule and answer:

- Where did this rule come from?
- Which evidence supported it?
- Who/what promoted it?
- When did it become operational?
- What changed from the prior version?
</definition_of_done>
