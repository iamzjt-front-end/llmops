# Bug Report - 2025年01月02日

## Bug 1: 修复 middleware.py 中未判断 account 是否存在

### 问题描述

在 `middleware.py` 中，使用解析的 `access_token` 查找账号，未判断账号是否存在直接返回，会导致 API 接口状态为 `fail`
，但是实际却是未授权，前端的跳转可能会发生错误。

### 复现步骤

1. 在前端登录账号后，后端重新构建项目时覆盖数据库；
2. 这时候前端存储了 `access_token`，该 `access_token` 为旧 token，是找不到账号的；
3. 但是接口返回的状态为 `fail`，前端不会重新跳转到登录页面，只能手动输入；

### 影响范围

在开发时覆盖数据库会导致页面只能手动切换到登录页面才能重新登录。

### 解决方案

在 `middleware.py` 中判断 `account` 是否存在，存在才返回，否则抛出错误。

```python
account = self.account_service.get_account(account_id)
if not account:
    raise UnauthorizedException("当前账户不存在，请重新登录")
return account
```