import os
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from backend.database import get_db
from backend.models import ExportFormat, QueryRequest, QueryResultResponse
from backend.services.export_service import build_filename, generate_export_content
from backend.services.pg_service import execute_query
from backend.services.sql_validator import validate_and_fix

router = APIRouter(tags=["query"])


@router.post("/dbs/{db_name}/query", response_model=QueryResultResponse)
async def run_query(
    db_name: str,
    body: QueryRequest,
    export: Optional[str] = Query(None, description="导出格式: csv 或 json"),
    output_path: Optional[str] = Query(None, description="服务器端保存路径（仅 export 指定时有效）"),
):
    """执行 SQL 查询（仅允许 SELECT，自动追加 LIMIT 1000）。

    支持通过 `?export=csv|json` 查询参数直接导出文件。
    支持通过 `&output_path=<path>` 指定服务器保存路径。
    """
    # 1. Validate export format if specified
    if export is not None:
        if export not in ("csv", "json"):
            raise HTTPException(status_code=400, detail={
                "code": "INVALID_EXPORT_FORMAT",
                "message": f"不支持的导出格式: '{export}'，仅支持 'csv' 或 'json'",
                "location": "query.export",
            })
        export_fmt = ExportFormat(export)

    # 2. Validate and fix SQL
    validation = validate_and_fix(body.sql)
    if not validation.valid:
        raise HTTPException(status_code=400, detail={
            "code": "INVALID_SQL",
            "message": validation.error or "SQL 语法错误",
            "location": "request.sql",
        })

    # 3. Get connection info from SQLite
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
                "location": "path.db_name",
            })
        db_url = row["db_url"]
    finally:
        await db.close()

    # 4. Execute query against PostgreSQL
    try:
        result = await execute_query(db_url, validation.sql)
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "code": "QUERY_FAILED",
            "message": f"查询执行失败: {e}",
            "location": "request.sql",
        })

    # 5. If export is requested, return file stream instead of JSON
    if export is not None:
        return _export_result(result, db_name, export_fmt, output_path)

    return result


def _export_result(
    result: QueryResultResponse,
    db_name: str,
    fmt: ExportFormat,
    output_path: Optional[str] = None,
) -> StreamingResponse:
    """将 QueryResult 转换为文件流响应。"""
    content = generate_export_content(result.columns, result.rows, fmt)
    filename = build_filename(db_name, fmt)

    # 如果指定了 output_path，额外写入服务器文件系统
    if output_path:
        try:
            resolved = os.path.abspath(output_path)
            dir_path = os.path.dirname(resolved)
            if not os.path.isdir(dir_path):
                raise HTTPException(status_code=400, detail={
                    "code": "EXPORT_PATH_ERROR",
                    "message": f"导出路径的目录不存在: {dir_path}",
                    "location": "query.output_path",
                })
            with open(resolved, "w", encoding="utf-8") as f:
                f.write(content)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail={
                "code": "EXPORT_PATH_ERROR",
                "message": f"无法写入导出文件: {e}",
                "location": "query.output_path",
            })

    # 确定 Media Type
    media_type = "text/csv; charset=utf-8" if fmt == ExportFormat.CSV else "application/json; charset=utf-8"

    return StreamingResponse(
        iter([content]),
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )
