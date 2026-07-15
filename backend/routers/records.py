"""日常记录路由"""

from fastapi import APIRouter, HTTPException, Query

from models import record_model
from schemas.record_schema import RecordCreate
from schemas.common import success

router = APIRouter(prefix="/api/records", tags=["日常记录"])


@router.get("")
async def list_records(
    student_id: int = Query(None),
    type: str = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    result = record_model.list_records(student_id, type, page, page_size)
    return success(result)


@router.post("", status_code=201)
async def create_record(body: RecordCreate):
    item = record_model.create_record(body.student_id, body.type, body.content, body.value)
    return success(item)


@router.delete("/{record_id}")
async def delete_record(record_id: int):
    if not record_model.delete_record(record_id):
        raise HTTPException(status_code=404, detail="记录不存在")
    return success(message="已删除")
