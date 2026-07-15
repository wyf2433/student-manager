"""课表数据访问层(常规课表 + 临时调课)"""

from database import get_db


def create_schedule(weekday: int, period: int, subject: str, class_name: str = None) -> dict:
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO schedule (weekday, period, subject, class_name) VALUES (?, ?, ?, ?)",
            (weekday, period, subject, class_name),
        )
        row = conn.execute("SELECT * FROM schedule WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return dict(row)


def get_schedule_by_id(schedule_id: int) -> dict | None:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM schedule WHERE id = ?", (schedule_id,)).fetchone()
        return dict(row) if row else None


def list_schedule(weekday: int = None) -> list:
    sql = "SELECT * FROM schedule WHERE 1=1"
    params = []
    if weekday is not None:
        sql += " AND weekday = ?"
        params.append(weekday)
    sql += " ORDER BY weekday, period"
    with get_db() as conn:
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]


def update_schedule(schedule_id: int, weekday: int = None, period: int = None,
                    subject: str = None, class_name: str = None) -> dict | None:
    with get_db() as conn:
        current = conn.execute("SELECT * FROM schedule WHERE id = ?", (schedule_id,)).fetchone()
        if not current:
            return None
        conn.execute(
            """UPDATE schedule SET weekday=?, period=?, subject=?, class_name=?
               WHERE id=?""",
            (
                weekday if weekday is not None else current["weekday"],
                period if period is not None else current["period"],
                subject if subject is not None else current["subject"],
                class_name if class_name is not None else current["class_name"],
                schedule_id,
            ),
        )
        row = conn.execute("SELECT * FROM schedule WHERE id = ?", (schedule_id,)).fetchone()
        return dict(row) if row else None


def delete_schedule(schedule_id: int) -> bool:
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM schedule WHERE id = ?", (schedule_id,))
        return cursor.rowcount > 0


def create_override(date: str, period: int, action: str,
                    new_subject: str = None, new_class_name: str = None,
                    note: str = None) -> dict:
    with get_db() as conn:
        cursor = conn.execute(
            """INSERT INTO schedule_override
               (date, period, action, new_subject, new_class_name, note)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (date, period, action, new_subject, new_class_name, note),
        )
        row = conn.execute(
            "SELECT * FROM schedule_override WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return dict(row)


def list_overrides(date: str = None) -> list:
    sql = "SELECT * FROM schedule_override WHERE 1=1"
    params = []
    if date is not None:
        sql += " AND date = ?"
        params.append(date)
    sql += " ORDER BY date, period"
    with get_db() as conn:
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]


def delete_override(override_id: int) -> bool:
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM schedule_override WHERE id = ?", (override_id,))
        return cursor.rowcount > 0


def get_today_schedule(weekday: int, date_str: str) -> list:
    """合并常规课表和调课,返回今日实际课程"""
    with get_db() as conn:
        regular = conn.execute(
            "SELECT * FROM schedule WHERE weekday = ? ORDER BY period",
            (weekday,),
        ).fetchall()
        overrides = conn.execute(
            "SELECT * FROM schedule_override WHERE date = ? ORDER BY period",
            (date_str,),
        ).fetchall()

    override_map = {}
    additions = []
    for ov in overrides:
        ov = dict(ov)
        if ov["action"] == "add":
            additions.append(ov)
        else:
            override_map[ov["period"]] = ov

    result = []
    for item in regular:
        item = dict(item)
        ov = override_map.get(item["period"])
        if ov:
            if ov["action"] == "cancel":
                continue
            elif ov["action"] in ("change", "substitute"):
                item["original_subject"] = item["subject"]
                if ov["new_subject"]:
                    item["subject"] = ov["new_subject"]
                if ov["new_class_name"]:
                    item["class_name"] = ov["new_class_name"]
                item["override_note"] = ov.get("note")
                item["is_overridden"] = True
        result.append(item)

    for add in additions:
        result.append({
            "id": None,
            "weekday": weekday,
            "period": add["period"],
            "subject": add["new_subject"] or "临时课",
            "class_name": add["new_class_name"],
            "created_at": None,
            "is_overridden": True,
            "override_note": add.get("note"),
        })

    result.sort(key=lambda x: x["period"])
    return result
