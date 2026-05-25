# Tasks: 数据库查询工具

**输入**: 来自 `specs/001-db-query-tool/` 的设计文档
**前提**: plan.md（必需）、spec.md（必需，含用户故事）、data-model.md、contracts/api.md、research.md
**任务总数**: 29
**MVP 范围**: Phase 1（T001–T016），可独立交付：用户能添加数据库连接并浏览表/视图

## 格式: `[ID] [P?] [Story?] Description`

- **[P]**: 可并行执行（不同文件，无依赖）
- **[Story]**: 所属用户故事（US1/US2/US3/US4），仅用户故事阶段必填

---

## Phase 1: 基础设施 + 连接管理（MVP）

**目标**: 项目骨架 → SQLite + PostgreSQL 服务 → 连接管理 API → 前端连接列表和表/视图树。完成后用户可添加数据库连接并浏览 metadata。

**独立测试**: 启动后端和前端 → 输入 JDBC URL 添加连接 → 看到表/视图列表 → 展开查看列信息。

### Setup — 项目初始化

- [ ] T001 创建后端项目目录结构 `backend/` 及以下子目录: `routes/`, `services/`, `tests/`
- [ ] T002 初始化前端项目结构：Vue CLI 创建 Vue 2 项目至 `frontend/`，安装 Element UI、axios、vue-router、monaco-editor

### Foundational — 核心基础设施

- [ ] T003 [P] 创建 FastAPI 应用入口 `backend/main.py`：配置 CORS 中间件（`allow_origins=["*"]`），注册路由，lifespan 事件中初始化 SQLite
- [ ] T004 [P] 创建环境配置 `backend/config.py`：Pydantic Settings 读取 LLM_BASE_URL、LLM_API_KEY、LLM_MODEL、LOCAL_DB_PATH、API_PORT
- [ ] T005 创建 SQLite 存储层 `backend/database.py`：使用 aiosqlite 初始化数据库，建表 `db_connections`（id, db_name UNIQUE, db_url, db_type, created_at）和 `table_metadata`（id, db_name, schema_name, table_name, table_type, columns_json, refreshed_at）
- [ ] T006 [P] 创建 Pydantic 数据模型 `backend/models.py`：DbCreateRequest、DbResponse、ColumnInfo、TableMetadataResponse、QueryRequest、NaturalQueryRequest、QueryResultResponse，配置 camelCase alias_generator
- [ ] T007 创建 PostgreSQL 服务 `backend/services/pg_service.py`：解析 JDBC URL → asyncpg/psycopg 连接参数；实现 `connect_and_fetch_metadata(db_url)` 查询 information_schema.tables 和 information_schema.columns 获取表/视图/列信息；实现 `execute_query(conn, sql)` 执行 SELECT 并返回 QueryResult
- [ ] T008 [P] 创建 SQL 验证服务 `backend/services/sql_validator.py`：使用 sqlglot 解析 SQL → 验证语法 → 检测语句类型（拒绝非 SELECT） → 检测 LIMIT 子句（无则追加 `LIMIT 1000`）

### User Story 1 — 添加连接并浏览 metadata

- [ ] T009 [US1] 实现 `GET /api/v1/dbs` 端点 `backend/routes/dbs.py`：从 SQLite 查询所有保存的连接，返回 DbResponse 列表
- [ ] T010 [US1] 实现 `POST /api/v1/dbs/{db_name}` 端点 `backend/routes/dbs.py`：校验 db_name 和 db_url（JDBC 格式）→ 调用 pg_service 连接并获取 metadata → 写入 db_connections 和 table_metadata → 返回 DbResponse（含 tableCount）
- [ ] T011 [US1] 实现 `GET /api/v1/dbs/{db_name}` 端点 `backend/routes/dbs.py`：查询 SQLite 中该 db_name 的 table_metadata 记录 → 解析 columns_json → 返回 TableMetadataResponse 列表
- [ ] T012 [P] [US1] 创建前端 API 服务封装 `frontend/src/services/api.js`：axios 实例配置 baseURL，封装 getDbs()、addDb(name, url)、getDbMetadata(name) 方法
- [ ] T013 [US1] 创建 DbList 组件 `frontend/src/components/DbList.vue`：Element UI 列表展示已保存连接；对话框表单输入 db_name 和 JDBC URL 添加新连接
- [ ] T014 [P] [US1] 创建 TableTree 组件 `frontend/src/components/TableTree.vue`：Element UI 树形控件展示表/视图，按 schema 分组，展开后显示列名和数据类型
- [ ] T015 [US1] 创建主查询页面 `frontend/src/views/QueryPage.vue`：左右布局，左侧 DbList + TableTree，右侧占位（Phase 2 添加编辑器）
- [ ] T016 [US1] 配置 Vue Router `frontend/src/router/index.js`：注册 QueryPage 为默认路由

