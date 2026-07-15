"""作业路由"""

from fastapi import APIRouter, HTTPException, Query

from models import homework_model
from schemas.homework_schema import HomeworkCreate, HomeworkStatusUpdate
from schemas.common import success, paged

router = APIRouter(prefix="/api/homework", tags=["作业"])


@router.get("")
async def list_homework(
    class_id: int = Query(None),
    status: str = Query(None),
):
    items = homework_model.list_homework(class_id, status)
    return paged(items, len(items), 1, len(items))


@router.get("/today")
async def today_homework():
    items = homework_model.get_today_homework()
    return success({"items": items, "total": len(items)})


@router.post("", status_code=201)
async def create_homework(body: HomeworkCreate):
    item = homework_model.create_homework(
        body.class_id, body.content, body.type, body.due_date, body.note
    )
    return success(item)


@router.patch("/{homework_id}/status")
async def update_status(homework_id: int, body: HomeworkStatusUpdate):
    item = homework_model.update_status(homework_id, body.status)
    if not item:
        raise HTTPException(status_code=404, detail="作业不存在")
    return success(item)


@router.delete("/{homework_id}")
async def delete_homework(homework_id: int):
    if not homework_model.delete_homework(homework_id):
        raise HTTPException(status_code=404, detail="作业不存在")
    return success(message="已删除")
