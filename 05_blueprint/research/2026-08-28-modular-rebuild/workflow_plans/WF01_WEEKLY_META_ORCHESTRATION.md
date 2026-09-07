# Workflow Plan 01: Weekly Meta-Orchestration Sweep

**Workflow ID:** WF-01  
**Target Domain:** Global Infrastructure & Cross-Repository Health  
**Target Repositories:** `apexai-os-meta`, `Investment`, `MasterOfArts`, `acim-secular`  
**Cognitive Architecture:** Tier 1 CLI Agent (Deep Reasoning & Strategy) directing Tier 2 Hermes CLI (`default` profile)

---

## 1. Operational Overview
The Weekly Meta-Orchestration Sweep is executed weekly (Sunday 23:00) or on-demand. A high-reasoning CLI agent reviews the operational state across all four native ext4 workspaces, checks Docker container health, verifies git branch status (divergence and uncommitted changes), executes the ext4 volume backup script, and writes an immutable `health-receipt.yaml`.

---

## 2. Step-by-Step Execution Procedure

1. **Workspace Health Sweep**:
   - Inspect git status, active branch, and uncommitted diffs across:
     - `/root/workspaces/apexai-os-meta`
     - `/root/workspaces/Investment`
     - `/root/workspaces/MasterOfArts`
     - `/root/workspaces/acim-secular`
2. **Container Infrastructure Inspection**:
   - Check status of both Docker environments:
     - WSL2 native dockerd (Private stack)
     - Windows Alpine Docker Desktop (Community stack)
3. **Backup Execution Drill**:
   - Execute `C:\GitDev\apexai-os-meta\ki-basis\scripts\backup-stack.sh` to verify ext4 volume archiving.
4. **Rollup Receipt Generation**:
   - Compile findings into `apex-meta/orchestration/rollups/health-receipt.yaml`.

---

## 3. Specific Test Run & Verification Protocol

### Test Command 1: Cross-Workspace Git Integrity
```bash
wsl.exe -d Ubuntu -u root -e bash -c "
for repo in apexai-os-meta Investment MasterOfArts acim-secular; do
    echo "=== \$repo ==="
    cd /root/workspaces/\$repo && git status -s -b
done
"
```
*Expected Output*: Displays branch and status for all 4 repositories with clean exit code 0.

### Test Command 2: Docker Container Health Sweep
```powershell
docker ps --format "table {{.Names}}	{{.Status}}	{{.Ports}}"
```
*Expected Output*: Returns healthy status for all 7 active containers.

---

## 4. Pass / Fail Criteria
* **PASS**: All 4 workspaces respond, Docker containers report healthy, and backup script completes without disk errors.
* **FAIL**: Any workspace unreachable, container in restart loop, or corrupted volume detected.

---

## 5. Operator Interaction Points
* **PAUSE & PROMPT**: If any repository has uncommitted merge conflicts or dirty git trees that require manual commit/stash approval.
