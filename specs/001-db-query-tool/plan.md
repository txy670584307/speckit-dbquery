# 实现计划：数据库查询工具

**分支**: `001-db-query-tool` | **日期**: 2026-05-25 | **规格**: [spec.md](./spec.md)

**输入**: 来自 `specs/001-db-query-tool/spec.md` 的功能规格说明书

---

## 摘要

构建一个内网数据库查询工具。用户通过 JDBC URL 添加 PostgreSQL 数据库连接，系统自动获取 metadata（表名、视图名、列名及数据类型），缓存到本地 SQLite 数据库。用户可在 Monaco Editor 编辑器中手写 SQL 查询，也可通过自然语言描述生成 SQL。所有 SQL 均经过 sqlglot 解析验证——仅允许 SELECT 语句，无 LIMIT 的查询自动追加 `LIMIT 1000`。查询结果以 JSON 格式（camelCase）返回，前端以表格形式渲染展示。

## 技术上下文

| 项目 | 内容 |
|------|------|
| **语言/版本** | Python 3.11+ (后端), JavaScript/TypeScript (前端) |
| **主要依赖** | 后端: FastAPI, sqlglot, httpx, aiosqlite, psycopg (异步), Pydantic; 前端: Vue 2, Vue Router, Element UI, Monaco Editor |
| **跨域** | FastAPI `CORSMiddleware`，`allow_origins=["*"]`，允许所有来源访问 |
| **存储** | SQLite（本地 metadata 缓存），PostgreSQL（目标查询数据库） |
| **测试** | 后端: pytest; 前端 v1: 手动测试 |
| **目标平台** | 后端: Linux/Windows 服务器; 前端: 桌面浏览器 |
| **项目类型** | Web 应用（后端 API + 前端 SPA） |
| **性能目标** | 查询结果 < 5 秒，metadata 获取 < 30 秒，1000 行表格流畅滚动 |
| **约束** | 无身份认证，camelCase JSON 输出，仅 SELECT 查询，单次最多 1000 行 |
| **规模/范围** | 单次内网部署，并发连接 < 100 |

## 宪法检查

*门控：Phase 0 研究前必须通过。Phase 1 设计后需复检。*

| 原则 | 状态 | 证据 |
|------|------|------|
| I. 类型安全与 Ergonomic 代码 | ✅ 通过 | 后端: 严格类型标注的 Python（Pydantic 模型）。前端: 严格类型标注的 TypeScript |
| II. Pydantic 数据建模 | ✅ 通过 | 所有数据模型（DbCreateRequest、DbResponse、ColumnInfo、QueryRequest、NaturalQueryRequest、QueryResultResponse）均定义为 Pydantic BaseModel |
| III. JSON camelCase 约定 | ✅ 通过 | Pydantic `alias_generator` 配置 camelCase 转换。所有 API 契约使用 camelCase |
| IV. 无身份认证 | ✅ 通过 | 无认证中间件，无 token/会话管理。CORS 对所有来源开放 |

## 项目结构

### 文档结构（本功能）

```
specs/001-db-query-tool/
├── plan.md              # 本文件（实现计划）
├── spec.md              # 功能规格说明书
├── research.md          # 技术调研（Phase 0 产出）
├── data-model.md        # 数据模型（Phase 1 产出）
├── quickstart.md        # 快速开始指南（Phase 1 产出）
├── contracts/
│   └── api.md           # API 接口契约（Phase 1 产出）
├── checklists/
│   └── requirements.md  # 需求质量检查清单
└── tasks.md             # 任务清单（/speckit-tasks 产出）
```

### 源代码结构

```
backend/
├── main.py              # FastAPI 应用入口，CORS 中间件，lifespan 事件
├── config.py            # 环境配置（Pydantic Settings）
├── database.py          # aiosqlite：本地 SQLite 初始化和连接管理
├── models.py            # Pydantic schemas（camelCase 输出）
├── routes/
│   ├── dbs.py           # GET/POST /api/v1/dbs，GET /api/v1/dbs/{db_name}
│   ├── query.py         # POST /api/v1/dbs/{db_name}/query
│   └── nl_query.py      # POST /api/v1/dbs/{db_name}/query/natural
├── services/
│   ├── pg_service.py    # PostgreSQL 操作：JDBC URL 解析→异步连接，metadata 获取，查询执行
│   ├── sql_validator.py # sqlglot 验证：仅允许 SELECT，LIMIT 检测/追加
│   └── llm_service.py   # httpx：OpenAI 兼容 Chat Completions API 调用
└── tests/
    ├── test_sql_validator.py
    ├── test_pg_service.py
    └── test_api.py

frontend/
├── src/
│   ├── components/
│   │   ├── DbList.vue            # 左侧数据库连接列表 + 添加功能
│   │   ├── TableTree.vue         # 表/视图树形展示组件
│   │   ├── SqlEditor.vue         # Monaco Editor 封装组件
│   │   └── ResultTable.vue       # 查询结果表格组件
│   ├── views/
│   │   └── QueryPage.vue         # 主查询页面（组合所有组件）
│   ├── services/
│   │   └── api.js                # axios API 调用封装
│   ├── router/
│   │   └── index.js
│   └── App.vue
├── public/
│   └── index.html
└── package.json

data/                               # 运行时自动创建
└── local.db                        # SQLite 数据库文件
```

