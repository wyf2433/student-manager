"""作业测试"""

import pytest
from conftest import API_KEY
from database import get_db, init_db


@pytest.fixture(autouse=True)
def clean_homework():
    init_db()
    with get_db() as conn:
        conn.execute("DELETE FROM homework")
    yield


def create_class(client, headers):
    res = client.post("/api/classes", json={"name": "初二1班", "grade": "初二"}, headers=headers)
    return res.json()["data"]["id"]


class TestHomework:
    def test_create(self, client, headers):
        cid = create_class(client, headers)
        res = client.post("/api/homework", json={
            "class_id": cid, "content": "完成练习册P20", "type": "daily"
        }, headers=headers)
        assert res.status_code == 201
        assert res.json()["data"]["content"] == "完成练习册P20"
        assert res.json()["data"]["status"] == "active"

    def test_list(self, client, headers):
        cid = create_class(client, headers)
        client.post("/api/homework", json={"class_id": cid, "content": "作业1", "type": "daily"}, headers=headers)
        client.post("/api/homework", json={"class_id": cid, "content": "作业2", "type": "review"}, headers=headers)
        res = client.get("/api/homework", headers=headers)
        assert res.json()["data"]["total"] == 2

    def test_list_by_class(self, client, headers):
        cid1 = create_class(client, headers)
        cid2 = client.post("/api/classes", json={"name": "初二2班"}, headers=headers).json()["data"]["id"]
        client.post("/api/homework", json={"class_id": cid1, "content": "作业A", "type": "daily"}, headers=headers)
        client.post("/api/homework", json={"class_id": cid2, "content": "作业B", "type": "daily"}, headers=headers)
        res = client.get(f"/api/homework?class_id={cid1}", headers=headers)
        items = res.json()["data"]["items"]
        assert len(items) == 1
        assert items[0]["content"] == "作业A"

    def test_today(self, client, headers):
        cid = create_class(client, headers)
        client.post("/api/homework", json={"class_id": cid, "content": "今日作业", "type": "daily"}, headers=headers)
        res = client.get("/api/homework/today", headers=headers)
        assert res.json()["data"]["total"] >= 1

    def test_update_status(self, client, headers):
        cid = create_class(client, headers)
        res = client.post("/api/homework", json={"class_id": cid, "content": "作业", "type": "daily"}, headers=headers)
        hid = res.json()["data"]["id"]
        res = client.patch(f"/api/homework/{hid}/status", json={"status": "collected"}, headers=headers)
        assert res.json()["data"]["status"] == "collected"

    def test_delete(self, client, headers):
        cid = create_class(client, headers)
        res = client.post("/api/homework", json={"class_id": cid, "content": "作业", "type": "daily"}, headers=headers)
        hid = res.json()["data"]["id"]
        res = client.delete(f"/api/homework/{hid}", headers=headers)
        assert res.json()["code"] == 0
