"""测试公共 fixture"""

import pytest
from fastapi.testclient import TestClient
from main import app
from database import init_db
from config import API_KEYS

API_KEY = API_KEYS[0]


@pytest.fixture
def client():
    init_db()
    return TestClient(app)


@pytest.fixture
def headers():
    return {"X-API-Key": API_KEY}
