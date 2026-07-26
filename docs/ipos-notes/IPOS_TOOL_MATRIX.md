# IPOS_TOOL_MATRIX.md

## Objective

Specify the tools enabled, conditional or denied in the **Investment & Research OS (IPOS)** project. This matrix operationalises the default‑deny policy while accommodating the research‑heavy workflows that require broader tool access.

## Inputs used

- **IPOS Agent Operating Model** – details mission, workflows, channels, automation candidates and guardrails for the research environment.
    
- **Tool and Skill Architecture** – provides a high‑level inventory of native tools and explains the default‑deny policy and supply‑chain risks.
    
- **OpenClaw security best practices** – emphasises disabling unnecessary tools, scoping filesystem access and confirming operations that could cause harm.
    

## Assumptions

1. IPOS is a collaborative research project with multiple trusted analysts. The environment needs web access to fetch market data and research but must enforce sandboxing to prevent script execution or malware.
    
2. Tools used for automation (e.g., cron) must follow the Automation Policy Baseline: each job has defined triggers, inputs, outputs, approval modes, rollback and logging.
    
3. GitHub interactions are primarily read‑only; write operations require explicit approval.
    
4. High‑risk tools (shell, elevated privileges) remain disabled. External email sending is optional and subject to approval.
    

## Tool matrix

|Tool|Description|Risk level|Status|Rationale|Allowed workflows|
|---|---|---|---|---|---|
|**read_file**|Read local documents.|Low|Enabled|Required to ingest research PDFs, CSVs, JSON files, playbooks and indicator files.|Reading research papers, playbooks, indicator data.|
|**write_file**|Create or overwrite files.|Medium|Enabled (confirmation)|Necessary for updating playbooks, writing extraction results and producing reports. Confirmation prevents accidental overwrites.|Writing indicator JSONL files, generating summary reports.|
|**edit_file**|Apply patches to files.|Medium|Enabled (confirmation)|Enables editing existing playbooks and scripts with version control. Confirmation reduces risk.|Modifying indicator scripts, updating playbooks.|
|**search**|Search within workspace or memory.|Low|Enabled|Needed for locating documents, scripts and context.|Finding specific research materials, indicators or memory entries.|
|**memory_search**|Retrieve conversation history.|Low|Enabled|Supports referencing past tasks and decisions.|Summarising prior analyses, retrieving previous outputs.|
|**api_tool (GitHub)**|Access GitHub repositories via connector.|Medium|Enabled (read‑only by default)|Analysts must fetch internal playbooks or scripts. Write operations require approval to prevent unintended changes.|Cloning playbooks, reading issue discussions, preparing patches.|
|**api_tool (other connectors)**|Access other internal or external APIs (e.g., Bloomberg).|High|Conditional|Use only vetted connectors. Each integration must be documented, require secrets stored securely and define allowed operations.|Fetching market data, retrieving proprietary indicators.|
|**browser.search**|Perform web searches.|High|Enabled (sandboxed)|Research tasks often require scanning the web for financial news. Sandbox prevents script execution and restricts cross‑domain requests. Confirm before opening untrusted domains and summarise content before using it.|Collecting market news, verifying financial data.|
|**browser.open**|Open and scrape web pages.|High|Enabled (sandboxed)|Complementary to `browser.search`; used to extract content from known sources. Use content sanitisation to prevent injection.|Extracting data from financial news sites, downloading PDF reports for analysis.|
|**cron.schedule**|Schedule recurring tasks.|Medium|Enabled|Essential for automated extraction, reconciliation, market summaries and maintenance jobs. Each job must specify triggers, idempotency, approval and rollback.|Weekly indicator extraction, daily market summary, reconciliation routines.|
|**email.send**|Send emails via configured provider.|High|Conditional|Optional if analysts prefer receiving reports via email. Always require preview and approval before sending, and avoid including sensitive data.|Sending summary reports to analysts who are not on Slack or Telegram.|
|**system.run**|Execute arbitrary shell commands.|Critical|Denied|High risk and unnecessary; extraction logic should be implemented within the agent or as vetted scripts. Prevents mis‑use of the host.|—|
|**elevated tools**|Privileged operations.|Critical|Denied|Elevated privileges are out of scope. The container’s non‑privileged user should enforce least privilege.|—|
|**Third‑party skills (approved)**|Audited skills such as summariser, gap updater, assumption checker, task classifier, schedule manager, research fetcher, report generator, PDF parser, indicator extractor.|Medium|Conditional|Only use vetted skills. New domain‑specific skills must undergo code review and security audit before installation.|Summarising documents, extracting indicators, generating reports, classifying tasks, scheduling cron jobs.|
|**Third‑party skills (unvetted)**|Unvetted or community skills.|High|Denied|Supply chain risk; not permitted without an audit.|—|

