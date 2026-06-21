import asyncio
import re
from typing import Any

from backend.models import ColumnInfo, QueryResultResponse

try:
    import asyncpg
except ImportError:
    asyncpg = None

try:
    import psycopg
except ImportError:
    psycopg = None

CONNECTION_TIMEOUT_SECONDS = 10.0


class JdbcUrl:
    """Parsed JDBC PostgreSQL URL components."""

    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password


def parse_jdbc_url(url: str) -> JdbcUrl:
    """Convert jdbc:postgresql://host:port/db?user=x&password=y to connection params."""
    pattern = r"jdbc:postgresql://(.*?):(\d+)/(.*?)\?(?:.*)user=(.*?)(?:&password=(.*))?$"
    match = re.match(pattern, url)
    if not match:
        raise ValueError(f"无效的 JDBC URL 格式: {url}")
    return JdbcUrl(
        host=match.group(1),
        port=int(match.group(2)),
        database=match.group(3),
        user=match.group(4),
        password=match.group(5) or "",
    )


async def connect_and_fetch_metadata(db_url: str) -> tuple[list[dict[str, Any]], JdbcUrl]:
    """
    Connect to PostgreSQL via JDBC URL, query information_schema,
    return list of table/view metadata dicts.
    """
    jdbc = parse_jdbc_url(db_url)

    if asyncpg is not None:
        try:
            conn = await asyncio.wait_for(
                asyncpg.connect(
                    host=jdbc.host,
                    port=jdbc.port,
                    database=jdbc.database,
                    user=jdbc.user,
                    password=jdbc.password,
                ),
                timeout=CONNECTION_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError:
            raise TimeoutError(
                f"连接 PostgreSQL 超时（{CONNECTION_TIMEOUT_SECONDS}s），请检查网络或数据库地址"
            )
        try:
            return await _query_metadata_asyncpg(conn, jdbc)
        finally:
            await conn.close()

    elif psycopg is not None:
        conn_info = (
            f"host={jdbc.host} port={jdbc.port} "
            f"dbname={jdbc.database} user={jdbc.user} password={jdbc.password}"
        )
        try:
            conn = await asyncio.wait_for(
                psycopg.AsyncConnection.connect(conn_info),
                timeout=CONNECTION_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError:
            raise TimeoutError(
                f"连接 PostgreSQL 超时（{CONNECTION_TIMEOUT_SECONDS}s），请检查网络或数据库地址"
            )
        async with conn:
            return await _query_metadata(conn, jdbc)

    else:
        raise ImportError("未安装任何 PostgreSQL 异步驱动（需要 asyncpg 或 psycopg）")


async def _query_metadata(conn, jdbc: JdbcUrl) -> tuple[list[dict[str, Any]], JdbcUrl]:
    """Query metadata using psycopg (Relational DB-API 2.0 style)."""
    tables = []
    async with conn.cursor() as cur:
        await cur.execute("""
            SELECT table_schema, table_name, table_type
            FROM information_schema.tables
            WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
              AND table_type IN ('BASE TABLE', 'VIEW')
            ORDER BY table_schema, table_name
        """)
        rows = await cur.fetchall()

        for schema, name, table_type in rows:
            await cur.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = %s AND table_name = %s
                ORDER BY ordinal_position
            """, (schema, name))

            columns = []
            async for col_name, col_type, nullable in cur:
                columns.append({
                    "name": col_name,
                    "dataType": col_type,
                    "nullable": nullable == "YES",
                })

            tables.append({
                "schemaName": schema,
                "tableName": name,
                "tableType": "view" if table_type == "VIEW" else "table",
                "columns": columns,
            })
    return tables, jdbc


async def _query_metadata_asyncpg(conn, jdbc: JdbcUrl) -> tuple[list[dict[str, Any]], JdbcUrl]:
    """Query metadata using asyncpg (native PostgreSQL driver)."""
    tables = []
    rows = await conn.fetch("""
        SELECT table_schema, table_name, table_type
        FROM information_schema.tables
        WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
          AND table_type IN ('BASE TABLE', 'VIEW')
        ORDER BY table_schema, table_name
    """)

    for row in rows:
        schema = row["table_schema"]
        name = row["table_name"]
        table_type = row["table_type"]

        col_rows = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = $1 AND table_name = $2
            ORDER BY ordinal_position
        """, schema, name)

        columns = [
            {
                "name": c["column_name"],
                "dataType": c["data_type"],
                "nullable": c["is_nullable"] == "YES",
            }
            for c in col_rows
        ]

        tables.append({
            "schemaName": schema,
            "tableName": name,
            "tableType": "view" if table_type == "VIEW" else "table",
            "columns": columns,
        })

    return tables, jdbc


async def execute_query(db_url: str, sql: str) -> QueryResultResponse:
    """Execute a SELECT query against PostgreSQL via JDBC URL."""
    jdbc = parse_jdbc_url(db_url)

    if asyncpg is not None:
        return await _execute_query_asyncpg(jdbc, sql)
    elif psycopg is not None:
        return await _execute_query_psycopg(jdbc, sql)
    else:
        raise ImportError("未安装任何 PostgreSQL 异步驱动（需要 asyncpg 或 psycopg）")


async def _execute_query_asyncpg(jdbc: JdbcUrl, sql: str) -> QueryResultResponse:
    """Execute query using asyncpg."""
    conn = await asyncio.wait_for(
        asyncpg.connect(
            host=jdbc.host,
            port=jdbc.port,
            database=jdbc.database,
            user=jdbc.user,
            password=jdbc.password,
        ),
        timeout=CONNECTION_TIMEOUT_SECONDS,
    )
    try:
        truncated = "LIMIT" in sql.upper()
        result = await conn.fetch(sql)

        if result:
            columns = [
                ColumnInfo(name=k, data_type=str(type(v).__name__), nullable=True)
                for k, v in dict(result[0]).items()
            ]
        else:
            columns = [ColumnInfo(name="?", data_type="unknown", nullable=True)]

        rows = [list(row.values()) for row in result]

        return QueryResultResponse(
            columns=columns,
            rows=rows,
            row_count=len(result),
            truncated=truncated,
            sql_executed=sql,
        )
    except asyncio.TimeoutError:
        raise TimeoutError(
            f"查询执行超时（{CONNECTION_TIMEOUT_SECONDS}s）"
        )
    finally:
        await conn.close()


async def _execute_query_psycopg(jdbc: JdbcUrl, sql: str) -> QueryResultResponse:
    """Execute query using psycopg (async)."""
    conn_info = (
        f"host={jdbc.host} port={jdbc.port} "
        f"dbname={jdbc.database} user={jdbc.user} password={jdbc.password}"
    )
    conn = await asyncio.wait_for(
        psycopg.AsyncConnection.connect(conn_info),
        timeout=CONNECTION_TIMEOUT_SECONDS,
    )
    try:
        truncated = "LIMIT" in sql.upper()
        async with conn.cursor() as cur:
            await cur.execute(sql)
            rows_raw = await cur.fetchall()

            if rows_raw:
                columns = [
                    ColumnInfo(
                        name=cur.description[i].name,
                        data_type=cur.description[i].type_object.display if cur.description[i].type_object else "unknown",
                        nullable=True,
                    )
                    for i in range(len(cur.description))
                ]
            else:
                columns = [ColumnInfo(name="?", data_type="unknown", nullable=True)]

            rows = [list(r) for r in rows_raw]

            return QueryResultResponse(
                columns=columns,
                rows=rows,
                row_count=len(rows_raw),
                truncated=truncated,
                sql_executed=sql,
            )
    except asyncio.TimeoutError:
        raise TimeoutError(
            f"查询执行超时（{CONNECTION_TIMEOUT_SECONDS}s）"
        )
    finally:
        await conn.close()
