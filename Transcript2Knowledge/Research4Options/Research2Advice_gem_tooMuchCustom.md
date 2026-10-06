## 1. Executive Summary

- **Decoupling of the Data Warehouse from Compute:** In the 2024–2026 ecosystem, heavy database servers (like PostgreSQL or TimescaleDB) are largely replaced in solo and small-team setups by embedded columnar engines (**DuckDB**) paired with compressed **Parquet** catalogs. This delivers near-zero infrastructure cost, sub-second analytical queries, and zero daemon maintenance.
    
      
    
- **Unified API Gateways Over Custom Scrapers:** Rather than maintaining fragile scrapers across Yahoo Finance, SEC EDGAR, and macroeconomic feeds, modern architectures standardize on unified open-source abstractions like **OpenBB Platform (v4)**. OpenBB acts as a provider-agnostic data layer that standardizes outputs into standard DataFrames and Pydantic schemas.
    
      
    
- **Strict Separation Between Accounting and Analytics:** Production-grade pipelines separate the _transactional ledger_ (which must obey strict double-entry accounting for tax lots, splits, and currency conversion) from the _analytical data lake_. Tools like **Beancount** (plain-text double entry) and **Ghostfolio** (self-hosted wealth management) have emerged as the standard backbones to prevent P&L drift.
    
      
    
- **The Shift to Convex Optimization and Risk Parity:** Classical Markowitz mean-variance optimization has taken a backseat to robust risk budgeting frameworks. **Riskfolio-Lib** (built on CVXPY) has become the gold standard open-source library, supporting Conditional Value-at-Risk (CVaR), Hierarchical Risk Parity (HRP), and Black-Litterman models with institutional-grade constraint solvers.
    
      
    
- **Multi-Agent LLMs as Structured Research Analysts, Not Direct Traders:** The industry has moved away from "black-box prompt-to-trade" bots toward structured, graph-orchestrated multi-agent teams (e.g., **TradingAgents**, **FinRobot**). In these setups, deterministic code handles the math, while LLMs debate qualitative filings, transcripts, and macro context to feed subjective views into quantitative models.
    
      
    
- **Best Starting Point:** For 95% of individual investors and small teams, the **Modern Sovereign Quant Stack** (**OpenBB Platform + DuckDB + Beancount/Ghostfolio + Riskfolio-Lib**) provides the best value-per-dollar ratio: 100% open source, zero cloud spend, deterministic execution, and seamless extensibility into multi-agent LLM overlays.
    
      
    

## 2. Reference Stacks

### Stack 1: The Modern Sovereign Quant Stack (Local-First OLAP & Optimization)

> _A zero-cloud-cost, highly reproducible, local-first analytics and optimization pipeline built for fundamental, factor, and tactical allocators._
> 
>   

