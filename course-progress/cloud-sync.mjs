export const LOCAL_STATE_KEY = "llmops-course-progress:v2";
export const LEGACY_STATE_KEY = "llmops-course-progress:v1";
export const SECRET_KEY = "llmops-course-sync-secret:v1";

const DATE_PATTERN = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/;

export function normalizeEndpoint(value) {
  const raw = String(value || "").trim();
  if (!raw) throw new TypeError("云同步地址未配置");

  let url;
  try {
    url = new URL(raw);
  } catch {
    throw new TypeError("云同步地址格式不正确");
  }

  const isLocal = ["localhost", "127.0.0.1"].includes(url.hostname);
  if (url.protocol !== "https:" && !(isLocal && url.protocol === "http:")) {
    throw new TypeError("云同步地址必须使用 HTTPS");
  }

  url.search = "";
  url.hash = "";
  url.pathname = url.pathname.replace(/\/api\/progress\/?$/, "").replace(/\/$/, "");
  return url.toString().replace(/\/$/, "");
}

export function normalizeProgress(value, validIds) {
  const validIdSet = validIds instanceof Set ? validIds : new Set(validIds);
  const completed = Array.isArray(value?.completed)
    ? [...new Set(value.completed.filter((id) => validIdSet.has(id)))]
    : [];
  const updatedAt = typeof value?.updatedAt === "string" && DATE_PATTERN.test(value.updatedAt)
    && Number.isFinite(Date.parse(value.updatedAt))
    ? new Date(value.updatedAt).toISOString()
    : null;

  return { version: 2, updatedAt, completed };
}

export function loadLocalProgress(storage, validIds) {
  try {
    const current = JSON.parse(storage.getItem(LOCAL_STATE_KEY) || "null");
    if (current && Array.isArray(current.completed)) {
      return { exists: true, state: normalizeProgress(current, validIds) };
    }
  } catch {
    // Try the legacy checkbox array below.
  }

  try {
    const legacy = JSON.parse(storage.getItem(LEGACY_STATE_KEY) || "null");
    if (Array.isArray(legacy)) {
      return {
        exists: legacy.length > 0,
        state: normalizeProgress({ completed: legacy, updatedAt: null }, validIds),
      };
    }
  } catch {
    // An invalid legacy value is equivalent to no local state.
  }

  return {
    exists: false,
    state: { version: 2, updatedAt: null, completed: [] },
  };
}

export function saveLocalProgress(storage, state, validIds) {
  const normalized = normalizeProgress(state, validIds);
  storage.setItem(LOCAL_STATE_KEY, JSON.stringify(normalized));
  storage.removeItem(LEGACY_STATE_KEY);
  return normalized;
}

export function chooseInitialProgress(local, remote) {
  const localHasProgress = local.state.completed.length > 0;
  if (!remote.updatedAt) return localHasProgress ? "upload-local" : "already-synced";
  if (!local.exists) return "use-remote";
  if (!local.state.updatedAt) {
    return localHasProgress && remote.completed.length === 0 ? "upload-local" : "use-remote";
  }

  return Date.parse(local.state.updatedAt) > Date.parse(remote.updatedAt)
    ? "upload-local"
    : "use-remote";
}

export function createProgressClient({ endpoint, secret, fetchImpl = fetch }) {
  const baseUrl = normalizeEndpoint(endpoint);
  const authorization = String(secret || "").trim();
  if (!authorization) throw new TypeError("请填写同步码");

  async function request(method, body) {
    const response = await fetchImpl(`${baseUrl}/api/progress`, {
      method,
      headers: {
        Authorization: `Bearer ${authorization}`,
        ...(body ? { "Content-Type": "application/json" } : {}),
      },
      ...(body ? { body: JSON.stringify(body) } : {}),
    });

    let payload = null;
    try {
      payload = await response.json();
    } catch {
      // Cloudflare platform failures may return a non-JSON body.
    }

    if (!response.ok) {
      const error = new Error(payload?.error || `云同步请求失败（${response.status}）`);
      error.status = response.status;
      throw error;
    }
    return payload;
  }

  return {
    get: () => request("GET"),
    put: (completed) => request("PUT", { completed }),
  };
}
