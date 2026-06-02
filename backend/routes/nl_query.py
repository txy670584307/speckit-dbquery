import json

from fastapi import APIRouter, HTTPException

from backend.database import get_db
from backend.models import NaturalQueryRequest, QueryResultResponse, parse_columns_json
from backend.services.llm_service import generate_sql
from backend.services.pg_service import execute_query
from backend.services.sql_validator import validate_and_fix

router = APIRouter(tags=["nl_query"])


@router.post("/dbs/{db_name}/query/natural", response_model=QueryResultResponse)
async def natural_language_query(db_name: str, body: NaturalQueryRequest):
    """将自然语言转换为 SQL 并执行"""
    if not body.natural or not body.natural.strip():
        raise HTTPException(status_code=400, detail={
            "code": "EMPTY_INPUT",
            "message": "请输入查询描述",
        })

    # 1. Get metadata context from SQLite cache
    db = await get_db()
    try:
        exists = await db.execute(
            "SELECT db_url FROM db_connections WHERE db_name = ?", (db_name,)
        )
        row = await exists.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail={
                "code": "DB_NOT_FOUND",
                "message": f"连接 '{db_name}' 不存在",
            })
        db_url = row["db_url"]

        # Build metadata context
        cursor = await db.execute(
            "SELECT * FROM table_metadata WHERE db_name = ? ORDER BY table_type, schema_name, table_name",
            (db_name,),
        )
        rows = await cursor.fetchall()
    finally:
        await db.close()

    if not rows:
        raise HTTPException(status_code=400, detail={
            "code": "NO_METADATA",
            "message": "该连接没有缓存 metadata，请先连接数据库",
        })

    # Format metadata for LLM context
    metadata_list = []
    for r in rows:
        columns = parse_columns_json(r["columns_json"])
        col_desc = ", ".join(f"{c.name} ({c.data_type})" for c in columns)
        metadata_list.append(
            f'- {r["table_type"]}: {r["schema_name"]}.{r["table_name"]} 列: [{col_desc}]'
        )
    metadata_context = "数据库表结构：\n" + "\n".join(metadata_list)

    # 2. Call LLM to generate SQL
    try:
        generated_sql = await generate_sql(
            db_name=db_name,
            natural_text=body.natural,
            metadata_json=metadata_context,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail={
            "code": "LLM_ERROR",
            "message": f"自然语言处理失败: {e}",
        })

    # 3. Validate generated SQL
    validation = validate_and_fix(generated_sql)
    if not validation.valid:
        # Return generated SQL so user can manually fix it
        raise HTTPException(status_code=400, detail={
            "code": "INVALID_GENERATED_SQL",
            "message": f"生成的 SQL 无效: {validation.error}",
            "generatedSql": generated_sql,
        })

    # 4. Execute validated SQL
    try:
        result = await execute_query(db_url, validation.sql)
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "code": "QUERY_FAILED",
            "message": f"查询执行失败: {e}",
            "generatedSql": validation.sql,
        })

    # Pass through the generated SQL for display
    result.sql_executed = validation.sql
    return result
