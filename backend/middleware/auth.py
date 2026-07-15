"""X-API-Key 认证中间件"""

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from config import API_KEY

EXEMPT_PATHS = {"/docs", "/openapi.json", "/redoc"}
EXEMPT_PREFIXES = ("/uploads/",)


class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if path in EXEMPT_PATHS or any(path.startswith(p) for p in EXEMPT_PREFIXES):
            return await call_next(request)

        api_key = request.headers.get("X-API-Key")
        if not api_key or api_key != API_KEY:
            return JSONResponse(
                status_code=401,
                content={"code": 401, "message": "Unauthorized: invalid or missing API key", "data": None},
            )

        return await call_next(request)
