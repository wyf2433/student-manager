"""速记路由"""

from fastapi import APIRouter, HTTPException, Query

from models import note_model
from schemas.note_schema import NoteCreate, NoteUpdateStudent
from schemas.common import success

router = APIRouter(prefix="/api/notes", tags=["速记"])


@router.get("")
async def list_notes(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    keyword: str = Query(None),
    date: str = Query(None),
):
    result = note_model.list_notes(page, page_size, keyword, date)
    return success(result)


@router.post("", status_code=201)
async def create_note(body: NoteCreate):
    item = note_model.create_note(body.content, body.student_id)
    return success(item)


@router.patch("/{note_id}")
async def update_note_student(note_id: int, body: NoteUpdateStudent):
    item = note_model.update_note_student(note_id, body.student_id)
    if not item:
        raise HTTPException(status_code=404, detail="速记不存在")
    return success(item)


@router.delete("/{note_id}")
async def delete_note(note_id: int):
    if not note_model.delete_note(note_id):
        raise HTTPException(status_code=404, detail="速记不存在")
    return success(message="已删除")