**Phase 1 检查点**: 启动服务 → 添加数据库连接 → 表/视图树正确展示 → MVP 可交付 ✅

---

## Phase 2: SQL 查询 + 缓存管理（US2 + US4）

**目标**: SQL 编辑器集成、查询执行、结果表格、metadata 缓存复用。

**独立测试**: 在已有连接上输入 SELECT 语句 → 执行 → 表格展示结果；关闭页面重开 → metadata 从缓存加载；测试自动 LIMIT 1000 和非 SELECT 拒绝。

### User Story 2 — 手写 SQL 查询

- [ ] T017 [US2] 实现 `POST /api/v1/dbs/{db_name}/query` 端点 `backend/routes/query.py`：读取 db_name 获取连接参数 → 调用 sql_validator 验证 SQL → 通过 pg_service 执行查询 → 返回 QueryResultResponse
- [ ] T018 [P] [US2] 创建 SqlEditor 组件 `frontend/src/components/SqlEditor.vue`：集成 Monaco Editor，配置 SQL 语法高亮，暴露 v-model 绑定 SQL 内容，emit execute 事件
- [ ] T019 [P] [US2] 创建 ResultTable 组件 `frontend/src/components/ResultTable.vue`：Element UI Table 组件，动态列渲染（columns → el-table-column），行数据绑定，底部显示 rowCount 和是否被截断的提示
- [ ] T020 [US2] 集成查询功能到 QueryPage `frontend/src/views/QueryPage.vue`：添加 SqlEditor 到右侧区域 + 执行按钮 + ResultTable；调用 api.js 的 queryDb() 方法并展示结果

### User Story 4 — Metadata 缓存管理

- [ ] T021 [US4] 实现缓存优先逻辑 `backend/services/pg_service.py` + `backend/routes/dbs.py`：GET /api/v1/dbs/{db_name} 优先返回 SQLite 缓存数据；添加 `?refresh=true` 查询参数支持时重新连接数据库刷新 metadata 并更新 SQLite
- [ ] T022 [US4] 添加缓存刷新入口到前端 `frontend/src/components/TableTree.vue`：添加"刷新"按钮，调用带 refresh 参数的 API；刷新失败时保留旧数据并提示用户

**Phase 2 检查点**: SQL 查询正常执行 → LIMIT 自动追加 → 非 SELECT 被拒绝 → 缓存复用工作 → 刷新功能正常 ✅

---

## Phase 3: 自然语言查询 + 打磨（US3 + Polish）

**目标**: LLM 集成实现自然语言→SQL 管道，完善错误处理、加载状态和边界情况。

**独立测试**: 用自然语言描述查询需求 → 系统自动生成 SQL 并执行返回结果；LLM 不可用时提示错误信息；各种边界情况均有合理提示。

### User Story 3 — 自然语言生成 SQL

