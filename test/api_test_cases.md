# 后端接口测试用例

---

## 模块一：连接管理

### TC-API-001：获取空连接列表

| 字段 | 值 |
|------|----|
| **前置条件** | 无任何已保存的数据库连接（如存在则先清理） |
| **请求** | `GET /api/v1/dbs` |
| **预期状态码** | 200 |
| **预期响应** | `[]` |
| **实际结果** | |
| **状态** | ⬚ |

### TC-API-002：添加数据库连接（成功）

| 字段 | 值 |
|------|----|
| **前置条件** | PostgreSQL 容器运行中，连接名 `testdb` 不存在 |
| **请求** | `POST /api/v1/dbs/testdb` |
| **请求体** | `{"db_url": "jdbc:postgresql://localhost:5432/testdb?user=postgres&password=postgres"}` |
| **预期状态码** | 201 |
| **预期响应字段** | `dbName`, `dbUrl`, `createdAt`, `tableCount`（应 ≥ 1） |
| **实际结果** | |
| **状态** | ⬚ |

### TC-API-003：添加同名连接（冲突）

| 字段 | 值 |
|------|----|
| **前置条件** | 连接 `testdb` 已存在 |
| **请求** | `POST /api/v1/dbs/testdb` |
| **请求体** | 同 TC-API-002 |
| **预期状态码** | 409 |
| **预期错误码** | `DB_NAME_EXISTS` |
| **实际结果** | |
| **状态** | ⬚ |

### TC-API-004：添加连接——无效 JDBC URL 格式

| 字段 | 值 |
|------|----|
| **前置条件** | — |
| **请求** | `POST /api/v1/dbs/baddb` |
| **请求体** | `{"db_url": "mysql://localhost:3306/test"}` |
| **预期状态码** | 400 |
| **预期错误码** | `INVALID_JDBC_URL` |
| **实际结果** | |
| **状态** | ⬚ |

### TC-API-005：添加连接——数据库不可达

| 字段 | 值 |
|------|----|
| **前置条件** | — |
| **请求** | `POST /api/v1/dbs/fakedb` |
| **请求体** | `{"db_url": "jdbc:postgresql://localhost:15432/test?user=postgres&password=postgres"}` |
| **预期状态码** | 400 |
| **预期错误码** | `CONNECTION_FAILED` |
| **实际结果** | |
| **状态** | ⬚ |

### TC-API-006：获取连接列表（含已添加的连接）

| 字段 | 值 |
|------|----|
| **前置条件** | 至少有一个已保存连接 |
| **请求** | `GET /api/v1/dbs` |
| **预期状态码** | 200 |
| **预期响应** | 返回数组，每项包含 `dbName`、`dbUrl`、`createdAt`、`tableCount` |
| **实际结果** | |
| **状态** | ⬚ |

---

## 模块二：Metadata

### TC-API-007：获取已有连接的 metadata

| 字段 | 值 |
|------|----|
| **前置条件** | `testdb` 连接已保存且有缓存 |
| **请求** | `GET /api/v1/dbs/testdb` |
| **预期状态码** | 200 |
| **预期响应** | 返回数组，每项包含 `schemaName`、`tableName`、`tableType`、`columns` |
| **验证点** | 应返回 `users`、`products`、`orders`、`order_items` 四张表 |
| **实际结果** | |
| **状态** | ⬚ |

### TC-API-008：获取不存在的连接的 metadata

| 字段 | 值 |
|------|----|
| **前置条件** | — |
| **请求** | `GET /api/v1/dbs/nonexistent` |
| **预期状态码** | 404 |
| **预期错误码** | `DB_NOT_FOUND` |
| **实际结果** | |
| **状态** | ⬚ |

### TC-API-009：强制刷新 metadata

| 字段 | 值 |
|------|----|
| **前置条件** | `testdb` 连接已保存 |
| **请求** | `GET /api/v1/dbs/testdb?refresh=true` |
| **预期状态码** | 200 |
| **预期响应** | 与 TC-API-007 格式一致，`refreshed_at` 应更新 |
| **实际结果** | |
| **状态** | ⬚ |

---

## 模块三：SQL 查询执行

### TC-API-010：执行简单 SELECT 查询

| 字段 | 值 |
|------|----|
| **前置条件** | `testdb` 连接已保存 |
| **请求** | `POST /api/v1/dbs/testdb/query` |
| **请求体** | `{"sql": "SELECT id, username FROM users LIMIT 3"}` |
| **预期状态码** | 200 |
| **预期响应字段** | `columns`（含 name、dataType、nullable）、`rows`、`rowCount`、`truncated`、`sqlExecuted` |
| **实际结果** | |
| **状态** | ⬚ |

### TC-API-011：SQL 无 LIMIT 自动追加

