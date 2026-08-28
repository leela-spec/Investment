# Investment Analysis & Portfolio Decision Pipeline — Architecture Specification

> **Governing Axiom**: *Code computes everything numeric; the LLM only narrates and orchestrates.*

---

## 1. Executive Summary

This specification defines the 7-step institutional investment analysis, portfolio decision, and trade execution pipeline. It provides the structured decision matrix evaluating open-source tools across every functional layer and specifies the #1 recommended combinatorial architecture.

---

## 2. 7-Step Functional Decision Matrix

```json
{
  "pipeline_steps": [
    {
      "step": 1,
      "name": "Portfolio Ingestion & Sync",
      "description": "Multi-broker holdings, tax lots, cash balances, base currency conversions",
      "primary_best_practice": {
        "name": "ibflex & ib-async",
        "repo": "csingley/ibflex",
        "license": "MIT",
        "score": 9.7,
        "rationale": "Automated headless parsing of IBKR Flex XML queries and live socket API. Zero desktop GUI needed."
      },
      "alternatives": [
        {"name": "Portfolio Performance (ppxml2db)", "repo": "buchen/portfolio", "license": "EPL-1.0", "score": 8.5},
        {"name": "Ghostfolio REST API", "repo": "ghostfolio/ghostfolio", "license": "AGPL-3.0", "score": 8.2},
        {"name": "ofxparse / pytr", "repo": "jseutter/ofxparse", "license": "MIT", "score": 7.8}
      ]
    },
    {
      "step": 2,
      "name": "Macro & Market Intelligence Engine",
      "description": "Factor scoring, regime classification, qualitative evidence aggregation",
      "primary_best_practice": {
        "name": "IPOS DuckDB + Karakeep Mirror",
        "license": "MIT / Apache-2.0",
        "score": 9.9,
        "rationale": "Deterministic DuckDB factor tables combined with Alpine Chrome headless DOM scraping and Meilisearch FTS."
      },
      "alternatives": [
        {"name": "OpenBB Platform Core", "repo": "OpenBB-finance/OpenBB", "license": "Apache-2.0", "score": 9.2},
        {"name": "Qlib (Microsoft)", "repo": "microsoft/qlib", "license": "MIT", "score": 8.8},
        {"name": "FinGPT / News APIs", "repo": "AI4Finance-Foundation/FinGPT", "license": "MIT", "score": 7.9}
      ]
    },
    {
      "step": 3,
      "name": "Portfolio Optimization & Risk Allocation",
      "description": "Black-Litterman view matrix algebra, Equal Risk Contribution (ERC), downside CVaR constraints",
      "primary_best_practice": {
        "name": "Riskfolio-Lib",
        "repo": "dcajasn/Riskfolio-Lib",
        "license": "BSD-3-Clause",
        "score": 9.8,
        "rationale": "Built on cvxpy. Industry gold standard for Black-Litterman (He-Litterman & Idzorek confidence mapping), Factor Risk Parity, and Maximum Drawdown / CVaR optimization."
      },
      "alternatives": [
        {"name": "PyPortfolioOpt", "repo": "PyPortfolio/PyPortfolioOpt", "license": "MIT", "score": 9.0},
        {"name": "VectorBT PRO", "repo": "polakowo/vectorbt", "license": "Apache-2.0", "score": 8.7},
        {"name": "QuantConnect / LEAN", "repo": "QuantConnect/Lean", "license": "Apache-2.0", "score": 8.4}
      ]
    },
    {
      "step": 4,
      "name": "Rebalancing Gap Analysis & Order Tickets",
      "description": "Drift tolerance bands (|Δw| > 3%), Mixed-Integer Linear Programming (MIP) lot sizing",
      "primary_best_practice": {
        "name": "PyPortfolioOpt DiscreteAllocation",
        "repo": "PyPortfolio/PyPortfolioOpt",
        "license": "MIT",
        "score": 9.5,
        "rationale": "MIP integer solver mapping continuous target weights into exact integer share lots with cash buffer management."
      },
      "alternatives": [
        {"name": "Custom IPOS Drift Band Engine", "license": "MIT", "score": 9.0},
        {"name": "Ghostfolio Order Generator", "repo": "ghostfolio/ghostfolio", "license": "AGPL-3.0", "score": 8.0},
        {"name": "VectorBT Order Simulator", "repo": "polakowo/vectorbt", "license": "Apache-2.0", "score": 8.3}
      ]
    },
    {
      "step": 5,
      "name": "Stock-Level Charting & Technical Sizing Gates",
      "description": "Candlestick charts, Chandelier Exit trailing stops, 3-gate CRV (Reward-to-Risk >= 2.5:1) screener",
      "primary_best_practice": {
        "name": "TradingView Lightweight Charts + Pandas-TA",
        "repo": "tradingview/lightweight-charts",
        "license": "Apache-2.0 / MIT",
        "score": 9.8,
        "rationale": "Ultra-fast 60 FPS HTML5 Canvas charting with overlay lines (Entry/Stop/Target) + Pandas-TA for Chuck LeBeau Chandelier Exits and ATR stops."
      },
      "alternatives": [
        {"name": "TA-Lib + mplfinance", "repo": "TA-Lib/ta-lib-python", "license": "BSD", "score": 9.1},
        {"name": "Plotly Candlesticks + SciPy", "repo": "plotly/plotly.py", "license": "MIT", "score": 8.4},
        {"name": "Finviz / Yahoo Scrapers", "license": "Various", "score": 7.0}
      ]
    },
    {
      "step": 6,
      "name": "Visual Dashboard & Reporting",
      "description": "Interactive telemetry, BI-as-Code, portfolio gap visualization, static archivable reports",
      "primary_best_practice": {
        "name": "Evidence.dev + OpenBB Workspace",
        "repo": "evidence-dev/evidence",
        "license": "MIT / Apache-2.0",
        "score": 9.6,
        "rationale": "BI-as-Code connecting directly to DuckDB via SQL inside Markdown to generate static reactive data apps with zero server overhead."
      },
      "alternatives": [
        {"name": "Tremor + shadcn/ui (Next.js)", "repo": "tremorlabs/tremor", "license": "Apache-2.0", "score": 9.2},
        {"name": "Ghostfolio Web UI", "repo": "ghostfolio/ghostfolio", "license": "AGPL-3.0", "score": 8.6},
        {"name": "Apache Superset / Streamlit", "repo": "apache/superset", "license": "Apache-2.0", "score": 8.0}
      ]
    },
    {
      "step": 7,
      "name": "Autonomous Multi-Agent Orchestration",
      "description": "Sandboxed cron scheduling, event-driven reconciliation, Slack/Telegram briefings",
      "primary_best_practice": {
        "name": "OpenClaw + LangGraph",
        "repo": "openclaw/openclaw",
        "license": "MIT",
        "score": 9.5,
        "rationale": "Sandboxed task execution with strict default-deny policy, coupled with LangGraph state graphs for human-in-the-loop trade approval."
      },
      "alternatives": [
        {"name": "OpenBB AI Agents", "repo": "OpenBB-finance/openbb-ai", "license": "Apache-2.0", "score": 9.0},
        {"name": "ai-hedge-fund (LangGraph)", "repo": "virattt/ai-hedge-fund", "license": "MIT", "score": 8.7},
        {"name": "APScheduler / GitHub Actions", "license": "MIT", "score": 8.1}
      ]
    }
  ]
}
```

