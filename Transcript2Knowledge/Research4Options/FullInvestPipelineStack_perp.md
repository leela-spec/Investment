Based on current open‑source practice and real deployments, there is now a clear “consensus stack” for individuals and small teams who want the full pipeline – from ingestion → bookkeeping/ledger → analysis → portfolio decisions – with minimal cost and maximal reuse.[[rasmusnes](https://rasmusnes.com/posts/stock-advisor-stack/)][[github](https://github.com/migbenav/Financial-Data-Pipeline-and-Analytics)][[duckdblab](https://duckdblab.org/en/post/duckdb-financial-dashboard-product/)][[github](https://github.com/AI4Finance-Foundation/Awesome_AI4Finance)]

Below is a ranked set of **existing, downloadable, open‑source combinations** that people actually use end‑to‑end, plus where they shine and where they’re weak.

---

## 1) “Zero‑Cost Individual Investor Stack” – best value per token/dollar

**Reference implementation:**

- Rasmus Nes, _“The Zero Cost Stack”_ (Go + GitHub Actions + DuckDB/MotherDuck + Dagster + Streamlit)[[rasmusnes](https://rasmusnes.com/posts/stock-advisor-stack/)]
- Similar pattern: _“Financial Data Pipeline and Analytics”_ (Python + GitHub Actions + Supabase + Streamlit)[[github](https://github.com/migbenav/Financial-Data-Pipeline-and-Analytics)]
- DuckDB Lab guide: _“Build an Automated Financial Dashboard Data Product with DuckDB”_[[duckdblab](https://duckdblab.org/en/post/duckdb-financial-dashboard-product/)]

**Typical architecture**

1. **Ingestion (ETL)**
    
    - Scheduled GitHub Actions (free tier) pull data from:
        
        - Market/fundamentals: Tiingo, Alpha Vantage, Yahoo Finance, etc.[[rasmusnes](https://rasmusnes.com/posts/stock-advisor-stack/)][[github](https://github.com/migbenav/Financial-Data-Pipeline-and-Analytics)]
    - Language: Go or Python scripts with retries, idempotent upserts.[[rasmusnes](https://rasmusnes.com/posts/stock-advisor-stack/)]
2. **Storage**
    
    - **DuckDB** (local) + **MotherDuck** (hosted, free tier) or Supabase Postgres.[[rasmusnes](https://rasmusnes.com/posts/stock-advisor-stack/)][[github](https://github.com/migbenav/Financial-Data-Pipeline-and-Analytics)][[duckdblab](https://duckdblab.org/en/post/duckdb-financial-dashboard-product/)]
    - Bronze/Silver/Gold style layers: raw → cleaned → analytics‑ready.[[rasmusnes](https://rasmusnes.com/posts/stock-advisor-stack/)][[github](https://github.com/Abdelrhman-Hussien-Bi/FinTech-Data-Engineering)]
3. **Orchestration & transformations**
    
    - **Dagster** (open source) triggered from GitHub Actions to:
        
        - Clean/transform data in DuckDB.
        - Train simple models (e.g., CatBoost) and store predictions/SHAP values.[[rasmusnes](https://rasmusnes.com/posts/stock-advisor-stack/)]
    - Alternatives: plain Python scripts + cron/GitHub Actions for simpler setups.[[github](https://github.com/migbenav/Financial-Data-Pipeline-and-Analytics)][[duckdblab](https://duckdblab.org/en/post/duckdb-financial-dashboard-product/)]
4. **Analysis & “bookkeeping”**
    
    - Tables for:
        
        - Prices, fundamentals, corporate actions.
        - Trades, positions, P&L, cash flows (your “bookkeeping” ledger).[[rasmusnes](https://rasmusnes.com/posts/stock-advisor-stack/)][[github](https://github.com/migbenav/Financial-Data-Pipeline-and-Analytics)]
    - SQL + Python for risk/performance metrics: volatility, max drawdown, Sharpe, etc.[[github](https://github.com/migbenav/Financial-Data-Pipeline-and-Analytics)]
5. **Dashboard & decision support**
    
    - **Streamlit** hosted on Streamlit Community Cloud (free) connected to DuckDB/Supabase.[[rasmusnes](https://rasmusnes.com/posts/stock-advisor-stack/)][[github](https://github.com/migbenav/Financial-Data-Pipeline-and-Analytics)][[duckdblab](https://duckdblab.org/en/post/duckdb-financial-dashboard-product/)]
    - Tabs for:
        
        - Market/stock views.
        - Risk & performance.
        - Portfolio overview and suggested rebalances.[[github](https://github.com/migbenav/Financial-Data-Pipeline-and-Analytics)]
6. **Portfolio decisions**
    
    - Often rule‑based or simple optimisation:
        
        - Threshold rebalancing, risk parity, or mean‑variance via **PyPortfolioOpt / Riskfolio‑Lib / skfolio**.[[github](https://github.com/wilsonfreitas/awesome-quant?ref=woz.lt)][[arxiv](https://arxiv.org/html/2605.19337v1)]
    - Some stacks add an LLM layer on top (see section 2).

**Why this ranks #1 for “value per cost”**

- **$0–$25/month** in practice; many run fully on free tiers.[[rasmusnes](https://rasmusnes.com/posts/stock-advisor-stack/)][[duckdblab](https://duckdblab.org/en/post/duckdb-financial-dashboard-product/)]
- Uses **standard, well‑documented tools** with large communities (DuckDB, GitHub Actions, Streamlit, Dagster).[[rasmusnes](https://rasmusnes.com/posts/stock-advisor-stack/)][[github](https://github.com/migbenav/Financial-Data-Pipeline-and-Analytics)][[duckdblab](https://duckdblab.org/en/post/duckdb-financial-dashboard-product/)]
- Covers **all four steps** you care about:
    
    1. Ingestion of market/fundamental data.
    2. Bookkeeping‑style storage of trades/positions.
    3. Analysis (risk, performance, signals).
    4. Portfolio decisions via rules/optimisers, optionally augmented by LLMs.[[rasmusnes](https://rasmusnes.com/posts/stock-advisor-stack/)][[github](https://github.com/migbenav/Financial-Data-Pipeline-and-Analytics)][[arxiv](https://arxiv.org/html/2605.19337v1)]

**Where to start (concrete repos)**

- **Stock‑advisor stack** (Zero Cost Stack):  
    [https://github.com/rasmusnes/stock-advisor](https://github.com/rasmusnes/stock-advisor) (blog explains each layer).[[rasmusnes](https://rasmusnes.com/posts/stock-advisor-stack/)]
- **Financial‑Data‑Pipeline‑and‑Analytics**:  
    [https://github.com/migbenav/Financial-Data-Pipeline-and-Analytics](https://github.com/migbenav/Financial-Data-Pipeline-and-Analytics)[[github](https://github.com/migbenav/Financial-Data-Pipeline-and-Analytics)]
- **DuckDB financial dashboard guide**:  
    [https://duckdblab.org/en/post/duckdb-financial-dashboard-product/](https://duckdblab.org/en/post/duckdb-financial-dashboard-product/)[[duckdblab](https://duckdblab.org/en/post/duckdb-financial-dashboard-product/)]

If your priority is **“best combination that many people agree on, with minimal cost”**, this pattern is currently the closest thing to a community standard for individuals.[[rasmusnes](https://rasmusnes.com/posts/stock-advisor-stack/)][[github](https://github.com/migbenav/Financial-Data-Pipeline-and-Analytics)][[duckdblab](https://duckdblab.org/en/post/duckdb-financial-dashboard-product/)]

---

## 2) “LLM Agent Stack” – best for AI‑driven research → portfolio decisions

These stacks add **LLM multi‑agent systems** on top of a data pipeline similar to (1). They focus on turning transcripts/research into signals and then into trades.

### 2.1 TradingAgents + standard data/infra

**Core:**

- **TradingAgents** (LangGraph multi‑agent framework): fundamental, sentiment, technical analysts; bull/bear debate; trader + risk team.[[github](https://github.com/AI4Finance-Foundation/Awesome_AI4Finance)][[github](https://github.com/NitcanKen/Trading-Agents)]
- Often combined with:
    
    - Data: OpenBB, yfinance, Tiingo, etc.
    - Backtesting: Backtrader, Zipline‑reloaded, vectorbt, or custom.[[github](https://github.com/wilsonfreitas/awesome-quant?ref=woz.lt)][[arxiv](https://arxiv.org/html/2605.19337v1)]
    - Portfolio optimisation: PyPortfolioOpt / Riskfolio‑Lib / skfolio.[[github](https://github.com/wilsonfreitas/awesome-quant?ref=woz.lt)]

**Pipeline pattern**

1. Ingest prices + fundamentals + news/transcripts (via APIs or local files).
2. LLM agents:
    
    - Parse earnings calls, filings, news.
    - Produce structured signals (bull/bear/neutral, confidence, rationale).[[github](https://github.com/AI4Finance-Foundation/Awesome_AI4Finance)][[aclanthology](https://aclanthology.org/2025.findings-emnlp.972.pdf)]
3. Map signals to a market view (sector/factor tilts) and compute deltas.
4. Trader/risk agents convert signals → position sizing, constraints, rebalancing rules.[[github](https://github.com/AI4Finance-Foundation/Awesome_AI4Finance)][[arxiv](https://arxiv.org/html/2605.19337v1)]

**Value profile**

- Very strong on your steps **(1)–(4)** conceptually, especially the **research → decision** mapping.[[github](https://github.com/AI4Finance-Foundation/Awesome_AI4Finance)][[arxiv](https://arxiv.org/html/2605.19337v1)][[aclanthology](https://aclanthology.org/2025.findings-emnlp.972.pdf)]
- Cost is mostly **LLM API usage**; infra can be the same zero‑cost stack as in (1).
- Best when you want **state‑of‑the‑art agentic research** and are okay treating backtests as experimental.

**Repos / references**

- TradingAgents: [https://github.com/TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) (and mirrors).[[github](https://github.com/AI4Finance-Foundation/Awesome_AI4Finance)][[github](https://github.com/NitcanKen/Trading-Agents)]
- Survey & ecosystem map: **awesome‑llm‑trading‑agents** (bettyguo) – includes honest notes on what’s rigorous vs hype.[[github](https://github.com/bettyguo/awesome-llm-trading-agents)]
- Example crypto portfolio agent paper (LLM pipeline → weekly trades):[[arxiv](https://arxiv.org/html/2501.00826v3)]

### 2.2 FinRobot / AI4Finance stack

**Core:**

- **FinRobot** (AI4Finance Foundation): multi‑agent platform for financial analysis + trading, with document analysis, forecasting, and strategy agents.[[github](https://github.com/AI4Finance-Foundation/Awesome_AI4Finance)][[sourceforge](https://sourceforge.net/projects/finrobot.mirror/)]
- Related: **FinRL** (RL trading), **FinGPT** (FinLLM toolkit).[[github](https://github.com/AI4Finance-Foundation/Awesome_AI4Finance)]

**Pipeline pattern**

- Data ingestion & feature engineering modules.
- LLM + RL agents for:
    
    - Document analysis (filings, news).
    - Strategy generation and backtesting.
    - Portfolio allocation examples.[[github](https://github.com/AI4Finance-Foundation/Awesome_AI4Finance)][[sourceforge](https://sourceforge.net/projects/finrobot.mirror/)]

**Value profile**

- Strong on **(1) analysis** and **(4) portfolio decisions**, with many examples and tutorials.[[github](https://github.com/AI4Finance-Foundation/Awesome_AI4Finance)][[sourceforge](https://sourceforge.net/projects/finrobot.mirror/)]
- Good if you want a **single repo family** covering data → models → trading, and you’re comfortable with Python + RL/LLM mix.

**Repos**

- FinRobot: [https://github.com/AI4Finance-Foundation/FinRobot](https://github.com/AI4Finance-Foundation/FinRobot)[[github](https://github.com/AI4Finance-Foundation/Awesome_AI4Finance)][[sourceforge](https://sourceforge.net/projects/finrobot.mirror/)]
- Awesome_AI4Finance curated list: [https://github.com/AI4Finance-Foundation/Awesome_AI4Finance](https://github.com/AI4Finance-Foundation/Awesome_AI4Finance)[[github](https://github.com/AI4Finance-Foundation/Awesome_AI4Finance)]

---

## 3) “Quant Platform + Optional LLM” – best for serious backtesting & factor research

If your main priority is **robust, reproducible quant research** (with optional LLM overlay), the consensus picks are:

- **Qlib** (Microsoft): full ML quant platform – data processing, factor engineering, model training, backtesting, portfolio simulation.[[github](https://github.com/AI4Finance-Foundation/Awesome_AI4Finance)][[github](https://github.com/bettyguo/awesome-llm-trading-agents)]
- **FinRL / FinRL‑X**: deep RL for trading and portfolio allocation, with clean environment abstraction.[[github](https://github.com/AI4Finance-Foundation/Awesome_AI4Finance)][[github](https://github.com/bettyguo/awesome-llm-trading-agents)]
- **skfolio / Riskfolio‑Lib / PyPortfolioOpt**: portfolio optimisation libraries often used on top of signals from Qlib/FinRL/LLMs.[[github](https://github.com/wilsonfreitas/awesome-quant?ref=woz.lt)][[arxiv](https://arxiv.org/html/2605.19337v1)]

**Pipeline pattern**

1. Use Qlib/FinRL data layer for point‑in‑time fundamentals, prices, factors.
2. Train ML/RL models to generate expected returns or signals.
3. Feed signals into portfolio optimisers (skfolio, Riskfolio‑Lib).
4. Optionally wrap with LLM agents for narrative generation and “delta to market view” explanations.[[arxiv](https://arxiv.org/html/2605.19337v1)][[aclanthology](https://aclanthology.org/2025.findings-emnlp.972.pdf)]

**Value profile**

- Best for **rigorous evaluation** and avoiding common backtest pitfalls (look‑ahead bias, overfitting).[[arxiv](https://arxiv.org/html/2605.19337v1)][[github](https://github.com/bettyguo/awesome-llm-trading-agents)]
- Slightly more “quant‑heavy”; LLM parts are usually added by you or via separate agent repos.

**Repos**

- Qlib: [https://github.com/microsoft/qlib](https://github.com/microsoft/qlib)
- FinRL: [https://github.com/AI4Finance-Foundation/FinRL](https://github.com/AI4Finance-Foundation/FinRL)
- skfolio: [https://github.com/skfolio/skfolio](https://github.com/skfolio/skfolio)[[github](https://github.com/wilsonfreitas/awesome-quant?ref=woz.lt)]

---

## 4) “Finance Lakehouse” – best if you care about enterprise‑style data engineering

If you like the idea of a **medallion lakehouse** (Bronze → Silver → Gold) and strong data quality controls:

- **FinanceLake**: open‑source platform for ingesting, processing, and visualising market/financial data.[[github](https://github.com/FinanceLake/financelake)]
- **FinTech‑Data‑Engineering** (Medallion Lakehouse + dbt + Power BI).[[github](https://github.com/Abdelrhman-Hussien-Bi/FinTech-Data-Engineering)]

These are more about **data infrastructure quality** than portfolio logic; you’d combine them with one of the quant/agent stacks above for actual decisions.

---

## Practical recommendation (minimal, high‑consensus setup)

If you want **one concrete combination** that:

- Is already done by many individuals,
- Has near‑zero infra cost,
- Covers ingestion → bookkeeping → analysis → portfolio decisions,
- Can later be augmented with LLM agents,

then the most agreed‑on pattern today is:

1. **Infra backbone:**
    
    - GitHub Actions (orchestration) + DuckDB/MotherDuck (storage) + Streamlit (dashboard).[[rasmusnes](https://rasmusnes.com/posts/stock-advisor-stack/)][[github](https://github.com/migbenav/Financial-Data-Pipeline-and-Analytics)][[duckdblab](https://duckdblab.org/en/post/duckdb-financial-dashboard-product/)]
2. **Data & bookkeeping:**
    
    - Daily price/fundamental ingestion into DuckDB tables.
    - Separate tables for trades, positions, cash flows (your ledger).[[rasmusnes](https://rasmusnes.com/posts/stock-advisor-stack/)][[github](https://github.com/migbenav/Financial-Data-Pipeline-and-Analytics)]
3. **Analysis:**
    
    - SQL/Python for risk & performance metrics; optional ML models (CatBoost, etc.) in Dagster or plain Python.[[rasmusnes](https://rasmusnes.com/posts/stock-advisor-stack/)][[github](https://github.com/migbenav/Financial-Data-Pipeline-and-Analytics)]
4. **Portfolio decisions:**
    
    - Rule‑based rebalancing or optimisation with **skfolio / Riskfolio‑Lib / PyPortfolioOpt**.[[github](https://github.com/wilsonfreitas/awesome-quant?ref=woz.lt)][[arxiv](https://arxiv.org/html/2605.19337v1)]
5. **Optional AI layer:**
    
    - Plug in **TradingAgents** or **FinRobot** on top of this data to generate signals and rationales, then feed those into your existing decision logic.[[github](https://github.com/AI4Finance-Foundation/Awesome_AI4Finance)][[sourceforge](https://sourceforge.net/projects/finrobot.mirror/)]

If you tell me:

- whether you prefer **Python‑only** or are fine with **Go + Python**, and
- whether you want **LLM‑first** or **quant‑first** as the main decision engine,

I can narrow this to a 2–3 repo “starter pack” with exact install steps for Windows and a suggested data source list (free/low‑cost).