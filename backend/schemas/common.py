"""统一响应模型"""

from typing import Any, Optional

from pydantic import BaseModel


class ApiResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Optional[Any] = None


def success(data: Any = None, message: str = "success") -> dict:
    return {"code": 0, "message": message, "data": data}


def error(message: str, code: int = -1) -> dict:
    return {"code": code, "message": message, "data": None}


class PagedData(BaseModel):
    items: list
    total: int
    page: int
    page_size: int


def paged(items: list, total: int, page: int, page_size: int) -> dict:
    return success({"items": items, "total": total, "page": page, "page_size": page_size})
