# LLMOps 课程进度

AI Agent 全栈开发工程师课程的学习进度网页，共 546 节视频、8 个阶段、24 个周单元。

线上地址：<https://llmops-course-progress.itsjtide.workers.dev>

## 进度保存在哪里

- 勾选课程后，进度会立即写入当前浏览器的 `localStorage`，键名为 `llmops-course-progress:v2`。
- 配置同步码后，页面还会自动同步到 Cloudflare KV 命名空间 `llmops-course-progress-progress`，KV 键名为 `llmops-course-progress:v1`。
- 同步码只保存在当前浏览器的 `localStorage` 中，键名为 `llmops-course-sync-secret:v1`，并通过 HTTPS 的 `Authorization` 请求头发送给本项目 Worker。
- 本地和云端都有数据时，以 `updatedAt` 较新的版本为准。断网时仍可继续勾选，恢复联网后会再次同步。
- 页面右上角也支持导出、导入 JSON 备份。

## 本地运行

由于页面使用 ES modules，请通过本地 HTTP 服务运行，不要直接双击 HTML 文件：

```bash
python3 -m http.server 4173 --bind 127.0.0.1
```

然后访问 <http://127.0.0.1:4173>。

## 测试与构建

```bash
npm test
npm run build
```

构建产物会生成在 `dist/`，不会提交到 Git。

## Cloudflare 部署

项目使用一个独立的 Cloudflare Worker、静态资源绑定和 KV 命名空间。首次部署时 Wrangler 会自动创建 KV，并把资源 ID 写入 `wrangler.jsonc`。

```bash
npx wrangler login
npm run deploy
npx wrangler secret put SYNC_SECRET
```

`SYNC_SECRET` 是访问 `/api/progress` 的同步码，不要写入源码或提交到 Git。

接口：

- `GET /health`：服务健康检查。
- `GET /api/progress`：读取 KV 进度，需要 Bearer 同步码。
- `PUT /api/progress`：写入 KV 进度，需要 Bearer 同步码。
