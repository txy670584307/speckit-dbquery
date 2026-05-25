# Research: 数据库查询工具

## 1. SQL 解析器选择

**Decision**: sqlglot

**Rationale**: sqlglot 是纯 Python SQL 解析器，支持 PostgreSQL 方言，可解析和转译多种 SQL 方言。能够：
- 验证 SQL 语法正确性（parse → 捕获异常）
- 判断语句类型（仅允许 SELECT）
- 检测是否存在 LIMIT 子句
- 支持对 AST 进行修改（自动追加 LIMIT）

**Alternatives considered**:
- sqlparse（python-sqlparse）：仅做格式化/分词，不做完整 AST 解析，无法可靠检测非 SELECT 语句。
- pglast（libpg_query 的 Python 绑定）：PostgreSQL 原生解析器，精确但仅支持 PG，且需要编译 C 扩展。

## 2. PostgreSQL Metadata 获取

**Decision**: information_schema（标准 SQL 方式）

**Rationale**:
- `information_schema.tables` — 获取表/视图列表（过滤 table_type）
- `information_schema.columns` — 获取列的详细信息（名、类型、是否可空）
- 跨 PostgreSQL 版本兼容
- 标准 SQL，代码可读性高

**Alternatives considered**:
- pg_catalog（PostgreSQL 系统目录）：更详细（注释、约束等），但查询更复杂且版本间可能有差异。不适合 v1 范围。
- sqlalchemy inspector：引入额外依赖，且 sqlalchemy 与 FastAPI 结合需要额外的会话管理。

## 3. Monaco Editor 集成

**Decision**: monaco-editor npm 包 + 手动 webpack worker 配置

**Rationale**:
- Monaco Editor 提供 SQL 语法高亮、自动补全、错误标记
- Vue 2 下手动集成（避免额外封装库如 vue-monaco-editor 的维护风险）
- 需配置 monaco-editor-webpack-plugin 处理 web workers

**Alternatives considered**:
- CodeMirror 6：更轻量但 SQL 模式不如 Monaco 成熟。
- Ace Editor：相对陈旧，SQL 高亮功能有限。

## 4. LLM 服务集成

**Decision**: httpx 调用 OpenAI Chat Completions 兼容 API

**Rationale**:
- 大多数 LLM 服务（OpenAI、Azure OpenAI、本地 vLLM/Ollama 等）都兼容 `/v1/chat/completions` 格式
- httpx 支持 async/await，与 FastAPI 异步模型天然适配
- 系统提示中注入 metadata context（表名、列名、关系）

**Alternatives considered**:
- openai 官方 Python SDK：功能全面但引入额外依赖，且可能限制非 OpenAI 服务。此处仅需 chat/completions 端点。
- langchain：过度工程化，对于单一 NL→SQL 任务过重。

## 5. SQLite 本地存储

**Decision**: aiosqlite（async SQLite driver）

**Rationale**:
- 存储连接字符串和 metadata 缓存
- aiosqlite 与 FastAPI 异步模型匹配
- 轻量零配置，符合内部工具定位

**Schema 设计**:
```sql
CREATE TABLE db_connections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    connection_string TEXT NOT NULL,
    db_type TEXT DEFAULT 'postgresql',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE table_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    connection_id INTEGER NOT NULL,
    schema_name TEXT NOT NULL,
    table_name TEXT NOT NULL,
    table_type TEXT NOT NULL,  -- 'table' or 'view'
    columns_json TEXT NOT NULL, -- JSON array of {name, type, nullable}
    refreshed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (connection_id) REFERENCES db_connections(id) ON DELETE CASCADE
);
```

## 6. 前后端通信

**Decision**: FastAPI REST API + JSON (camelCase)

**Rationale**:
- 所有查询均为请求-响应模式，无需 WebSocket
- FastAPI 自带 OpenAPI 文档生成
- JSON 输出格式天然适合前端 DataTable 渲染
- camelCase 符合宪法 III 要求（Python snake_case → 序列化为 camelCase）

## Summary

| 领域 | 选择 | 关键理由 |
|------|------|---------|
| SQL 解析 | sqlglot | 纯 Python，AST 级别控制 |
| PG metadata | information_schema | 标准 SQL，跨版本兼容 |
| SQL 编辑器 | Monaco Editor | 成熟 SQL 支持，Vue 2 可集成 |
| LLM 集成 | httpx + OpenAI-compat API | 异步，广泛兼容 |
| 本地存储 | aiosqlite | 异步，零配置 |
| 前后端通信 | FastAPI REST + JSON | 与堆栈一致，文档自动生成 |
