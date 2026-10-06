Here’s a focused, value‑ranked shortlist of **existing, downloadable, open‑source skills / scripts / frameworks** that best cover your four tasks:

1. Analyse transcripts & research
2. Map signals into an existing market analysis
3. Create deltas to that market analysis
4. Transform deltas into portfolio decisions

Ranking is by **coverage of all four steps + maturity + documentation + ease of reuse on Windows**.

---

## Top tier (highest value for your exact workflow)

### 1) **FinRobot** – `AI4Finance-Foundation/FinRobot`

**Type:** Multi‑agent platform (Python)  
**Repo:** [https://github.com/AI4Finance-Foundation/FinRobot](https://github.com/AI4Finance-Foundation/FinRobot)[[arxiv](https://arxiv.org/html/2405.14767v2)][[ar5iv.labs.arxiv](https://ar5iv.labs.arxiv.org/html/2405.14767)][[github](https://github.com/arkink1/finrobot)][[github](https://github.com/LLMQuant/awesome-trading-agents)]

**Why it’s #1:**

- Explicitly designed for **financial research automation + portfolio construction**.
- Includes **research pipelines** (company research, earnings, DCF, comps, IC memo) and **portfolio/trading agents**.[[github](https://github.com/arkink1/finrobot)]
- Combines LLM agents with **quant/RL components** (FinRL lineage) for **portfolio allocation and risk**.[[ar5iv.labs.arxiv](https://ar5iv.labs.arxiv.org/html/2405.14767)][[github](https://github.com/arkink1/finrobot)]
- Open‑source, actively maintained, and documented as a full **agent platform**, not just a script.[[arxiv](https://arxiv.org/html/2405.14767v2)][[ar5iv.labs.arxiv](https://ar5iv.labs.arxiv.org/html/2405.14767)]

**Coverage of your steps:**

- (1) Earnings/filings/research analysis via dedicated analyst agents.
- (2–3) Research → signals → reports that can be mapped to your market view (you can plug your own schema).
- (4) Portfolio construction/trading agents and RL‑based allocation.[[ar5iv.labs.arxiv](https://ar5iv.labs.arxiv.org/html/2405.14767)][[github](https://github.com/arkink1/finrobot)]

**Best if:** You want a **single repo** that already implements most of the pipeline and you’re comfortable running Python agents locally.

---

### 2) **TradingAgents** – `TauricResearch/TradingAgents`

**Type:** Multi‑agent trading framework (LangGraph)  
**Mentioned in:** `LLMQuant/awesome-trading-agents` as a top agent framework.[[github](https://github.com/LLMQuant/awesome-trading-agents)]

**Why it’s high value:**

- Multi‑agent setup with **analysts, bull/bear researchers, trader, risk control, portfolio manager** that **debate before deciding**.[[github](https://github.com/LLMQuant/awesome-trading-agents)]
- Directly matches your desired flow: research → debate → risk check → portfolio decision.
- Built on **LangGraph**, so you can extend it with your own market‑view and delta logic.

**Coverage:**

- (1) Analyst agents process research and fundamentals.
- (2–3) Bull/bear debate + risk control effectively create **deltas to a base view**.
- (4) Portfolio manager agent turns the debated view into allocation/trade decisions.[[github](https://github.com/LLMQuant/awesome-trading-agents)]

**Best if:** You like the **debate‑style decision process** and want a clean multi‑agent architecture to build on.

---

### 3) **claude‑trading‑skills** – `tradermonty/claude-trading-skills`

**Type:** Skill pack for Claude Code / Claude (many small reusable skills + workflows)  
**Repo:** [https://github.com/tradermonty/claude-trading-skills](https://github.com/tradermonty/claude-trading-skills)[[raw.githubusercontent](https://raw.githubusercontent.com/LLMQuant/awesome-trading-agents/refs/heads/master/README.md)][[github](https://github.com/tradermonty/claude-trading-skills/blob/main/README.md)]

**Why it’s valuable:**

- Very large, well‑structured set of **production‑ready skills** for:
    
    - Market regime & breadth analysis
    - Portfolio review & rebalancing (`portfolio-manager`)
    - Earnings analysis, screeners, trade planning, and **trade memory** (journaling + postmortems).[[github](https://github.com/tradermonty/claude-trading-skills/blob/main/README.md)]
- Includes **workflows** that chain skills into repeatable processes (daily market check, weekly portfolio review, performance review).[[github](https://github.com/tradermonty/claude-trading-skills/blob/main/README.md)]
- Strong emphasis on **risk gates, drawdown circuit breakers, and disciplined process** – ideal for mapping research → decisions.[[github](https://github.com/tradermonty/claude-trading-skills/blob/main/README.md)]

**Coverage:**

- (1) Earnings & research skills (`earnings-calendar`, `earnings-trade-analyzer`, `us-stock-analysis`, etc.).
- (2–3) Market regime + scenario analysis + memory skills let you create **deltas and track thesis changes**.
- (4) `portfolio-manager` + position sizing + rebalancing recommendations map views to **portfolio actions** (via Alpaca MCP or manual).[[github](https://github.com/tradermonty/claude-trading-skills/blob/main/README.md)]

**Best if:** You use **Claude Code / Claude** and want a **library of small, composable skills** plus documented workflows instead of one monolithic framework.

---

### 4) **finance‑skills** – `himself65/finance-skills`

**Type:** Skill pack (Agent Skills standard) for multiple agents  
**Repo:** [https://github.com/himself65/finance-skills](https://github.com/himself65/finance-skills)[[github](https://github.com/LLMQuant/awesome-trading-agents)][[raw.githubusercontent](https://raw.githubusercontent.com/LLMQuant/awesome-trading-agents/refs/heads/master/README.md)][[github](https://github.com/himself65/finance-skills)]

**Why it’s valuable:**

- Focused on **financial analysis skills**: valuation, earnings preview/recap, estimate analysis, SaaS compression, correlation, liquidity, etc.[[github](https://github.com/himself65/finance-skills)]
- Clean separation into plugin groups (market analysis, social readers, data providers).
- Easy to install via `npx skills add` into supported agents.[[github](https://github.com/himself65/finance-skills)]

**Coverage:**

- (1) Very strong on **company/earnings analysis** and structured valuation outputs.
- (2–3) Less explicit on market‑view deltas, but you can combine with your own schema.
- (4) No built‑in portfolio optimisation; you’d pair with a separate portfolio tool or custom script.[[github](https://github.com/himself65/finance-skills)]

**Best if:** You want **high‑quality, reusable analysis skills** and are fine building the “market view → portfolio” glue yourself.

---

## Second tier (strong pieces, more assembly required)

### 5) **FinCon** – `The-FinAI/FinCon`

**Type:** Multi‑agent LLM framework for financial tasks (paper + code)  
**Paper:** “FinCon: A Synthesized LLM Multi-Agent System with …”[[arxiv](https://arxiv.org/html/2407.06567v3)]

**Value:**

- Designed for **single‑stock trading and portfolio management** with conceptual verbal reinforcement.
- Good reference architecture if you want to **design your own agents** based on proven patterns.[[arxiv](https://arxiv.org/html/2407.06567v3)]

**Coverage:** Strong on (1) and (4), moderate on (2–3) unless you extend it.

---

### 6) **MASS** – `gta0804/MASS`

**Type:** Multi‑agent simulation for **end‑to‑end portfolio construction**  
**Paper + code:** [https://github.com/gta0804/MASS](https://github.com/gta0804/MASS)[[arxiv](https://arxiv.org/html/2505.10278v2)]

**Value:**

- Frames portfolio construction as **dynamic online learning** with multi‑agent simulation.
- Useful if you care most about **step 4** and want a research‑grade approach.[[arxiv](https://arxiv.org/html/2505.10278v2)]

**Coverage:** Strong on (4), weaker on transcript/research parsing (1) and market‑view mapping (2–3).

---

### 7) **awesome‑trading‑agents** – `LLMQuant/awesome-trading-agents`

**Type:** Curated list (not a framework itself)  
**Repo:** [https://github.com/LLMQuant/awesome-trading-agents](https://github.com/LLMQuant/awesome-trading-agents)[[github](https://github.com/LLMQuant/awesome-trading-agents)][[raw.githubusercontent](https://raw.githubusercontent.com/LLMQuant/awesome-trading-agents/refs/heads/master/README.md)]

**Value:**

- Best **“database of AI skills”** for your use case: agents, MCP servers, and skill packs.
- Use it to **discover more specialized skills** (e.g., earnings Q&A agents, backtesting agents, portfolio MCPs).[[github](https://github.com/LLMQuant/awesome-trading-agents)]

**Coverage:** Not a solution by itself, but the best **index** to extend your stack.

---

## Practical recommendation (minimal stack to cover all 4 steps)

If you want a concrete, open‑source starting point on Windows:

1. **Core engine:**
    
    - Use **FinRobot** or **TradingAgents** as your **multi‑agent backbone** (covers 1–4 at a high level).[[arxiv](https://arxiv.org/html/2405.14767v2)][[ar5iv.labs.arxiv](https://ar5iv.labs.arxiv.org/html/2405.14767)][[github](https://github.com/arkink1/finrobot)][[github](https://github.com/LLMQuant/awesome-trading-agents)]
2. **Skill layer for deep analysis:**
    
    - Add **finance‑skills** and/or **claude‑trading‑skills** for **structured earnings/filings analysis, valuation, and portfolio review**.[[github](https://github.com/tradermonty/claude-trading-skills/blob/main/README.md)][[github](https://github.com/himself65/finance-skills)]
3. **Your market‑view & delta logic:**
    
    - Implement a simple schema (Markdown/JSON) for your market analysis and deltas.
    - Wire agent outputs into this schema via small Python/PowerShell scripts.
4. **Portfolio decisions:**
    
    - Use the portfolio agents in **FinRobot/TradingAgents**, or
    - Use `portfolio-manager` + position sizing skills from **claude‑trading‑skills** with a broker MCP (e.g., Alpaca) or manual CSV workflow.[[github](https://github.com/tradermonty/claude-trading-skills/blob/main/README.md)]

---

If you tell me:

- whether you prefer **Python frameworks** (FinRobot/TradingAgents) or **Claude Code skills** (claude‑trading‑skills/finance‑skills), and
- whether you need **live trading** or just **research + paper portfolio**,

I can narrow this to a 2–3 repo “starter pack” with exact install steps for Windows.