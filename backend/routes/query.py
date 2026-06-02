from fastapi import APIRouter, HTTPException

from backend.database import get_db
from backend.models import QueryRequest, QueryResultResponse
from backend.services.pg_service import execute_query
from backend.services.sql_validator import validate_and_fix

router = APIRouter(tags=["query"])


@router.post("/dbs/{db_name}/query", response_model=QueryResultResponse)
async def run_query(db_name: str, body: QueryRequest):
    """执行 SQL 查询（仅允许 SELECT，自动追加 LIMIT 1000）"""
    # 1. Validate and fix SQL
    validation = validate_and_fix(body.sql)
    if not validation.valid:
        raise HTTPException(status_code=400, detail={
            "code": "INVALID_SQL",
            "message": validation.error or "SQL 语法错误",
            "location": "request.sql",
        })

    # 2. Get connection info from SQLite
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT db_url FROM db_connections WHERE db_name = ?",
            (db_name,),
        )
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail={
                "code": "DB_NOT_FOUND",
                "message": f"连接 '{db_name}' 不存在",
            })
        db_url = row["db_url"]
    finally:
        await db.close()

    # 3. Execute query against PostgreSQL
    try:
        result = await execute_query(db_url, validation.sql)
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "code": "QUERY_FAILED",
            "message": f"查询执行失败: {e}",
        })

    return result
