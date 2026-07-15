"""成绩数据访问层"""

from database import get_db


def create_score(student_id: int, exam_name: str, subject: str, score: float = None) -> dict:
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO scores (student_id, exam_name, subject, score) VALUES (?, ?, ?, ?)",
            (student_id, exam_name, subject, score),
        )
        row = conn.execute("SELECT * FROM scores WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return dict(row)


def list_scores(student_id: int = None, exam_name: str = None, subject: str = None) -> list:
    sql = "SELECT * FROM scores WHERE 1=1"
    params = []
    if student_id:
        sql += " AND student_id = ?"
        params.append(student_id)
    if exam_name:
        sql += " AND exam_name = ?"
        params.append(exam_name)
    if subject:
        sql += " AND subject = ?"
        params.append(subject)
    sql += " ORDER BY created_at DESC, id DESC"
    with get_db() as conn:
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]


def batch_create_scores(scores: list[dict]) -> int:
    with get_db() as conn:
        for s in scores:
            conn.execute(
                "INSERT INTO scores (student_id, exam_name, subject, score) VALUES (?, ?, ?, ?)",
                (s["student_id"], s["exam_name"], s["subject"], s.get("score")),
            )
        return len(scores)


def delete_score(score_id: int) -> bool:
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM scores WHERE id = ?", (score_id,))
        return cursor.rowcount > 0


def get_exam_names() -> list:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT DISTINCT exam_name FROM scores ORDER BY exam_name"
        ).fetchall()
        return [r["exam_name"] for r in rows]
