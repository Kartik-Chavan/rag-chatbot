# utils/session_db.py
import sqlite3
from config.settings import DB_DIR

SESSION_DB_PATH = DB_DIR / "session.db"

def get_connection():
    return sqlite3.connect(SESSION_DB_PATH, check_same_thread=False)

def init_session_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_name TEXT,
            thread_id TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def create_session(session_name, thread_id):
    conn = get_connection()
    conn.execute(
        "INSERT INTO sessions (session_name, thread_id) VALUES (?, ?)",
        (session_name, thread_id)
    )
    conn.commit()
    conn.close()

def get_sessions():
    conn = get_connection()
    rows = conn.execute(
        "SELECT session_name, thread_id FROM sessions ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return rows

def delete_session(thread_id):
    conn = get_connection()
    conn.execute(
        "DELETE FROM sessions WHERE thread_id = ?",
        (thread_id,)
    )
    conn.commit()
    conn.close()


def rename_session(thread_id, new_name):
    conn = get_connection()
    conn.execute(
        "UPDATE sessions SET session_name = ? WHERE thread_id = ?",
        (new_name, thread_id)
    )
    conn.commit()
    conn.close()

