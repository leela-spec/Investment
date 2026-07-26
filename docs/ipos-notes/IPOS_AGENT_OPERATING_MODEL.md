# IPOS_AGENT_OPERATING_MODEL.md

## Objective

Define a comprehensive operating model for the **Investment & Research OS (IPOS)** project. IPOS provides a private research environment for building playbooks, extracting indicators and analysing sensitive financial documents. This model addresses the project’s mission, trust boundary, sensitivity profile, core workflows, interaction patterns, tool and channel matrices, automation candidates, guardrails, model policy, knowledge structure and runbook patch implications. The aim is to ensure secure, repeatable research operations while enabling collaboration where appropriate.

## Inputs used

- **OpenClaw Project IPOS.md** – runbook detailing provisioning and operation of the IPOS research environment; includes tool configuration, workspace organisation and automation suggestions.
    
- **Status.md** – interim report mentioning a forthcoming IPOS blueprint and describing existing extraction and reconciliation pipelines.
    
- **General best‑practices document**, **Channel Decision Memo**, **Guardrail Architecture**, **Model Routing Policy**, **Tool and Skill Architecture**, **Automation Policy Baseline** – Stage 1 documents providing baseline guidance.
    
- **Assumption Register** – includes assumptions on trust boundaries, Tailscale usage and model tiers.
    

## Assumptions

1. The IPOS environment runs on a dedicated VPS accessible only via Tailscale Serve or SSH tunnel (A2). One project equals one agent and workspace, but multiple analysts may interact with the agent via approved channels (A3).
    
2. The IPOS blueprint is not yet available. The current model relies on existing runbooks and will be updated when the blueprint arrives.
    
3. The default model tier is Frontier (e.g., GPT‑5 Mini) because research tasks are complex and high‑stakes; mid‑tier models are used for routine summarisation.
    
4. The project uses Slack for team collaboration and Telegram for personal interactions, as specified in the Channel Decision Memo. All messaging interactions require pairing or allowlists.
    

## Main analysis

### Mission

IPOS serves as a **private investment and research operating system**. Its mission is to enable analysts to ingest, process and analyse financial documents (e.g., PDFs, JSON files, market reports), build and update playbooks, extract indicators, run reconciliation workflows and generate reports. The environment must protect sensitive data (e.g., proprietary indicators, research insights) while facilitating collaboration within the trusted team.

### Trust boundary

The server is a single tenant environment: one VPS with one `openclaw` user. However, multiple trusted users (analysts) may interact with the agent via messaging channels and the Control UI. The trust boundary includes these analysts; no unpaired users or external groups are allowed. Each analyst is paired individually and assigned roles (viewer, editor). Team collaboration occurs within Slack channels, not public forums.

### Sensitivity profile

High sensitivity: IPOS handles confidential research documents, proprietary trading strategies, indicator extraction routines and possibly personal data (e.g., client information). Any breach could have financial and legal consequences. Therefore, data must remain private, and external exposure must be strictly controlled. Only trusted analysts with the need to know may access the environment.

### Core workflows

1. **Data ingestion**: Analysts upload research papers, PDFs and CSV/JSON files into the workspace (`playbooks/`, `indicators/`); they use `read_file` and `write_file` to manage content. Use `api_tool` to fetch documents from GitHub or other internal sources.
    
2. **Indicator extraction**: Run scripts or agent tasks that parse documents and extract indicators into JSONL files. Use `cron.schedule` to automate weekly or daily extractions. The extraction logic resides in the workspace (scripts or skills) and uses allowed tools (`read`, `write`, `edit`, `search`, `browser` if necessary).
    
3. **Playbook generation and updates**: Assemble extracted indicators and market data into structured playbooks (Markdown or JSON). Use the agent to summarise research, compile rules and update playbook files. Use GitHub to manage versioning (read‑only or read‑write with approval).
    
4. **Research summarisation**: Generate summary reports of the latest market conditions or research findings. These may be delivered to analysts via Slack or stored in `reports/`.
    
5. **Reconciliation workflows**: Compare extracted indicators with previously stored values to detect discrepancies. Write results into logs or update indicator files. Use cron for periodic reconciliation.
    
