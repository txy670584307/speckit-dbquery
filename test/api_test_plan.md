# 后端接口测试计划

## 1. 概述

本文档描述 DB Query Tool 后端 API 的测试范围、策略和方法。后端基于 FastAPI，部署于 `http://127.0.0.1:8000`，所有 API 前缀为 `/api/v1`。

## 2. 测试范围

| 模块 | 端点 | 说明 |
|------|------|------|
| 连接管理 | `GET /api/v1/dbs` | 获取所有已保存数据库连接 |
| 连接管理 | `POST /api/v1/dbs/{db_name}` | 添加新数据库连接 |
| Metadata | `GET /api/v1/dbs/{db_name}` | 获取数据库表/视图 metadata |
| Metadata | `GET /api/v1/dbs/{db_name}?refresh=true` | 强制刷新 metadata 缓存 |
| 查询执行 | `POST /api/v1/dbs/{db_name}/query` | 执行 SQL 查询 |
| 自然语言 | `POST /api/v1/dbs/{db_name}/query/natural` | 自然语言生成 SQL 并执行 |

## 3. 测试策略

### 3.1 层级

- **单元测试**：service 层独立测试（sql_validator、pg_service）
- **集成测试**：route 层 + 真实 PostgreSQL + SQLite 本地存储
- **端到端测试**：完整请求链（HTTP 请求 → 业务逻辑 → 数据库 → 响应）

### 3.2 测试数据

使用 Docker 容器中的测试数据库 `testdb`（localhost:5432），包含 `users`、`products`、`sales.orders`、`sales.order_items` 四张表。

### 3.3 环境要求

- 后端服务运行中（`uv run uvicorn backend.main:app --port 8000`）
- PostgreSQL 容器运行中（port 5432）
- （可选）Ollama 运行中（port 11434，用于 NL 测试）

## 4. 测试分类

### 4.1 正常流程（Happy Path）

验证 API 在正常输入下的正确行为。

### 4.2 异常流程（Error Path）

验证 API 在无效输入、资源不存在、服务不可用等异常情况下的错误处理和响应格式。

### 4.3 边界条件（Boundary）

验证空列表、空结果、最大长度、超时等边界情况。

## 5. 通过标准

- 正常流程：HTTP 状态码正确 + 响应体字段完整 + 数据类型正确
- 异常流程：HTTP 4xx/5xx + 统一错误格式 `{"detail": {"code", "message", "location?"}}`
- 边界条件：系统不崩溃、响应在合理时间内返回
