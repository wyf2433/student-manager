"""学生数据访问层"""

from database import get_db


def create_student(class_id: int, name: str, student_no: str = None, gender: str = None) -> dict:
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO students (class_id, name, student_no, gender) VALUES (?, ?, ?, ?)",
            (class_id, name, student_no, gender),
        )
        row = conn.execute("SELECT * FROM students WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return dict(row)


def get_student_by_id(student_id: int) -> dict | None:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
        return dict(row) if row else None


def list_students(class_id: int = None, keyword: str = None, page: int = 1, page_size: int = 50) -> dict:
    offset = (page - 1) * page_size
    sql = "SELECT * FROM students WHERE 1=1"
    params = []
    if class_id:
        sql += " AND class_id = ?"
        params.append(class_id)
    if keyword:
        sql += " AND (name LIKE ? OR student_no LIKE ?)"
        params.extend([f"%{keyword}%", f"%{keyword}%"])
    count_sql = sql.replace("SELECT *", "SELECT COUNT(*) as cnt", 1)
    with get_db() as conn:
        total = conn.execute(count_sql, params).fetchone()["cnt"]
        sql += " ORDER BY id LIMIT ? OFFSET ?"
        params.extend([page_size, offset])
        rows = conn.execute(sql, params).fetchall()
        return {"items": [dict(r) for r in rows], "total": total, "page": page, "page_size": page_size}


def batch_create_students(students: list[dict]) -> int:
    with get_db() as conn:
        for s in students:
            conn.execute(
                "INSERT INTO students (class_id, name, student_no, gender) VALUES (?, ?, ?, ?)",
                (s["class_id"], s["name"], s.get("student_no"), s.get("gender")),
            )
        return len(students)


def update_student(student_id: int, **kwargs) -> dict | None:
    with get_db() as conn:
        current = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
        if not current:
            return None
        fields = ["class_id", "name", "student_no", "gender"]
        updates = []
        params = []
        for f in fields:
            if f in kwargs and kwargs[f] is not None:
                updates.append(f"{f} = ?")
                params.append(kwargs[f])
        if not updates:
            return dict(current)
        params.append(student_id)
        conn.execute(f"UPDATE students SET {', '.join(updates)} WHERE id = ?", params)
        row = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
        return dict(row) if row else None


def delete_student(student_id: int) -> bool:
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
        return cursor.rowcount > 0
