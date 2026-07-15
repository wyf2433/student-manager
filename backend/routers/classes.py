"""班级路由"""

from fastapi import APIRouter, HTTPException

from models import class_model
from schemas.class_schema import ClassCreate, ClassUpdate
from schemas.common import success, paged

router = APIRouter(prefix="/api/classes", tags=["班级"])


@router.get("")
async def list_classes():
    items = class_model.list_classes()
    return paged(items, len(items), 1, len(items))


@router.post("", status_code=201)
async def create_class(body: ClassCreate):
    item = class_model.create_class(body.name, body.grade)
    return success(item)


@router.put("/{class_id}")
async def update_class(class_id: int, body: ClassUpdate):
    item = class_model.update_class(class_id, body.name, body.grade)
    if not item:
        raise HTTPException(status_code=404, detail="班级不存在")
    return success(item)


@router.delete("/{class_id}")
async def delete_class(class_id: int):
    if not class_model.delete_class(class_id):
        raise HTTPException(status_code=404, detail="班级不存在")
    return success(message="已删除")
