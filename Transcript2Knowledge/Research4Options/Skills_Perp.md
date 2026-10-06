You’re right — the previous answer drifted into products. Here’s the correction: a focused map of **AI skill sets** (capabilities/techniques) you need to build or assemble to go from investment statements → portfolio decisions.

I’ll structure this exactly along your four steps and keep it tool‑agnostic.

---

## 1) Skills to analyse transcripts and research

Core problem: turn unstructured text (10‑K/10‑Q, earnings calls, research notes) into structured, comparable signals.

### 1.1 NLP / LLM fundamentals

- **Text preprocessing & chunking**
    
    - Split long documents (10‑K, transcripts) into manageable chunks (e.g., ≤8k tokens) while preserving section boundaries.[[biblos.hec](https://biblos.hec.ca/biblio/memoires/seguin_benjamin_m2025.pdf)]
    - Handle speaker attribution and Q&A segmentation in transcripts.[[docs.fiscal](https://docs.fiscal.ai/docs/guides/mcp-skills)]
- **Transformer‑based models**
    
    - Use encoder models (BERT / FinBERT / DeBERTa) for classification and sentiment.[[biblos.hec](https://biblos.hec.ca/biblio/memoires/seguin_benjamin_m2025.pdf)][[rpc.cfainstitute](https://rpc.cfainstitute.org/research/foundation/2025/chapter-7-natural-language-processing)]
    - Use decoder/LLM models (GPT‑style) for summarisation, Q&A, and structured extraction.[[rpc.cfainstitute](https://rpc.cfainstitute.org/research/foundation/2025/chapter-7-natural-language-processing)][[rpc.cfainstitute](https://rpc.cfainstitute.org/sites/default/files/docs/support/rf_aiinassetmanagement_practitioner-briefs_07_naturallanguageprocessing_online.pdf)]

### 1.2 Domain‑specific NLP skills

- **Financial sentiment & tone analysis**
    
    - Apply **FinBERT** or similar finance‑pretrained models to score sentiment in earnings calls, press releases, and news.[[biblos.hec](https://biblos.hec.ca/biblio/memoires/seguin_benjamin_m2025.pdf)][[rpc.cfainstitute](https://rpc.cfainstitute.org/sites/default/files/docs/support/rf_aiinassetmanagement_practitioner-briefs_07_naturallanguageprocessing_online.pdf)][[pmc.ncbi.nlm.nih](https://pmc.ncbi.nlm.nih.gov/articles/PMC11033520/)]
    - Optionally combine with lexicon methods (e.g., Loughran–McDonald) for robustness.[[biblos.hec](https://biblos.hec.ca/biblio/memoires/seguin_benjamin_m2025.pdf)]
- **Topic & theme extraction**
    
    - Use topic modelling or embedding‑based clustering (e.g., SBERT/FinBERT embeddings + k‑means) to identify recurring themes: margin pressure, capex plans, demand outlook, risk factors.[[rpc.cfainstitute](https://rpc.cfainstitute.org/sites/default/files/docs/support/rf_aiinassetmanagement_practitioner-briefs_07_naturallanguageprocessing_online.pdf)]
- **Named entity recognition (NER) for finance**
    
    - Extract entities: company names, products, geographies, executives, competitors, KPIs, guidance figures.[[biblos.hec](https://biblos.hec.ca/biblio/memoires/seguin_benjamin_m2025.pdf)][[rpc.cfainstitute](https://rpc.cfainstitute.org/sites/default/files/docs/support/rf_aiinassetmanagement_practitioner-briefs_07_naturallanguageprocessing_online.pdf)]
- **Guidance & forward‑looking statement extraction**
    
    - Detect and parse forward‑looking language: “expect”, “anticipate”, “guidance”, “outlook”, and extract numeric ranges and time horizons.[[raw.githubusercontent](https://raw.githubusercontent.com/NeverSight/skills_feed/refs/heads/main/data/skills-md/octagonai/skills/earnings-financial-guidance/SKILL.md)]
- **Risk discussion analysis**
    
    - Apply hierarchical transformer models to risk sections (e.g., “Risk Factors” in 10‑K) to predict volatility or risk metrics.[[ceur-ws](https://ceur-ws.org/Vol-3910/aics2024_p31.pdf)]

### 1.3 Structured output skills

- **Schema‑driven extraction**
    
    - Define a JSON/Markdown schema for each company/period (e.g., revenue guidance, margin outlook, capex, key risks, tone score).
    - Use LLMs with strict output schemas or function‑calling to enforce structure.[[skills](https://skills.rest/skill/earnings-review-xbtlin)][[kimi](https://www.kimi.ai/resources/financial-analysis-skills-for-agents)]
- **Verification & source linking**
    
    - For each extracted claim/number, store the source passage (page/section/timestamp) to enable audit and later validation.[[docs.fiscal](https://docs.fiscal.ai/docs/guides/mcp-skills)][[skills](https://skills.rest/skill/earnings-review-xbtlin)]

**Resulting skill set label:**  
`financial-document-analyst` – transforms raw filings/transcripts into structured, source‑linked signals.

---

## 2) Skills to map signals into an existing market analysis

Core problem: connect company‑level signals to your higher‑level market view (sector theses, factor tilts, macro regime).

### 2.1 Knowledge representation

- **Market view schema**
    
    - Represent your market analysis as structured data:
        
        - Sector views (bull/base/bear, confidence, drivers).
        - Factor exposures (value, quality, momentum, size).
        - Macro regime assumptions (rates, growth, inflation, credit spreads).
- **Mapping layer**
    
    - Define rules or learned mappings from company signals → sector/factor/macroeconomic implications.
        
        - Example: “guidance cut + margin compression” → negative for sector demand, negative for quality factor.

### 2.2 Reasoning & aggregation skills

- **Signal aggregation**
    
    - Aggregate multiple company signals into sector‑level indicators (e.g., % of companies cutting guidance in semis).
- **Delta detection**
    
    - Compare new signals vs previous period to detect **changes in narrative**:
        
        - New risks mentioned?
        - Shift from “cautious” to “confident”?
        - Change in consensus around demand/costs?[[skills](https://skills.rest/skill/earnings-review-xbtlin)][[arxiv](https://arxiv.org/html/2607.11141v1)]
- **Thematic clustering**
    
    - Use embeddings to cluster companies by similar narrative changes (e.g., “AI capex boom”, “pricing power erosion”).[[rpc.cfainstitute](https://rpc.cfainstitute.org/sites/default/files/docs/support/rf_aiinassetmanagement_practitioner-briefs_07_naturallanguageprocessing_online.pdf)]

**Resulting skill set label:**  
`market-view-mapper` – ingests company signals and updates/annotates your existing market analysis with deltas and confidence scores.

---

## 3) Skills to create deltas to the existing market analysis

This is more about workflow design than new ML, but still requires specific AI capabilities.

### 3.1 Versioned narrative management

- **Diffing narratives**
    
    - Use LLMs to generate “diff” summaries between market view versions:
        
        - What changed in sector outlook?
        - Which drivers were added/removed?
        - How did confidence levels shift?[[arxiv](https://arxiv.org/html/2607.11141v1)]
- **Causal attribution**
    
    - Link each delta to specific underlying signals (e.g., “Semis sector view downgraded due to 6/10 companies cutting capex guidance in Q2 calls”).[[arxiv](https://arxiv.org/html/2607.11141v1)][[bloomberg](https://www.bloomberg.com/professional/insights/artificial-intelligence/how-ai-is-reshaping-the-foundation-of-front-office-investment-workflows/)]

### 3.2 Explainability & audit

- **Rationale generation**
    
    - For each delta, generate a concise, human‑readable rationale with references to source documents.[[arxiv](https://arxiv.org/html/2607.11141v1)][[arxiv](https://arxiv.org/html/2505.11065v2)]
- **Confidence calibration**
    
    - Attach confidence scores to deltas based on:
        
        - Number of supporting companies.
        - Strength of signal (e.g., large guidance cut vs vague comment).
        - Consistency across transcripts/filings.[[arxiv](https://arxiv.org/html/2505.11065v2)]

**Resulting skill set label:**  
`market-delta-engine` – produces versioned, source‑backed updates to your market analysis.

---

## 4) Skills to transform deltas into portfolio decisions

This is where you move from research to concrete positions, weights, and trades.

### 4.1 Signal → position mapping

- **Signal scoring**
    
    - Convert qualitative deltas into numeric scores (e.g., −2 to +2) per sector/factor/security.[[arxiv](https://arxiv.org/html/2607.11141v1)][[arxiv](https://arxiv.org/html/2505.11065v2)]
- **Rule‑based or model‑based mapping**
    
    - Define rules:
        
        - “If sector score ≥ +1 and risk OK → overweight by X%.”
        - “If company‑specific negative delta and high exposure → reduce/exit position.”
    - Or train ML models to map signal vectors to expected returns/risk adjustments.[[pmc.ncbi.nlm.nih](https://pmc.ncbi.nlm.nih.gov/articles/PMC11033520/)]

### 4.2 Portfolio construction & risk control

- **Optimisation skills**
    
    - Use mean‑variance, risk‑parity, or more advanced optimisers to translate target views into weights under constraints (long‑only, position limits, turnover, liquidity).[[pmc.ncbi.nlm.nih](https://pmc.ncbi.nlm.nih.gov/articles/PMC11033520/)][[ceur-ws](https://ceur-ws.org/Vol-3910/aics2024_p31.pdf)][[arxiv](https://arxiv.org/html/2607.11141v1)]
- **Risk analytics**
    
    - Compute and monitor:
        
        - Factor exposures (value, momentum, quality, etc.).
        - Concentration (sector, single‑name).
        - Drawdown and scenario analysis.[[arxiv](https://arxiv.org/html/2607.11141v1)][[arxiv](https://arxiv.org/html/2505.11065v2)]
- **Execution constraints**
    
    - Incorporate transaction costs, cash constraints, and position limits before finalising trades.[[arxiv](https://arxiv.org/html/2607.11141v1)][[arxiv](https://arxiv.org/html/2505.11065v2)]

### 4.3 Multi‑agent orchestration (optional but powerful)

Research prototypes show a clean pattern:

- **Analyst agents**: Fundamental, Technical, Macro, Policy, etc., each producing structured signals (bull/bear/neutral + rationale).[[arxiv](https://arxiv.org/html/2505.11065v2)]
- **Portfolio manager agent**: Aggregates signals, applies risk constraints, outputs target allocations and trade list.[[arxiv](https://arxiv.org/html/2607.11141v1)][[arxiv](https://arxiv.org/html/2505.11065v2)]

Key skills here:

- **Agent design**: define roles, inputs/outputs, and handoffs.
- **Shared memory**: maintain portfolio state, past decisions, and rationales for learning.[[arxiv](https://arxiv.org/html/2505.11065v2)]
- **Constraint enforcement**: ensure proposals satisfy risk/operational limits before execution.[[arxiv](https://arxiv.org/html/2607.11141v1)]

**Resulting skill set label:**  
`portfolio-constructor` – turns scored views/deltas into target weights and trade proposals under explicit constraints.

---

## 5) Concrete skill inventory you can use

If you’re building or hiring, think in terms of these AI skill modules:

1. **financial-document-analyst**
    
    - Transcript/filing parsing, FinBERT sentiment, guidance extraction, structured JSON output with source links.[[biblos.hec](https://biblos.hec.ca/biblio/memoires/seguin_benjamin_m2025.pdf)][[docs.fiscal](https://docs.fiscal.ai/docs/guides/mcp-skills)][[ceur-ws](https://ceur-ws.org/Vol-3910/aics2024_p31.pdf)][[skills](https://skills.rest/skill/earnings-review-xbtlin)][[kimi](https://www.kimi.ai/resources/financial-analysis-skills-for-agents)]
2. **market-view-mapper**
    
    - Mapping company signals to sector/factor/macroeconomic views; aggregation and thematic clustering.[[rpc.cfainstitute](https://rpc.cfainstitute.org/sites/default/files/docs/support/rf_aiinassetmanagement_practitioner-briefs_07_naturallanguageprocessing_online.pdf)][[arxiv](https://arxiv.org/html/2607.11141v1)][[bloomberg](https://www.bloomberg.com/professional/insights/artificial-intelligence/how-ai-is-reshaping-the-foundation-of-front-office-investment-workflows/)]
3. **market-delta-engine**
    
    - Versioned diffs of market narratives, causal attribution, confidence scoring, rationale generation.[[arxiv](https://arxiv.org/html/2607.11141v1)][[arxiv](https://arxiv.org/html/2505.11065v2)]
4. **portfolio-constructor**
    
    - Signal scoring, optimisation, risk analytics, constraint handling, trade proposal generation.[[pmc.ncbi.nlm.nih](https://pmc.ncbi.nlm.nih.gov/articles/PMC11033520/)][[ceur-ws](https://ceur-ws.org/Vol-3910/aics2024_p31.pdf)][[arxiv](https://arxiv.org/html/2607.11141v1)][[arxiv](https://arxiv.org/html/2505.11065v2)]
5. **orchestration layer**
    
    - Multi‑agent workflow, shared memory, logging, and evaluation (track how often deltas → correct moves).[[arxiv](https://arxiv.org/html/2607.11141v1)][[arxiv](https://arxiv.org/html/2505.11065v2)]

If you’d like, I can next:

- sketch a minimal architecture (e.g., Python + open‑source models + local files) that implements these skill sets, or
- list concrete open‑source models/libraries and example prompts for each skill.