- [ ] T023 [US3] 创建 LLM 服务 `backend/services/llm_service.py`：使用 httpx 异步调用 OpenAI 兼容 `/v1/chat/completions` API；构建 system prompt 注入当前连接的表/视图 metadata（表名、列名、关系）作为上下文；返回生成的 SQL 文本
- [ ] T024 [US3] 实现 `POST /api/v1/dbs/{db_name}/query/natural` 端点 `backend/routes/nl_query.py`：接收 natural 文本 → 从 SQLite 获取 metadata 上下文 → 调用 llm_service 生成 SQL → sql_validator 验证 → 若通过则查询执行返回结果；若 SQL 无效则返回错误含原始 SQL 供用户手动修正
- [ ] T025 [US3] 添加自然语言模式到前端 `frontend/src/views/QueryPage.vue`：在 SqlEditor 上方添加输入模式切换（SQL 编辑 / 自然语言）；自然语言模式下显示输入框 + 生成按钮
- [ ] T026 [US3] 实现 LLM 失败回退 `frontend/src/components/SqlEditor.vue` + `frontend/src/views/QueryPage.vue`：LLM 生成 SQL 失败时切换到 SQL 编辑模式并预填生成的 SQL，展示错误提示供用户手动修正后执行

### Polish — 横切打磨

- [ ] T027 统一后端错误处理 `backend/routes/`：所有端点使用统一的异常处理和 JSON 错误响应格式 `{"detail": {"code": "...", "message": "...", "location": "..."}}`；覆盖场景：JDBC URL 无效(400)、连接失败(400)、db_name 不存在(404)、SQL 语法错误(400)、非 SELECT 拒绝(400)、数据库查询错误(500)、LLM 不可用(400)
- [ ] T028 [P] 添加加载状态和空状态提示到前端 `frontend/src/views/QueryPage.vue` + 各组件：连接加载中 spinner、metadata 加载中骨架屏、查询执行中 loading、空结果"查询未返回任何结果"、空表"该数据库中没有表或视图"
- [ ] T029 边界情况处理：连接超时提示（后端 10s 超时 → 前端展示"连接超时，请检查网络或数据库地址"）、大结果集截断提示（truncated=true 时展示"已限制显示前 1000 行"）、多连接切换时清空查询结果

**Phase 3 检查点**: 自然语言→SQL→结果完整可用 → LLM 失败有合理降级 → 所有错误态/空态/加载态覆盖 → 功能完整可发布 ✅

---

## 依赖图

```
Phase 1: T001,T002 → T003,T004,T005,T006 → T007,T008 → T009,T010,T011 → T012,T013,T014 → T015 → T016
                              (Foundational 可部分并行)    (US1 端点)    (前端组件并行)   (组装页面)

Phase 2: Phase 1 完成 → T017 → T018,T019(并行) → T020 → T021 → T022

Phase 3: Phase 2 完成 → T023 → T024 → T025 → T026 → T027,T028(并行) → T029
```

## 并行执行示例

**Phase 1 内并行**:
- T003（main.py）和 T004（config.py）可同时创建
- T006（models.py）可与 T005（database.py）并行
- T008（sql_validator.py）可与 T007（pg_service.py）并行
- T012（api.js）、T013（DbList.vue）、T014（TableTree.vue）三者互不依赖，可并行

**Phase 2 内并行**:
- T018（SqlEditor.vue）和 T019（ResultTable.vue）可并行开发

**Phase 3 内并行**:
- T027（后端错误处理）和 T028（前端加载/空状态）可并行

## 每个用户故事的独立测试标准

- **US1 (Phase 1)**: 启动后端 → `POST /api/v1/dbs/testdb` 添加连接 → `GET /api/v1/dbs` 看到连接 → `GET /api/v1/dbs/testdb` 返回表/视图列表。前端展示树形结构。
- **US2 (Phase 2)**: 在已连接数据库上 `POST /api/v1/dbs/testdb/query {"sql": "SELECT 1"}` → 返回结果。前端 SqlEditor 输入查询 → 表格展示。
- **US4 (Phase 2)**: 关闭页面 → 重新打开 → metadata 从缓存加载（不重新连接）。点击刷新 → 更新为最新数据。
- **US3 (Phase 3)**: `POST /api/v1/dbs/testdb/query/natural {"natural": "查询所有表"}` → LLM 生成 SQL → 执行 → 返回结果。输入模糊描述 → 合理提示或生成。

## MVP 范围

**Phase 1 即为 MVP**（T001–T016）：用户能添加 PostgreSQL 连接并在前端浏览表/视图结构。这是一个独立可用的数据库浏览器。
