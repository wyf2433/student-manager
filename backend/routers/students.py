"""学生路由"""

from fastapi import APIRouter, HTTPException, Query, UploadFile, File

from models import student_model
from schemas.student_schema import StudentCreate, StudentBatchCreate, StudentUpdate
from services.excel_parser import parse_student_excel, validate_excel_size
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


@router.post("/import/preview")
async def import_preview(file: UploadFile = File(...)):
    content = await file.read()
    validate_excel_size(len(content))
    try:
        students = parse_student_excel(content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return success({"students": students, "total": len(students)})


@router.post("/import/confirm")
async def import_confirm(body: dict):
    class_id = body.get("class_id")
    students = body.get("students", [])
    if not class_id:
        raise HTTPException(status_code=400, detail="缺少 class_id")
    if not students:
        raise HTTPException(status_code=400, detail="无有效数据")
    for s in students:
        s["class_id"] = class_id
    count = student_model.batch_create_students(students)
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
