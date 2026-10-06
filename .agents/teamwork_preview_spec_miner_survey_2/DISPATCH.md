## 2026-09-28T08:40:45Z

You are the Consolidated Stack Spec Miner for the IPOS project.
Working directory: c:\GitDev\Investment\.agents\teamwork_preview_spec_miner_survey_2
Identity: Spec Miner surveying World 2 (Ratified WSL2-Native Consolidated Architecture).

MANDATORY INSTRUCTION: You MUST read the original user request at:
c:\GitDev\Investment\.agents\ORIGINAL_REQUEST.md
before starting your analysis. Do NOT skip reading this file.

OBJECTIVE:
Thoroughly inspect and extract all architectural decisions, network topologies, database boundaries, port allocations, and persistence layouts from the ratified WSL2-native consolidated architecture specification directory:
`c:\GitDev\apexai-os-meta\apex-meta\orchestration\architecture-improvements\03-wsl2-native-stack-consolidation\`

INPUT SOURCES:
- c:\GitDev\Investment\.agents\ORIGINAL_REQUEST.md
- All files in `c:\GitDev\apexai-os-meta\apex-meta\orchestration\architecture-improvements\03-wsl2-native-stack-consolidation\` (including plan, decisions, architecture docs, compose templates, handovers, etc.)
- c:\GitDev\Investment\HANDOVER_INFRASTRUCTURE_ARCHITECTURE.okf.md

SCOPE BOUNDARIES:
- Read-only exploration and specification mining! DO NOT write, edit, or delete any source code, tests, or documentation outside your working directory.
- Write only to your working directory: c:\GitDev\Investment\.agents\teamwork_preview_spec_miner_survey_2/

SPECIFIC INVESTIGATION ITEMS:
1. Ratified decisions inventory: Enumerate and summarize all ratified architectural decisions (D-01 through D-18), specifically their impact on IPOS.
2. Unified network and port matrix:
   - Complete mapping of host ports vs container ports vs container internal networks (shared Docker network e.g. `172.20.0.0/16`).
   - Host runtime ports (127.0.0.1): 8084 (Karakeep), 8086 (Activepieces), 8010 (OpenProject private), 8642 (Hermes MCP/API), 3000 (OpenProject community/Grafana/web), etc.
   - Protocols (HTTP, TCP, UNIX sockets), loopback binding rules, edge gateway rules (Caddy/Nginx).
   - Ensure zero port conflicts with existing Apex containers.
3. Database isolation and security matrix:
   - PostgreSQL cluster `ki-basis-shared-postgres` configuration.
   - Database names: `priv_openproject` (38 work packages), `comm_openproject` (56 work packages), and any IPOS-specific database/schemas.
   - Strict role isolation: users, passwords/auth mechanisms, search paths, and explicit `REVOKE CONNECT ON DATABASE ... FROM PUBLIC` rules to guarantee zero cross-tenant contamination.
4. Persistence and filesystem boundaries:
   - Windows host NTFS (`C:\GitDev\Investment`) vs WSL2 ext4 (`/var/lib/docker/volumes/`).
   - 9P cross-filesystem avoidance: what runs on Windows NTFS (Python numerical compute, git repository, local caches), what runs on WSL2 ext4 (Docker container engines, PostgreSQL databases, Karakeep asset storage).
   - Exact volume names, mounts, and fail-closed append-only receipts.
5. Hermes Agent container wiring:
   - Container configuration, MCP server endpoints, profile management (`investment` profile), how it connects to local files / APIs without compromising host sovereignty.
6. Guardrails for live data protection:
   - Specific commands and policies to prevent clobbering OpenProject 17.8 tables, Karakeep evidence, or Smartbroker ledgers.

OUTPUT DELIVERABLE:
Write a comprehensive, evidence-backed specification mining report to:
`c:\GitDev\Investment\.agents\teamwork_preview_spec_miner_survey_2\survey_world2_report.md`
and write your self-contained `c:\GitDev\Investment\.agents\teamwork_preview_spec_miner_survey_2\handoff.md` with:
- Observation (exact decisions, tables, configs, port numbers)
- Logic Chain (how WSL2 native stack maps to IPOS requirements)
- Caveats (potential friction points, 9P bottlenecks)
- Conclusion (verified architectural parameters for M1 & M2)
- Verification Method

Notify the parent orchestrator via send_message when complete.

## 2026-09-28T08:44:24Z

**Context**: World 2 Survey & WSL2 Consolidated Architecture
**Content**: Critical operator guidance received. (1) Anti-overengineering mandate: no speculative desktop GUI in Docker, no 9P cross-mount DBs causing file-lock corruption/latency. (2) Strict technical realities: Pure Python IPOS runs on Windows 11 Python (.venv); background containers (Karakeep, Activepieces, Hermes) run in WSL2 "Apex" Docker engine; Wealthfolio runs as Windows desktop Electron/Tauri app (%APPDATA%\com.teymz.wealthfolio); TradingView Pro is Cloud via CSV exports & inbound webhooks. (3) Structure findings around concrete User Stories with exact execution environments, host/container port mappings, and database role isolation.
**Action**: Incorporate these technical realities and user story decomposition into your survey_world2_report.md and handoff.md.
