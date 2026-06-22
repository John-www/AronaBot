import json
import os
import sqlite3
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("DUNGEON_DB_PATH", PROJECT_DIR / "dungeon_game.db")).resolve()


def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def init_db():
    with connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS dungeon_players (
                user_id TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def load_player(user_id):
    init_db()
    with connect() as conn:
        row = conn.execute(
            "SELECT data FROM dungeon_players WHERE user_id = ?",
            (str(user_id),),
        ).fetchone()
    if not row:
        return None
    return json.loads(row["data"])


def save_player(state):
    init_db()
    data = json.dumps(state, ensure_ascii=False)
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO dungeon_players (user_id, data, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                data = excluded.data,
                updated_at = CURRENT_TIMESTAMP
            """,
            (str(state["user_id"]), data),
        )


def delete_player(user_id):
    init_db()
    with connect() as conn:
        conn.execute("DELETE FROM dungeon_players WHERE user_id = ?", (str(user_id),))


def diagnostics():
    info = {
        "db_path": str(DB_PATH),
        "exists": DB_PATH.exists(),
        "size": DB_PATH.stat().st_size if DB_PATH.exists() else 0,
        "env_path": os.getenv("DUNGEON_DB_PATH") or "",
        "ok": False,
        "error": "",
    }
    try:
        init_db()
        with connect() as conn:
            integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
            journal_mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
            count = conn.execute("SELECT COUNT(*) FROM dungeon_players").fetchone()[0]
        info.update({"ok": integrity == "ok", "integrity": integrity, "journal_mode": journal_mode, "players": count})
    except Exception as exc:
        info["error"] = repr(exc)
    return info
