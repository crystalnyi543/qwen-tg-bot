"""
SQLite база для хранения истории диалогов пользователей.
"""
import sqlite3
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
DB_PATH = Path("data/bot.db")


class Database:
    def __init__(self):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id       INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id  INTEGER NOT NULL,
                    role     TEXT    NOT NULL,
                    content  TEXT    NOT NULL,
                    ts       DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_id ON chat_history(user_id)
            """)
            conn.commit()
        logger.info("✅ БД инициализирована")

    def add_message(self, user_id: int, role: str, content: str):
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO chat_history (user_id, role, content) VALUES (?, ?, ?)",
                (user_id, role, content)
            )
            conn.commit()

    def get_history(self, user_id: int, limit: int = 20) -> list[dict]:
        """Возвращает последние N сообщений пользователя."""
        with self._connect() as conn:
            rows = conn.execute(
                """SELECT role, content FROM chat_history
                   WHERE user_id = ?
                   ORDER BY ts DESC LIMIT ?""",
                (user_id, limit)
            ).fetchall()
        # Возвращаем в хронологическом порядке
        return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]

    def clear_history(self, user_id: int):
        with self._connect() as conn:
            conn.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
            conn.commit()

    def get_stats(self) -> dict:
        """Статистика бота."""
        with self._connect() as conn:
            users = conn.execute(
                "SELECT COUNT(DISTINCT user_id) as cnt FROM chat_history"
            ).fetchone()["cnt"]
            msgs = conn.execute(
                "SELECT COUNT(*) as cnt FROM chat_history"
            ).fetchone()["cnt"]
        return {"users": users, "messages": msgs}