- **Core Repositories & Tools:**
    
      
    - Ingestion: [OpenBB Platform](https://github.com/OpenBB-finance/OpenBB) (unified market, fundamental, and macroeconomic data gateway)
        
          
        
    - Storage & Engine: [DuckDB](https://github.com/duckdb/duckdb) (in-process SQL OLAP engine over local Parquet)
        
          
        
    - Ledger / Bookkeeping: [Beancount](https://github.com/beancount/beancount) with [Fava](https://github.com/beancount/fava) (or [Ghostfolio](https://github.com/ghostfolio/ghostfolio) via Docker)
        
          
        
    - Analysis & Portfolio Decisions: [Riskfolio-Lib](https://github.com/dcajasn/Riskfolio-Lib) (CVXPY-based portfolio optimization) and [QuantStats](https://github.com/ranaroussi/quantstats) (portfolio risk tear-sheets)
        
          
        
    - UI / Dashboard: [Streamlit](https://github.com/streamlit/streamlit)
        
          
        
    - Automation: Local cron / Windows Task Scheduler or [GitHub Actions](https://github.com/features/actions)
        
          
        
- **Architecture Flow:**
    
      
    
    $$\text{OpenBB Gateway} \xrightarrow{\text{DataFrames}} \text{DuckDB / Parquet Lake} \xrightarrow{\text{Prices}} \text{Beancount Ledger (Lots, Cash, P\&L)}$$
    
    $$\Big\downarrow$$
    
    $$\text{Riskfolio-Lib (CVaR/HRP/Black-Litterman)} \longrightarrow \text{Target Weights} \longrightarrow \text{Rebalancing Trade Generator} \longrightarrow \text{Streamlit}$$
    
- **How It Handles Steps 1–4:**
    
      
    1. **Ingestion:** OpenBB ingests prices, historical financial statements, EDGAR filings, and analyst estimates from free/low-cost providers (yfinance, FMP, SEC EDGAR, FRED). Data is appended to a local partitioned Parquet directory partitioned by `year/month`.
        
          
        
    2. **Bookkeeping:** Beancount tracks trades using double-entry plain text (handling corporate actions, dividends, commission fees, and FIFO/specific-lot tax accounting). DuckDB directly queries Beancount via the `beanquery` Python API or SQLite export to fetch real-time net exposures and cash positions.
        
          
        
    3. **Analysis:** QuantStats generates daily risk tearsheets (Sharpe, Sortino, drawdowns, tail risk). Returns matrices flow into DuckDB for factor regression against Fama-French or custom ETF benchmarks.
        
          
        
    4. **Decisions:** Riskfolio-Lib ingests the returns matrix and current position weights. It runs Mean-Variance, CVaR, or Hierarchical Risk Parity (HRP) under customizable turnover constraints, asset bounds, and minimum weight cutoffs, producing the exact rebalancing order ticket.
        
          
        
- **Pros & Cons:**
    
      
    - _Pros:_ True $0 infrastructure cost; zero server management; extreme query speed over local Parquet; mathematically rigorous tax-lot bookkeeping. Runs natively on Windows via Python/pip.
        
          
        
    - _Cons:_ Manual broker execution (unless integrated with Alpaca/Interactive Brokers via script); lacks real-time sub-second tick streaming.
        
          
        
- **Cost Profile:** **$0/month** for infrastructure. Optional $0–$15/month for basic commercial API tiers (e.g., Financial Modeling Prep or Alpha Vantage).
    
      
    

### Stack 2: The High-Throughput Event-Driven Quant Stack

> _A high-frequency/intraday event-driven backtesting and live trading engine engineered for systematic multi-asset execution._
> 
>   

- **Core Repositories & Tools:**
    
      
    - Engine & Ledger: [NautilusTrader](https://github.com/nautechsystems/nautilus_trader) (Rust core with Python bindings via PyO3)
        
          
        
    - Exploratory Data & Prototyping: [vectorbt](https://github.com/polakowo/vectorbt) or [vectorbt-pro](https://vectorbt.pro/)
        
          
        
    - Data Storage: Local Parquet data catalog managed by NautilusTrader
        
          
        
    - Alternative Comprehensive Engine: [QuantConnect LEAN](https://github.com/QuantConnect/Lean) (C# engine with Python wrapper)
        
          
        
- **Architecture Flow:**
    
      
    
    $$\text{Broker Feeds (IBKR / Crypto / Polygon)} \xrightarrow{\text{Tick/Bar Events}} \text{Nautilus Parquet Catalog}$$
    
    $$\Big\downarrow$$
    
    $$\text{Nautilus Core (Rust Event Engine)} \longleftrightarrow \text{Internal Portfolio / Order Cache (State \& Margin)}$$
    
    $$\Big\downarrow$$
    
    $$\text{Strategy Actors} \longrightarrow \text{Risk Engine / Position Sizer} \longrightarrow \text{Execution Adapters (Live Orders)}$$
    
- **How It Handles Steps 1–4:**
    
      
    1. **Ingestion:** Data is ingested as millisecond/nanosecond raw ticks, quotes, and trade bars via vendor adapters (Interactive Brokers, Binance, Databento) into an optimized, append-only Parquet historical catalog.
        
          
        
    2. **Bookkeeping:** Nautilus includes an internal, stateful double-entry cash and position tracking engine. It continuously accounts for open margin, realized/unrealized P&L, commissions, and fill latency.
        
          
        
    3. **Analysis:** High-speed vectorized signal generation is prototyped in `vectorbt`. Once validated, strategies are converted into event-driven Nautilus `Actor` or `Strategy` classes that subscribe to order-book and bar events.
        
          
        
    4. **Decisions:** Sizing algorithms evaluate risk per trade (e.g., ATR-based fractional volatility parity, Kelly criterion). Orders are matched against internal risk limits (max drawdown, max position size) before triggering execution adapters.
        
          
        
- **Pros & Cons:**
    
      
    - _Pros:_ Institutional-grade execution speed; zero backtest-to-live code divergence; handles complex order types (bracket, trailing stop, OCO) and real-time execution.
        
          
        
    - _Cons:_ Steep learning curve; setup requires compiling/configuring Rust bindings; ill-suited for fundamental screening or long-horizon macro rebalancing.
        
          
        
- **Cost Profile:** **$0** software license (LGPL-3.0). Data costs scale with need: $0 (free crypto/yfinance feeds) to $50–$200/month (Databento / Polygon tick data) + optional VPS ($10–$40/month).
    
      
    

### Stack 3: The Multi-Agent LLM Research & Decision Stack

> _A collaborative multi-agent architecture that leverages LLMs to synthesize qualitative data into structured investment decisions with quantitative guardrails._
> 
>   

- **Core Repositories & Tools:**
    
      
    - Multi-Agent Orchestration: [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) (LangGraph-based multi-agent trading team) or [AI4Finance/FinRobot](https://github.com/AI4Finance-Foundation/FinRobot) (PydanticAI/FastAPI multi-agent research framework)
        
          
        
    - Data & Tool Interface: [OpenBB Agents](https://github.com/OpenBB-finance/openbb-agents) / OpenBB Platform
        
          
        
    - SEC & Filing Ingestion: [edgar-tools](https://www.google.com/search?q=https://github.com/edgar-tools/edgar-tools) and Financial Modeling Prep (FMP)
        
          
        
    - Structured Extraction & Guardrails: [Instructor](https://github.com/jxnl/instructor) or [Pydantic](https://github.com/pydantic/pydantic)
        
          
        
- **Architecture Flow:**
    
      
    
    $$\text{SEC 10-K/Q, Transcripts, News} \xrightarrow{\text{OpenBB / EDGAR}} \text{Analyst Agent Team (Fundamentals, Technicals, Sentiment)}$$
    
    $$\Big\downarrow$$
    
    $$\text{Bull Researcher} \underset{\text{Structured Debate}}{\rightleftharpoons} \text{Bear Researcher}$$
    
    $$\Big\downarrow$$
    
    $$\text{Risk Analyst (Checks Portfolio Context \& Max Drawdown)} \longrightarrow \text{Portfolio Manager (Action JSON)}$$
    
    $$\Big\downarrow$$
    
    $$\text{Deterministic Optimizer (CVXPY / Riskfolio-Lib)} \longrightarrow \text{Validated Order Batch}$$
    
- **How It Handles Steps 1–4:**
    
      
    1. **Ingestion:** Financial statements, earnings call transcripts, 8-K filings, and news feeds are pulled via OpenBB Agents and parsed into structured context blocks using RAG or large context windows.
        
          
        
    2. **Bookkeeping:** Ingests an existing portfolio state via a validated Pydantic schema (e.g., `PortfolioContext` containing cash, open positions, and average cost basis) passed directly into the system prompt.
        
          
        
    3. **Analysis:** Multiple specialized agents perform role-based analysis:
        
          
        - _Fundamentals Analyst:_ Assesses ROIC, debt coverage, and valuation multiples.
            
              
            
        - _Sentiment/News Analyst:_ Scans recent news for litigation or regulatory risks.
            
              
            
        - _Bull vs. Bear Debate:_ Two agents critique each other’s hypotheses to suppress hallucinated consensus.
            
              
            
    4. **Decisions:** The Portfolio Manager agent issues proposed target allocations. **Crucial Rule:** The LLM does _not_ do raw mathematical sizing directly. Instead, it outputs subjective asset views (expected return bounds and confidence scores), which are injected as views into a Black-Litterman model inside Riskfolio-Lib to generate constraint-checked rebalancing orders.
        
          
        
- **Pros & Cons:**
    
      
    - _Pros:_ Automates qualitative synthesis of earnings calls and 10-Ks that quant algorithms cannot read; structured debate eliminates single-prompt bias.
        
          
        
    - _Cons:_ API token costs add up quickly with daily runs; non-deterministic outputs require strict schema validation; slower cycle times (30–90 seconds per ticker run).
        
          
        
- **Cost Profile:** Frameworks are free open source. LLM inference costs run **$10–$50/month** on cloud models (Claude 3.5 Sonnet, GPT-4o) or **$0** if running open-weights models (Qwen 2.5 32B, DeepSeek-R1 distillations) locally via Ollama / llama.cpp.
    
      
    

### Stack 4: The Institutional AI Quant & Factor Stack (Qlib + MLflow)

> _A machine-learning-centric research platform optimized for alpha factor mining, GBDT/transformer models, and automated backtesting over cross-sectional universes._
> 
>   

- **Core Repositories & Tools:**
    
      
    - ML Quant Engine: [Microsoft Qlib](https://github.com/microsoft/qlib) (AI-oriented quantitative investment platform)
        
          
        
    - ML Experiment Tracking: [MLflow](https://github.com/mlflow/mlflow)
        
          
        
    - Feature Engineering & Data: Qlib compact binary storage format + OpenBB data pipeline
        
          
        
    - Sizing & Execution: Qlib Portfolio Generator + [CVXPY](https://github.com/cvxpy/cvxpy)
        
          
        
- **Architecture Flow:**
    
      
    
    $$\text{OpenBB / Yahoo / EODHD} \xrightarrow{\text{Qlib Ingestion Script}} \text{Qlib Binary Factor Store (Alpha158 / 360)}$$
    
    $$\Big\downarrow$$
    
    $$\text{Model Training (LightGBM / DoubleEnsemble / Transformer)} \longleftrightarrow \text{MLflow Model Tracking}$$
    
    $$\Big\downarrow$$
    
    $$\text{Predictive Score Generator (Cross-Sectional Rank)} \longrightarrow \text{Top-k / Drop-N Portfolio Builder} \longrightarrow \text{CVXPY Optimizer}$$
    
- **How It Handles Steps 1–4:**
    
      
    1. **Ingestion:** Raw daily OHLCV and fundamental metrics are converted via Qlib’s data dump script into a fast, memory-mapped binary array structure containing pre-calculated factor datasets (e.g., Alpha158, Alpha360).
        
          
        
    2. **Bookkeeping:** Tracks portfolio simulation via Qlib’s backtest state engine, modeling trade slippage, borrow fees, and execution round-trips.
        
          
        
    3. **Analysis:** Uses Machine Learning models (LightGBM, XGBoost, GRU, ALSTM) to predict cross-sectional return rankings. It calculates Information Coefficient (IC), Rank IC, and Long-Short Sharpe ratios across defined holding periods.
        
          
        
    4. **Decisions:** Executes Top-K, Drop-N, or weight optimization routines via quadratic programming (CVXPY) to rebalance the portfolio based on model scores subject to sector neutrality and maximum asset weight constraints.
        
          
        
- **Pros & Cons:**
    
      
    - _Pros:_ World-class factor mining infrastructure; out-of-the-box ML models for quantitative finance; highly optimized cross-sectional backtesting.
        
          
        
    - _Cons:_ Requires compiling C++ extensions (setup on native Windows often requires Visual C++ Build Tools or WSL2); rigid data format conventions; steep learning curve.
        
          
        
- **Cost Profile:** **$0** software cost. Compute-heavy: benefits from an NVIDIA GPU for deep learning models.
    
      
    

## 3. Ranked Comparison

|**Metric / Criterion**|**Stack 1: Modern Sovereign Quant**|**Stack 2: Event-Driven Nautilus**|**Stack 3: Multi-Agent LLM (TradingAgents)**|**Stack 4: ML Factor (Qlib)**|
|---|---|---|---|---|
|**Coverage of Steps 1–4**|**9.5 / 10**<br><br>  <br>  <br><br>(Complete end-to-end; excellent accounting & optimization)|**8.5 / 10**<br><br>  <br>  <br><br>(Focuses heavily on 1, 2, & 4; weak on fundamental analysis)|**8.0 / 10**<br><br>  <br>  <br><br>(Superb on 1 & 3; requires external library for rigorous 2 & 4)|**8.5 / 10**<br><br>  <br>  <br><br>(Superb on 1, 3, & 4; lacks real-world tax-lot ledger)|
|**Community Adoption & Stars**|**High**<br><br>  <br>  <br><br>(DuckDB: 28k+, OpenBB: 35k+, Riskfolio: 2k+)|**Moderate–High**<br><br>  <br>  <br><br>(Nautilus: ~2.5k+, highly active Discord)|**Rapidly Growing**<br><br>  <br>  <br><br>(TradingAgents / FinRobot: 5k–10k+ stars combined)|**Very High**<br><br>  <br>  <br><br>(Qlib: 17k+ stars, academic and hedge-fund standard)|
|**Documentation & Windows Setup**|**10 / 10**<br><br>  <br>  <br><br>(Pure pip/uv wheels on native Windows; comprehensive docs)|**6.5 / 10**<br><br>  <br>  <br><br>(Requires Rust toolchain or exact wheel match; complex API)|**8.5 / 10**<br><br>  <br>  <br><br>(Standard Python packages; simple `.env` config; CLI ready)|**6.0 / 10**<br><br>  <br>  <br><br>(Requires MSVC Build Tools or WSL2; dense docs)|
|**Cost Efficiency (Value / $)**|**10 / 10**<br><br>  <br>  <br><br>($0 infrastructure; zero token overhead)|**8.5 / 10**<br><br>  <br>  <br><br>($0 software; data feeds can cost money)|**7.5 / 10**<br><br>  <br>  <br><br>(Consumes $10–$50/mo in LLM tokens unless using local models)|**9.0 / 10**<br><br>  <br>  <br><br>($0 software; local compute)|
|**Overall Rank**|**#1 (Best All-Rounder)**|**#3 (Best for Live Execution)**|**#2 (Best for Qualitative Synthesis)**|**#4 (Best for Pure ML Researchers)**|

## 4. Recommended Starter Packs

For an individual investor or small team operating on **Windows with Python**, who wants a battle-tested backbone that can later accommodate LLM agents, we recommend two progressive paths:

  

### Starter Pack A: The Sovereign Core (Quant + Ledger Backbone)

_Recommended for:_ Investors who want a deterministic, mathematically sound foundation for portfolio tracking, fundamental screening, and rebalancing.

  

```
       [OpenBB Platform v4]
                 │
                 ▼
          [DuckDB Storage]  ◄────►  [Beancount / Fava Ledger]
                 │
                 ▼
         [Riskfolio-Lib]
                 │
                 ▼
      [Streamlit / Order Ticket]
```

#### Exact Repositories to Clone / Install

- Data Ingestion: [OpenBB Platform](https://github.com/OpenBB-finance/OpenBB) (`pip install openbb`)
    
      
    
- Storage: [DuckDB](https://github.com/duckdb/duckdb) (`pip install duckdb`)
    
      
    
- Ledger: [Beancount](https://github.com/beancount/beancount) (`pip install beancount fava`)
    
      
    
- Portfolio Optimization: [Riskfolio-Lib](https://github.com/dcajasn/Riskfolio-Lib) (`pip install riskfolio-lib cvxpy`)
    
      
    
- Reporting & UI: [QuantStats](https://github.com/ranaroussi/quantstats) & [Streamlit](https://github.com/streamlit/streamlit) (`pip install quantstats streamlit`)
    
      
    

#### Minimal Viable Setup on Windows (PowerShell)

PowerShell

```
# 1. Create a clean virtual environment (Python 3.11 or 3.12 recommended)
uv venv quant_env --python 3.11
.\quant_env\Scripts\activate

# 2. Install core packages (pre-compiled binary wheels available for Windows)
uv pip install openbb duckdb beancount fava riskfolio-lib quantstats streamlit
```

#### Data Flow Implementation

1. **Ingest to DuckDB:** Fetch historical close prices and fundamentals with OpenBB, writing them to a single local file (`market_data.duckdb`) or Parquet directory:
    
      
    
    Python
    
    ```
    import duckdb
    from openbb import obb
    
    # Fetch historical data (e.g. S&P 500 ETF and tech basket)
    data = (
        obb.equity.price.historical(
            "SPY,QQQ,AAPL,MSFT", start_date="2023-01-01", provider="yfinance"
        )
        .to_df()
        .reset_index()
    )
    
    con = duckdb.connect("market_data.duckdb")
    con.execute(
        "CREATE OR REPLACE TABLE daily_prices AS SELECT * FROM data"
    )
    ```
    

```
2. **Read Current State from Ledger:** In your `portfolio.beancount` file, track stock purchases, cash deposits, and lots. Use Beancount’s Python loader to export existing weights into a pandas DataFrame:
   ```python
   from beancount import loader
   from beancount.query import query

   entries, errors, options = loader.load_file("portfolio.beancount")
   # Query current positions and cash balances via BQL
   _, rows = query.run_query(
       entries,
       options,
       "SELECT account, sum(position) WHERE account ~ 'Assets:Investments' GROUP BY account",
   )
```

3. **Optimize with Riskfolio-Lib:** Feed returns into `Riskfolio-Lib` to generate optimal portfolio weights under target risk constraints:
    
      
    
    Python
    
    ```
    import riskfolio as rp
    
    # returns: DataFrame of daily percentage changes from DuckDB
    port = rp.Portfolio(returns=returns_df)
    port.assets_stats(method_mu="hist", method_cov="hist")
    
    # Calculate optimal portfolio maximizing Sharpe under CVaR (Conditional VaR)
    weights = port.optimization(
        model="Classic", rm="CVaR", obj="Sharpe", rf=0.04
    )
    print(weights)  # Output: Target allocation matrix
    ```
    

```
4. **Order Generation:** Compute $\text{Target Value} - \text{Current Value}$ to output an exact CSV rebalancing ticket for your broker.

---

### Starter Pack B: The Hybrid Agent-Enhanced Stack (LLM + Quant Backbone)
*Recommended for:* Investors who already have the data backbone running and want AI agents to read SEC filings, earnings call transcripts, and macroeconomic indicators, outputting quantified inputs for the portfolio optimizer.

```

```
              [SEC EDGAR / News / Transcripts]
                              │
                              ▼
       [TradingAgents Multi-Agent Research Graph]
           (Fundamental, Sentiment, Bull/Bear)
                              │
                              ▼
         [Structured Investment View (P & Q Vectors)]
                              │
                              ▼
      [Riskfolio-Lib (Black-Litterman Portfolio Engine)]
                              │
                              ▼
            [Validated Order Execution / Alerts]
```

```

#### Exact Repositories to Clone
* Multi-Agent Core: [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents)
  ```bash
  git clone https://github.com/TauricResearch/TradingAgents.git
```

- Agent Tool Connector: [openbb-agents](https://github.com/OpenBB-finance/openbb-agents)
    
      
    
- Structured Output Validation: [Instructor](https://github.com/jxnl/instructor)
    
      
    

#### How to Add the LLM Layer Without Rewriting Your Pipeline

The biggest architectural flaw in early LLM systems was letting language models pick final share quantities directly. The proper hybrid pattern uses LLMs strictly as **subjective view estimators** for a **Black-Litterman optimization model**:

  

1. **Step 1 (Agent Research):** Run `TradingAgents` over your investment universe. The Bull and Bear researcher debate evaluates whether a company’s upcoming quarter will outperform historical trends.
    
      
    
2. **Step 2 (Structured View Extraction):** Use `instructor` or Pydantic to extract the final agent consensus into a machine-readable schema:
    
      
    
    Python
    
    ```
    from pydantic import BaseModel, Field
    
    
    class AssetView(BaseModel):
      ticker: str
      expected_excess_return: float = Field(
          description="Expected annual outperformance vs benchmark (e.g. 0.05"
          " for +5%)"
      )
      confidence: float = Field(
          description="Confidence score between 0.0 and 1.0 based on evidence"
          " weight"
      )
    ```
    

```
3. **Step 3 (Inject into Riskfolio-Lib Black-Litterman):** Rather than letting the LLM invent portfolio allocations, map the agent’s `expected_excess_return` and `confidence` directly into the Pick Matrix ($P$) and View Vector ($Q$) of Riskfolio-Lib’s Black-Litterman optimizer:
   ```python
   # P: Links views to specific assets; Q: Vector of expected views
   # Omega: Covariance of views, scaled down inversely by agent confidence
   port.black_litterman_stats(
       P=P_matrix, Q=Q_vector, omega=omega_matrix, rf=0.04
   )
   weights = port.optimization(model="BL", rm="MV", obj="Sharpe")
```

This hybrid architecture provides complete explainability: the quantitative risk engine guarantees that portfolio constraints, volatility limits, and diversification mandates are never violated, while the LLM research agent contributes automated qualitative due diligence that traditional price-only algorithms ignore.