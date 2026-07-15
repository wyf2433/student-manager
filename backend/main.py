"""FastAPI 入口"""

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from config import BACKEND_HOST, BACKEND_PORT
from database import init_db
from middleware.auth import APIKeyMiddleware
from middleware.rate_limit import limiter
from routers import classes, students, records, notes, dashboard, schedule, homework, scores
from schemas.common import success

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="学生管理类 App API",
    description="初中物理老师端 - 后端接口",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://servicewechat.com"],
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["X-API-Key", "Content-Type"],
)

app.add_middleware(APIKeyMiddleware)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "服务器内部错误", "data": None},
    )


@app.on_event("startup")
async def startup():
    init_db()
    logger.info("数据库已初始化")


@app.get("/api/health")
async def health():
    return success({"status": "ok"})


app.include_router(classes.router)
app.include_router(students.router)
app.include_router(records.router)
app.include_router(notes.router)
app.include_router(dashboard.router)
app.include_router(schedule.router)
app.include_router(homework.router)
app.include_router(scores.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=BACKEND_HOST, port=BACKEND_PORT, reload=True)
