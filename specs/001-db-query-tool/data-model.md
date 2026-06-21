# Data Model: 数据库查询工具

## Entity Relationship

```
DatabaseConnection (1) ──── (N) TableMetadata
```

## Entities

### DatabaseConnection

表示一个已保存的数据库连接配置。API 路由以 `db_name` 作为唯一标识。

| Field | Type | Constraints | Description |
|-------|------|------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | 内部自增 ID |
| db_name | TEXT | NOT NULL, UNIQUE | 用户自定义名称，用作 API 路径标识 |
| db_url | TEXT | NOT NULL | JDBC 格式连接字符串 |
| db_type | TEXT | NOT NULL, DEFAULT 'postgresql' | 数据库类型 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

**Validation (Pydantic)**:
- `db_name`: non-empty string, max 128 chars, URL-safe（用作路径参数）
- `db_url`: non-empty string, must match JDBC URL pattern: `jdbc:postgresql://...`
- `db_type`: must be `"postgresql"`

**JDBC URL 格式**:
```
jdbc:postgresql://<host>:<port>/<database>?user=<user>&password=<password>
```

后端需将 JDBC URL 转换为 psycopg/asyncpg 异步驱动可用的连接参数。

**State**: Active (default) — 无软删除，删除即物理删除（CASCADE 到 TableMetadata）。

### TableMetadata

表示一个数据库表或视图的 metadata 缓存。

| Field | Type | Constraints | Description |
|-------|------|------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | 唯一标识 |
| db_name | TEXT | NOT NULL | 所属连接名称（对应 DatabaseConnection.db_name） |
| schema_name | TEXT | NOT NULL | Schema 名（如 public） |
| table_name | TEXT | NOT NULL | 表或视图名 |
| table_type | TEXT | NOT NULL | 'table' 或 'view' |
| columns_json | TEXT | NOT NULL | 列信息 JSON |
| refreshed_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 刷新时间 |

**columns_json 结构**:
```json
[
  {"name": "id", "dataType": "integer", "nullable": false},
  {"name": "username", "dataType": "character varying", "nullable": true}
]
```

**唯一约束**: (db_name, schema_name, table_name) 组合唯一

**生命周期**:
- Created: 添加数据库连接时自动获取
- Updated: 用户手动刷新时更新 `columns_json` 和 `refreshed_at`
- Deleted: 删除连接时级联清除

### QueryResult (内存对象，不持久化)

表示一次查询的执行结果。仅在内存中存在。

| Field | Type | Description |
|-------|------|-------------|
| columns | list[ColumnInfo] | 列名和类型列表 |
| rows | list[list[Any]] | 行数据（二维数组） |
| row_count | int | 总行数 |
| truncated | bool | 是否被 LIMIT 截断 |
| sql_executed | str | 实际执行的 SQL |

## Pydantic Schemas (Backend)

```python
from pydantic import BaseModel, Field
from datetime import datetime

class DbCreateRequest(BaseModel):
    db_url: str = Field(..., description="JDBC PostgreSQL connection URL")

class DbResponse(BaseModel):
    db_name: str
    db_url: str
    created_at: datetime
    table_count: int = 0

class ColumnInfo(BaseModel):
    name: str
    data_type: str
    nullable: bool

class TableMetadataResponse(BaseModel):
    schema_name: str
    table_name: str
    table_type: str  # 'table' | 'view'
    columns: list[ColumnInfo]

class QueryRequest(BaseModel):
    sql: str

class NaturalQueryRequest(BaseModel):
    natural: str

class QueryResultResponse(BaseModel):
    columns: list[ColumnInfo]
    rows: list[list]
    row_count: int
    truncated: bool
    sql_executed: str
```

### ExportFormat（枚举，非持久化）

表示导出文件的目标格式。

| Value | Description |
|-------|-------------|
| `CSV` | RFC 4180 逗号分隔值文件，UTF-8 BOM |
| `JSON` | 标准 JSON 数组文件，UTF-8 |

在 API 查询参数和前端导出下拉菜单中使用。后端通过 `ExportFormat` 枚举选择序列化策略。

```python
from enum import Enum

class ExportFormat(str, Enum):
    CSV = "csv"
    JSON = "json"
```

### ExportResult（内存对象，不持久化）

```python
class ExportResult(BaseModel):
    file_name: str          # 文件名（含扩展名）
    content_type: str       # MIME type（text/csv 或 application/json）
    content: str            # 文件内容（字符串）
    format: ExportFormat    # 导出格式
    truncated: bool         # 是否被 LIMIT 截断
```

## camelCase JSON 输出

后端 Pydantic model 使用 Python snake_case 字段名，通过 `model_config` 配置 `alias_generator` 实现自动转换为 camelCase：

```python
def to_camel(string: str) -> str:
    first, *rest = string.split('_')
    return first + ''.join(x.title() for x in rest)

class BaseSchema(BaseModel):
    model_config = {
        "alias_generator": to_camel,
        "populate_by_name": True,
        "from_attributes": True,
    }
```
