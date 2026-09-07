# Bug Report - 2025年01月01日

## Bug 1: 缺少 @login_required 装饰器

### 问题描述

在 `AnalysisHandler` 类的 `get_app_analysis` 方法中，缺少 `@login_required` 装饰器，导致未认证的用户也能访问该方法，存在潜在的安全隐患。

### 复现步骤

1. 调用 API 接口获取分析数据。
2. 没有进行身份验证的情况下，可以直接访问 `get_app_analysis` 接口，但是无法获取到 `current_user` 信息。
3. 返回未授权或错误的响应，或直接能访问到数据。

### 影响范围

所有未认证的用户都能访问需要登录的分析接口，可能会泄露敏感的用户数据或统计信息。

### 解决方案

在 `get_app_analysis` 方法上添加 `@login_required` 装饰器，确保只有认证过的用户才能访问该接口。

```python
@inject
@dataclass
class AnalysisHandler:
    """统计分析处理器"""
    analysis_service: AnalysisService

    @login_required  # 添加 @login_required 装饰器
    def get_app_analysis(self, app_id: UUID):
        """根据传递的应用id获取应用的统计信息"""
        app_analysis = self.analysis_service.get_app_analysis(app_id, current_user)
        return success_json(app_analysis)
```

## Bug 2: 模型 updated_at 字段不会自动更新

### 问题描述

在表模型中添加了 `updated_at` 字段并配置 `server_onupdate=text("CURRENT_TIMESTAMP(0)")`，但是在数据更新的时候，该字段并不会自动更新。

### 复现步骤

1. 调用任意一个更新 Model 的 API 接口，例如：`更新应用基础信息`；
2. 更新 Model 信息后，`updated_at` 字段并不会记录更新的时间；

### 影响范围

所有 Model 在更新的时候均不会更新 `updated_at` 字段，导致数据信息记录缺失。

### 解决方案

为所有 Model 的 `updated_at` 字段添加 `onupdate` 参数，并传递 `datetime.now` 函数作为参数，并剔除 `server_onupdate`，使用
Python 的表达式动态计算更新事件，并剔除在服务中，手动设置 `updated_at` 字段的函数，修改如下：

```python
from datetime import datetime

updated_at = Column(
    DateTime,
    nullable=False,
    server_default=text("CURRENT_TIMESTAMP(0)"),
    onupdate=datetime.now,
)
```