---

## 3. The Winning Target Architecture (The Institutional Python-Native Quant Stack)

```
[1. User Portfolio] ─── (ibflex / CSV Inbox) ────────► Current Holdings ($1M: SPY 35%, QQQ 25%, TLT 18%, Cash 12%)
                                                                │
[2. Macro Signals]  ─── (IPOS DuckDB + Karakeep)   ────► Stance: Growth +0.40, Equities -0.15, Duration -0.36
                                                         Regime: UNCERTAIN (0.4x Risk Scaler)
                                                                │
[3. Optimization]   ─── (Riskfolio-Lib + cvxpy)    ────► Optimal Target Weights (SPY 30%, QQQ 18%, TLT 10%, Cash 30%)
                                                                │
[4. Rebalancing]    ─── (PyPortfolioOpt MIP)       ────► Discrete Orders: SELL $50k SPY, SELL $70k QQQ, BUY $180k T-Bills
                                                                │
[5. Stock Screener] ─── (Pandas-TA + TV LWC)       ────► Candidate Stocks (JPM, NVDA, PLTR):
                                                         • JPM: Approved (CRV 3.2:1, Entry $218, Stop $204)
                                                         • NVDA: Wait for pullback ($118 Support)
                                                         • PLTR: Gated by Red-Flag Contradiction Rule
                                                                │
[6. Visual Output]  ─── (Evidence.dev + DuckDB)    ────► Interactive Institutional Execution Dashboard
```

---

## 4. Architectural Rules for AI Agents

1. **Deterministic Separation**: The quantitative pipeline computes all numbers (weights, orders, ATR stops, CRV ratios) using compiled numerical packages (`Riskfolio-Lib`, `PyPortfolioOpt`, `Pandas-TA`, `DuckDB`).
2. **LLM Narration Only**: The AI model consumes the JSON output emitted by Step 4 and Step 5 to draft executive briefings, explain contradictions, and summarize macro posture without calculating numbers.
3. **Zero Server Bloat**: The system executes locally via embedded DuckDB and static HTML canvas/Evidence.dev reports, requiring zero cloud database infrastructure.
