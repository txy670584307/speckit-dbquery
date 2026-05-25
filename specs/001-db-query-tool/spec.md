# Feature Specification: 数据库查询工具

**Feature Branch**: `001-db-query-tool`

**Created**: 2026-05-20

**Status**: Draft

**Input**: User description: "这是一个数据库查询工具。用户可以添加一个db url,系统会连接到数据库，获取数据库的metadata，然后将数据库的table和view的信息展示出来，然后用户可以自己输入sql查询，也可以通过自然语言来生成查询。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 添加数据库连接并浏览表/视图 (Priority: P1) 🎯 MVP

作为一个数据分析师，我希望能添加一个 PostgreSQL 数据库连接，系统自动获取该数据库的表和视图信息并展示给我，这样我就能快速了解数据库中有哪些数据。

**Why this priority**: 这是工具的基础入口。没有数据库连接，后续所有查询功能都无法使用。

**Independent Test**: 可独立测试——添加一条数据库连接后，系统能展示该数据库下所有表的列表及各表的列信息。

**Acceptance Scenarios**:

1. **Given** 用户打开工具，**When** 输入有效的 PostgreSQL 连接字符串并点击"连接"，**Then** 系统成功连接数据库、获取 metadata（表名、视图名、列名及类型）、将 metadata 缓存到本地 SQLite，并在界面上展示表/视图树形列表。
2. **Given** 存在一个已保存的数据库连接，**When** 用户点击该连接，**Then** 系统优先展示缓存的 metadata，后台可刷新最新信息。
3. **Given** 用户输入的连接字符串无效，**When** 点击"连接"，**Then** 系统显示明确的错误信息（如"无法连接到数据库，请检查连接字符串"）。

---

### User Story 2 - 手写 SQL 查询 (Priority: P2)

作为一个数据分析师，我希望能在一个 SQL 编辑器中输入 SELECT 语句，执行查询后结果以表格形式展示，这样我就能用熟悉的 SQL 查询数据。

**Why this priority**: SQL 查询是工具的核心价值。在自然语言功能之上，手写 SQL 提供精确控制。

**Independent Test**: 可独立测试——输入一条 SELECT 语句，系统验证语法、执行查询、返回 JSON 结果并在前端表格中正确展示。

**Acceptance Scenarios**:

1. **Given** 已连接数据库，**When** 用户在 SQL 编辑器中输入一条正确的 SELECT 语句并执行，**Then** 系统返回 JSON 格式的查询结果，前端以表格形式展示。
2. **Given** 用户输入的 SELECT 语句不包含 LIMIT 子句，**When** 执行查询，**Then** 系统自动追加 `LIMIT 1000`，并在结果中标注此行数限制。
3. **Given** 用户输入的 SQL 包含 INSERT/UPDATE/DELETE 等非 SELECT 语句，**When** 执行查询，**Then** 系统拒绝执行并返回错误提示："仅支持 SELECT 查询"。
4. **Given** 用户输入的 SQL 语法不正确，**When** 执行查询，**Then** 系统返回具体的语法错误信息及错误位置。

---

### User Story 3 - 自然语言生成 SQL (Priority: P3)

作为一个非技术用户，我希望用日常语言描述查询需求（如"查询过去7天订单数最多的前10个客户"），系统自动生成对应的 SQL 并执行，这样我不需要学习 SQL 也能查询数据。

**Why this priority**: 降低使用门槛，让非技术人员也能查询数据。但依赖手写 SQL 功能和 LLM 服务可用性。

**Independent Test**: 可独立测试——输入自然语言查询描述，系统生成有效 SQL 并返回结果。

**Acceptance Scenarios**:

1. **Given** 已连接数据库，**When** 用户用自然语言描述查询需求（如"显示 users 表中所有活跃用户"），**Then** 系统将表/视图 metadata 作为上下文传递给 LLM，生成对应的 SELECT 语句，执行并返回结果。
2. **Given** LLM 生成的 SQL 有语法错误，**When** 系统尝试执行，**Then** 系统捕获错误并向用户展示原始 SQL 及错误信息，同时提供"手动修正"选项。
3. **Given** 用户对生成结果不满意，**When** 用户修改自然语言描述重新生成，**Then** 系统重新生成并执行。

---

### User Story 4 - Metadata 缓存管理 (Priority: P2)

作为一个经常使用该工具的用户，我希望系统缓存已获取的数据库 metadata，这样我每次打开工具查看表结构时无需重新连接数据库。

**Why this priority**: metadata 缓存提升用户体验，减少重复连接开销。可在 US1 完成后并行开发。

**Independent Test**: 可独立测试——添加数据库连接后关闭工具再打开，表结构信息仍可展示。

**Acceptance Scenarios**:

