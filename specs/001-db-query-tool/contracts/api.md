# API Contracts: 数据库查询工具

所有 API 端点前缀: `/api/v1`
CORS: 允许所有 origin 访问（`Access-Control-Allow-Origin: *`）

---

## 端点列表

### 1. 获取所有已连接的数据库

#### GET /api/v1/dbs

列出所有已保存的数据库连接。

**Response** (200):
```json
[
  {
    "dbName": "mydb",
    "dbUrl": "jdbc:postgresql://localhost:5432/postgres?user=postgres&password=postgres",
    "createdAt": "2026-05-25T10:00:00Z",
    "tableCount": 15
  }
]
```

---

### 2. 添加数据库连接

#### POST /api/v1/dbs/{db_name}

添加新的数据库连接并自动获取 metadata。

**Path Parameter**:
- `db_name` — 用户自定义的数据库连接名称（用作后续 API 路径中的唯一标识）

**Request Body**:
```json
{
  "db_url": "jdbc:postgresql://localhost:5432/postgres?user=postgres&password=postgres"
}
```

**Response** (201):
```json
{
  "dbName": "mydb",
  "dbUrl": "jdbc:postgresql://localhost:5432/postgres?user=postgres&password=postgres",
  "createdAt": "2026-05-25T10:00:00Z",
  "tableCount": 15
}
```

**Errors**:
- `400` — JDBC URL 格式无效或数据库无法连接
- `409` — 同名连接 (`db_name`) 已存在

---

### 3. 获取数据库 metadata

#### GET /api/v1/dbs/{db_name}

获取指定连接的所有表和视图的 metadata。

**Path Parameter**:
- `db_name` — 数据库连接名称

**Response** (200):
```json
[
  {
    "schemaName": "public",
    "tableName": "users",
    "tableType": "table",
    "columns": [
      { "name": "id", "dataType": "integer", "nullable": false },
      { "name": "email", "dataType": "character varying", "nullable": true }
    ]
  },
  {
    "schemaName": "public",
    "tableName": "user_stats",
    "tableType": "view",
    "columns": [
      { "name": "user_id", "dataType": "integer", "nullable": false },
      { "name": "login_count", "dataType": "bigint", "nullable": true }
    ]
  }
]
```

**Errors**:
- `404` — 连接 (`db_name`) 不存在

---

### 4. 执行 SQL 查询

#### POST /api/v1/dbs/{db_name}/query

执行 SQL 查询（仅允许 SELECT，自动 LIMIT 1000）。

**Path Parameter**:
- `db_name` — 数据库连接名称

**Request Body**:
```json
{
  "sql": "select * from table_name"
}
```

**Response** (200):
```json
{
  "columns": [
    { "name": "id", "dataType": "integer", "nullable": false },
    { "name": "email", "dataType": "character varying", "nullable": true }
  ],
  "rows": [
    [1, "alice@example.com"],
    [2, "bob@example.com"]
  ],
  "rowCount": 2,
  "truncated": false,
  "sqlExecuted": "SELECT id, email FROM users WHERE active = true LIMIT 1000"
}
```

**Errors**:
- `400` — SQL 语法错误或包含非 SELECT 语句
- `404` — 连接 (`db_name`) 不存在
- `500` — 数据库查询执行错误

---

### 5. 自然语言生成 SQL 查询

#### POST /api/v1/dbs/{db_name}/query/natural

将自然语言转换为 SQL 并执行。

**Path Parameter**:
- `db_name` — 数据库连接名称

**Request Body**:
```json
{
  "natural": "查询所有用户"
}
```

**Response** (200): 同 `/query` 端点（QueryResult 格式）

**Errors**:
- `400` — LLM 服务不可用或生成的 SQL 无法执行
- `404` — 连接 (`db_name`) 不存在

---

## 全局错误格式

所有错误响应统一格式：
```json
{
  "detail": {
    "code": "INVALID_SQL",
    "message": "仅支持 SELECT 查询",
    "location": "line 1, col 1"
  }
}
```
