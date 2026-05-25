# Quickstart: 数据库查询工具

## 前置条件

- Python 3.11+
- Node.js 18+
- PostgreSQL 数据库（用于查询目标）
- LLM 服务（OpenAI 兼容 API，用于自然语言查询功能）

## 快速启动

### 1. 克隆并安装后端依赖

```bash
git clone <repo-url>
cd db_query

# 使用 uv 管理 Python 依赖
uv sync
```

### 2. 安装前端依赖

```bash
cd frontend
npm install
```

### 3. 配置环境变量

创建 `.env` 文件（后端根目录）：

```env
# LLM 配置（用于自然语言 → SQL）
LLM_BASE_URL=http://localhost:11434/v1   # Ollama 或 OpenAI 兼容端点
LLM_API_KEY=ollama                        # API key（如不需要可留空）
LLM_MODEL=qwen2.5:7b                      # 模型名

# SQLite 本地数据库路径
LOCAL_DB_PATH=./data/local.db

# 服务端口
API_PORT=8000
```

### 4. 启动后端

```bash
uv run uvicorn main:app --reload --port 8000
```

API 文档自动生成：`http://localhost:8000/docs`

### 5. 启动前端

```bash
cd frontend
npm run serve
```

前端默认地址：`http://localhost:8080`

### 6. 使用

1. 打开 `http://localhost:8080`
2. 点击"添加连接"，输入 PostgreSQL 连接字符串（如 `postgresql://user:pass@localhost:5432/mydb`）
3. 系统自动获取并展示表/视图列表
4. 在 SQL 编辑器中输入查询或输入自然语言描述
5. 执行查询，结果以表格形式展示

## 项目结构

```
db_query/
├── backend/
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py            # 配置管理
│   ├── database.py          # SQLite 本地存储
│   ├── models.py            # Pydantic 数据模型
│   ├── routes/
│   │   ├── connections.py   # 连接管理 API
│   │   ├── metadata.py      # Metadata 浏览 API
│   │   ├── query.py         # SQL 查询 API
│   │   └── nl_query.py      # 自然语言查询 API
│   ├── services/
│   │   ├── pg_connector.py  # PostgreSQL 连接与查询
│   │   ├── sql_validator.py # sqlglot 验证
│   │   └── llm_service.py   # LLM 调用
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── components/      # Vue 组件
│   │   │   ├── ConnectionList.vue
│   │   │   ├── TableTree.vue
│   │   │   ├── SqlEditor.vue
│   │   │   └── ResultTable.vue
│   │   ├── views/           # 页面
│   │   │   └── QueryPage.vue
│   │   ├── services/        # API 调用
│   │   │   └── api.js
│   │   ├── router/          # Vue Router
│   │   └── App.vue
│   └── package.json
└── data/                    # SQLite 数据库文件目录（自动创建）
```
