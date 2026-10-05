# TradingAgents Local Installation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Install and verify the official TradingAgents framework locally beneath the Investment workspace without mixing its source or dependencies into IPOS.

**Architecture:** The upstream repository is an independent nested Git checkout at `external/TradingAgents`, explicitly ignored by the parent repository. It owns a Python 3.13 `.venv` created by `uv`; IPOS's existing `.venv` remains untouched.

**Tech Stack:** Git, PowerShell, uv 0.12+, CPython 3.13, TauricResearch/TradingAgents

## Global Constraints

- Install at exactly `C:\GitDev\Investment\external\TradingAgents`.
- Use a private virtual environment at exactly `C:\GitDev\Investment\external\TradingAgents\.venv`.
- Do not add API keys or secret values.
- Do not execute a market analysis or contact an LLM provider.
- Do not alter IPOS runtime dependencies.

---

### Task 1: Protect the parent repository

**Files:**
- Modify: `.gitignore`

**Interfaces:**
- Consumes: The Investment repository's existing ignore rules.
- Produces: A parent-repository exclusion for `/external/TradingAgents/`.

- [ ] **Step 1: Verify the target is not already ignored**

Run from `C:\GitDev\Investment`:

```powershell
git check-ignore -v external/TradingAgents
```

Expected: no output and exit code 1.

- [ ] **Step 2: Add the narrow ignore rule**

Append this section to `.gitignore` without changing existing rules:

```gitignore

# --- locally installed third-party applications ---
/external/TradingAgents/
```

- [ ] **Step 3: Verify the rule and formatting**

```powershell
git check-ignore -v external/TradingAgents/example
git diff --check -- .gitignore
```

Expected: the first command identifies `.gitignore` and the new rule; the second emits no errors.

- [ ] **Step 4: Commit the repository rule**

```powershell
git add -- .gitignore
git commit -m "chore: ignore local TradingAgents installation" -- .gitignore
```

Expected: a commit containing only `.gitignore`.

### Task 2: Clone and install TradingAgents

**Files:**
- Create locally, ignored by parent Git: `external/TradingAgents/`
- Create locally, ignored by parent Git: `external/TradingAgents/.venv/`

**Interfaces:**
- Consumes: Official repository `https://github.com/TauricResearch/TradingAgents.git` and `uv`.
- Produces: The `tradingagents` Python package and `tradingagents` CLI inside the private environment.

- [ ] **Step 1: Confirm the destination is absent**

```powershell
Test-Path 'C:\GitDev\Investment\external\TradingAgents'
```

Expected: `False`. If it is `True`, inspect it and stop rather than overwrite it.

- [ ] **Step 2: Clone the official repository**

```powershell
git clone https://github.com/TauricResearch/TradingAgents.git 'C:\GitDev\Investment\external\TradingAgents'
```

Expected: a successful checkout whose `origin` is the official repository.

- [ ] **Step 3: Create the private environment**

Run from `C:\GitDev\Investment\external\TradingAgents`:

```powershell
uv venv --python 3.13 .venv
```

Expected: `.venv\Scripts\python.exe` exists and reports Python 3.13.

- [ ] **Step 4: Install the upstream package**

```powershell
uv pip install --python '.venv\Scripts\python.exe' .
```

Expected: dependency resolution and installation complete successfully.

### Task 3: Verify the installation without running an analysis

**Files:**
- Read only: `external/TradingAgents/.git/config`
- Execute locally: `external/TradingAgents/.venv/Scripts/python.exe`
- Execute locally: `external/TradingAgents/.venv/Scripts/tradingagents.exe`

**Interfaces:**
- Consumes: The checkout and environment produced by Task 2.
- Produces: Evidence that the source, interpreter, import, CLI, and parent ignore boundary are correct.

- [ ] **Step 1: Verify source and interpreter**

```powershell
git -C 'C:\GitDev\Investment\external\TradingAgents' remote get-url origin
& 'C:\GitDev\Investment\external\TradingAgents\.venv\Scripts\python.exe' --version
```

Expected: the official TauricResearch URL and Python 3.13.x.

- [ ] **Step 2: Verify the package import**

```powershell
& 'C:\GitDev\Investment\external\TradingAgents\.venv\Scripts\python.exe' -c "import tradingagents; print(tradingagents.__file__)"
```

Expected: a module path inside `external\TradingAgents`.

- [ ] **Step 3: Verify CLI startup**

```powershell
& 'C:\GitDev\Investment\external\TradingAgents\.venv\Scripts\tradingagents.exe' --help
```

Expected: help text and exit code 0, with no market analysis started.

- [ ] **Step 4: Verify parent Git isolation**

Run from `C:\GitDev\Investment`:

```powershell
git check-ignore -v external/TradingAgents/README.md
git status --short -- .gitignore external/TradingAgents
```

Expected: the checkout is matched by `.gitignore`; the status command reports no untracked TradingAgents content.
