#!/usr/bin/env node
"use strict";

/**
 * Portable OpenProject operation runner.
 *
 *   node opCall.js <operation> [--key value ...] [--data '<json>'] [--confirmed] [--json]
 *
 * Reads OPENPROJECT_BASE_URL / OPENPROJECT_TOKEN (+ optional OPENPROJECT_EXPECT_*)
 * from the environment. Two safety gates apply to every mutating operation:
 *   1. Instance identity — verifyInstance() must pass (unless OPENPROJECT_EXPECT_* is unset).
 *   2. Two-phase write-confirm — a mutating op without --confirmed prints a preview and does NOT run.
 *      Set OP_WRITE_CONFIRM=0 only for a dedicated write lab.
 *
 * Exit codes: 0 ok, 2 usage error, 3 confirm-required (no write done), 4 identity gate failed,
 *             5 HTTP error status, 1 transport error.
 */

const path = require("path");
const op = require(path.join(__dirname, "opClient.js"));

// ---- arg parsing -----------------------------------------------------------
function parseArgs(argv) {
  const args = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith("--")) {
      const key = a.slice(2);
      const next = argv[i + 1];
      if (next === undefined || next.startsWith("--")) {
        args[key] = true; // boolean flag
      } else {
        args[key] = next;
        i++;
      }
    } else {
      args._.push(a);
    }
  }
  return args;
}

const num = (v) => {
  const n = Number(v);
  return Number.isFinite(n) ? n : v;
};

// ---- operation table -------------------------------------------------------
// mutating: true → gated by identity + write-confirm.
const OPS = {
  root: { method: "GET", path: () => "/api/v3", read: true },
  whoami: { method: "GET", path: () => "/api/v3/users/me", read: true },
  "project.list": { method: "GET", path: () => "/api/v3/projects", read: true },
  "project.get": { method: "GET", path: (a) => `/api/v3/projects/${enc(a.id)}`, need: ["id"], read: true },
  "status.list": { method: "GET", path: () => "/api/v3/statuses", read: true },
  // --project <id> lists the types ENABLED for that project (not the global set).
  "type.list": { method: "GET", path: (a) => (a.project ? `/api/v3/projects/${enc(a.project)}/types` : "/api/v3/types"), read: true },
  "wp.list": {
    method: "GET",
    path: (a) => (a.project ? `/api/v3/projects/${enc(a.project)}/work_packages` : "/api/v3/work_packages") + qs(a),
    read: true,
  },
  "wp.get": { method: "GET", path: (a) => `/api/v3/work_packages/${enc(a.id)}`, need: ["id"], read: true },
  "wp.activities": { method: "GET", path: (a) => `/api/v3/work_packages/${enc(a.id)}/activities`, need: ["id"], read: true },
  "relation.list": { method: "GET", path: () => "/api/v3/relations", read: true },
  "relation.get": { method: "GET", path: (a) => `/api/v3/relations/${enc(a.id)}`, need: ["id"], read: true },

  "project.create": {
    method: "POST",
    path: () => "/api/v3/projects",
    mutating: true,
    need: ["name|data"],
    body: (a) => a.data ? JSON.parse(a.data) : {
      name: a.name,
      identifier: a.identifier,
      ...(a.description ? { description: { raw: String(a.description) } } : {}),
    },
  },
  "project.update": {
    // PATCH a project (e.g. enable/disable its work-package types via _links.types).
    // Send the full HAL body via --data; a prior project.get supplies lockVersion if required.
    method: "PATCH",
    path: (a) => `/api/v3/projects/${enc(a.id)}`,
    mutating: true,
    need: ["id", "data"],
    body: (a) => JSON.parse(a.data),
  },
  "wp.create": {
    method: "POST",
    path: () => "/api/v3/work_packages",
    mutating: true,
    need: ["subject|data"],
    body: (a) => a.data ? JSON.parse(a.data) : {
      subject: a.subject,
      _links: {
        project: { href: `/api/v3/projects/${enc(a.project)}` },
        ...(a.type ? { type: { href: `/api/v3/types/${enc(a.type)}` } } : {}),
      },
      ...(a.description ? { description: { raw: String(a.description) } } : {}),
    },
  },
  "wp.update": {
    method: "PATCH",
    // OpenProject PATCH requires lockVersion from a prior GET. Pass the full HAL body via --data.
    path: (a) => `/api/v3/work_packages/${enc(a.id)}${a.notify ? `?notify=${enc(a.notify)}` : ""}`,
    mutating: true,
    need: ["id", "data"],
    body: (a) => JSON.parse(a.data),
  },
  "wp.delete": {
    method: "DELETE",
    path: (a) => `/api/v3/work_packages/${enc(a.id)}`,
    mutating: true,
    need: ["id"],
  },
  "wp.comment": {
    method: "POST",
    path: (a) => `/api/v3/work_packages/${enc(a.id)}/activities`,
    mutating: true,
    need: ["id", "comment"],
    body: (a) => ({ comment: { raw: String(a.comment) } }),
  },
  "wp.attach": {
    // Upload a local file as an attachment. --id <wp> --file <path> [--name <fileName>] [--description <text>]
    method: "POST",
    path: (a) => `/api/v3/work_packages/${enc(a.id)}/attachments`,
    mutating: true,
    need: ["id", "file"],
    attach: true,
    body: (a) => ({ file: String(a.file), fileName: a.name || path.basename(String(a.file)) }),
  },
  "relation.create": {
    method: "POST",
    path: (a) => `/api/v3/work_packages/${enc(a.id)}/relations`,
    mutating: true,
    need: ["id", "to|data"],
    body: (a) => a.data ? JSON.parse(a.data) : {
      _links: { to: { href: `/api/v3/work_packages/${enc(a.to)}` } },
      type: a.type || "relates",
    },
  },
  "relation.delete": {
    method: "DELETE",
    path: (a) => `/api/v3/relations/${enc(a.id)}`,
    mutating: true,
    need: ["id"],
  },
  "project.delete": {
    // Destructive: schedules deletion of the project and all its work packages.
    method: "DELETE",
    path: (a) => `/api/v3/projects/${enc(a.id)}`,
    mutating: true,
    need: ["id"],
  },
};

