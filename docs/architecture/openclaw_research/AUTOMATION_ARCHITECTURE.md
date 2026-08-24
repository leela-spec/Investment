# IPOS_AUTOMATION_ARCHITECTURE.md

## Objective

Design a robust, scalable and secure automation architecture for the **Investment & Research OS (IPOS)** project. IPOS automations must handle complex data extraction and analysis tasks while protecting highly sensitive financial information and supporting collaboration among multiple analysts. Each automation is defined with explicit triggers, inputs, model tiers, tool usage, approval modes, outputs, failure handling, rollback procedures and risk levels, in line with the Automation Policy Baseline.

## Inputs used

- **IPOS Agent Operating Model** – outlines the mission, workflows, candidate automations and tool/channel policies for the IPOS project.
    
- **Automation Policy Baseline** – specifies the required attributes of every automation (trigger, inputs, agent, model, tools, approvals, outputs, failure mode, rollback, logging) and defines risk classes.
    
- **Automation Best Practices (Tencent Cloud)** – emphasises the five stages of a reliable workflow (trigger, collect, decide, act, observe), the importance of idempotency and backpressure, and the need for structured output and observation loops.
    
- **Cross‑project documents** – particularly the Guardrail Architecture and Model Routing Policy, which guide tool use, sandboxing, model selection and approval triggers.
    

## Assumptions

1. The IPOS environment is a dedicated VPS accessible only via Tailscale; multiple analysts interact via Slack and Telegram DM. Slack messages are considered external side effects and always require approval. Telegram DM to a single analyst also counts as an external side effect.
    
2. Extraction scripts and reconciliation logic are written as skills or scripts in the workspace; arbitrary shell access is forbidden. The `browser` tool is sandboxed and cannot execute untrusted scripts or download files.
    
3. The default model tier is Frontier (e.g., GPT‑5 Mini) for complex research tasks, with Mid‑tier used for summarisation and Fast tier for classification or formatting. Model selection follows the Model Routing Policy.
    
4. Cron scheduling is available via `cron.schedule` and supports standard cron expressions; each job must be idempotent and produce structured logs.
    

## Automation inventory

|ID|Automation name|Trigger|Inputs|Tools|Model tier|Approval mode|Output|Failure mode|Rollback|Risk level|
|---|---|---|---|---|---|---|---|---|---|---|
|IPOS‑A1|**Weekly indicator extraction**|`0 4 * * 1` (Monday at 04:00 UTC)|New research documents in `playbooks/` and `indicators/`; extraction scripts in `process/`|`read_file`, `search`, `edit_file`, `write_file`, `cron.schedule`|Mid‑tier (extraction) + Frontier (summarisation)|**Draft** – generate and store new indicators; analysts review before publication|A JSONL file `indicators/extracted-YYYY-WW.jsonl` containing parsed indicators and a summary report `reports/extraction-summary-YYYY-WW.md`|If parsing fails, log error and skip; retry once. If summarisation fails, fall back to Mid‑tier model.|Retain previous `indicators.jsonl`; do not overwrite. If results are incorrect, restore from backup and re‑run after fixing script.|High|
|IPOS‑A2|**Weekly reconciliation job**|`0 5 * * 1` (Monday at 05:00 UTC)|Current and previous indicator files (`indicators/`); reconciliation script|`read_file`, `write_file`, `edit_file`|Fast (diffing) + Mid‑tier (analysis)|**Draft** – produce a reconciliation report; analysts review before updating indicators|A report `reports/reconciliation-YYYY-WW.md` highlighting discrepancies and recommendations|If diffing fails, log error; skip update; notify analysts via Slack.|The job does not modify data automatically; rollback involves discarding the report.|Medium|
|IPOS‑A3|**Daily market summary**|`30 7 * * *` (07:30 UTC daily)|Market news via `browser.search` (predefined sources), previous summary files|`browser.search`, `read_file`, `write_file`|Frontier (news summarisation)|**Ask before action** – compile summary and ask before posting to Slack|A Markdown report `reports/market-summary-YYYY-MM-DD.md` and a Slack message summarising key developments|If browser search fails (e.g., network error), log and retry once. If summarisation fails, downgrade to Mid‑tier model.|No external side effect occurs until approval. If message posted incorrectly, analysts can post a correction.|High|
|IPOS‑A4|**Monthly playbook refresh**|`0 3 1 * *` (first day of month at 03:00 UTC)|Indicator files (`indicators/`), existing playbooks (`playbooks/`), scripts for generating new playbooks|`read_file`, `edit_file`, `write_file`, `api_tool (GitHub)`|Frontier (synthesis)|**Advisory** – generate new playbook draft; require approval before committing to GitHub|A new playbook file `playbooks/draft-playbook-YYYY-MM.md` and a summary report; optional draft pull request to GitHub via `api_tool` (if write permission configured)|If generation fails, log error and skip; do not modify playbooks. If API call fails, log and require manual push.|The automation writes a draft; no automatic merge occurs. Analysts can discard or modify the draft.|High|
|IPOS‑A5|**Weekly maintenance alert**|`0 6 * * 1` (Monday at 06:00 UTC)|Output logs from `openclaw doctor` and `openclaw security audit` (run manually or by separate script)|`read_file`, `write_file`|Fast|**Draft** – compile a maintenance alert; analysts review|A report `reports/maintenance-alert-YYYY-WW.md` summarising any issues; optional Slack DM to admin|If reading logs fails, record error and notify admin; skip report|This automation does not change state; rollback is not applicable|Low|

