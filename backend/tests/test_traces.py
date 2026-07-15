"""工作留痕测试"""

import io
import pytest
from conftest import API_KEY
from database import get_db, init_db


@pytest.fixture(autouse=True)
def clean_traces():
    init_db()
    with get_db() as conn:
        conn.execute("DELETE FROM traces")
    yield


class TestTraceCRUD:
    def test_create(self, client, headers):
        res = client.post("/api/traces", json={
            "title": "课堂纪律检查", "type": "classroom_discipline", "note": "初二1班表现良好"
        }, headers=headers)
        assert res.status_code == 201
        data = res.json()["data"]
        assert data["title"] == "课堂纪律检查"
        assert data["type"] == "classroom_discipline"
        assert data["image_urls"] == []
        assert data["student_ids"] == []

    def test_create_with_images(self, client, headers):
        res = client.post("/api/traces", json={
            "title": "实验课记录", "type": "experiment_record",
            "image_urls": ["/uploads/a.jpg", "/uploads/b.jpg"],
            "student_ids": [1, 2]
        }, headers=headers)
        assert res.status_code == 201
        data = res.json()["data"]
        assert len(data["image_urls"]) == 2
        assert len(data["student_ids"]) == 2

    def test_create_invalid_type(self, client, headers):
        res = client.post("/api/traces", json={
            "title": "test", "type": "invalid_type"
        }, headers=headers)
        assert res.status_code == 400

    def test_list(self, client, headers):
        client.post("/api/traces", json={"title": "留痕1", "type": "other"}, headers=headers)
        client.post("/api/traces", json={"title": "留痕2", "type": "student_talk"}, headers=headers)
        res = client.get("/api/traces", headers=headers)
        assert res.json()["data"]["total"] == 2

    def test_list_by_type(self, client, headers):
        client.post("/api/traces", json={"title": "留痕1", "type": "other"}, headers=headers)
        client.post("/api/traces", json={"title": "留痕2", "type": "student_talk"}, headers=headers)
        res = client.get("/api/traces?type=student_talk", headers=headers)
        items = res.json()["data"]["items"]
        assert len(items) == 1
        assert items[0]["type"] == "student_talk"

    def test_get_by_id(self, client, headers):
        create = client.post("/api/traces", json={"title": "详情测试", "type": "other"}, headers=headers)
        tid = create.json()["data"]["id"]
        res = client.get(f"/api/traces/{tid}", headers=headers)
        assert res.json()["data"]["title"] == "详情测试"

    def test_update(self, client, headers):
        create = client.post("/api/traces", json={"title": "原标题", "type": "other"}, headers=headers)
        tid = create.json()["data"]["id"]
        res = client.put(f"/api/traces/{tid}", json={
            "title": "新标题", "note": "补充备注"
        }, headers=headers)
        assert res.json()["data"]["title"] == "新标题"
        assert res.json()["data"]["note"] == "补充备注"

    def test_delete(self, client, headers):
        create = client.post("/api/traces", json={"title": "待删除", "type": "other"}, headers=headers)
        tid = create.json()["data"]["id"]
        res = client.delete(f"/api/traces/{tid}", headers=headers)
        assert res.json()["code"] == 0
        res = client.get(f"/api/traces/{tid}", headers=headers)
        assert res.status_code == 404


class TestImageUpload:
    def test_upload_image(self, client, headers):
        img_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde'
        res = client.post(
            "/api/traces/upload/image",
            files={"file": ("test.png", io.BytesIO(img_bytes), "image/png")},
            headers=headers,
        )
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["url"].startswith("/uploads/")
        assert data["filename"].endswith(".png")

    def test_upload_invalid_type(self, client, headers):
        res = client.post(
            "/api/traces/upload/image",
            files={"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")},
            headers=headers,
        )
        assert res.status_code == 400
