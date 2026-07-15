"""日常记录接口测试"""


def _create_student(client, headers):
    cid = client.post("/api/classes", json={"name": "初二1班"}, headers=headers).json()["data"]["id"]
    sid = client.post("/api/students", json={"class_id": cid, "name": "张三"}, headers=headers).json()["data"]["id"]
    return sid


def test_create_attendance(client, headers):
    sid = _create_student(client, headers)
    resp = client.post(
        "/api/records",
        json={"student_id": sid, "type": "attendance", "content": "迟到"},
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json()["data"]["type"] == "attendance"


def test_create_leave(client, headers):
    sid = _create_student(client, headers)
    resp = client.post(
        "/api/records",
        json={"student_id": sid, "type": "leave", "content": "病假"},
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json()["data"]["content"] == "病假"


def test_create_score(client, headers):
    sid = _create_student(client, headers)
    resp = client.post(
        "/api/records",
        json={"student_id": sid, "type": "score", "content": "课堂表现", "value": -2},
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json()["data"]["value"] == -2


def test_list_by_student(client, headers):
    sid = _create_student(client, headers)
    client.post("/api/records", json={"student_id": sid, "type": "attendance", "content": "迟到"}, headers=headers)
    client.post("/api/records", json={"student_id": sid, "type": "score", "value": 3}, headers=headers)
    resp = client.get(f"/api/records?student_id={sid}", headers=headers)
    assert resp.json()["data"]["total"] >= 2


def test_list_by_type(client, headers):
    sid = _create_student(client, headers)
    client.post("/api/records", json={"student_id": sid, "type": "leave"}, headers=headers)
    resp = client.get("/api/records?type=leave", headers=headers)
    assert resp.json()["data"]["total"] >= 1


def test_delete_record(client, headers):
    sid = _create_student(client, headers)
    create = client.post("/api/records", json={"student_id": sid, "type": "attendance"}, headers=headers)
    rid = create.json()["data"]["id"]
    resp = client.delete(f"/api/records/{rid}", headers=headers)
    assert resp.status_code == 200
