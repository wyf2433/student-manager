"""日常记录数据访问层(考勤/请假/加扣分)"""

from database import get_db


def create_record(student_id: int, type: str, content: str = None, value: float = None) -> dict:
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO records (student_id, type, content, value) VALUES (?, ?, ?, ?)",
            (student_id, type, content, value),
        )
        row = conn.execute("SELECT * FROM records WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return dict(row)


def get_record_by_id(record_id: int) -> dict | None:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM records WHERE id = ?", (record_id,)).fetchone()
        return dict(row) if row else None


def list_records(student_id: int = None, type: str = None, page: int = 1, page_size: int = 50) -> dict:
    offset = (page - 1) * page_size
    sql = "SELECT * FROM records WHERE 1=1"
    params = []
    if student_id:
        sql += " AND student_id = ?"
        params.append(student_id)
    if type:
        sql += " AND type = ?"
        params.append(type)
    count_sql = sql.replace("SELECT *", "SELECT COUNT(*) as cnt", 1)
    with get_db() as conn:
        total = conn.execute(count_sql, params).fetchone()["cnt"]
        sql += " ORDER BY created_at DESC, id DESC LIMIT ? OFFSET ?"
        params.extend([page_size, offset])
        rows = conn.execute(sql, params).fetchall()
        return {"items": [dict(r) for r in rows], "total": total, "page": page, "page_size": page_size}


def delete_record(record_id: int) -> bool:
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM records WHERE id = ?", (record_id,))
        return cursor.rowcount > 0


def count_today_by_type(date_str: str) -> dict:
    """统计今日各类型记录数"""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT type, COUNT(*) as cnt FROM records WHERE date(created_at) = ? GROUP BY type",
            (date_str,),
        ).fetchall()
        result = {"attendance": 0, "leave": 0, "score": 0}
        for row in rows:
            result[row["type"]] = row["cnt"]
        return result
