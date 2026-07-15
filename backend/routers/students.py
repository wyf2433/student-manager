"""学生路由"""

from fastapi import APIRouter, HTTPException, Query

from models import student_model
from schemas.student_schema import StudentCreate, StudentBatchCreate, StudentUpdate
from schemas.common import success

router = APIRouter(prefix="/api/students", tags=["学生"])


@router.get("")
async def list_students(
    class_id: int = Query(None),
    keyword: str = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    result = student_model.list_students(class_id, keyword, page, page_size)
    return success(result)


@router.get("/{student_id}")
async def get_student(student_id: int):
    item = student_model.get_student_by_id(student_id)
    if not item:
        raise HTTPException(status_code=404, detail="学生不存在")
    return success(item)


@router.post("", status_code=201)
async def create_student(body: StudentCreate):
    item = student_model.create_student(body.class_id, body.name, body.student_no, body.gender)
    return success(item)


@router.post("/batch", status_code=201)
async def batch_create_students(body: StudentBatchCreate):
    count = student_model.batch_create_students([s.model_dump() for s in body.students])
    return success({"imported_count": count})


@router.put("/{student_id}")
async def update_student(student_id: int, body: StudentUpdate):
    item = student_model.update_student(
        student_id,
        class_id=body.class_id,
        name=body.name,
        student_no=body.student_no,
        gender=body.gender,
    )
    if not item:
        raise HTTPException(status_code=404, detail="学生不存在")
    return success(item)


@router.delete("/{student_id}")
async def delete_student(student_id: int):
    if not student_model.delete_student(student_id):
        raise HTTPException(status_code=404, detail="学生不存在")
    return success(message="已删除")