### Detailed description

1. **Weekly indicator extraction (IPOS‑A1)** – The agent scans the `playbooks/` and `indicators/` directories for new or updated research documents. It runs a custom extraction script (packaged as a skill) to parse indicators such as technical metrics, economic indicators or risk scores. The script writes parsed data into a JSONL file and logs errors. The agent then uses a Frontier model to summarise the extraction (e.g., highlight major findings) and stores the summary in a report. Analysts review the output before updating the master indicator file. The automation runs in draft mode to prevent unapproved changes.
    
2. **Weekly reconciliation job (IPOS‑A2)** – After extraction, the agent compares newly extracted indicators with previous values. It uses a Fast model or simple diff algorithm to flag differences. A Mid‑tier model analyses discrepancies and suggests actions (e.g., update, investigate, ignore). The resulting report lists changes and recommendations but does not modify data. Analysts review the report and manually update indicator files if needed.
    
3. **Daily market summary (IPOS‑A3)** – Each morning, the agent performs a curated browser search for market news on approved domains (e.g., official financial news sites). It retrieves summaries to avoid prompt injection and uses a Frontier model to synthesise the information into a concise report. Because posting to Slack is an external side effect, the agent requests approval via Slack or Control UI before sending the summary message to the `#ipos-updates` channel. If the operator declines, the report is stored for offline review.
    
4. **Monthly playbook refresh (IPOS‑A4)** – On the first day of each month, the agent generates updated playbooks. It synthesises the latest indicators and research notes into a structured document. The automation produces a draft file and a summary describing changes. It may create a draft pull request using the GitHub connector if write permissions are configured. Analysts review and merge after approval. Running in advisory mode ensures human oversight over strategic documents.
    
5. **Weekly maintenance alert (IPOS‑A5)** – The agent reads logs produced by `openclaw doctor` and `openclaw security audit` (executed manually or by a separate script). It summarises any issues and potential updates in a report and optionally notifies the admin via Slack. This automation helps maintain the system’s health and ensures compliance with the Guardrail Architecture.
    

## Logging and observation

Each automation writes a log entry into `logs/ipos-automations.log` with fields: timestamp, automation ID, status (success/failure), retries, runtime, and key messages. For automations with external side effects (Slack/Telegram), log whether approval was granted or denied. Each automation also produces a small JSON summary of its outputs and errors, facilitating weekly reviews and continuous improvement.

