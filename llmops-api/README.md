# LLMOps API 接口文档

# AI 应用模块

## 第 11 周开放 API 模块配置

启用账号登录、GitHub OAuth 和开放 API 前，请在 `.env` 中配置：

```dotenv
# HS256 密钥，生产环境请使用至少 32 字节的随机值
JWT_SECRET_KEY=

# GitHub OAuth（不使用 GitHub 登录时可留空）
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
GITHUB_REDIRECT_URI=
```

升级已有数据库：

```shell
flask --app app.http.app:app db upgrade
```
