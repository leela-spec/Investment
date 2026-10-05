# TradingAgents Local Installation Design

## Goal

Install TauricResearch/TradingAgents locally beneath the Investment workspace so it is easy to find and run without mixing its source code or Python dependencies into IPOS.

## Layout

TradingAgents will be cloned to:

`C:\GitDev\Investment\external\TradingAgents`

The checkout will retain its own `.git` metadata and use its own virtual environment at:

`C:\GitDev\Investment\external\TradingAgents\.venv`

## Git behavior

The parent Investment repository will ignore `/external/TradingAgents/`. The upstream checkout and its generated files will therefore remain local and will not be committed as IPOS source code.

TradingAgents remains independently updateable using Git commands executed inside its directory. A fresh clone of Investment will not automatically contain TradingAgents.

## Installation

Clone the official `https://github.com/TauricResearch/TradingAgents.git` repository. Use `uv` to create a Python 3.13 virtual environment in the checkout and install the project and its dependencies into that environment.

Do not put API keys into tracked files. Copy the upstream environment template only if configuration is needed, and leave all secret values unset for the user to supply securely.

## Verification

Installation succeeds when:

1. The checkout's Git remote points to `TauricResearch/TradingAgents`.
2. The private virtual environment uses a supported Python version.
3. `tradingagents` imports successfully from that environment.
4. The installed CLI displays its help output without executing an analysis or contacting an LLM provider.
5. The parent Investment repository reports the TradingAgents directory as ignored.

## Boundaries

This work installs and verifies the upstream framework only. It does not connect TradingAgents to IPOS, configure paid API services, execute an investment analysis, or change IPOS runtime dependencies.
