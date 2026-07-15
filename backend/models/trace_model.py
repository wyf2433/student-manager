"""工作留痕数据访问层"""

import json

from database import get_db


def create_trace(title: str, type: str, note: str = None,
                 image_urls: list = None, student_ids: list = None) -> dict:
    with get_db() as conn:
        cursor = conn.execute(
            """INSERT INTO traces (title, type, note, image_urls, student_ids)
               VALUES (?, ?, ?, ?, ?)""",
            (
                title, type, note,
                json.dumps(image_urls, ensure_ascii=False) if image_urls else None,
                json.dumps(student_ids, ensure_ascii=False) if student_ids else None,
            ),
        )
        row = conn.execute("SELECT * FROM traces WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return _row_to_dict(row)


def get_trace_by_id(trace_id: int) -> dict | None:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM traces WHERE id = ?", (trace_id,)).fetchone()
        return _row_to_dict(row) if row else None


def list_traces(type: str = None, page: int = 1, page_size: int = 50) -> dict:
    offset = (page - 1) * page_size
    sql = "SELECT * FROM traces WHERE 1=1"
    params = []
    if type:
        sql += " AND type = ?"
        params.append(type)
    count_sql = sql.replace("SELECT *", "SELECT COUNT(*) as cnt", 1)
    with get_db() as conn:
        total = conn.execute(count_sql, params).fetchone()["cnt"]
        sql += " ORDER BY created_at DESC, id DESC LIMIT ? OFFSET ?"
        params.extend([page_size, offset])
        rows = conn.execute(sql, params).fetchall()
        return {"items": [_row_to_dict(r) for r in rows], "total": total, "page": page, "page_size": page_size}


def update_trace(trace_id: int, title: str = None, type: str = None,
                 note: str = None, image_urls: list = None,
                 student_ids: list = None) -> dict | None:
    with get_db() as conn:
        current = conn.execute("SELECT * FROM traces WHERE id = ?", (trace_id,)).fetchone()
        if not current:
            return None
        updates = []
        params = []
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if type is not None:
            updates.append("type = ?")
            params.append(type)
        if note is not None:
            updates.append("note = ?")
            params.append(note)
        if image_urls is not None:
            updates.append("image_urls = ?")
            params.append(json.dumps(image_urls, ensure_ascii=False) if image_urls else None)
        if student_ids is not None:
            updates.append("student_ids = ?")
            params.append(json.dumps(student_ids, ensure_ascii=False) if student_ids else None)
        if not updates:
            return _row_to_dict(current)
        params.append(trace_id)
        conn.execute(f"UPDATE traces SET {', '.join(updates)} WHERE id = ?", params)
        row = conn.execute("SELECT * FROM traces WHERE id = ?", (trace_id,)).fetchone()
        return _row_to_dict(row) if row else None


def delete_trace(trace_id: int) -> bool:
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM traces WHERE id = ?", (trace_id,))
        return cursor.rowcount > 0


def count_today(date_str: str) -> int:
    with get_db() as conn:
        return conn.execute(
            "SELECT COUNT(*) as cnt FROM traces WHERE date(created_at) = ?",
            (date_str,),
        ).fetchone()["cnt"]


def _row_to_dict(row) -> dict:
    d = dict(row)
    if d.get("image_urls"):
        try:
            d["image_urls"] = json.loads(d["image_urls"])
        except (ValueError, TypeError):
            d["image_urls"] = []
    else:
        d["image_urls"] = []
    if d.get("student_ids"):
        try:
            d["student_ids"] = json.loads(d["student_ids"])
        except (ValueError, TypeError):
            d["student_ids"] = []
    else:
        d["student_ids"] = []
    return d
