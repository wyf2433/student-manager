"""工作留痕路由"""

import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query, UploadFile, File

from config import UPLOAD_DIR, MAX_IMAGE_SIZE
from models import trace_model
from schemas.trace_schema import TraceCreate, TraceUpdate
from schemas.common import success, paged

router = APIRouter(prefix="/api/traces", tags=["工作留痕"])

VALID_TYPES = {
    "classroom_discipline", "experiment_record", "homework_feedback",
    "exam_analysis", "student_talk", "parent_communication", "other",
}


@router.get("")
async def list_traces(
    type: str = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    result = trace_model.list_traces(type, page, page_size)
    return success(result)


@router.get("/{trace_id}")
async def get_trace(trace_id: int):
    item = trace_model.get_trace_by_id(trace_id)
    if not item:
        raise HTTPException(status_code=404, detail="留痕不存在")
    return success(item)


@router.post("", status_code=201)
async def create_trace(body: TraceCreate):
    if body.type not in VALID_TYPES:
        raise HTTPException(status_code=400, detail=f"无效类型,可选: {', '.join(VALID_TYPES)}")
    item = trace_model.create_trace(
        body.title, body.type, body.note, body.image_urls, body.student_ids
    )
    return success(item)


@router.put("/{trace_id}")
async def update_trace(trace_id: int, body: TraceUpdate):
    if body.type is not None and body.type not in VALID_TYPES:
        raise HTTPException(status_code=400, detail=f"无效类型")
    item = trace_model.update_trace(
        trace_id,
        title=body.title, type=body.type, note=body.note,
        image_urls=body.image_urls, student_ids=body.student_ids,
    )
    if not item:
        raise HTTPException(status_code=404, detail="留痕不存在")
    return success(item)


@router.delete("/{trace_id}")
async def delete_trace(trace_id: int):
    if not trace_model.delete_trace(trace_id):
        raise HTTPException(status_code=404, detail="留痕不存在")
    return success(message="已删除")


@router.post("/upload/image")
async def upload_image(file: UploadFile = File(...)):
    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=400, detail=f"图片不能超过 {MAX_IMAGE_SIZE // 1024 // 1024}MB")

    allowed_types = {"image/jpeg", "image/png", "image/jpg", "image/webp", "image/gif"}
    if file.content_type and file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="仅支持 jpg/png/webp/gif 格式")

    ext = ".jpg"
    for e in [".jpg", ".jpeg", ".png", ".webp", ".gif"]:
        if file.filename and file.filename.lower().endswith(e):
            ext = e
            break

    upload_path = Path(UPLOAD_DIR)
    upload_path.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{ext}"
    file_full_path = upload_path / filename
    file_full_path.write_bytes(content)

    url = f"/uploads/{filename}"
    return success({"url": url, "filename": filename})
