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

## 7. 数据导出 — CSV 生成

**Decision**: Python 标准库 `csv` 模块

**Rationale**:
- `csv.writer` 默认遵循 RFC 4180：逗号分隔、双引号转义包含分隔符/换行符的字段
- 零外部依赖，与 Python 内置环境一致
- 使用 `io.StringIO` 构造内存中的 CSV 缓冲区，避免写入临时文件
- 从 QueryResult.rows 直接转换为 CSV 行，列名作为首行表头

**Alternatives considered**:
- pandas（`df.to_csv`）：引入额外重量级依赖，对于简单的行→CSV 转换过度工程化。
- tablib：额外依赖，本项目仅需 CSV + JSON，无需通用数据交换库。

## 8. 数据导出 — JSON 生成

**Decision**: Python 标准库 `json` 模块

**Rationale**:
- `json.dumps(rows, ensure_ascii=False, indent=2)` 生成可读的标准 JSON
- 输出格式：`[{"col1": val1, "col2": val2}, ...]`，键名使用 camelCase（与 FR-008 一致）
- 零外部依赖
- 使用 `io.StringIO` 构建内存缓冲区

**Alternatives considered**:
- orjson：性能更快但需单独安装，本项目 1000 行数据量级下标准库 json 已足够。

## 9. 文件下载与 BOM 处理

**Decision**: FastAPI `StreamingResponse` 触发浏览器下载；CSV 文件添加 UTF-8 BOM

**Rationale**:
- `StreamingResponse(iterable, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=..."})` 标准文件下载模式
- CSV 添加 `\ufeff`（UTF-8 BOM）以兼容 Excel 打开 CSV 时正确识别 UTF-8 编码的中文字符
- JSON 使用 `application/json` media type，UTF-8 without BOM

**Alternatives considered**:
- 前端生成下载：大数据量内存占用高，CSV 转义逻辑复杂。后端生成更可靠。

## 10. CLI 自动化导出

**Decision**: API 查询参数 `?export=csv|json` + 可选 `output_path`

**Rationale**:
- 复用现有 `POST /api/v1/dbs/{db_name}/query` 端点，添加 `export` 查询参数
- `export=csv` 或 `export=json` 时返回文件流而非 JSON body
- `output_path` 参数（可选）指定服务器端保存路径；未指定时返回标准下载响应
- 可通过 curl 或 Claude Code Command 一键触发：`curl -X POST ... -d '{"sql":"..."}' "http://.../query?export=csv&output_path=./result.csv"`

**Alternatives considered**:
- 独立导出端点：增加路由数量，不如参数化现有端点简洁。
- WebSocket 推送：对于简单请求-响应模式过于复杂。

## Summary

| 领域 | 选择 | 关键理由 |
|------|------|---------|
| SQL 解析 | sqlglot | 纯 Python，AST 级别控制 |
| PG metadata | information_schema | 标准 SQL，跨版本兼容 |
| SQL 编辑器 | Monaco Editor | 成熟 SQL 支持，Vue 2 可集成 |
| LLM 集成 | httpx + OpenAI-compat API | 异步，广泛兼容 |
| 本地存储 | aiosqlite | 异步，零配置 |
| 前后端通信 | FastAPI REST + JSON | 与堆栈一致，文档自动生成 |
| CSV 导出 | Python 标准库 csv | RFC 4180，零依赖 |
| JSON 导出 | Python 标准库 json | 标准格式，零依赖 |
| 文件下载 | StreamingResponse + UTF-8 BOM (CSV) | 浏览器兼容，Excel 友好 |
| CLI 自动化 | 查询参数 `?export=csv\|json` | 复用现有端点，简洁 |
