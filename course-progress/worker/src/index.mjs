const PROGRESS_KEY = "llmops-course-progress:v1";
const ID_PATTERN = /^[a-f0-9]{12}$/;
const MAX_COMPLETED_ITEMS = 600;

function configuredOrigins(env) {
  return String(env.ALLOWED_ORIGINS || "")
    .split(",")
    .map((origin) => origin.trim())
    .filter(Boolean);
}

export function isAllowedOrigin(origin, requestUrl, env) {
  if (!origin) return true;
  if (origin === new URL(requestUrl).origin) return true;
  if (configuredOrigins(env).includes(origin)) return true;
  return /^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(origin);
}

function corsHeaders(origin) {
  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Methods": "GET, PUT, OPTIONS",
    "Access-Control-Allow-Headers": "Authorization, Content-Type",
    "Access-Control-Max-Age": "86400",
    "Vary": "Origin",
  };
}

function jsonResponse(payload, status, origin = "") {
  return new Response(JSON.stringify(payload), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
      ...(origin ? corsHeaders(origin) : {}),
    },
  });
}

async function secureEqual(value, expected) {
  const encoder = new TextEncoder();
  const [valueHash, expectedHash] = await Promise.all([
    crypto.subtle.digest("SHA-256", encoder.encode(value)),
    crypto.subtle.digest("SHA-256", encoder.encode(expected)),
  ]);
  const left = new Uint8Array(valueHash);
  const right = new Uint8Array(expectedHash);
  let difference = left.length ^ right.length;
  for (let index = 0; index < Math.max(left.length, right.length); index += 1) {
    difference |= (left[index] || 0) ^ (right[index] || 0);
  }
  return difference === 0;
}

async function isAuthorized(request, secret) {
  const authorization = request.headers.get("Authorization") || "";
  const match = authorization.match(/^Bearer\s+(.+)$/i);
  return Boolean(match && await secureEqual(match[1], secret));
}

export function normalizeCompleted(value) {
  if (!Array.isArray(value) || value.length > MAX_COMPLETED_ITEMS) {
    throw new TypeError("completed 必须是最多包含 600 项的数组");
  }

  const completed = [...new Set(value)];
  if (completed.some((id) => typeof id !== "string" || !ID_PATTERN.test(id))) {
    throw new TypeError("completed 中包含无效课程 ID");
  }
  return completed.sort();
}

async function handleProgress(request, env, origin) {
  if (!env.SYNC_SECRET) {
    return jsonResponse({ error: "SYNC_SECRET 尚未配置" }, 503, origin);
  }
  if (!await isAuthorized(request, env.SYNC_SECRET)) {
    return jsonResponse({ error: "同步码不正确" }, 401, origin);
  }

  if (request.method === "GET") {
    const saved = await env.PROGRESS.get(PROGRESS_KEY, "json");
    return jsonResponse(saved || {
      version: 1,
      updatedAt: null,
      completed: [],
    }, 200, origin);
  }

  if (request.method === "PUT") {
    let body;
    try {
      body = await request.json();
    } catch {
      return jsonResponse({ error: "请求内容不是有效 JSON" }, 400, origin);
    }

    let completed;
    try {
      completed = normalizeCompleted(body?.completed);
    } catch (error) {
      return jsonResponse({ error: error.message }, 400, origin);
    }

    const progress = {
      version: 1,
      updatedAt: new Date().toISOString(),
      completed,
    };
    await env.PROGRESS.put(PROGRESS_KEY, JSON.stringify(progress));
    return jsonResponse(progress, 200, origin);
  }

  return jsonResponse({ error: "Method not allowed" }, 405, origin);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const origin = request.headers.get("Origin") || "";

    if (url.pathname === "/health") {
      return jsonResponse({ ok: true, storage: "cloudflare-kv" }, 200, origin);
    }

    if (url.pathname === "/api/progress") {
      if (!isAllowedOrigin(origin, request.url, env)) {
        return jsonResponse({ error: "Origin not allowed" }, 403);
      }
      if (request.method === "OPTIONS") {
        return new Response(null, { status: 204, headers: corsHeaders(origin) });
      }
      return handleProgress(request, env, origin);
    }

    return env.ASSETS.fetch(request);
  },
};
