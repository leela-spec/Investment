"use strict";

/**
 * Portable OpenProject API v3 client (no AnythingLLM, no upstream `op` CLI).
 *
 * One shared client owns: base-URL/profile selection, Basic `apikey:<token>`
 * auth from the environment, headers, timeouts, JSON/HAL parsing, redaction,
 * and instance-identity verification. It is engine-agnostic: point it at any
 * OpenProject base URL via env.
 *
 * Config (env only — never hard-code a token, never read a token from a repo file):
 *   OPENPROJECT_BASE_URL   e.g. http://127.0.0.1:8083   (no trailing slash needed)
 *   OPENPROJECT_TOKEN      OpenProject API key (from a user's account page)
 *   OPENPROJECT_EXPECT_VERSION_PREFIX   optional, e.g. "17."  (write-safety gate)
 *   OPENPROJECT_EXPECT_HOST             optional, e.g. "127.0.0.1:8083"
 *   OPENPROJECT_EXPECT_INSTANCE_NAME    optional, exact instanceName string
 */

const http = require("http");
const https = require("https");
const fs = require("fs");
const { URL } = require("url");

function readConfig(env = process.env) {
  return {
    baseUrl: String(env.OPENPROJECT_BASE_URL || "").replace(/\/+$/, ""),
    token: String(env.OPENPROJECT_TOKEN || ""),
    expect: {
      versionPrefix: env.OPENPROJECT_EXPECT_VERSION_PREFIX || "",
      host: env.OPENPROJECT_EXPECT_HOST || "",
      instanceName: env.OPENPROJECT_EXPECT_INSTANCE_NAME || "",
    },
  };
}

function authHeader(token) {
  return "Basic " + Buffer.from("apikey:" + token).toString("base64");
}

/** Redact anything token-shaped from a string before it reaches a log/evidence file. */
function redact(text, token) {
  let s = String(text == null ? "" : text);
  if (token) s = s.split(token).join("***REDACTED***");
  return s.replace(/(Basic\s+)[A-Za-z0-9+/=]+/g, "$1***REDACTED***");
}

/**
 * Low-level request. Returns { status, json, ok }.
 * Never throws on HTTP status; only on transport/timeout errors.
 */
function request(method, path, cfg, { body, timeoutMs = 15000 } = {}) {
  if (!cfg || !cfg.baseUrl) {
    return Promise.reject(new Error("OPENPROJECT_BASE_URL is not set"));
  }
  const url = new URL(cfg.baseUrl + path);
  const lib = url.protocol === "https:" ? https : http;
  const payload = body === undefined ? undefined : JSON.stringify(body);
  const headers = { Authorization: authHeader(cfg.token), Accept: "application/json" };
  if (payload !== undefined) {
    headers["Content-Type"] = "application/json";
    headers["Content-Length"] = Buffer.byteLength(payload);
  }
  return new Promise((resolve, reject) => {
    const req = lib.request(url, { method, headers, timeout: timeoutMs }, (res) => {
      let data = "";
      res.on("data", (c) => (data += c));
      res.on("end", () => {
        let json = null;
        try {
          json = data ? JSON.parse(data) : null;
        } catch {
          json = { _type: "Error", _raw: data.slice(0, 4000) };
        }
        const status = res.statusCode || 0;
        resolve({ status, json, ok: status >= 200 && status < 300 });
      });
    });
    req.on("timeout", () => req.destroy(new Error(`timeout after ${timeoutMs}ms`)));
    req.on("error", reject);
    if (payload !== undefined) req.write(payload);
    req.end();
  });
}

async function getRoot(cfg) {
  return request("GET", "/api/v3", cfg);
}

async function getMe(cfg) {
  return request("GET", "/api/v3/users/me", cfg);
}

/**
 * Verify the base URL actually points at the intended instance BEFORE any write.
 * Compares live root against OPENPROJECT_EXPECT_* fingerprints.
 * Returns { ok, coreVersion, instanceName, host, problems[] }.
 */
async function verifyInstance(cfg) {
  const { status, json } = await getRoot(cfg);
  const host = new URL(cfg.baseUrl).host;
  if (status !== 200 || !json) {
    return { ok: false, host, status, problems: [`/api/v3 returned status ${status}`] };
  }
  const coreVersion = json.coreVersion || (json._embedded && json._embedded.coreVersion) || "";
  const instanceName = json.instanceName || "";
  const problems = [];
  const e = cfg.expect || {};
  if (e.versionPrefix && !String(coreVersion).startsWith(e.versionPrefix)) {
    problems.push(`coreVersion "${coreVersion}" does not start with "${e.versionPrefix}"`);
  }
  if (e.host && host !== e.host) {
    problems.push(`host "${host}" != expected "${e.host}"`);
  }
  if (e.instanceName && instanceName !== e.instanceName) {
    problems.push(`instanceName "${instanceName}" != expected "${e.instanceName}"`);
  }
  return { ok: problems.length === 0, coreVersion, instanceName, host, problems };
}

/** List the work-package types ENABLED for a specific project (not the global set). */
async function getProjectTypes(cfg, projectId) {
  return request("GET", `/api/v3/projects/${encodeURIComponent(String(projectId))}/types`, cfg);
}

/**
 * Resolve a work-package type NAME (e.g. "Feature") to its id, scoped to a project's
 * enabled types. Fails (ok:false) if the type is not enabled for that project or is
 * ambiguous — so a create can never silently target a wrong/disabled type.
 * Returns { ok, id?, name?, available?, problems? }.
 */
async function resolveTypeName(cfg, projectId, typeName) {
  const res = await getProjectTypes(cfg, projectId);
  if (res.status !== 200 || !res.json) {
    return { ok: false, problems: [`could not read types for project ${projectId} (status ${res.status})`] };
  }
  const els = (res.json._embedded && res.json._embedded.elements) || [];
  const available = els.map((t) => t.name);
  const wanted = String(typeName).trim().toLowerCase();
  const matches = els.filter((t) => String(t.name).trim().toLowerCase() === wanted);
  if (matches.length === 0) {
    return { ok: false, available, problems: [`type "${typeName}" is not enabled in project ${projectId}`] };
  }
  if (matches.length > 1) {
    return { ok: false, available, problems: [`type "${typeName}" is ambiguous in project ${projectId}`] };
  }
  const m = matches[0];
  const selfHref = (m._links && m._links.self && m._links.self.href) || "";
  const id = m.id != null ? m.id : selfHref.split("/").pop();
  return { ok: true, id, name: m.name, available };
}

/**
 * Upload a local file as an attachment on a work package (multipart/form-data).
 * Uses Node's global fetch/FormData/Blob (Node 18+). Returns { status, json, ok }.
 */
async function attachFile(cfg, wpId, filePath, fileName, description = "") {
  const buf = fs.readFileSync(filePath);
  const fd = new FormData();
  fd.append("metadata", JSON.stringify({ fileName, description: { raw: description } }));
  fd.append("file", new Blob([buf]), fileName);
  const res = await fetch(cfg.baseUrl + `/api/v3/work_packages/${encodeURIComponent(String(wpId))}/attachments`, {
    method: "POST",
    headers: { Authorization: authHeader(cfg.token) }, // do NOT set Content-Type; fetch adds the multipart boundary
    body: fd,
  });
  let json = null;
  try { json = await res.json(); } catch { json = null; }
  return { status: res.status, json, ok: res.status >= 200 && res.status < 300 };
}

module.exports = {
  readConfig,
  authHeader,
  redact,
  request,
  getRoot,
  getMe,
  verifyInstance,
  getProjectTypes,
  resolveTypeName,
  attachFile,
};