6. **Collaboration and feedback**: Use Slack channels (e.g., `#ipos-requests`, `#ipos-updates`) for team requests and notifications. Analysts issue tasks to the agent (e.g., “extract indicators from document X”) and receive outputs or notifications.
    
7. **Maintenance and audits**: Perform monthly updates, snapshots and security audits; rotate API keys; monitor resource usage.
    

### User interaction patterns

- **Personal interactions**: Analysts can interact with the agent via Telegram DM for private tasks or commands. DM pairing is required; only pre‑approved analysts can use the bot.
    
- **Team collaboration**: The agent is integrated with Slack. Analysts communicate through `#ipos-requests` (requests) and `#ipos-updates` (results). The bot responds only when mentioned and uses allowlists to restrict accepted users. It posts summaries and notifications as messages. No direct messages are accepted.
    
- **Admin/debug**: Control UI via Tailscale Serve is used for configuration, logs and manual triggers. Only admin users access it. SSH via Tailscale is a fallback for emergency tasks.
    
- **No public channels or group chats**: Discord and WhatsApp are not used. Signal may be considered for ultra‑sensitive tasks but is not enabled initially.
    

### Tool matrix

|Tool|Status|Notes|
|---|---|---|
|read_file, write_file, edit_file|Enabled (with confirmation)|Required for ingesting and updating research documents. Confirm before overwriting.|
|search, memory_search|Enabled|Needed to retrieve context and locate information in files and memory.|
|api_tool (GitHub, internal connectors)|Enabled (read‑only)|Access internal repositories for playbooks or indicator definitions; can be enabled for write with approval. Use least‑privilege tokens.|
|browser.search, browser.open|Enabled (sandboxed)|Research often requires web searches; the tool runs in a sandbox without executing scripts. Confirm before opening untrusted domains and summarise content before using it.|
|cron.schedule|Enabled|Essential for scheduled extractions, reconciliations and summary generation. Each job must define triggers, inputs, outputs, approvals and rollback, per the Automation Policy Baseline.|
|email.send|Conditional|May send reports via email to analysts; always require approval and preview; can be integrated via Slack message instead.|
|system.run, elevated|Denied|Shell access is not allowed. Write extraction scripts as part of skills or tasks rather than executing arbitrary commands.|
|Third‑party skills|Conditional|Only vetted skills are allowed (document summariser, gap updater, assumption checker, task classifier, schedule manager, research fetcher, report generator). Domain‑specific skills (e.g., PDF parser, indicator extractor) must undergo code review.|
|analytics connectors (e.g., Bloomberg API)|Conditional|If needed, integrate via `api_tool` connectors; require explicit approval and secret management.|

### Channel matrix