1. **Given** 用户已添加数据库连接且 metadata 已缓存，**When** 用户重新打开工具，**Then** 系统直接展示缓存的表/视图信息，无需重新连接数据库。
2. **Given** 缓存的 metadata 可能已过时，**When** 用户点击"刷新"，**Then** 系统重新连接数据库获取最新 metadata 并更新缓存。
3. **Given** 数据库连接失败（如网络中断），**When** 用户尝试刷新，**Then** 系统保留旧缓存并提示"刷新失败，显示的是上次缓存的数据"。

---

### Edge Cases

- 数据库连接超时或网络中断时，系统应显示明确错误信息而非空白页面。
- 用户连接的数据库中无任何表或视图时，系统应展示"该数据库中没有表或视图"并给出建议。
- SQL 查询结果为空（0 行）时，系统应展示空表格并提示"查询未返回任何结果"。
- 用户输入的查询结果集非常大时，系统受 LIMIT 1000 约束，应在结果中标注"已限制显示前 1000 行"。
- 自然语言描述过于模糊或无法映射到数据库 schema 时，系统应提示用户提供更具体的描述。
- 多个数据库连接同时存在时，用户应能清晰区分当前操作的是哪个数据库。
- 删除已保存的数据库连接时，系统应同时清理对应缓存。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 系统 MUST 允许用户添加、保存和删除 PostgreSQL 数据库连接字符串。
- **FR-002**: 系统 MUST 在添加连接时自动连接数据库并获取 metadata（schema、表名、视图名、列名、列类型）。
- **FR-003**: 系统 MUST 将数据库连接字符串和 metadata 缓存到本地 SQLite 数据库中，以供后续复用。
- **FR-004**: 系统 MUST 以树形或列表形式在前端展示数据库的表和视图信息。
- **FR-005**: 系统 MUST 提供 SQL 编辑器（Monaco Editor），支持 SQL 语法高亮和自动补全。
- **FR-006**: 系统 MUST 使用 sqlparser 对所有输入的 SQL 进行语法验证，拒绝执行非 SELECT 语句并给出错误提示。
- **FR-007**: 系统 MUST 对未包含 LIMIT 子句的 SELECT 语句自动追加 `LIMIT 1000`。
- **FR-008**: 系统 MUST 以 JSON 格式返回所有查询结果，属性名使用 camelCase。
- **FR-009**: 系统 MUST 支持用户用自然语言描述查询需求，自动生成 SQL 语句并执行。
- **FR-010**: 系统 MUST 在自然语言生成 SQL 时将数据库 metadata 作为上下文传递给 LLM。
- **FR-011**: 系统 MUST 在前端以表格形式展示 JSON 查询结果。
- **FR-012**: 系统 MUST 允许用户手动刷新数据库 metadata 缓存。

### Key Entities

- **DatabaseConnection**: 表示一个已保存的数据库连接。包含连接字符串（url）、连接名称、数据库类型（PostgreSQL）。与 TableMetadata 为一对多关系。
- **TableMetadata**: 表示数据库中的一个表或视图的 metadata。包含 schema 名称、表/视图名、列信息（列名、数据类型、是否可空）。属于一个 DatabaseConnection。
- **QueryResult**: 表示一次查询的执行结果。包含列信息列表、行数据列表、总行数、是否被 LIMIT 截断。
- **QueryHistory**: 表示一次查询的历史记录。包含原始 SQL（或自然语言描述）、生成的 SQL、执行时间戳。可选关联到 DatabaseConnection。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 用户在 1 分钟内可以完成数据库连接添加并看到表/视图列表。
- **SC-002**: 数据库 metadata 获取在 30 秒内完成（含大 schema 场景，表数 < 500）。
- **SC-003**: SQL 查询执行结果在 5 秒内返回给前端并完成表格渲染。
- **SC-004**: SQL 语法错误在用户提交查询时即时反馈，不产生无效的数据库请求。
- **SC-005**: 自然语言生成 SQL 的一次生成成功率 ≥ 80%（生成的 SQL 通过 sqlparser 验证且可执行）。
- **SC-006**: 前端表格支持 1000 行数据流畅滚动，无明显卡顿。

## Assumptions

- 目标数据库仅支持 PostgreSQL，不涉及 MySQL、SQLite 等其他数据库类型。
- 工具为内网部署，无身份认证和权限控制，任何能访问服务的人均可使用。
- 用户具备基本的数据库概念（知道什么是表、列、SELECT 查询）。
- 系统运行环境可访问 LLM 服务（用于自然语言生成 SQL），LLM 接口兼容 OpenAI Chat Completions 格式。
- 数据库连接字符串由用户自行管理，系统仅保存明文（无加密要求，基于无认证的内部工具定位）。
- 前端不支持移动端适配，面向桌面浏览器使用。
- metadata 缓存不自动过期，由用户手动刷新或删除连接时清除。
