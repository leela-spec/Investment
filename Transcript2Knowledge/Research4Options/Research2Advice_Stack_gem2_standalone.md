Rather than designing custom glue code or theoretical formulas, there are existing, battle-tested open-source repositories designed for this process: **ingesting research $\to$ extracting claims $\to$ debating/reconciling against market consensus $\to$ rebalancing an actual portfolio**.

  

The two most widely adopted projects automating this pipeline are **`TauricResearch/TradingAgents`** and **`virattt/ai-hedge-fund`**, along with **`TradingGoose Studio`** for live broker execution.

  

### Solution 1: `TauricResearch/TradingAgents` (LangGraph Multi-Agent Engine)

- **Repository:** [github.com/TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) (~109k GitHub stars)
    
      
    
- **What it is:** A multi-agent framework built on LangGraph that executes end-to-end research synthesis, bull/bear conflict debate, and portfolio-aware trade generation.
    
      
    

```
[SEC EDGAR / News / Finnhub / Reddit]
                   │
                   ▼
       1. Analyst Team (Parallel)
   (Fundamentals, Market, News, Social)
                   │
                   ▼
       2. Researcher Team (Debate)
     (Bull Researcher ⮀ Bear Researcher)
                   │
                   ▼
    3. Trader & Risk Management Team
  (Reconciles Thesis vs. Risk Constraints)
                   │
                   ▼
   4. Portfolio Manager (PortfolioContext)
(Compares against current book ➔ Action JSON)
```

#### How It Automates Your 4-Step Process:

1. **Research & Data Ingestion:**
    
      
    - Built-in tool adapters ingest raw SEC EDGAR 10-K/10-Q/8-K filings, earnings news, analyst revisions, and price action via providers like Finnhub, Alpha Vantage, or yfinance.
        
          
        
2. **Claim & Analysis Extraction:**
    
      
    - The **Analyst Team** runs specialized agents in parallel:
        
          
        - `Fundamentals Analyst`: Extracts financial metrics, balance sheet leverage, and filing changes.
            
              
            
        - `News Analyst`: Extracts headline catalysts, litigation, and guidance updates.
            
              
            
        - `Market Analyst`: Ingests price trends and technical indicators.
            
              
            
3. **Merging Claims into Market Opinion (Conflict Resolution):**
    
      
    - Instead of overwriting an opinion or hallucinating consensus, the extracted claims feed into the **Researcher Team**.
        
          
        
    - A **Bull Researcher** and a **Bear Researcher** run a multi-round debate: they pit new research claims against prevailing market valuations and risks.
        
          
        
    - A **Research Manager** moderates the debate, filters out noise, and establishes an updated consensus conviction score.
        
          
        
4. **Portfolio Modification (Rebalancing):**
    
      
    - The updated conviction passes to the **Trader Agent** and **Risk Management Team**.
        
          
        
    - The **Portfolio Manager** takes in your actual current book via `PortfolioContext` (cash balance, current positions, cost basis). It evaluates whether the new consensus justifies paying transaction costs and taking on risk, outputting a concrete portfolio action (e.g., `BUY`, `SELL`, `HOLD`, target share quantity, or position weight).
        
          
        

#### Minimal Setup & Execution (Windows / Python):

PowerShell

```
# 1. Clone & install
git clone https://github.com/TauricResearch/TradingAgents.git
cd TradingAgents
pip install .

# 2. Configure environment (.env)
# Set your LLM (OpenAI, Anthropic, or local Ollama) and data provider API key
Set-Content .env "OPENAI_API_KEY=sk-...\nFINNHUB_API_KEY=..."
```

**Run an End-to-End Analysis Against Your Current Portfolio:**

  

Python

```
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.portfolio import PortfolioContext

# Initialize graph
config = DEFAULT_CONFIG.copy()
ta = TradingAgentsGraph(config=config)

# Pass your existing ledger / positions into the run
current_portfolio = PortfolioContext.model_validate({
    "cash": 15000.0,
    "currency": "USD",
    "positions": [{"ticker": "NVDA", "quantity": 50, "average_price": 120.0}],
})

# Run the complete pipeline (Ingest -> Extract -> Debate -> Rebalance)
state, decision = ta.propagate(
    ticker="NVDA", date="2026-09-25", portfolio=current_portfolio
)

print(decision)
# Output: Reconciled thesis, Bull/Bear debate summary, and concrete order recommendation
```

### Solution 2: `virattt/ai-hedge-fund` (Multi-Persona Committee & Rebalance Monitor)