|Channel|Purpose|Restrictions|
|---|---|---|
|**Telegram DM**|Personal commands or research tasks; used by individual analysts.|Pairing required; only approved analysts can send commands.|
|**Slack (#ipos-requests)**|Team requests to the agent. Analysts mention `@OpenClaw` to trigger tasks.|Membership restricted to trusted analysts; mentions required; no direct messages.|
|**Slack (#ipos-updates)**|Channel for posting results, reports and notifications.|Read‑only for analysts; only the bot posts updates.|
|**Control UI (Tailscale Serve)**|Configuration, logs, job management.|Accessible only to admin users via tailnet.|
|**SSH (Tailscale)**|Emergency or manual maintenance.|Use only when necessary; restrict to admin.|
|**No WhatsApp/Discord**|Not used. Signal considered only for highly sensitive tasks; not enabled initially.||

### Automation candidates

IPOS relies heavily on automation to process data and generate reports. All automations follow the baseline policy:

1. **Weekly extraction routine** – A cron job runs a script to parse new research PDFs or JSON files, extract indicators and append them to `indicators.jsonl`. It triggers on a weekly schedule (e.g., Monday 04:00 UTC). Inputs: new files. Tools: `read`, `write`, `edit`, `search`. The job produces a summary file and stores logs. Runs in draft mode; analysts review indicator changes in Slack.
    
2. **Reconciliation job** – A weekly job compares indicators extracted this week with previous values, flags discrepancies and writes results to `reports/reconciliation-YYYY-WW.md`. Runs in draft mode; analysts review before updates.
    
3. **Market summary** – A daily or weekly automation that uses `browser.search` to fetch market news or data (subject to sandbox restrictions), summarises using the agent and posts a report to Slack `#ipos-updates`. Requires approval before posting.
    
4. **Monthly playbook refresh** – A cron job generates new versions of playbooks based on updated indicators and research. It writes to `playbooks/` and posts a summary. Requires approval before merging with the main branch in GitHub.
    
5. **Maintenance alert** – A weekly job runs `openclaw doctor` and `openclaw security audit` and notifies the admin if issues are found.
    

Each automation must define triggers, inputs, agent, model tier, tools, approvals, output location, failure mode, rollback and logging, as prescribed by the Automation Policy Baseline.

### Guardrails

IPOS inherits baseline guardrails with the following project‑specific adjustments:

- **Network/exposure**: Gateway bound to localhost; accessible via tailnet only; Tailscale Serve provides HTTPS. Slack uses outbound connections; inbound connections are not required.
    
- **Access control**: Use pairing and allowlists for Telegram and Slack; require mentions in Slack channels. Use strong tokens for Control UI. Analysts have role‑based access (viewer vs editor). Public channels are disabled.
    
- **Session isolation**: Dedicated workspace for IPOS; separate from other projects. If multiple agents are created (e.g., extraction agent, analysis agent), each has its own workspace and memory files.
    
- **Tool policy**: Enable browser tools only in sandbox; restrict system.run and elevated tools. Limit GitHub operations to read-only unless specifically approved. Manage connectors via `api_tool`. Provide sandbox for any custom extraction scripts.
    
- **Sandboxing**: All tasks run inside non‑privileged containers with read‑only filesystems except the workspace. The browser tool cannot execute scripts or download files outside the allowed domain list.
    
- **Prompt/behaviour**: SOUL.md emphasises research ethics, confidentiality, and compliance. AGENTS.md instructs the agent to ask for confirmation before sending data externally (e.g., Slack messages or emails). Include injection awareness; summarise external content before acting..
    
- **Operations/audit**: Run weekly and monthly security audits and updates. Maintain logs of all automations, model calls and external communications. Keep snapshots and prepare rollback plans. Conduct periodic adversarial reviews to detect prompt injection or data leakage.
    

### Model policy

- **Default model**: Frontier tier (e.g., GPT‑5 Mini) because research tasks often require complex reasoning, multi‑document synthesis and high accuracy. Use Mid‑tier models (e.g., GPT‑4 Turbo) for routine extraction and summarisation tasks. Use Fast models for simple classification or formatting tasks. Escalation triggers follow the Model Routing Policy: high ambiguity, complex reasoning, multi‑document synthesis, or high‑risk actions.
    
- **Budget management**: IPOS has a larger budget than other projects but still requires cost controls. Set monthly budget thresholds; alert at 80 % usage; adjust triggers or batch tasks to reduce cost. Use caching of summarisation results where possible.
    
- **Fallback chain**: Frontier → Mid‑tier → Fast → manual. If a higher‑tier model fails, fallback to the next tier and notify analysts.
    

### Knowledge structure

- **Bootstrap files**: SOUL.md defines mission and compliance requirements; AGENTS.md defines rules (e.g., ask for approval before posting results to Slack; confirm before updating playbooks); USER.md captures preferences (e.g., preferred report format); TOOLS.md lists allowed and denied tools; MODEL_POLICY.md summarises model routing policy.
    
- **Workspace structure**: `playbooks/` for structured documents; `indicators/` for JSONL indicator files; `rules/` for trading rules; `process/` for scripts and extraction logic; `reports/` for summaries; `memory/` for durable instructions. Use index files to track available documents.
    
- **Retrieval index**: memory_search enabled. Ensure that important instructions (e.g., “never send data externally without approval”) are written into MEMORY.md and referenced in AGENTS.md.
    

### Runbook patch implications

Update the IPOS runbook to reflect this operating model:

1. **Tool configuration**: Confirm that `config.yaml` allows `browser` but only in sandbox; restrict `api_tool` to read-only by default; deny `system.run` and elevated tools.
    
2. **Channel policy**: Document the use of Telegram DM and Slack channels. Specify channel names and mention requirements. Provide instructions on pairing users and configuring Slack tokens.
    
3. **Model policy**: Create `MODEL_POLICY.md` with default model (Frontier), fallback chain and escalation triggers. In AGENTS.md, instruct the agent to refer to this policy when selecting models.
    
4. **Automation templates**: Add sample automation manifests for extraction, reconciliation, market summary and playbook refresh. Ensure each includes triggers, inputs, approvals, rollback and logging.
    
5. **Guardrail cross‑reference**: Link to the Guardrail Architecture and summarise IPOS‑specific controls. Include risk‑trigger matrix in the runbook for typical tasks.
    
6. **Role management**: Include a section on pairing and assigning roles to analysts; provide instructions for adding or removing users via the Control UI or config files.
    
7. **Data handling**: Emphasise the high sensitivity of financial data. Provide guidance on storing secrets via `openclaw config --secret` and on encrypting sensitive files if necessary.
    

## Decision / recommendation

- **Adopt this operating model** for IPOS. It balances research capability with strong guardrails, enabling automation while preserving data privacy and integrity. It sets clear roles, channels and tools and defines rigorous automation requirements.
    
- **Update the runbook** according to the patch implications. Ensure all team members understand channel policies, tool restrictions, and approval processes.
    
- **Implement automations** in incremental steps. Start with weekly extraction and reconciliation jobs in draft mode; refine scripts and confirm outputs before enabling Slack notifications. Expand into market summary and playbook refresh once basic flows are stable.
    
- **Prepare for blueprint integration**: When the IPOS blueprint arrives, review this model and adjust workflows, tools and policies accordingly.
    

## Risks and trade‑offs

- **Complexity**: IPOS has more moving parts (Slack integration, browser searches, multiple automations) than other projects. This increases risk of misconfiguration. Mitigate by documenting all settings and using the risk‑trigger matrix.
    
- **Cost**: Frontier models are expensive; heavy research can consume budgets quickly. Use mid‑tier models where possible and monitor usage.
    
- **Data leakage**: Slack messages are not end‑to‑end encrypted. Use Slack only for operational notifications; avoid including sensitive data. Consider enabling Signal for highly confidential tasks.
    
- **Automation failure**: Cron jobs could fail or produce incorrect data. Implement robust logging, error handling and rollback. Always require human review before updating critical files.
    
- **Dependency risk**: Reliance on external APIs (e.g., market data providers) introduces dependencies. Monitor API changes and ensure fallback plans exist.
    

## Critique

This operating model anticipates the needs of a complex research environment but may still overlook specific workflows in the forthcoming IPOS blueprint. For example, if the blueprint introduces real‑time trading agents or integrates with financial platforms, additional guardrails and approvals will be necessary. The model also does not specify concurrency controls when multiple analysts request tasks simultaneously; a queuing mechanism may be needed. The use of Slack could be problematic if stricter data residency or confidentiality requirements apply. The plan to use browser search for market news must consider site licensing and API availability.

## Patch

Future iterations should:

1. **Integrate the IPOS blueprint**: When available, update the operating model to include any new workflows, data sources or compliance requirements.
    
2. **Add concurrency controls**: Define how tasks are queued or prioritised when multiple analysts interact simultaneously. Consider per‑user queues or locks.
    
3. **Evaluate Signal or Matrix**: Assess whether a more secure messaging platform is needed for highly confidential communication. If so, develop integration guidelines.
    
4. **Improve automation resilience**: Implement robust retry and backoff strategies, and integrate alerts when automations fail. Develop a dashboard in the Control UI for monitoring automation status.
    
5. **Establish training**: Provide onboarding materials for analysts to understand the risk‑trigger matrix, model policy and tool usage. Conduct periodic training to refresh knowledge.
    

## CHECKPOINT

The **IPOS Agent Operating Model** has been drafted and critiqued. It adapts the general architecture to the research environment, emphasising complex workflows, collaboration, automation and strict guardrails. Once this model and its patches are reviewed, Stage 2 is complete.