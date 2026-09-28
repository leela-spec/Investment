# OpenProject write policy (pilot)

Write autonomy is **operator-open** (decision D6 / OQ-01). Until the operator selects a policy, the
skill defaults to the safe side: **reads are automatic; every mutation is blocked until `--confirmed`
for that specific action, and identity is verified before any write.**

## Two-phase confirm

1. A mutating call without `--confirmed` prints the planned `{operation, method, path, body}` and
   exits `3` without writing.
2. Re-run the identical call with `--confirmed` only after operator OK.
3. `OP_WRITE_CONFIRM=0` disables the gate — use only in a dedicated, disposable write lab, never
   against real data.

Note: the reference handlers' shipped helper confirmed only PATCH/PUT/DELETE (POST/GET passed), while
their manifests claimed POST needed confirmation too — an unresolved conflict. This skill resolves it
to the **safe** default: confirm **all** mutations including create. The operator may loosen it.

## Risk classes (for the pending operator decision)

Every mutating operation the skill implements is listed below by class. Read-only ops are shown for
completeness; they are not gated beyond the identity check.

| Class | Operations (this skill) | Default treatment |
|---|---|---|
| Read-only | `wp.get`, `wp.list`, `wp.activities`, `project.list`, `project.get`, `status.list`, `type.list`, `relation.list`, `relation.get`, `doctor` | automatic after identity check |
| Low-impact reversible | `wp.comment`, `wp.attach` (upload an attachment) | explicit per-task authorization; verify by reread |
| Workflow / structure | `wp.create` (incl. child), `wp.update` (status / subject / assignee / priority), `relation.create`, `project.create` | per-action confirmation until operator decides |
| High-impact | `project.update` (project settings / metadata), close/archive, bulk edits, membership | explicit operator confirmation |
| Destructive | `project.delete` (irreversible — deletes a project and all its work packages), `wp.delete`, `relation.delete`, irreversible conversions | separate approval + recovery expectation |

## Always

- Verify instance identity (host + `17.` version + fingerprint) before a write; mismatch = stop.
- Reread the object after every mutation; compare intended vs observed; a partial/unexpected change is a stop.
- Keep test writes inside the dedicated Leela test project; never write to an unapproved project.
- Never write PostgreSQL directly; never target community or the stopped duplicate.
