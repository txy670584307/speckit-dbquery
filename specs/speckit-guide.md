# Speckit AI 程序开发工作流指南

> 中文版 · 基于 Speckit 官方工作流编写
> 适用场景：使用 AI 编码助手（DeepSeek / Claude / Cursor）进行功能开发

---

## 一、Speckit 是什么

Speckit 是一套**结构化的 AI 程序开发工作流**。它将功能开发分解为 9 个标准化步骤，每一步都有明确的输入、输出和质量门控。目标是让 AI 编码从"写代码"升级为"管项目"。

### 核心原则

| 原则 | 说明 |
|------|------|
| **先写规再写码** | 每个功能先输出 spec → plan → tasks，确认后才实现 |
| **可追溯** | 每条代码对应一个任务，每个任务对应一个需求 |
| **质量内建** | 每一步有检查清单，问题早发现早解决 |
| **渐进交付** | 按用户故事分阶段交付，每个阶段可独立测试 |

### 工作流全景

```
用户需求
    │
    ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ speckit-    │───▶│ speckit-    │───▶│ speckit-    │
│ specify     │    │ clarify     │    │ plan        │
│ (写规格)     │    │ (澄清)       │    │ (规划)       │
└─────────────┘    └─────────────┘    └─────────────┘
                                              │
                                              ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ speckit-    │◀───│ speckit-    │◀───│ speckit-    │
│ implement   │    │ tasks       │    │ checklist   │
│ (实现)       │    │ (任务)       │    │ (检查清单)    │
└─────────────┘    └─────────────┘    └─────────────┘
```

---

## 二、命令详解与完整示例

### 2.1 `speckit-constitution` — 项目宪法

**用途**：定义项目的最高规则——技术栈、编码规范、设计原则。所有 spec 和代码必须遵循。

**产物**：`.specify/memory/constitution.md`

**用法示例**：

对话中输入：
```
用 speckit-constitution，创建项目宪法：
- 后端 Python (uv) + FastAPI，前端 Vue 2 + Element UI
- 使用 Pydantic 定义数据模型，JSON 输出用 camelCase
- 无需身份认证
- SQL 必须经 sqlglot 验证，仅允许 SELECT
```

效果：生成 `.specify/memory/constitution.md`，包含技术栈声明、API 约定、安全规则等。

---

### 2.2 `speckit-specify` — 功能规格定义

**用途**：将模糊的自然语言需求转化为结构化的 `spec.md`，包含功能需求（FR）、用户故事、验收标准和成功指标。

**产物**：`specs/<feature-dir>/spec.md`

**用法示例 1** — 从一句话需求开始：

```
speckit-specify，添加一个数据库查询工具：
用户可以添加 PostgreSQL 连接，浏览表结构，输入 SQL 查询，
也可以用自然语言生成 SQL。
```

执行后生成：
- `specs/001-db-query-tool/spec.md`
- `checklists/requirements.md`

**用法示例 2** — 从详细需求开始：

```
speckit-specify，详细功能如下：

功能：数据库查询工具
- 用户添加数据库连接（JDBC URL）
- 系统自动获取 metadata（表/视图/列）
- 用户可手写 SQL 查询或自然语言生成 SQL
- 仅支持 SELECT，自动 LIMIT 1000
- 输出 JSON 格式
- 连接信息和 metadata 缓存到 SQLite
```

**spec.md 的结构**：

```markdown
# Feature: 数据库连接管理

## 概述
用户可以添加 PostgreSQL 数据库连接...

## Functional Requirements
- FR-001：用户可以通过 JDBC URL 添加数据库连接
- FR-002：系统校验 JDBC URL 格式是否合法
- FR-003：添加时自动连接数据库并获取 metadata

## User Stories
- [US1] 作为用户，我可以添加数据库连接...
- [US2] 作为用户，我可以浏览表/视图的列信息...
- [US3] 作为用户，我可以用自然语言描述查询需求...

## Success Criteria
- 添加连接耗时 < 5 秒
- metadata 正确返回所有表和列信息

## Edge Cases
- JDBC URL 格式错误 → 返回具体错误提示
- 数据库不可达 → 超时提示，连接不保存
```

---

### 2.3 `speckit-clarify` — 规格澄清