**结构决策**: Web 应用，采用前后端分离。选用 plan 模板中的 Option 2（Web application）。

## 复杂度跟踪

> 无宪法违规。此表故意留空。

## 后端 API 端点汇总

所有端点前缀：`/api/v1`。所有 JSON 响应使用 camelCase 属性名。

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/v1/dbs` | 获取所有已连接的数据库列表 |
| `POST` | `/api/v1/dbs/{db_name}` | 添加数据库连接（JDBC URL），自动获取并缓存 metadata |
| `GET` | `/api/v1/dbs/{db_name}` | 获取指定连接的 metadata（表名、视图名、列信息） |
| `POST` | `/api/v1/dbs/{db_name}/query` | 执行 SQL 查询（仅 SELECT，自动追加 LIMIT 1000） |
| `POST` | `/api/v1/dbs/{db_name}/query/natural` | 自然语言生成 SQL 并执行 |

**关键设计决策**:
- 连接以 `db_name` 作为 API 路径中的唯一标识（而非数字 ID）
- 连接字符串使用 JDBC URL 格式（`jdbc:postgresql://...`），后端负责转换为异步驱动可用参数
- SQL 验证在查询执行前完成，语法错误立即返回，不产生无效数据库请求
- CORS 中间件允许所有 origin，适配前后端分离部署和内网使用场景

## 执行阶段

### Phase 1: 项目初始化（Setup）
创建项目骨架、配置依赖、搭建目录结构、配置 CORS 中间件。

- 后端：uv 初始化 FastAPI 项目，安装 sqlglot / httpx / aiosqlite / psycopg / Pydantic
- 前端：Vue CLI 初始化 Vue 2 项目，安装 Element UI / Monaco Editor / axios / vue-router

### Phase 2: 基础设施（Foundational）
构建所有用户故事的前置依赖，本阶段完成前不能开始任何用户故事开发。

- 本地 SQLite 存储（`aiosqlite` 初始化，建表：`db_connections`、`table_metadata`）
- Pydantic 数据模型（请求/响应 schema，camelCase 别名生成器）
- PostgreSQL 连接服务（JDBC URL 解析 → 异步连接驱动）
- sqlglot SQL 验证器（语法解析、语句类型检测、LIMIT 检测与追加）

### Phase 3: 用户故事 1 — 添加数据库连接并浏览表/视图 (P1) 🎯 MVP
用户通过 JDBC URL 连接 PostgreSQL，系统自动获取 metadata 并展示。

- `GET /api/v1/dbs` — 列出所有已保存连接
- `POST /api/v1/dbs/{db_name}` — 添加连接 → 连接 PostgreSQL → 查询 `information_schema` → 缓存到 SQLite → 返回连接信息
- `GET /api/v1/dbs/{db_name}` — 返回缓存的 metadata（表/视图树形数据）
- 前端：DbList 组件（连接列表 + 添加表单），TableTree 组件（表/视图树）

### Phase 4: 用户故事 2 — 手写 SQL 查询 (P2)
SQL 编辑器集成，查询执行与结果展示。

- `POST /api/v1/dbs/{db_name}/query` — 接收 SQL → sqlglot 验证 → 追加 LIMIT → 执行 → 返回 JSON 结果
- 前端：SqlEditor 组件（Monaco Editor 封装），ResultTable 组件（Element UI 表格）

### Phase 5: 用户故事 4 — Metadata 缓存管理 (P2)
缓存复用、手动刷新、过期数据处理。

- 打开已有连接时优先展示缓存数据
- 手动刷新按钮触发重新获取 metadata
- 网络失败时保留旧缓存并提示用户

### Phase 6: 用户故事 3 — 自然语言生成 SQL (P3)
LLM 集成，自然语言到 SQL 的生成与执行管道。

- `POST /api/v1/dbs/{db_name}/query/natural` — 接收自然语言 → 注入 metadata 上下文 → 调用 LLM → 生成 SQL → 验证 → 执行 → 返回结果
- 前端：自然语言输入框（可切换 SQL 编辑器 / 自然语言模式）

### Phase 7: 打磨与横切关注点（Polish）
错误处理完善、加载状态、边界情况处理、最终验证。

- 统一的错误响应格式
- 连接失败 / 查询超时 / LLM 不可用等异常场景的用户提示
- 空表、空结果的友好展示
- 多连接切换时的状态管理
