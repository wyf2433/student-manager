"""作业数据访问层"""

from database import get_db


def create_homework(class_id: int, content: str, type: str,
                    due_date: str = None, note: str = None) -> dict:
    with get_db() as conn:
        cursor = conn.execute(
            """INSERT INTO homework (class_id, content, type, due_date, note)
               VALUES (?, ?, ?, ?, ?)""",
            (class_id, content, type, due_date, note),
        )
        row = conn.execute("SELECT * FROM homework WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return dict(row)


def get_homework_by_id(homework_id: int) -> dict | None:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM homework WHERE id = ?", (homework_id,)).fetchone()
        return dict(row) if row else None


def list_homework(class_id: int = None, status: str = None) -> list:
    sql = "SELECT * FROM homework WHERE 1=1"
    params = []
    if class_id:
        sql += " AND class_id = ?"
        params.append(class_id)
    if status:
        sql += " AND status = ?"
        params.append(status)
    sql += " ORDER BY created_at DESC, id DESC"
    with get_db() as conn:
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]


def get_today_homework() -> list:
    """今日布置的作业"""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM homework WHERE date(created_at) = date('now', 'localtime') ORDER BY id DESC",
        ).fetchall()
        return [dict(r) for r in rows]


def update_status(homework_id: int, status: str) -> dict | None:
    with get_db() as conn:
        current = conn.execute("SELECT * FROM homework WHERE id = ?", (homework_id,)).fetchone()
        if not current:
            return None
        conn.execute("UPDATE homework SET status = ? WHERE id = ?", (status, homework_id))
        row = conn.execute("SELECT * FROM homework WHERE id = ?", (homework_id,)).fetchone()
        return dict(row) if row else None


def delete_homework(homework_id: int) -> bool:
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM homework WHERE id = ?", (homework_id,))
        return cursor.rowcount > 0
