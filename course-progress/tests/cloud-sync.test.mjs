import assert from "node:assert/strict";
import test from "node:test";

import {
  LEGACY_STATE_KEY,
  LOCAL_STATE_KEY,
  chooseInitialProgress,
  createProgressClient,
  loadLocalProgress,
  normalizeEndpoint,
  saveLocalProgress,
} from "../cloud-sync.mjs";

function memoryStorage(initial = {}) {
  const values = new Map(Object.entries(initial));
  return {
    getItem: (key) => values.get(key) ?? null,
    setItem: (key, value) => values.set(key, value),
    removeItem: (key) => values.delete(key),
    values,
  };
}

const ids = new Set(["08684e280591", "c1320ae66b44"]);

test("normalizes an HTTPS Worker endpoint", () => {
  assert.equal(
    normalizeEndpoint("https://progress.example.workers.dev/api/progress?ignored=yes"),
    "https://progress.example.workers.dev",
  );
  assert.throws(() => normalizeEndpoint("http://progress.example.com"), /HTTPS/);
});

test("migrates the original checkbox array without losing completed lessons", () => {
  const storage = memoryStorage({
    [LEGACY_STATE_KEY]: JSON.stringify(["08684e280591", "unknown"]),
  });
  const local = loadLocalProgress(storage, ids);
  assert.equal(local.exists, true);
  assert.deepEqual(local.state.completed, ["08684e280591"]);

  saveLocalProgress(storage, local.state, ids);
  assert.equal(storage.getItem(LEGACY_STATE_KEY), null);
  assert.deepEqual(JSON.parse(storage.getItem(LOCAL_STATE_KEY)).completed, ["08684e280591"]);
});

test("uses the newer side during initial synchronization", () => {
  const local = {
    exists: true,
    state: { updatedAt: "2026-08-23T08:00:00.000Z", completed: ["08684e280591"] },
  };
  assert.equal(chooseInitialProgress(local, {
    updatedAt: "2026-08-23T07:00:00.000Z",
    completed: [],
  }), "upload-local");
  assert.equal(chooseInitialProgress(local, {
    updatedAt: "2026-08-23T09:00:00.000Z",
    completed: ["c1320ae66b44"],
  }), "use-remote");
});

test("uploads a legacy local record when the cloud is empty", () => {
  const local = {
    exists: true,
    state: { updatedAt: null, completed: ["08684e280591"] },
  };
  assert.equal(chooseInitialProgress(local, {
    updatedAt: null,
    completed: [],
  }), "upload-local");
});

test("sends the sync code only to the progress API", async () => {
  let request;
  const client = createProgressClient({
    endpoint: "https://progress.example.workers.dev",
    secret: "sync-only-secret",
    fetchImpl: async (url, options) => {
      request = { url, options };
      return new Response(JSON.stringify({
        version: 1,
        updatedAt: "2026-08-23T08:00:00.000Z",
        completed: [],
      }), { status: 200, headers: { "Content-Type": "application/json" } });
    },
  });
  await client.put(["08684e280591"]);
  assert.equal(request.url, "https://progress.example.workers.dev/api/progress");
  assert.equal(request.options.headers.Authorization, "Bearer sync-only-secret");
  assert.deepEqual(JSON.parse(request.options.body), { completed: ["08684e280591"] });
});
