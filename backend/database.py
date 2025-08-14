
import os
import sqlite3
from pathlib import Path

DB_PATH = Path(os.getenv("DB_PATH", Path(__file__).parent / "urls.db"))

def get_conn():
    # check_same_thread=False lets us reuse the connection in FastAPI
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_code TEXT UNIQUE NOT NULL,
            long_url TEXT NOT NULL,
            clicks INTEGER NOT NULL DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_urls_short_code ON urls(short_code);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_urls_long_url ON urls(long_url);")
    conn.commit()
    conn.close()
