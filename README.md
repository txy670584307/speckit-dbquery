# DB Query Tool

数据库查询工具——连接 PostgreSQL 数据库，浏览表/视图结构，手写或自然语言生成 SQL 查询，结果以表格展示。

## 技术栈

| 层 | 技术 |
|---|------|
| **后端** | Python 3.11+, FastAPI, sqlglot, Pydantic, aiosqlite, httpx |
| **前端** | Vue 2, Element UI, Monaco Editor, axios, Vue Router |
| **目标数据库** | PostgreSQL |
| **本地缓存** | SQLite（连接信息 + metadata） |
| **LLM 服务** | OpenAI Chat Completions 兼容 API（Ollama / vLLM / OpenAI 等） |

## 环境要求

- Python 3.11+
- uv（Python 包管理器）
- Node.js 18+
- npm（随 Node.js 安装）
- PostgreSQL 数据库（作为查询目标）
- （可选）LLM 服务，用于自然语言生成 SQL

## 快速启动

### 1. 安装后端依赖

```bash
cd db_query
uv sync
```

### 2. 安装前端依赖

```bash
cd frontend
npm install
```

### 3. 配置环境变量

在项目根目录创建 `.env` 文件：

```env
# LLM 服务配置（自然语言→SQL 功能）
LLM_BASE_URL=http://localhost:11434/v1   # Ollama 或 OpenAI 兼容 API 端点
LLM_API_KEY=                              # API key，按需填写
LLM_MODEL=qwen2.5:7b                      # 模型名称

# SQLite 本地数据库存放路径
LOCAL_DB_PATH=./data/local.db

# API 服务端口
API_PORT=8000
```

### 4. 启动后端

```bash
uv run uvicorn backend.main:app --reload --port 8000
```

启动后访问 `http://127.0.0.1:8000/docs` 查看自动生成的 API 交互文档。

### 5. 启动前端

```bash
cd frontend
npm run serve
```

前端默认启动在 `http://localhost:8080`（如 8080 被占用则自动递增）。

### 6. 使用

1. 打开浏览器，访问 `http://localhost:8080`
2. 点击左侧「添加」按钮
3. 填写**连接名称**（如 `production-db`）和 **JDBC URL**
4. 点击「连接」→ 左侧展示该数据库的表/视图树（可展开查看列名和数据类型）
5. **SQL 编辑模式**：在 Monaco Editor 中输入 `SELECT` 语句 → 点击「执行」或按 `Ctrl+Enter`
6. **自然语言模式**：切换到「自然语言」→ 输入查询描述（如"查询所有用户"）→ 点击「生成 SQL 并查询」

> 自动限制：SQL 默认仅允许 `SELECT`，无 `LIMIT` 的查询自动追加 `LIMIT 1000`。非 SELECT 语句会被拒绝。

## 完整 API

所有端点返回 JSON，属性名使用 camelCase。CORS 允许所有来源。

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/v1/dbs` | 获取所有已保存的数据库连接 |
| `POST` | `/api/v1/dbs/{db_name}` | 添加数据库连接（含 JDBC URL），自动获取 metadata |
| `GET` | `/api/v1/dbs/{db_name}` | 获取指定连接的 metadata（表/视图/列信息） |
| `GET` | `/api/v1/dbs/{db_name}?refresh=true` | 强制从数据库重新获取 metadata 并更新缓存 |
| `POST` | `/api/v1/dbs/{db_name}/query` | 执行 SQL 查询（仅 SELECT，自动 LIMIT 1000） |
| `POST` | `/api/v1/dbs/{db_name}/query/natural` | 自然语言生成 SQL 并执行 |

### API 请求/响应示例

**添加连接：**

```bash
curl -X POST http://127.0.0.1:8000/api/v1/dbs/mydb \
  -H "Content-Type: application/json" \
  -d '{"db_url": "jdbc:postgresql://localhost:5432/mydb?user=admin&password=secret"}'
```

**执行查询：**

```bash
curl -X POST http://127.0.0.1:8000/api/v1/dbs/mydb/query \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELECT id, name FROM users LIMIT 5"}'
```

**自然语言查询：**

```bash
curl -X POST http://127.0.0.1:8000/api/v1/dbs/mydb/query/natural \
  -H "Content-Type: application/json" \
  -d '{"natural": "显示 users 表中所有活跃用户"}'
