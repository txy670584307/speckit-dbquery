import json
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query

from backend.database import get_db
from backend.models import (
    ColumnInfo,
    DbCreateRequest,
    DbResponse,
    TableMetadataResponse,
    parse_columns_json,
)
from backend.services.pg_service import connect_and_fetch_metadata

router = APIRouter(tags=["dbs"])


@router.get("/dbs", response_model=list[DbResponse])
async def list_databases():
    """获取所有已连接的数据库"""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM db_connections ORDER BY created_at DESC")
        rows = await cursor.fetchall()
        results = []
        for row in rows:
            # count tables for each connection
            count_cursor = await db.execute(
                "SELECT COUNT(*) as cnt FROM table_metadata WHERE db_name = ?",
                (row["db_name"],),
            )
            count_row = await count_cursor.fetchone()
            resp = DbResponse(
                db_name=row["db_name"],
                db_url=row["db_url"],
                created_at=row["created_at"],
                table_count=count_row["cnt"] if count_row else 0,
            )
            results.append(resp)
        return results
    finally:
        await db.close()


@router.post("/dbs/{db_name}", response_model=DbResponse, status_code=201)
async def create_database(db_name: str, body: DbCreateRequest):
    """添加数据库连接，自动连接并获取 metadata 缓存"""
    # Validate JDBC URL format
    if not body.db_url.startswith("jdbc:postgresql://"):
        raise HTTPException(status_code=400, detail={
            "code": "INVALID_JDBC_URL",
            "message": "JDBC URL 必须以 jdbc:postgresql:// 开头",
        })

    # Connect to PostgreSQL and fetch metadata
    try:
        tables, jdbc = await connect_and_fetch_metadata(body.db_url)
    except Exception as e:
        raise HTTPException(status_code=400, detail={
            "code": "CONNECTION_FAILED",
            "message": f"数据库连接失败: {e}",
        })

    db = await get_db()
    try:
        # Insert db_connection
        try:
            await db.execute(
                "INSERT INTO db_connections (db_name, db_url, db_type) VALUES (?, ?, 'postgresql')",
                (db_name, body.db_url),
            )
        except Exception:
            raise HTTPException(status_code=409, detail={
                "code": "DB_NAME_EXISTS",
                "message": f"连接 '{db_name}' 已存在",
            })

        # Insert table_metadata
        now = datetime.now(timezone.utc).isoformat()
        for tbl in tables:
            columns_json = json.dumps(
                [{"name": c["name"], "dataType": c["dataType"], "nullable": c["nullable"]}
                 for c in tbl["columns"]]
            )
            await db.execute(
                """INSERT OR REPLACE INTO table_metadata
                   (db_name, schema_name, table_name, table_type, columns_json, refreshed_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (db_name, tbl["schemaName"], tbl["tableName"], tbl["tableType"], columns_json, now),
            )

        await db.commit()

        return DbResponse(
            db_name=db_name,
            db_url=body.db_url,
            created_at=datetime.now(timezone.utc),
            table_count=len(tables),
        )
    finally:
        await db.close()


@router.get("/dbs/{db_name}", response_model=list[TableMetadataResponse])
async def get_database_metadata(
    db_name: str,
    refresh: bool = Query(False, description="设为 true 时强制从数据库重新获取 metadata"),
):
    """获取数据库的 metadata（表/视图信息）。默认返回缓存，refresh=true 时重新连接数据库并刷新缓存。"""
    # Check connection exists first
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

        # If refresh requested, re-fetch from database and update cache
        if refresh:
            db_url = row["db_url"]
            db.close()  # close before reconnecting

            try:
                tables, _ = await connect_and_fetch_metadata(db_url)
            except Exception as e:
                # Failed to refresh — return stale cache
                db2 = await get_db()
                try:
                    cursor = await db2.execute(
                        "SELECT * FROM table_metadata WHERE db_name = ? ORDER BY table_type, schema_name, table_name",
                        (db_name,),
                    )
                    rows = await cursor.fetchall()
                finally:
                    await db2.close()

                if not rows:
                    raise HTTPException(status_code=400, detail={
                        "code": "REFRESH_FAILED",
                        "message": f"刷新失败: {e}。无缓存数据可用",
                    })

                # Build result from stale cache
                results = []
                for r in rows:
                    results.append(TableMetadataResponse(
                        schema_name=r["schema_name"],
                        table_name=r["table_name"],
                        table_type=r["table_type"],
                        columns=parse_columns_json(r["columns_json"]),
                    ))
                return results  # stale data returned

            # Update cache with fresh data
            db2 = await get_db()
            try:
                now = datetime.now(timezone.utc).isoformat()
                # Delete old cache for this db_name
                await db2.execute("DELETE FROM table_metadata WHERE db_name = ?", (db_name,))
                for tbl in tables:
                    columns_json = json.dumps(
                        [{"name": c["name"], "dataType": c["dataType"], "nullable": c["nullable"]}
                         for c in tbl["columns"]]
                    )
                    await db2.execute(
                        """INSERT INTO table_metadata
                           (db_name, schema_name, table_name, table_type, columns_json, refreshed_at)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (db_name, tbl["schemaName"], tbl["tableName"], tbl["tableType"], columns_json, now),
                    )
                await db2.commit()
            finally:
                await db2.close()

            # Return fresh data
            return [
                TableMetadataResponse(
                    schema_name=tbl["schemaName"],
                    table_name=tbl["tableName"],
                    table_type=tbl["tableType"],
                    columns=[
                        ColumnInfo(name=c["name"], data_type=c["dataType"], nullable=c["nullable"])
                        for c in tbl["columns"]
                    ],
                )
                for tbl in tables
            ]

        # Normal (cached) path
        cursor = await db.execute(
            "SELECT * FROM table_metadata WHERE db_name = ? ORDER BY table_type, schema_name, table_name",
            (db_name,),
        )
        rows = await cursor.fetchall()
        if not rows:
            return []  # connection exists but no tables yet

        results = []
        for r in rows:
            columns = parse_columns_json(r["columns_json"])
            results.append(TableMetadataResponse(
                schema_name=r["schema_name"],
                table_name=r["table_name"],
                table_type=r["table_type"],
                columns=columns,
            ))
        return results
    finally:
        try:
            await db.close()
        except Exception:
            pass


@router.delete("/dbs/{db_name}", status_code=200)
async def delete_database(db_name: str):
    """删除数据库连接及其 metadata 缓存"""
    db = await get_db()
    try:
        # Check if connection exists
        exists = await db.execute(
            "SELECT 1 FROM db_connections WHERE db_name = ?", (db_name,)
        )
        if not await exists.fetchone():
            raise HTTPException(status_code=404, detail={
                "code": "DB_NOT_FOUND",
                "message": f"连接 '{db_name}' 不存在",
            })

        # Delete metadata first, then connection
        await db.execute("DELETE FROM table_metadata WHERE db_name = ?", (db_name,))
        await db.execute("DELETE FROM db_connections WHERE db_name = ?", (db_name,))
        await db.commit()

        return {"detail": {"code": "DELETED", "message": f"连接 '{db_name}' 已删除"}}
    finally:
        await db.close()
