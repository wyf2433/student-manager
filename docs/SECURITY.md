# 安全规范

> 后端暴露在公网 IP,安全是重中之重。本文件为强制规范,不可违反。

## 1. API Key 认证(核心)

### 规则
- 所有接口必须校验 `X-API-Key` 请求头
- API Key 存储在环境变量 `API_KEY` 中(通过 `.env` 加载)
- 禁止硬编码进任何源文件
- `.env` 必须在 `.gitignore` 中

### 实现
```python
# backend/middleware/auth.py
from fastapi import Request, HTTPException

async def verify_api_key(request: Request):
    api_key = request.headers.get("X-API-Key")
    expected = os.environ.get("API_KEY")
    if not api_key or api_key != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")
```

### 云函数配置
```javascript
// 云函数环境变量中设置 BACKEND_API_KEY
const apiKey = process.env.BACKEND_API_KEY
// 转发时携带
axios({ headers: { "X-API-Key": apiKey }, ... })
```

## 2. SQL 注入防护

### 规则
- **必须参数化查询**,使用 `?` 占位符
- **禁止** f-string / 字符串拼接 SQL

### 正确示例
```python
cursor.execute("SELECT * FROM students WHERE class_id = ? AND name LIKE ?", 
               (class_id, f"%{keyword}%"))
```

### 错误示例(禁止)
```python
# 禁止!
cursor.execute(f"SELECT * FROM students WHERE name = '{name}'")
```

## 3. 文件上传安全

### Excel 导入
- 校验扩展名:.xlsx / .xls
- 校验 MIME 类型:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
- 限制大小:≤ 10MB
- 用 openpyxl 解析(不执行宏)

### 图片上传
- 校验扩展名:.jpg / .jpeg / .png
- 校验 MIME 类型:image/jpeg / image/png
- 限制大小:≤ 5MB
- 存储路径:非 web 根目录,通过接口访问

## 4. CORS 配置

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://servicewechat.com"],  # 仅微信
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["X-API-Key", "Content-Type"],
)
```

> 注:微信小程序请求通常不触发 CORS,但云函数转发可能触发,保留配置。

## 5. 速率限制

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.route("/api/scores/import/preview")
@limiter.limit("5/minute")
async def import_preview(request: Request):
    ...
```

- 全局:60 次/分钟
- 导入接口:5 次/分钟

## 6. 错误信息脱敏

### 规则
- 生产环境不返回堆栈详情
- 只返回错误码 + 简短消息
- 详细错误记日志(服务器本地)

### 实现
```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "服务器内部错误", "data": None}
    )
```

## 7. 环境变量管理

### .env 文件(不提交 git)
```env
API_KEY=your-secret-key-here
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
DB_PATH=./data/student_manager.db
UPLOAD_DIR=./uploads
MAX_EXCEL_SIZE_MB=10
MAX_IMAGE_SIZE_MB=5
```

### .env.example(提交 git,供参考)
```env
API_KEY=change-me
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
DB_PATH=./data/student_manager.db
UPLOAD_DIR=./uploads
```

## 8. 定期备份

- SQLite 单文件,定期 `cp data/student_manager.db data/backup_$(date +%Y%m%d).db`
- 建议每日 cron 备份,保留 30 天

## 9. 接入第三方 MCP 审查清单(参考)

如未来引入 MCP 工具,需审查:

| 审查项 | 要求 |
|--------|------|
| 读写边界 | 只读 / 读写 |
| 权限范围 | 已限制到子目录 / 全盘访问 |
| 网络行为 | 请求流向 |
| 敏感距离 | 无法访问 .env / 可访问 |
| 审计日志 | 有 / 无 |
| 重试风险 | 幂等 / 有副作用 |
| 供应链 | 官方 / 个人项目 |
