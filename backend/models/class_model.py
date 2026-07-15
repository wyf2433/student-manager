"""班级数据访问层"""

from database import get_db


def create_class(name: str, grade: str = None) -> dict:
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO classes (name, grade) VALUES (?, ?)",
            (name, grade),
        )
        row = conn.execute("SELECT * FROM classes WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return dict(row)


def get_class_by_id(class_id: int) -> dict | None:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM classes WHERE id = ?", (class_id,)).fetchone()
        return dict(row) if row else None


def list_classes() -> list[dict]:
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM classes ORDER BY id").fetchall()
        return [dict(r) for r in rows]


def update_class(class_id: int, name: str = None, grade: str = None) -> dict | None:
    with get_db() as conn:
        current = conn.execute("SELECT * FROM classes WHERE id = ?", (class_id,)).fetchone()
        if not current:
            return None
        conn.execute(
            "UPDATE classes SET name = ?, grade = ? WHERE id = ?",
            (
                name if name is not None else current["name"],
                grade if grade is not None else current["grade"],
                class_id,
            ),
        )
        row = conn.execute("SELECT * FROM classes WHERE id = ?", (class_id,)).fetchone()
        return dict(row)


def delete_class(class_id: int) -> bool:
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM classes WHERE id = ?", (class_id,))
        return cursor.rowcount > 0