```

## 项目结构

```
db_query/
├── backend/                      # 后端（Python / FastAPI）
│   ├── main.py                   # 应用入口：CORS 中间件、全局异常处理、路由注册
│   ├── config.py                 # 环境配置（Pydantic-Settings）
│   ├── database.py               # SQLite 存储（aiosqlite：连接 + metadata 缓存）
│   ├── models.py                 # Pydantic 数据模型（camelCase 别名生成器）
│   ├── routes/
│   │   ├── dbs.py                # GET/POST /dbs, GET /dbs/{db_name}
│   │   ├── query.py              # POST /dbs/{db_name}/query
│   │   └── nl_query.py           # POST /dbs/{db_name}/query/natural
│   ├── services/
│   │   ├── pg_service.py         # PostgreSQL 连接（JDBC URL 解析 → asyncpg）
│   │   ├── sql_validator.py      # sqlglot：语法验证、SELECT 校验、LIMIT 追加
│   │   └── llm_service.py        # httpx：OpenAI 兼容 API 调用
│   └── tests/                    # 单元测试
│       └── test_sql_validator.py
│
├── frontend/                     # 前端（Vue 2 / Element UI）
│   ├── src/
│   │   ├── main.js               # Vue 应用入口
│   │   ├── App.vue               # 根组件
│   │   ├── components/
│   │   │   ├── DbList.vue        # 数据库连接列表 + 添加对话框
│   │   │   ├── TableTree.vue     # 表/视图三级树（schema → table → column）
│   │   │   ├── SqlEditor.vue     # Monaco Editor 封装
│   │   │   └── ResultTable.vue   # 动态列结果表格
│   │   ├── views/
│   │   │   └── QueryPage.vue     # 主页面（左侧面板 + SQL/NL 模式切换）
│   │   ├── services/
│   │   │   └── api.js            # axios API 封装
│   │   └── router/
│   │       └── index.js          # Vue Router 配置
│   ├── public/
│   │   └── index.html
│   ├── vue.config.js             # webpack + devServer 代理
│   └── package.json
│
├── data/                         # 运行时自动创建，存放 local.db（SQLite）
├── specs/                        # 功能规格文档（Spec Kit 工作流）
│   └── 001-db-query-tool/        # 当前 feature
│       ├── spec.md               # 功能规格
│       ├── plan.md               # 实现计划
│       ├── research.md           # 技术调研
│       ├── data-model.md         # 数据模型
│       ├── quickstart.md         # 快速上手
│       ├── tasks.md              # 任务清单
│       ├── contracts/
│       │   └── api.md            # API 契约
│       └── checklists/
│           └── requirements.md   # 需求质量检查清单
│
├── .env                          # 环境变量配置文件
├── .python-version               # Python 版本
├── pyproject.toml                # Python 依赖（uv）
└── README.md                     # 本文件
```

## 核心设计说明

### 连接字符串

采用 JDBC URL 格式 `jdbc:postgresql://host:port/db?user=x&password=y`，后端自动解析为 asyncpg 可用的连接参数。

### SQL 安全

所有 SQL 在发送到 PostgreSQL 之前经过 sqlglot 解析：
- 非 `SELECT` 语句 → 拒绝并返回错误
- 无 `LIMIT` 的查询 → 自动追加 `LIMIT 1000`
- 语法错误 → 返回具体错误位置

### LLM 集成

自然语言→SQL 流程：
1. 从 SQLite 缓存读取该连接的 metadata（表名、列名、类型）
2. 构造 system prompt 注入 metadata 作为上下文
3. 调用 OpenAI 兼容 API 生成 SQL
4. 通过 sqlglot 验证后执行
5. 生成的 SQL 无效时，返回原始 SQL 供用户手动修正

### 缓存策略

- 添加连接时自动从 PostgreSQL 获取 metadata 并缓存到 SQLite
- 打开已有连接时优先返回缓存
- 支持手动刷新（`GET /dbs/{db_name}?refresh=true`）
- 刷新失败时保留旧缓存

## 常见问题

### 端口被占用

后端默认 8000、前端默认 8080。可通过 `.env` 中的 `API_PORT` 修改后端端口，前端端口在 `frontend/package.json` 的 `serve` 脚本中加 `--port` 参数。

### 前端代理

开发模式下前端通过 vue.config.js 配置的 devServer proxy 将 `/api` 请求转发到后端 `http://localhost:8000`。生产部署时需配置反向代理（如 nginx）指向后端。

### 连接超时

默认连接超时 10 秒。超时后前端会提示"连接 PostgreSQL 超时，请检查网络或数据库地址"。
