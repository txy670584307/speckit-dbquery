import aiosqlite
import json
from datetime import datetime, timezone

from backend.config import settings


async def get_db() -> aiosqlite.Connection:
    db = await aiosqlite.connect(settings.local_db_path)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    return db


async def init_db():
    db = await get_db()
    try:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS db_connections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                db_name TEXT NOT NULL UNIQUE,
                db_url TEXT NOT NULL,
                db_type TEXT NOT NULL DEFAULT 'postgresql',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS table_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                db_name TEXT NOT NULL,
                schema_name TEXT NOT NULL,
                table_name TEXT NOT NULL,
                table_type TEXT NOT NULL,
                columns_json TEXT NOT NULL,
                refreshed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(db_name, schema_name, table_name)
            );
        """)
        await db.commit()
    finally:
        await db.close()
