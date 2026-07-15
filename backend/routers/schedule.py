"""课表路由(常规课表 + 临时调课)"""

from datetime import date

from fastapi import APIRouter, HTTPException, Query

from models import schedule_model
from schemas.schedule_schema import ScheduleCreate, ScheduleUpdate, OverrideCreate
from schemas.common import success, paged

router = APIRouter(prefix="/api/schedule", tags=["课表"])


@router.get("")
async def list_schedule(weekday: int = Query(None, ge=1, le=7)):
    items = schedule_model.list_schedule(weekday)
    return paged(items, len(items), 1, len(items))


@router.get("/today")
async def today_schedule():
    today = date.today()
    weekday = today.isoweekday()
    date_str = today.isoformat()
    items = schedule_model.get_today_schedule(weekday, date_str)
    return success({"date": date_str, "weekday": weekday, "items": items})


@router.post("", status_code=201)
async def create_schedule_item(body: ScheduleCreate):
    try:
        item = schedule_model.create_schedule(body.weekday, body.period, body.subject, body.class_name)
    except Exception as e:
        if "UNIQUE" in str(e):
            raise HTTPException(status_code=409, detail="该时段已有课程")
        raise
    return success(item)


@router.put("/{schedule_id}")
async def update_schedule_item(schedule_id: int, body: ScheduleUpdate):
    item = schedule_model.update_schedule(
        schedule_id,
        weekday=body.weekday,
        period=body.period,
        subject=body.subject,
        class_name=body.class_name,
    )
    if not item:
        raise HTTPException(status_code=404, detail="课表项不存在")
    return success(item)


@router.delete("/{schedule_id}")
async def delete_schedule_item(schedule_id: int):
    if not schedule_model.delete_schedule(schedule_id):
        raise HTTPException(status_code=404, detail="课表项不存在")
    return success(message="已删除")


@router.get("/overrides")
async def list_overrides(date: str = Query(None)):
    items = schedule_model.list_overrides(date)
    return paged(items, len(items), 1, len(items))


@router.post("/overrides", status_code=201)
async def create_override(body: OverrideCreate):
    item = schedule_model.create_override(
        body.date, body.period, body.action,
        body.new_subject, body.new_class_name, body.note,
    )
    return success(item)


@router.delete("/overrides/{override_id}")
async def delete_override(override_id: int):
    if not schedule_model.delete_override(override_id):
        raise HTTPException(status_code=404, detail="调课记录不存在")
    return success(message="已删除")
