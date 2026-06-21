import json
from datetime import datetime
from typing import Optional

from enum import Enum
from pydantic import BaseModel, Field


def to_camel(string: str) -> str:
    first, *rest = string.split("_")
    return first + "".join(x.title() for x in rest)


class BaseSchema(BaseModel):
    model_config = {
        "alias_generator": to_camel,
        "populate_by_name": True,
        "from_attributes": True,
    }


# --- Requests ---

class DbCreateRequest(BaseModel):
    db_url: str = Field(..., description="JDBC PostgreSQL connection URL")


class QueryRequest(BaseModel):
    sql: str


class NaturalQueryRequest(BaseModel):
    natural: str


# --- Responses ---

class DbResponse(BaseSchema):
    db_name: str
    db_url: str
    created_at: datetime
    table_count: int = 0


class ColumnInfo(BaseSchema):
    name: str
    data_type: str
    nullable: bool


class TableMetadataResponse(BaseSchema):
    schema_name: str
    table_name: str
    table_type: str  # 'table' | 'view'
    columns: list[ColumnInfo]


class QueryResultResponse(BaseSchema):
    columns: list[ColumnInfo]
    rows: list[list]
    row_count: int
    truncated: bool
    sql_executed: str


class ExportFormat(str, Enum):
    """导出文件格式枚举"""
    CSV = "csv"
    JSON = "json"


class ExportResult(BaseSchema):
    """导出结果（内存对象，不持久化）"""
    file_name: str
    content_type: str
    content: str
    format: ExportFormat
    truncated: bool


def parse_columns_json(raw: str) -> list[ColumnInfo]:
    items = json.loads(raw)
    return [ColumnInfo(name=c["name"], data_type=c["dataType"], nullable=c["nullable"]) for c in items]