**用途**：识别 spec 中的模糊点，提出最多 5 个问题，用户回答后自动更新 spec.md。

**产物**：更新 `spec.md`（增加 `## Clarifications` 章节）

**用法示例**：

```
speckit-clarify，检查刚生成的 spec 是否有模糊点。
```

可能提出的问题：
```
Q1：连接字符串支持哪些 PostgreSQL 认证方式？
    A. 仅用户名+密码  B. 支持 SSL 证书  C. 都支持

Q2：自然语言生成 SQL 需要支持中文输入吗？
    A. 仅中文  B. 中英文都支持  C. 仅英文
```

用户选择后，spec 自动更新。

---

### 2.4 `speckit-plan` — 实现规划

**用途**：基于 spec 生成完整的实现计划，包括技术选型、数据模型、API 契约、项目结构规划。

**产物**：
- `research.md` — 技术调研
- `data-model.md` — 数据模型
- `contracts/api.md` — API 契约
- `quickstart.md` — 快速开始
- `plan.md` — 完整实现计划

**用法示例**：

```
speckit-plan，为 db-query-tool 生成实现计划。
```

**plan.md 的结构**：

```markdown
# Implementation Plan: 数据库查询工具

## Tech Stack
- 后端：Python 3.11+, FastAPI, sqlglot, aiosqlite, asyncpg
- 前端：Vue 2, Element UI, Monaco Editor, axios

## Architecture
- 三层：routes → services → database
- SQLite 缓存连接信息和 metadata
- PostgreSQL 为查询目标

## Phase 1: Setup & MVP
  Phase 1-1: 项目初始化（uv sync, npm install）
  Phase 1-2: 后端基础（数据库、配置、模型）
  Phase 1-3: 前端基础（Vue Router、API 封装）

## Phase 2: 连接管理 + Metadata 浏览 [US1]
  T017: 实现添加连接对话框
  T018: 实现表/视图树组件
  ...
```

---

### 2.5 `speckit-checklist` — 质量检查清单

**用途**：生成"需求的单元测试"——验证 spec 的质量、清晰度和完整性。

**产物**：`specs/<feature-dir>/checklists/requirements.md`

**用法示例**：

```
speckit-checklist，检查 db-query-tool 的 spec 质量。
```

输出示例：
```markdown
- [ ] CHK001 - "活跃用户"是否明确定义？[Clarity, FR-003]
- [ ] CHK002 - 连接超时时间是否量化？[Clarity, FR-001]
- [ ] CHK003 - LIMIT 策略是否在所有查询端点上一致？[Consistency]
- [ ] CHK004 - 空结果是否定义了展示方式？[Completeness]
```

---

### 2.6 `speckit-tasks` — 任务清单生成

**用途**：将 plan 和 spec 转化为可执行的、按用户故事组织的任务列表。

**产物**：`specs/<feature-dir>/tasks.md`

**用法示例**：

```
speckit-tasks，为 db-query-tool 生成任务清单。
```

**tasks.md 的结构**：

```markdown
# Tasks: 数据库查询工具

Total: 29 tasks | US1: 16 | US2: 6 | US3: 4 | Polish: 3

## Phase 1: Setup & Infrastructure [US1]
- [X] T001 Setup 项目初始化（pyproject.toml, vue.config.js）
- [X] T002 Setup 后端配置（config.py, database.py）
- [ ] T003 [US1] 实现 DbCreateRequest/QueryRequest 模型
...

## Phase 2: SQL 查询与执行 [US2]
- [ ] T017 [P] [US2] 实现 SqlEditor.vue 组件
- [ ] T018 [P] [US2] 实现 ResultTable.vue 组件
...

## Phase 3: 自然语言查询 [US3]
- [ ] T023 [US3] 创建 llm_service.py
...
```

**标记说明**：

| 标记 | 含义 |
|------|------|
| `[X]` | 已完成 |
| `[ ]` | 待完成 |
| `[P]` | 可并行执行 |
| `[US1]` | 属于 User Story 1 |
| `T001` | 任务编号 |

---

### 2.7 `speckit-analyze` — 跨制品一致性分析

**用途**：检查 spec.md、plan.md、tasks.md 之间是否存在矛盾、重复、模糊和覆盖缺口。

