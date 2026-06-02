"""Models 序列化单元测试"""
import json
from datetime import datetime

from backend.models import (
    ColumnInfo,
    DbResponse,
    QueryResultResponse,
    TableMetadataResponse,
    NaturalQueryRequest,
    QueryRequest,
    DbCreateRequest,
    parse_columns_json,
)


class TestCamelCaseAlias:
    """camelCase 别名生成测试"""

    def test_db_response_serialization(self):
        """DbResponse 序列化为 camelCase"""
        dt = datetime(2026, 5, 27, 12, 0, 0)
        resp = DbResponse(db_name="testdb", db_url="jdbc:...", created_at=dt, table_count=4)
        data = resp.model_dump(by_alias=True)
        assert "dbName" in data
        assert "dbUrl" in data
        assert "createdAt" in data
        assert "tableCount" in data
        assert data["dbName"] == "testdb"
        assert data["tableCount"] == 4

    def test_db_response_snake_case_input(self):
        """DbResponse 也能接收 snake_case 输入"""
        dt = datetime(2026, 5, 27, 12, 0, 0)
        resp = DbResponse(db_name="test", db_url="url", created_at=dt, table_count=2)
        assert resp.db_name == "test"

    def test_query_result_response(self):
        """QueryResultResponse 序列化"""
        columns = [ColumnInfo(name="id", data_type="integer", nullable=True)]
        resp = QueryResultResponse(
            columns=columns,
            rows=[[1]],
            row_count=1,
            truncated=True,
            sql_executed="SELECT * FROM users LIMIT 1000",
        )
        data = resp.model_dump(by_alias=True)
        assert data["rowCount"] == 1
        assert data["truncated"] is True
        assert data["sqlExecuted"] is not None

    def test_table_metadata_response(self):
        """TableMetadataResponse 序列化"""
        columns = [ColumnInfo(name="id", data_type="integer", nullable=False)]
        resp = TableMetadataResponse(
            schema_name="public",
            table_name="users",
            table_type="table",
            columns=columns,
        )
        data = resp.model_dump(by_alias=True)
        assert data["schemaName"] == "public"
        assert data["tableName"] == "users"
        assert data["tableType"] == "table"
        assert len(data["columns"]) == 1
        assert data["columns"][0]["name"] == "id"

    def test_column_info_bool(self):
        """ColumnInfo nullable 布尔值"""
        col = ColumnInfo(name="col", data_type="text", nullable=True)
        assert col.nullable is True
        assert col.name == "col"
        assert col.data_type == "text"


class TestRequestModels:
    """请求体模型测试"""

    def test_db_create_request(self):
        req = DbCreateRequest(db_url="jdbc:postgresql://...")
        assert req.db_url == "jdbc:postgresql://..."

    def test_query_request(self):
        req = QueryRequest(sql="SELECT 1")
        assert req.sql == "SELECT 1"

    def test_natural_query_request(self):
        req = NaturalQueryRequest(natural="查询所有用户")
        assert req.natural == "查询所有用户"


class TestParseColumnsJson:
    """parse_columns_json 工具函数测试"""

    def test_parse_valid(self):
        raw = json.dumps([
            {"name": "id", "dataType": "integer", "nullable": True},
            {"name": "name", "dataType": "varchar", "nullable": False},
        ])
        result = parse_columns_json(raw)
        assert len(result) == 2
        assert result[0].name == "id"
        assert result[0].data_type == "integer"
        assert result[0].nullable is True
        assert result[1].name == "name"
        assert result[1].nullable is False

    def test_parse_empty(self):
        result = parse_columns_json("[]")
        assert result == []