- **Repository:** [github.com/virattt/ai-hedge-fund](https://github.com/virattt/ai-hedge-fund) (~64k GitHub stars)
    
      
    
- **What it is:** A production CLI and application that simulates an investment committee (personas based on Buffett, Burry, Graham, etc.) paired with an earnings analyst, consensus models, and a portfolio rebalancing monitor.
    
      
    

```
[Financial Datasets API / SEC 8-K / Earnings]
                      │
                      ▼
         1. Earnings & Valuation Agents
         (Extracts surprises, beats, guidance)
                      │
                      ▼
       2. Investment Committee Consensus
   (Buffett, Burry, Ackman + Consensus Agent)
                      │
                      ▼
        3. Portfolio Construction Engine
(Modern Portfolio Theory / Risk Parity / Target Weights)
                      │
                      ▼
          4. Rebalance Drift Monitor
   (`rebalance_monitor.py` ➔ Urgency & Trade Delta)
```

#### How It Automates Your 4-Step Process:

1. **Research Ingestion:**
    
      
    - Automated collectors pull SEC 8-K surprise filings, earnings call revisions, and fundamentals via Financial Datasets API, SEC EDGAR, or Yahoo Finance.
        
          
        
2. **Claim & Metric Extraction:**
    
      
    - **Earnings Analyst**: Scans earnings releases to extract EPS surprises, historical beat rates, and margin trends.
        
          
        
    - **Wall Street Consensus Analyst**: Extracts consensus price targets, upside/downside percentages, and buy/hold/sell revisions.
        
          
        
    - **Macro Strategist**: Measures volatility regimes (VIX, index trends).
        
          
        
3. **Merging Claims into Market Opinion:**
    
      
    - Multiple persona agents independently evaluate the extracted claims through different lenses (e.g., Buffett examines moat and ROE; Burry checks debt and overvaluation).
        
          
        
    - A **Consensus Mechanism** compiles individual agent conviction scores (-1.0 to +1.0) into a single blended market thesis for the ticker.
        
          
        
4. **Portfolio Rebalancing:**
    
      
    - Uses built-in Modern Portfolio Theory (MPT) / Risk Parity routines.
        
          
        
    - Runs `rebalance_monitor.py`: Compares new target weights generated by the consensus against your recorded portfolio holdings, flags portfolio drift, and emits an alert with urgency (`HIGH`, `MEDIUM`, `LOW`) and exact rebalancing trades.
        
          
        

#### Minimal Setup & Execution (Windows / Terminal):

PowerShell

```
# 1. Install via pipx or uv
uv tool install aihf
# Or clone from source:
# git clone https://github.com/virattt/ai-hedge-fund.git && cd ai-hedge-fund && poetry install

# 2. Interactive Run (Prompts for API keys on first launch and saves to ~/.hedge-fund/.env)
aihf

# 3. Direct Portfolio Rebalancing Run:
# Checks your current holdings against current research consensus
ai-hedge-fund rebalance AAPL:0.3,MSFT:0.3,NVDA:0.4 --last-rebalanced 2026-06-01
```

### Solution 3: `TradingGoose Studio` (Execution Layer for Alpaca)

- **Repository:** [github.com/TradingGoose/TradingGoose.github.io](https://github.com/TradingGoose/TradingGoose.github.io)
    
      
    
- **What it is:** A full-stack open-source platform that turns the TradingAgents workflow into a live, scheduled trading system integrated with broker APIs (specifically Alpaca).
    
      
    

#### How It Automates Your Process End-to-End:

- **Analysis & Extraction:** Triggers multi-agent fundamental, news, and technical evaluation on a schedule or via webhooks.
    
      
    
- **Opinion Merge:** Runs the multi-agent consensus module to settle on final target ratings.
    
      
    
- **Execution & Ledger:** Directly reads your live account holdings, cash balances, and margin limits via the Alpaca API. The Portfolio Manager agent calculates position sizing rules and sends rebalancing orders (with a manual approval gate or full automation).
    

### Summary: Which One to Run

|**Requirement**|**Best-Fitting Repo**|**Why**|
|---|---|---|
|**Complete Python library with programmatic API**|**`TauricResearch/TradingAgents`**|Direct LangGraph workflow; handles the research debate and takes a `PortfolioContext` object containing your current positions directly into the function call.|
|**Zero-code CLI tool with portfolio drift monitor**|**`virattt/ai-hedge-fund`**|Runs out-of-the-box (`uv tool install aihf`); has built-in `rebalance_monitor.py` for tracking drift against current holdings.|
|**Automated broker execution**|**`TradingGoose Studio`**|Connects the multi-agent research analysis directly to Alpaca paper or live trading accounts.|