## Rollback plan

- **IPOS‑A1**: Keep the previous `indicators.jsonl` and `playbooks/` backups. If extracted indicators are incorrect, restore from backup and adjust the extraction script. Because the automation runs in draft mode, no unapproved updates occur.
    
- **IPOS‑A2**: As it does not modify data, rollback consists of discarding the reconciliation report.
    
- **IPOS‑A3**: If an incorrect market summary is posted, an analyst can post a correction. Minimising content helps mitigate risk; require approval to avoid erroneous posts.
    
- **IPOS‑A4**: Since the playbook refresh is advisory, the draft can simply be deleted if flawed. If a GitHub draft pull request is created, close it and discard the branch.
    
- **IPOS‑A5**: No state changes occur; rollback is not applicable.
    

## Decision / recommendation

Implement the five automations listed above in the sequence shown: start with extraction (IPOS‑A1) and reconciliation (IPOS‑A2), then add market summaries (IPOS‑A3) once the team is comfortable with external fetches and summarisation, proceed with monthly playbook refresh (IPOS‑A4) for strategic updates, and include maintenance alerts (IPOS‑A5) to maintain system health. Use draft or advisory modes for all automations that produce or send reports to ensure human oversight and reduce the risk of erroneous actions.

## Risks and trade‑offs

- **Data quality**: Extraction scripts may misinterpret data or miss indicators. Mitigate by reviewing extraction logic and verifying outputs before updating the master file.
    
- **Prompt injection**: Browser searches for market news expose the agent to untrusted content. Limit sources to approved domains, summarise externally and run outputs through an input audit layer.
    
- **Approval fatigue**: Frequent approvals (daily market summaries) may frustrate analysts. After establishing trust and accuracy, consider moving market summaries to draft mode during low‑volatility periods.
    
- **Performance and cost**: Frontier models are expensive; use Mid‑tier models where possible (e.g., extraction summarisation if adequate). Monitor monthly usage and adjust triggers if costs grow.
    
- **Dependency risk**: Relying on connectors (Slack, GitHub) introduces external dependencies. Ensure connectors are monitored and fallback procedures exist (e.g., sending reports via email if Slack fails).
    
- **Concurrency**: Multiple analysts may trigger manual tasks concurrently. Implement a task queue or lock mechanism to avoid race conditions during extraction or playbook refresh.
    

## Critique

While this architecture covers key research automations, it may require further customisation once the forthcoming IPOS blueprint arrives. Additional flows could include on‑demand indicator extraction (triggered via Slack), real‑time market monitoring, portfolio risk analysis or integration with third‑party data providers (e.g., Bloomberg). Also, concurrency controls and a centralised dashboard for automation status are missing. A more granular scheduling system could allow analysts to adjust timings based on market hours. Finally, the automation matrix does not address potential long‑running tasks; adding timeouts or progressive summarisation may be necessary.

## Patch

1. **Add on‑demand extraction**: Implement a Slack command (e.g., `/extract-indicators`) that triggers IPOS‑A1 outside of the scheduled time. This requires a separate approval flow.
    
2. **Develop a monitoring dashboard**: Build a simple dashboard (within the Control UI or Slack) summarising automation runs, statuses, outputs and errors. Include filters by date and automation ID.
    
3. **Integrate concurrency controls**: Use a queue or lock file so that only one extraction or playbook refresh runs at a time. Document the behaviour in the runbook.
    
4. **Customise schedules**: Allow analysts to modify cron expressions via configuration files, subject to admin approval. Provide guidelines for scheduling around market hours.
    
5. **Plan for blueprint updates**: When the IPOS blueprint is delivered, revisit this architecture and incorporate any new workflows or data sources.
    

## CHECKPOINT

The **IPOS Automation Architecture** is drafted. It defines five initial automations (indicator extraction, reconciliation, market summary, playbook refresh, maintenance alert) with their triggers, tools, models, approval modes, outputs, failure handling, rollback procedures and risk levels. The document awaits critique and patching.