function enc(v) {
  return encodeURIComponent(String(v));
}
function qs(a) {
  const p = new URLSearchParams();
  for (const k of ["filters", "sortBy", "pageSize", "offset"]) {
    if (a[k] !== undefined && a[k] !== true) p.set(k, String(a[k]));
  }
  const s = p.toString();
  return s ? `?${s}` : "";
}

function checkNeed(spec, a) {
  for (const clause of spec.need || []) {
    const anyOf = clause.split("|");
    if (!anyOf.some((k) => a[k] !== undefined && a[k] !== "")) {
      return `missing required arg: ${anyOf.join(" or ")}`;
    }
  }
  return null;
}

function out(obj) {
  const cfg = op.readConfig();
  process.stdout.write(op.redact(JSON.stringify(obj, null, 2), cfg.token) + "\n");
}

// ---- doctor (read-only self-check) -----------------------------------------
// Verifies the whole chain BEFORE any write is attempted: reachability + auth,
// correct instance (fingerprint), optional project access + its enabled types,
// and that the write-gate is active. Performs NO mutation. Exit 0 = pass, 5 = fail.
async function doctorRun(cfg, a) {
  const checks = [];
  const add = (check, ok, detail) => checks.push({ check, ok, detail });

  add("config", !!(cfg.baseUrl && cfg.token), { baseUrl: cfg.baseUrl, tokenSet: !!cfg.token });

  try {
    const me = await op.getMe(cfg);
    add("auth_whoami", me.ok, me.ok
      ? { id: me.json && me.json.id, name: me.json && me.json.name, admin: me.json && me.json.admin }
      : { status: me.status });
  } catch (e) {
    add("auth_whoami", false, { error: op.redact(e.message, cfg.token) });
  }

  const expectConfigured = cfg.expect.versionPrefix || cfg.expect.host || cfg.expect.instanceName;
  if (expectConfigured) {
    try {
      const v = await op.verifyInstance(cfg);
      add("instance_fingerprint", v.ok, { coreVersion: v.coreVersion, instanceName: v.instanceName, host: v.host, problems: v.problems });
    } catch (e) {
      add("instance_fingerprint", false, { error: op.redact(e.message, cfg.token) });
    }
  } else {
    add("instance_fingerprint", null, "no OPENPROJECT_EXPECT_* configured — write-safety fingerprint is OFF");
  }

  if (a.project !== undefined && a.project !== true) {
    try {
      const pr = await op.request("GET", `/api/v3/projects/${enc(a.project)}`, cfg);
      add("project_access", pr.ok, pr.ok ? { id: pr.json && pr.json.id, name: pr.json && pr.json.name } : { status: pr.status });
      const tr = await op.getProjectTypes(cfg, a.project);
      const types = tr.ok && tr.json && tr.json._embedded ? tr.json._embedded.elements.map((t) => t.name) : [];
      add("project_types", tr.ok, { allowed: types });
    } catch (e) {
      add("project_access", false, { error: op.redact(e.message, cfg.token) });
    }
  } else {
    add("project_types", null, "pass --project <id> to also check that project's access + enabled types");
  }

  const writeConfirmEnabled = !/^(0|false|off|no)$/i.test(String(process.env.OP_WRITE_CONFIRM || "1"));
  add("write_gate", writeConfirmEnabled,
    writeConfirmEnabled ? "mutations require --confirmed (safe)" : "OP_WRITE_CONFIRM disables the gate (UNSAFE for real data)");

  const failed = checks.filter((c) => c.ok === false);
  const verdict = failed.length === 0 ? "pass" : "fail";
  out({ operation: "doctor", verdict, checks });
  process.exit(verdict === "pass" ? 0 : 5);
}