**产物**：结构化分析报告（控制台输出）

**用法示例**：

```
speckit-analyze，检查 db-query-tool 的制品一致性。
```

输出示例：
```
| ID | 严重性 | 位置 | 摘要 | 建议 |
|----|--------|------|------|------|
| 01 | HIGH | plan.md §2 | 引用了 pg_connector.py 但实际文件名为 pg_service.py | 更新文件名引用 |
| 02 | MEDIUM | tasks.md | T023 无对应的 FR 需求映射 | 补充 FR 映射 |
```

**覆盖摘要**：

```
| 需求键 | 有任务？ | 任务 ID |
|--------|---------|---------|
| FR-001 | ✅ | T002, T003, T004 |
| FR-002 | ❌ | — |
```

---

### 2.8 `speckit-implement` — 实现执行

**用途**：按 tasks.md 定义的任务列表，分阶段、按顺序执行代码实现。

**用法示例**：

```
speckit-implement，开始实现 db-query-tool Phase 1。
```

执行过程：
```
Phase 1: Setup & Infrastructure
  T001 ✅ 项目初始化
  T002 ✅ 后端配置（config.py, database.py）
  T003 ✅ 数据模型定义
  T004 ✅ 主入口 + CORS

Phase 2: [US1] 连接管理
  T005 ✅ 实现 pg_service.py（JDBC URL 解析）
  T006 ✅ 实现 POST /api/v1/dbs/{db_name}
  ...

Progress: 8/29 tasks completed.
```

---

### 2.9 `speckit-git` — Git 集成

**用途**：管理 Git 仓库初始化、feature 分支创建、自动提交。

**子命令**：

```
speckit-git init       # 初始化仓库并首次提交
speckit-git feature    # 创建 feature 分支（如 001-db-query-tool）
speckit-git commit     # 自动提交变更
speckit-git remote     # 检测远程仓库
speckit-git validate   # 验证分支命名规范
```

**用法示例**：

```
speckit-git feature，创建 db-query-tool 的 feature 分支。
```

输出：创建并切换到 `001-db-query-tool` 分支。

---

### 2.10 `speckit-taskstoissues` — 任务转 Issue

**用途**：将 tasks.md 中的每个任务转换为 GitHub Issue。

**用法示例**：

```
speckit-taskstoissues，将当前 tasks 推送到 GitHub Issues。
```

输出：
```
Created 8 issues:
  #1  T001 - 项目初始化
  #2  T002 - 后端配置
  ...
```

---

## 三、工作流完整示例：从零开始一个功能

### 场景：开发一个数据库查询工具

#### Step 1：建立宪法

```
speckit-constitution，项目规则：
- 后端 Python (uv) + FastAPI + sqlglot
- 前端 Vue 2 + Element UI + Monaco Editor
- MVP：连接 PostgreSQL → 浏览表 → 执行 SQL
- 所有 SQL 必须经 sqlglot 验证
- JSON 输出 camelCase
- 无需认证
```

→ 生成 `.specify/memory/constitution.md`

#### Step 2：写规格

```
speckit-specify，详细需求如下：
用户可以添加 PostgreSQL 数据库连接（JDBC URL），
系统自动获取表/视图/列信息并缓存到 SQLite，
用户可以手写 SQL 查询或用自然语言描述需求。
仅支持 SELECT 语句，无 LIMIT 自动追加 1000。
```

→ 生成 `specs/001-db-query-tool/spec.md`

#### Step 3：澄清模糊点

```
speckit-clarify
```

→ AI 提出 3 个问题：
- 自然语言支持中文还是英文？
- 连接失败时是否保留已缓存的数据？
- 表多时是否需要分页加载？

#### Step 4：制定实现计划

```
speckit-plan
```

→ 生成：research.md / data-model.md / contracts/api.md / quickstart.md / plan.md

#### Step 5：质量检查

```
speckit-checklist
```

→ 生成 `checklists/requirements.md`

#### Step 6：拆解任务

```
speckit-tasks
```

→ 生成 `tasks.md`（29 个任务，分 3 个 Phase）

#### Step 7：开始实现

```
speckit-implement
```

→ AI 按 Phase 1→2→3 依次实现，每完成一个任务报告进度

#### Step 8：代码审查

