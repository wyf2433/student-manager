"""速记接口测试"""


def test_create_note(client, headers):
    resp = client.post("/api/notes", json={"content": "张三今天表现不错"}, headers=headers)
    assert resp.status_code == 201
    assert resp.json()["data"]["content"] == "张三今天表现不错"


def test_list_notes(client, headers):
    client.post("/api/notes", json={"content": "测试速记1"}, headers=headers)
    client.post("/api/notes", json={"content": "测试速记2"}, headers=headers)
    resp = client.get("/api/notes", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["total"] >= 2


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