// ---- main ------------------------------------------------------------------
async function main() {
  const argv = process.argv.slice(2);
  const a = parseArgs(argv);
  const operation = a._[0];

  if (!operation || a.help) {
    out({ usage: "node opCall.js <operation> [--key value] [--data <json>] [--confirmed]", operations: [...Object.keys(OPS), "doctor"] });
    process.exit(operation ? 0 : 2);
  }

  if (operation === "doctor") {
    const dcfg = op.readConfig();
    if (!dcfg.baseUrl || !dcfg.token) {
      out({ error: "OPENPROJECT_BASE_URL and OPENPROJECT_TOKEN must be set in the environment" });
      process.exit(2);
    }
    await doctorRun(dcfg, a);
    return; // doctorRun exits
  }

  const spec = OPS[operation];
  if (!spec) {
    out({ error: `unknown operation: ${operation}`, operations: [...Object.keys(OPS), "doctor"] });
    process.exit(2);
  }
  const needErr = checkNeed(spec, a);
  if (needErr) {
    out({ error: needErr, operation });
    process.exit(2);
  }

  const cfg = op.readConfig();
  if (!cfg.baseUrl || !cfg.token) {
    out({ error: "OPENPROJECT_BASE_URL and OPENPROJECT_TOKEN must be set in the environment" });
    process.exit(2);
  }

  // Resolve a work-package type NAME → id, scoped to the project's enabled types, so a
  // create can never silently use a wrong or project-disabled numeric id. Applies only
  // when --type is a non-numeric name and no raw --data body was supplied. Read-only.
  if (operation === "wp.create" && a.type && !a.data && !/^\d+$/.test(String(a.type))) {
    if (a.project === undefined || a.project === true) {
      out({ error: "wp.create with a type NAME requires --project so the type can be resolved to that project's enabled types", operation });
      process.exit(2);
    }
    const r = await op.resolveTypeName(cfg, a.project, a.type);
    if (!r.ok) {
      out({ error: "type name resolution failed", operation, detail: r });
      process.exit(2);
    }
    a.type = r.id;
  }

  const writeConfirmEnabled = !/^(0|false|off|no)$/i.test(String(process.env.OP_WRITE_CONFIRM || "1"));
  const reqPath = spec.path(a);
  const body = spec.body ? spec.body(a) : undefined;

  if (spec.mutating) {
    // Gate 1 — identity (only enforced if any OPENPROJECT_EXPECT_* is configured).
    const expectConfigured = cfg.expect.versionPrefix || cfg.expect.host || cfg.expect.instanceName;
    if (expectConfigured) {
      const v = await op.verifyInstance(cfg);
      if (!v.ok) {
        out({ blocked: "identity gate failed — refusing to write", verify: v });
        process.exit(4);
      }
    }
    // Gate 2 — two-phase write-confirm.
    if (writeConfirmEnabled && !a.confirmed) {
      out({
        confirm_required: true,
        message: "Mutating operation NOT executed. Re-run the same call with --confirmed after operator OK.",
        planned: { operation, method: spec.method, path: reqPath, body },
      });
      process.exit(3);
    }
  }

  try {
    const res = spec.attach
      ? await op.attachFile(cfg, a.id, a.file, a.name || path.basename(String(a.file)), a.description || "")
      : await op.request(spec.method, reqPath, cfg, { body });
    out({ operation, method: spec.method, path: reqPath, status: res.status, ok: res.ok, result: res.json });
    process.exit(res.ok ? 0 : 5);
  } catch (err) {
    out({ operation, method: spec.method, path: reqPath, error: op.redact(err.message, cfg.token) });
    process.exit(1);
  }
}

main();
