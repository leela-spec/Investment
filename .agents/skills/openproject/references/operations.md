# OpenProject operation catalog

Endpoints and payloads for `client/opCall.js`. Grounded in OpenProject API v3 (HAL/HATEOAS) and
cross-checked against the reference handlers in `docs/ProjectMM/openproject/openproject/`. Verify
exact fields against the **live** instance's own `GET /api/v3/spec.json` before relying on a payload;
an older instance may differ from the newest online docs.

HAL notes:
- Collections return `{ _type: "...Collection", total, _embedded: { elements: [...] } }`.
- Single resources carry `_links` (project/type/status/assignee/parent/priority) and `lockVersion`.
- Relationships are set by `_links.<rel> = { href: "/api/v3/<resource>/<id>" }`, not by bare id.

## Reads (no confirmation)

| Operation | Method + path | Args |
|---|---|---|
| `root` | `GET /api/v3` | — (instanceName, coreVersion) |
| `whoami` | `GET /api/v3/users/me` | — |
| `project.list` | `GET /api/v3/projects` | — |
| `project.get` | `GET /api/v3/projects/{id}` | `--id` |
| `wp.list` | `GET /api/v3/work_packages` or `GET /api/v3/projects/{project}/work_packages` | `--project?`, `--filters?`, `--sortBy?`, `--pageSize?`, `--offset?` |
| `wp.get` | `GET /api/v3/work_packages/{id}` | `--id` |
| `wp.activities` | `GET /api/v3/work_packages/{id}/activities` | `--id` |
| `status.list` | `GET /api/v3/statuses` | — |
| `type.list` | `GET /api/v3/types` **or** `GET /api/v3/projects/{project}/types` | `--project?` (with `--project`, lists the types **enabled for that project**, not the global set) |
| `doctor` | composite read-only self-check (no mutation) | `--project?` |
| `relation.list` | `GET /api/v3/relations` | `--filters?` |
| `relation.get` | `GET /api/v3/relations/{id}` | `--id` |

`--filters` is a JSON array string, e.g. `--filters '[{"status":{"operator":"o","values":[]}}]'`.

## Writes (blocked until `--confirmed`; reread after)

### wp.create — `POST /api/v3/work_packages`
Convenience: `--subject "<text>" --project <id> [--type <id|name>] [--description "<text>"]`
`--type` accepts a **name** (e.g. `--type "Feature"`); it is resolved against the project's
**enabled** types before the create, and fails clearly if that type is not enabled/ambiguous for the
project (requires `--project`). A numeric id is used as-is. Run `doctor --project <id>` first to see the
enabled types.
Or full control: `--data '<HAL json>'`, e.g.
```json
{ "subject": "Test WP",
  "_links": { "project": { "href": "/api/v3/projects/3" }, "type": { "href": "/api/v3/types/1" } } }
```

### wp.update — `PATCH /api/v3/work_packages/{id}`
Requires `lockVersion` from a prior `wp.get`. Send the full body via `--data`:
```json
{ "lockVersion": 3, "subject": "New subject" }
```
Status change: `{ "lockVersion": 3, "_links": { "status": { "href": "/api/v3/statuses/7" } } }`
Assignee: `{ "lockVersion": 3, "_links": { "assignee": { "href": "/api/v3/users/4" } } }`
Add `--notify false` to suppress email.

### wp.comment — `POST /api/v3/work_packages/{id}/activities`
`--id <wp> --comment "<markdown>"` → body `{ "comment": { "raw": "<markdown>" } }`

### wp.attach — `POST /api/v3/work_packages/{id}/attachments`
`--id <wp> --file <local path> [--name <fileName>] [--description <text>]` — uploads a local file as an
attachment (multipart/form-data via Node's `fetch`/`FormData`). Gated like other mutations (preview →
`--confirmed` → the attachment is then visible on the work package).

### relation.create — `POST /api/v3/work_packages/{id}/relations`
`--id <from> --to <toId> [--type relates|follows|precedes|blocks|blocked|includes|requires|...]`
Or `--data '{ "_links": { "to": { "href": "/api/v3/work_packages/60" } }, "type": "follows" }'`

### wp.delete — `DELETE /api/v3/work_packages/{id}` · relation.delete — `DELETE /api/v3/relations/{id}`
High-impact: do not run without explicit operator authorization and a recovery expectation.

## Identity / fingerprint fields
`GET /api/v3` → `instanceName`, `coreVersion`. Use these plus the base-URL host as the
`OPENPROJECT_EXPECT_*` write-safety fingerprint.
