<system_instruction>
Perform a head-to-head integration evaluation of Karakeep and Zotero for IPOS.

Do not conduct a generic product review.

The output must decide:
KARAKEEP_ONLY
ZOTERO_ONLY
BOTH_WITH_CLEAR_ROLE_BOUNDARIES
NEITHER
</system_instruction>

<target_workloads>
Test/evaluate these exact IPOS workloads:

1. YouTube research
2. financial web articles
3. PDFs/research reports
4. academic papers
5. central-bank papers
6. corporate filings
7. newsletter/email research
8. highlighted quotations
9. personal notes
10. source provenance
11. citation/reference management
12. machine retrieval by an agent/script
13. offline/archive recovery
14. automated intake
</target_workloads>

<research>
For each product verify current:

- license
- self-host/local characteristics
- APIs
- CLI
- MCP/skill integrations
- import/export
- attachment storage
- web snapshots
- PDF annotation
- notes/highlights
- metadata
- DOI/citation support
- duplicate handling
- RSS
- webhooks
- automation
- search
- full text
- collections/lists/tags
- backup/restore
- interoperability
</research>

<interop_test>
Determine whether BOTH can coexist without duplicate canonical truth.

If both:
define exactly which owns:

SOURCE RECORD
WEB ARCHIVE
PDF
BIBLIOGRAPHIC METADATA
HIGHLIGHTS
NOTES
TAGS
RESEARCH STATUS
CITATION DATA
FULL TEXT
IPOS SOURCE ID

Investigate existing synchronizers/connectors before proposing custom code.
</interop_test>

<poc>
If feasible, create a disposable test corpus containing:

- 2 web articles
- 2 PDFs, one with DOI
- 1 YouTube-related transcript artifact
- 1 personal note
- 1 duplicate resource

Attempt the same workflows in both systems.

Record:
setup time
manual actions
machine actions
data retained
data lost
export quality
searchability
API accessibility
failure points
</poc>

<mcda>
Weights:
IPOS workload fit 20
provenance 15
web evidence 10
academic/PDF evidence 10
automation/API 10
export/portability 10
determinism 10
local/free 5
maturity 5
operator friction 5
</mcda>

<deliverables>
1. KARAKEEP_VS_ZOTERO.md
2. WORKLOAD_TEST_RESULTS.md
3. ROLE_BOUNDARY_IF_BOTH.md
4. MCDA.json
5. FINAL_DECISION.json
</deliverables>

<rule>
"BOTH" is only acceptable if each system has a clearly different responsibility.
Two databases holding overlapping canonical copies without ownership rules is a rejection.
</rule>
