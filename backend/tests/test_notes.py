"""速记接口测试"""

import pytest
from database import get_db, init_db


@pytest.fixture(autouse=True)
def clean_notes():
    init_db()
    with get_db() as conn:
        conn.execute("DELETE FROM quick_notes")
    yield


def test_create_note(client, headers):
    resp = client.post("/api/notes", json={"content": "张三今天表现不错"}, headers=headers)
    assert resp.status_code == 201
    assert resp.json()["data"]["content"] == "张三今天表现不错"


def test_list_notes(client, headers):
    client.post("/api/notes", json={"content": "测试速记1"}, headers=headers)
    client.post("/api/notes", json={"content": "测试速记2"}, headers=headers)
    resp = client.get("/api/notes", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["total"] == 2


def test_search_notes(client, headers):
    client.post("/api/notes", json={"content": "张三今天表现不错"}, headers=headers)
    client.post("/api/notes", json={"content": "李四请假了"}, headers=headers)
    resp = client.get("/api/notes?keyword=张三", headers=headers)
    assert resp.json()["data"]["total"] == 1
    assert "张三" in resp.json()["data"]["items"][0]["content"]


def test_filter_notes_by_date(client, headers):
    client.post("/api/notes", json={"content": "今天的速记"}, headers=headers)
    from datetime import date
    today = date.today().isoformat()
    resp = client.get(f"/api/notes?date={today}", headers=headers)
    assert resp.json()["data"]["total"] == 1


def test_link_student(client, headers):
    cid = client.post("/api/classes", json={"name": "初二1班"}, headers=headers).json()["data"]["id"]
    sid = client.post("/api/students", json={"class_id": cid, "name": "李四"}, headers=headers).json()["data"]["id"]
    note = client.post("/api/notes", json={"content": "李四上课说话"}, headers=headers).json()["data"]["id"]
    resp = client.patch(f"/api/notes/{note}", json={"student_id": sid}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["student_id"] == sid


def test_delete_note(client, headers):
    note = client.post("/api/notes", json={"content": "待删除"}, headers=headers).json()["data"]["id"]
    resp = client.delete(f"/api/notes/{note}", headers=headers)
    assert resp.status_code == 200