### Filesystem scoping

The IPOS agent must restrict filesystem access to the workspace directories (`/workspace/playbooks`, `/workspace/indicators`, `/workspace/reports`, `/workspace/process`) and optional caches. Disallow reading from sensitive directories such as `~/.ssh`, `/etc`, `/root` and system directories. Use container mounts to enforce read/write boundaries.

### Network and domain restrictions

For `browser.search` and `browser.open`, implement domain allowlists and content sanitisation. Allow only known financial news sites, official data providers or company intranet pages. Deny requests to arbitrary domains. Always summarise content before acting on it and avoid injecting untrusted text into prompts.

### How to enable additional tools

If a new tool or connector is needed (e.g., Slack API for advanced notifications):

1. Determine the workflow requiring the tool and document it.
    
2. Assess the security risk and supply‑chain implications. Only integrate connectors vetted by the security team.
    
3. Update the matrix with status, rationale, allowed workflows and guardrails.
    
4. Modify runbooks and AGENTS.md to include the new tool and instructions.
    

## Decision / recommendation

Adopt this tool matrix for IPOS. It provides the flexibility required for research (web access, API connectors, scheduled tasks) while maintaining strong guardrails by sandboxing browser operations, denying shell access and requiring confirmation for writes. Use the matrix as the basis for the IPOS tool configuration (e.g., `config.yaml`) and update it as new workflows emerge.

## Risks and trade‑offs

- **Attack surface**: Enabling browser and external API connectors increases the attack surface. Sandbox and domain allowlists mitigate but do not eliminate risks. Regularly review and update allowlists.
    
- **Cost and resource consumption**: Frequent web scraping and large data ingestion can consume bandwidth and computing resources. Monitor usage and adjust tasks accordingly.
    
- **Complexity**: Managing multiple connectors and automations requires careful configuration and oversight. Documented workflows and approval matrices are essential.
    
- **Email risk**: Sending emails may expose data if misconfigured. Slack is the preferred channel for notifications; emails should be limited to low‑sensitivity summaries.
    
- **Skill supply chain**: Installing domain‑specific skills adds risk. Vetting and regular audits are mandatory to prevent malicious code or prompt injection.
    

## Critique

This tool matrix strikes a balance between capability and safety, but some details may require refinement. For example, Slack and Telegram channels are configured outside the tool matrix; the integration details (tokens, channel IDs) must be handled via the `api_tool` or the channel configuration, which is not reflected here. The matrix may also need to accommodate additional analytics connectors or data transformation tools once the IPOS blueprint is available. Additional guidance is required for concurrency management when multiple analysts schedule tasks concurrently.

## Patch

1. **Refine browser restrictions**: Develop a curated list of allowed financial data sources and implement domain‑specific parsing logic to avoid injecting malicious content.
    
2. **Add concurrency controls**: Create a queuing mechanism or locking strategy to handle simultaneous tasks from multiple analysts, preventing race conditions or resource contention.
    
3. **Expand connectors**: When new data providers or APIs are required, design and audit wrappers that integrate via `api_tool` with proper secret management and logging.
    
4. **Provide automation templates**: Include ready‑to‑use cron job definitions for common workflows (extraction, reconciliation, summary) with placeholders for parameters and approval modes.
    
5. **Enhance logging and monitoring**: Integrate with a central logging service to track tool usage, automation results and failures. Use this telemetry to refine tool policies and detect anomalies.
    

## CHECKPOINT

The IPOS tool matrix is drafted. It outlines tool statuses, rationales, workflows and guardrails for the research environment. Review and updates will follow after feedback and after the IPOS blueprint becomes available.