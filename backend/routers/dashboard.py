"""首页聚合路由"""

from datetime import date

from fastapi import APIRouter, Query

from models import record_model, note_model
from database import get_db
from schemas.common import success

router = APIRouter(prefix="/api/dashboard", tags=["首页聚合"])


@router.get("/today")
async def today_overview():
    """今日概览:各类型记录数统计"""
    today = date.today().isoformat()
    record_counts = record_model.count_today_by_type(today)
    note_count = note_model.count_today(today)
    return success({
        "date": today,
        "attendance_count": record_counts["attendance"],
        "leave_count": record_counts["leave"],
        "score_count": record_counts["score"],
        "note_count": note_count,
    })


@router.get("/recent")
async def recent_records(
    limit: int = Query(20, ge=1, le=100),
):
    """最近记录列表(records + notes 混合流,按时间倒序)"""
    today = date.today().isoformat()
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT 'record' AS source, id, student_id, type AS sub_type, content, 
                   CAST(value AS TEXT) AS extra, created_at
            FROM records
            UNION ALL
            SELECT 'note' AS source, id, student_id, NULL AS sub_type, content,
                   NULL AS extra, created_at
            FROM quick_notes
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        items = [dict(r) for r in rows]
    return success({"items": items, "total": len(items)})
