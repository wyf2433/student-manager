"""速记数据访问层"""

from database import get_db


def create_note(content: str, student_id: int = None) -> dict:
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO quick_notes (content, student_id) VALUES (?, ?)",
            (content, student_id),
        )
        row = conn.execute("SELECT * FROM quick_notes WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return dict(row)


def get_note_by_id(note_id: int) -> dict | None:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM quick_notes WHERE id = ?", (note_id,)).fetchone()
        return dict(row) if row else None


def list_notes(page: int = 1, page_size: int = 50) -> dict:
    offset = (page - 1) * page_size
    with get_db() as conn:
        total = conn.execute("SELECT COUNT(*) as cnt FROM quick_notes").fetchone()["cnt"]
        rows = conn.execute(
            "SELECT * FROM quick_notes ORDER BY created_at DESC, id DESC LIMIT ? OFFSET ?",
            (page_size, offset),
        ).fetchall()
        return {"items": [dict(r) for r in rows], "total": total, "page": page, "page_size": page_size}


def update_note_student(note_id: int, student_id: int) -> dict | None:
    with get_db() as conn:
        current = conn.execute("SELECT * FROM quick_notes WHERE id = ?", (note_id,)).fetchone()
        if not current:
            return None
        conn.execute("UPDATE quick_notes SET student_id = ? WHERE id = ?", (student_id, note_id))
        row = conn.execute("SELECT * FROM quick_notes WHERE id = ?", (note_id,)).fetchone()
        return dict(row)


def delete_note(note_id: int) -> bool:
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM quick_notes WHERE id = ?", (note_id,))
        return cursor.rowcount > 0


def count_today(date_str: str) -> int:
    with get_db() as conn:
        return conn.execute(
            "SELECT COUNT(*) as cnt FROM quick_notes WHERE date(created_at) = ?",
            (date_str,),
        ).fetchone()["cnt"]
