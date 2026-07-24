"""配置加载:从 .env 读取所有配置"""

import os
from dotenv import load_dotenv

load_dotenv()

def _load_api_keys() -> list[str]:
    """从环境变量加载 API Key 白名单(逗号分隔)。无配置或为默认值时拒绝启动。"""
    raw = os.environ.get("API_KEYS") or os.environ.get("API_KEY")
    if not raw or raw == "change-me":
        raise RuntimeError("API_KEYS/API_KEY 未配置或仍为默认值,拒绝启动(安全红线)")
    return [k.strip() for k in raw.split(",") if k.strip()]


API_KEYS = _load_api_keys()
API_KEY = API_KEYS[0]
BACKEND_HOST = os.environ.get("BACKEND_HOST", "0.0.0.0")
BACKEND_PORT = int(os.environ.get("BACKEND_PORT", "8000"))
DB_PATH = os.environ.get("DB_PATH", "./data/student_manager.db")
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "./uploads")
MAX_EXCEL_SIZE_MB = int(os.environ.get("MAX_EXCEL_SIZE_MB", "10"))
MAX_IMAGE_SIZE_MB = int(os.environ.get("MAX_IMAGE_SIZE_MB", "5"))
WECHAT_APPID = os.environ.get("WECHAT_APPID", "")
WECHAT_APP_SECRET = os.environ.get("WECHAT_APP_SECRET", "")
WECHAT_UPLOAD_KEY_PATH = os.environ.get("WECHAT_UPLOAD_KEY_PATH", "")

MAX_EXCEL_SIZE = MAX_EXCEL_SIZE_MB * 1024 * 1024
MAX_IMAGE_SIZE = MAX_IMAGE_SIZE_MB * 1024 * 1024