| 字段 | 值 |
|------|----|
| **前置条件** | `testdb` 连接已保存 |
| **请求** | `POST /api/v1/dbs/testdb/query` |
| **请求体** | `{"sql": "SELECT * FROM users"}` |
| **预期** | `sqlExecuted` 应以 `LIMIT 1000` 结尾，`truncated` 为 true |
| **实际结果** | |
| **状态** | ⬚ |

### TC-API-012：拒绝非 SELECT 语句

| 字段 | 值 |
|------|----|
| **前置条件** | `testdb` 连接已保存 |
| **请求** | `POST /api/v1/dbs/testdb/query` |
| **请求体** | `{"sql": "DELETE FROM users WHERE id = 1"}` |
| **预期状态码** | 400 |
| **预期错误码** | `INVALID_SQL` |
| **实际结果** | |
| **状态** | ⬚ |

### TC-API-013：SQL 语法错误

| 字段 | 值 |
|------|----|
| **前置条件** | `testdb` 连接已保存 |
| **请求** | `POST /api/v1/dbs/testdb/query` |
| **请求体** | `{"sql": "SELECCT * FORM users"}` |
| **预期状态码** | 400 |
| **预期错误码** | `INVALID_SQL` |
| **实际结果** | |
| **状态** | ⬚ |

### TC-API-014：连接不存在时执行查询

| 字段 | 值 |
|------|----|
| **前置条件** | — |
| **请求** | `POST /api/v1/dbs/nonexistent/query` |
| **请求体** | `{"sql": "SELECT 1"}` |
| **预期状态码** | 404 |
| **预期错误码** | `DB_NOT_FOUND` |
| **实际结果** | |
| **状态** | ⬚ |

### TC-API-015：空 SQL

| 字段 | 值 |
|------|----|
| **前置条件** | `testdb` 连接已保存 |
| **请求** | `POST /api/v1/dbs/testdb/query` |
| **请求体** | `{"sql": ""}` |
| **预期状态码** | 400 |
| **预期错误码** | `INVALID_SQL` |
| **实际结果** | |
| **状态** | ⬚ |

---

## 模块四：自然语言查询

### TC-API-016：自然语言查询（成功）

| 字段 | 值 |
|------|----|
| **前置条件** | `testdb` 连接已保存，Ollama 服务运行中 |
| **请求** | `POST /api/v1/dbs/testdb/query/natural` |
| **请求体** | `{"natural": "查询所有活跃用户"}` |
| **预期状态码** | 200 |
| **预期** | `sqlExecuted` 含 `WHERE is_active` 或等效条件，响应含用户列表 |
| **实际结果** | |
| **状态** | ⬚ |

### TC-API-017：自然语言查询——复杂查询

| 字段 | 值 |
|------|----|
| **前置条件** | `testdb` 连接已保存，Ollama 运行中 |
| **请求** | `POST /api/v1/dbs/testdb/query/natural` |
| **请求体** | `{"natural": "按产品分类统计数量和平均价格，显示分类名、数量和均价"}` |
| **预期状态码** | 200 |
| **预期** | 生成含 `GROUP BY` 的 SQL，返回分类统计数据 |
| **实际结果** | |
| **状态** | ⬚ |

### TC-API-018：自然语言查询——空输入

| 字段 | 值 |
|------|----|
| **前置条件** | `testdb` 连接已保存 |
| **请求** | `POST /api/v1/dbs/testdb/query/natural` |
| **请求体** | `{"natural": ""}` |
| **预期状态码** | 400 |
| **预期错误码** | `EMPTY_INPUT` |
| **实际结果** | |
| **状态** | ⬚ |

### TC-API-019：自然语言查询——连接不存在

| 字段 | 值 |
|------|----|
| **前置条件** | — |
| **请求** | `POST /api/v1/dbs/nonexistent/query/natural` |
| **请求体** | `{"natural": "查询所有用户"}` |
| **预期状态码** | 404 |
| **预期错误码** | `DB_NOT_FOUND` |
| **实际结果** | |
| **状态** | ⬚ |

---

## 模块五：响应格式验证

### TC-API-020：统一错误格式

| 字段 | 值 |
|------|----|
| **覆盖端点** | 所有返回 4xx/5xx 的端点 |
| **预期格式** | `{"detail": {"code": "ERROR_CODE", "message": "..."}}` |
| **预期** | 所有错误响应均遵循此格式，`code` 为大写蛇形命名 |
| **实际结果** | |
| **状态** | ⬚ |

### TC-API-021：camelCase 响应字段

| 字段 | 值 |
|------|----|
| **覆盖端点** | 所有返回 200/201 的端点 |
| **预期** | 所有 JSON 属性名使用 camelCase（如 `dbName`、`tableCount`、`schemaName`）而非 snake_case |
| **实际结果** | |
| **状态** | ⬚ |
