"""成绩路由"""

from fastapi import APIRouter, HTTPException, Query, UploadFile, File

from config import MAX_EXCEL_SIZE
from models import score_model, student_model, class_model
from schemas.score_schema import ScoreCreate, ScoreImportConfirm
from services.excel_parser import parse_score_excel, validate_excel_size
from schemas.common import success, paged

router = APIRouter(prefix="/api/scores", tags=["成绩"])


@router.get("")
async def list_scores(
    student_id: int = Query(None),
    exam_name: str = Query(None),
    subject: str = Query(None),
):
    items = score_model.list_scores(student_id, exam_name, subject)
    return paged(items, len(items), 1, len(items))


@router.get("/exams")
async def list_exams():
    items = score_model.get_exam_names()
    return success({"items": items})


@router.post("", status_code=201)
async def create_score(body: ScoreCreate):
    item = score_model.create_score(body.student_id, body.exam_name, body.subject, body.score)
    return success(item)


@router.post("/import/preview")
async def import_preview(file: UploadFile = File(...)):
    content = await file.read()
    validate_excel_size(len(content))
    try:
        result = parse_score_excel(content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return success(result)


@router.post("/import/confirm")
async def import_confirm(body: ScoreImportConfirm):
    scores_to_insert = []
    auto_created_students = 0
    auto_created_classes = 0
    class_cache = {}

    all_classes = class_model.list_classes()
    for c in all_classes:
        class_cache[c["name"]] = c["id"]

    for s in body.students:
        name = s.get("name")
        score_val = s.get("score")
        student_id = s.get("student_id")

        if student_id is None and not name:
            continue

        class_name_raw = s.get("class_name")
        target_class_id = body.class_id

        if class_name_raw and body.grade_prefix:
            full_class_name = body.grade_prefix + class_name_raw
            if full_class_name in class_cache:
                target_class_id = class_cache[full_class_name]
            else:
                new_class = class_model.create_class(full_class_name)
                class_cache[full_class_name] = new_class["id"]
                target_class_id = new_class["id"]
                auto_created_classes += 1

        if student_id is None:
            if target_class_id is None:
                raise HTTPException(status_code=400, detail="无法确定班级,请选择班级或提供年级前缀")

            existing = student_model.list_students(class_id=target_class_id, keyword=name)
            items = existing.get("items", [])
            matched = [st for st in items if st["name"] == name]
            if matched:
                student_id = matched[0]["id"]
            else:
                new_student = student_model.create_student(target_class_id, name)
                student_id = new_student["id"]
                auto_created_students += 1

        scores_to_insert.append({
            "student_id": student_id,
            "exam_name": body.exam_name,
            "subject": body.subject,
            "score": score_val,
        })

    if not scores_to_insert:
        raise HTTPException(status_code=400, detail="无有效数据")
    count = score_model.batch_create_scores(scores_to_insert)
    return success({
        "imported_count": count,
        "auto_created_students": auto_created_students,
        "auto_created_classes": auto_created_classes,
    })


@router.delete("/{score_id}")
async def delete_score(score_id: int):
    if not score_model.delete_score(score_id):
        raise HTTPException(status_code=404, detail="成绩不存在")
    return success(message="已删除")