```
speckit-analyze，检查已实现的代码是否符合 spec 和 plan。
```

→ 输出一致性分析报告

#### Step 9：提交代码

```
speckit-git commit，提交 Phase 1 实现。
```

---

## 四、最佳实践与常见问题

### 4.1 什么时候用哪个命令

| 阶段 | 命令 | 输出 |
|------|------|------|
| 项目启动 | `speckit-constitution` | 项目宪法 |
| 新功能 | `speckit-specify` | spec.md |
| 需求模糊 | `speckit-clarify` | 更新 spec |
| 设计规划 | `speckit-plan` | plan + data-model + contracts |
| 质量预检 | `speckit-checklist` | 检查清单 |
| 拆解任务 | `speckit-tasks` | tasks.md |
| 编写代码 | `speckit-implement` | 代码文件 |
| 一致性审查 | `speckit-analyze` | 分析报告 |
| 版本管理 | `speckit-git` | Git 操作 |

### 4.2 常见错误与解决

| 问题 | 原因 | 解决 |
|------|------|------|
| `speckit-specify` 后没有生成目录 | 缺少 `.specify/` 配置 | 先执行 `speckit-constitution` |
| `speckit-plan` 报错 | spec 中有未解决的 `[NEEDS CLARIFICATION]` | 先执行 `speckit-clarify` |
| `speckit-implement` 跳过任务 | tasks.md 中任务状态标记不对 | 确认 `[ ]` vs `[X]` |

### 4.3 与 AI 配合的技巧

1. **需求描述越具体，spec 质量越高** — 给出具体的字段名、按钮文字、错误提示
2. **及时澄清** — spec 中残留 `[NEEDS CLARIFICATION]` 会影响后续所有步骤
3. **渐进实现** — 可以用 `speckit-implement Phase 1` 指定只实现某个阶段
4. **多次 analyze** — 开发过程中可多次执行 `speckit-analyze` 检查一致性
5. **保留制品** — spec/plan/tasks 是项目文档，也是后续维护的依据

### 4.4 项目目录结构

```
project/
├── .specify/
│   ├── memory/
│   │   └── constitution.md       # 项目宪法
│   ├── templates/                 # 模板文件
│   ├── extensions.yml
│   └── feature.json              # 当前 feature 元数据
│
├── specs/
│   ├── instruction.md            # 总说明
│   ├── 001-db-query-tool/        # 每个功能一个目录
│   │   ├── spec.md               # 功能规格
│   │   ├── plan.md               # 实现计划
│   │   ├── research.md           # 技术调研
│   │   ├── data-model.md         # 数据模型
│   │   ├── quickstart.md         # 快速开始
│   │   ├── tasks.md              # 任务清单
│   │   ├── contracts/
│   │   │   └── api.md            # API 契约
│   │   └── checklists/
│   │       └── requirements.md   # 质量检查清单
│   └── speckit-guide.md          # 本手册
│
├── backend/                      # 实现代码
├── frontend/
└── test/
```

---

## 五、快速参考

### 命令速查

| 命令 | 一句话用途 |
|------|-----------|
| `speckit-constitution` | 定项目规矩（技术栈、规范） |
| `speckit-specify` | 把需求写成 spec |
| `speckit-clarify` | 找出 spec 中的模糊点 |
| `speckit-plan` | 制定实现计划 |
| `speckit-checklist` | 检查 spec 质量 |
| `speckit-tasks` | 拆解成可执行的任务 |
| `speckit-implement` | 按任务列表写代码 |
| `speckit-analyze` | 检查 spec/plan/tasks 一致性 |
| `speckit-git` | Git 辅助操作 |
| `speckit-taskstoissues` | 任务转 GitHub Issues |

### 产物文件速查

| 文件 | 来源 | 必读对象 |
|------|------|---------|
| `constitution.md` | speckit-constitution | 所有 AI 和开发人员 |
| `spec.md` | speckit-specify | 产品、测试、开发 |
| `plan.md` | speckit-plan | 开发架构师 |
| `data-model.md` | speckit-plan | 后端开发 |
| `contracts/` | speckit-plan | 前后端开发 |
| `tasks.md` | speckit-tasks | 执行开发的 AI |
| `checklists/` | speckit-checklist | 质量保障 |
