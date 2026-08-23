import assert from "node:assert/strict";
import test from "node:test";

import worker, { isAllowedOrigin, normalizeCompleted } from "../worker/src/index.mjs";

function createEnvironment(overrides = {}) {
  const records = new Map();
  return {
    ALLOWED_ORIGINS: "http://127.0.0.1:4173",
    SYNC_SECRET: "correct-horse-battery-staple",
    PROGRESS: {
      async get(key, type) {
        const value = records.get(key);
        return type === "json" && value ? JSON.parse(value) : value;
      },
      async put(key, value) {
        records.set(key, value);
      },
    },
    ASSETS: { fetch: async () => new Response("asset") },
    ...overrides,
  };
}

function progressRequest(method = "GET", options = {}) {
  const headers = new Headers({
    Origin: options.origin || "https://llmops-course-progress.itsjtide.workers.dev",
    Authorization: "Bearer correct-horse-battery-staple",
    ...options.headers,
  });
  return new Request("https://llmops-course-progress.itsjtide.workers.dev/api/progress", {
    method,
    headers,
    body: options.body,
  });
}

test("allows same-origin and local development requests", () => {
  const env = createEnvironment();
  const requestUrl = "https://llmops-course-progress.itsjtide.workers.dev/api/progress";
  assert.equal(isAllowedOrigin("https://llmops-course-progress.itsjtide.workers.dev", requestUrl, env), true);
  assert.equal(isAllowedOrigin("http://127.0.0.1:4173", requestUrl, env), true);
  assert.equal(isAllowedOrigin("https://attacker.example", requestUrl, env), false);
});

test("normalizes valid lesson ids and rejects malformed data", () => {
  assert.deepEqual(normalizeCompleted(["c1320ae66b44", "08684e280591", "c1320ae66b44"]), [
    "08684e280591",
    "c1320ae66b44",
  ]);
  assert.throws(() => normalizeCompleted(["not-an-id"]), /无效课程 ID/);
});

test("requires the configured sync secret", async () => {
  const response = await worker.fetch(progressRequest("GET", {
    headers: { Authorization: "Bearer wrong-secret" },
  }), createEnvironment());
  assert.equal(response.status, 401);
});

test("writes progress to KV and reads it back", async () => {
  const env = createEnvironment();
  const putResponse = await worker.fetch(progressRequest("PUT", {
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ completed: ["c1320ae66b44", "08684e280591"] }),
  }), env);
  assert.equal(putResponse.status, 200);
  const saved = await putResponse.json();
  assert.deepEqual(saved.completed, ["08684e280591", "c1320ae66b44"]);
  assert.match(saved.updatedAt, /^\d{4}-\d{2}-\d{2}T/);

  const getResponse = await worker.fetch(progressRequest(), env);
  assert.equal(getResponse.status, 200);
  assert.deepEqual(await getResponse.json(), saved);
});

test("rejects browser requests from an unrelated origin", async () => {
  const response = await worker.fetch(progressRequest("GET", {
    origin: "https://attacker.example",
  }), createEnvironment());
  assert.equal(response.status, 403);
  assert.equal(response.headers.get("Access-Control-Allow-Origin"), null);
});

test("serves static assets outside the API", async () => {
  const response = await worker.fetch(
    new Request("https://llmops-course-progress.itsjtide.workers.dev/"),
    createEnvironment(),
  );
  assert.equal(await response.text(), "asset");
});
