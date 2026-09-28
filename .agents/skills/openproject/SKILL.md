---
name: openproject
description: Use when an Investment workspace task involves the private Leela OpenProject API v3, work packages, PM status, hierarchy, dependencies, or writing evidence back under confirmation.
allowed-tools: Bash
---

# OpenProject skill (portable)

Operate the **private Leela OpenProject** instance through its REST API v3. This workspace-local
copy is the sole OpenProject runtime for `C:\GitDev\Investment`: a plain Node CLI plus one shared
client, with no browser login, AnythingLLM runtime, or upstream `op` CLI dependency.

## When to use

- Read a Work Package, its children, relations, status, or activity.
- List projects, statuses, or types.
- Create/update a Work Package, add a comment, or create a relation — **in an authorized test scope**.
- Write task evidence back to an OpenProject Work Package under the accepted write policy.

## Target instance — never guess

The target is the **private** Leela OpenProject only. There is also a community instance and a
**stopped duplicate** — never operate against those.

Configure via environment (never put a token in a repo file, command argument, or log):

```
OPENPROJECT_BASE_URL=http://127.0.0.1:8083      # the private instance base URL
OPENPROJECT_TOKEN=<api key from the dedicated Leela agent account>
OPENPROJECT_EXPECT_VERSION_PREFIX=17.            # write-safety fingerprint
OPENPROJECT_EXPECT_HOST=127.0.0.1:8083           # write-safety fingerprint
```

Load credentials from `C:\GitDev\leela-op178\op.env`; never print the token. In PowerShell, load
only `KEY=VALUE` lines into the current process, then force the private-instance fingerprint and
run from this skill directory:

```powershell
$secretPath = 'C:\GitDev\leela-op178\op.env'
Get-Content -LiteralPath $secretPath | ForEach-Object {
  if ($_ -match '^\s*([^#=\s]+)=(.*)$') {
    [Environment]::SetEnvironmentVariable($Matches[1], $Matches[2].TrimEnd("`r"), 'Process')
  }
}
$env:OPENPROJECT_BASE_URL = 'http://127.0.0.1:8083'
$env:OPENPROJECT_EXPECT_VERSION_PREFIX = '17.'
$env:OPENPROJECT_EXPECT_HOST = '127.0.0.1:8083'
Set-Location 'C:\GitDev\Investment\.agents\skills\openproject'
```

For WSL/bash, use the CRLF-safe equivalent and run from the workspace-local skill:

```bash
set -a; . <(tr -d '\r' < /mnt/c/GitDev/leela-op178/op.env); set +a
export OPENPROJECT_BASE_URL=http://127.0.0.1:8083
export OPENPROJECT_EXPECT_VERSION_PREFIX=17.
export OPENPROJECT_EXPECT_HOST=127.0.0.1:8083
cd /mnt/c/GitDev/Investment/.agents/skills/openproject
```

Before any **write**, the client re-checks `GET /api/v3` against the `OPENPROJECT_EXPECT_*`
fingerprints and refuses if the live host/version does not match. Start every OpenProject task with
this read-only sequence; resolve the project id from `project.list` rather than guessing it:

```bash
node client/opCall.js root       # instanceName + coreVersion
node client/opCall.js whoami     # authenticated identity
node client/opCall.js project.list
node client/opCall.js doctor --project <id>   # read-only preflight: reachability, auth, fingerprint,
                                              # project access, that project's enabled types, write-gate
```

Run `doctor` before any real work: it composes the checks above into one read-only pass/fail and never
mutates. `type.list --project <id>` lists the types actually enabled for a project (types are enabled
per project, so a create with a globally-defined but project-disabled type is correctly rejected).

## Running an operation

```bash
node client/opCall.js <operation> [--key value ...] [--data '<json>'] [--confirmed]
```

`--json` output is always structured JSON. Read `references/operations.md` before selecting a
payload or endpoint. Read `references/write-policy.md` before previewing any mutation.

Common reads:

```bash
node client/opCall.js project.list
node client/opCall.js wp.get --id 59
node client/opCall.js wp.list --project 3 --pageSize 20
node client/opCall.js status.list
```

## Write policy — two phases, always reread

1. Every mutating op (`wp.create`, `wp.update`, `wp.delete`, `wp.comment`, `relation.create`,
   `relation.delete`) is **blocked by default**: it prints a preview and exits without writing.
2. Re-run the identical call with `--confirmed` **only after operator OK for that specific action**.
3. After every mutation, **reread** the object (`wp.get` / `relation.get`) and compare intended vs
   observed state. A partial or unexpected result is a stop condition.

`wp.update` requires the current `lockVersion` — `wp.get` first, then send the full HAL body via
`--data`. Risk classes and the current autonomy policy: `references/write-policy.md`.

Write autonomy beyond reads and explicitly authorized test-scope mutations is **not yet decided**
(operator-open). Do not self-authorize workflow, structural, high-impact, or destructive writes.

## Verification requirement

Prove a result, don't assume it: for a read, echo the returned id + a stable field; for a write,
show the post-write reread. Distinguish a skill/routing failure from an API failure by repeating the
same call directly against the API when in doubt.

## Boundaries

- Never use a browser to operate OpenProject and never ask for the web password; API-token auth is
  separate from website login.
- Never target the community instance or start the stopped duplicate.
- Never write PostgreSQL directly; all changes go through API v3.
- No BMAD or other framework unless the operator explicitly selects it for the current task.
- The 58-unit AnythingLLM package under `docs/ProjectMM/openproject/openproject/` is **reference
  only** (endpoint/payload provenance) — never a runtime dependency.
