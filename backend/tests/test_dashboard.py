"""首页聚合接口测试"""


def test_today_overview_empty(client, headers):
    resp = client.get("/api/dashboard/today", headers=headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["attendance_count"] == 0
    assert data["leave_count"] == 0
    assert data["score_count"] == 0
    assert data["note_count"] == 0


def test_today_overview_with_data(client, headers):
    cid = client.post("/api/classes", json={"name": "初二1班"}, headers=headers).json()["data"]["id"]
    sid = client.post("/api/students", json={"class_id": cid, "name": "张三"}, headers=headers).json()["data"]["id"]
    client.post("/api/records", json={"student_id": sid, "type": "attendance", "content": "迟到"}, headers=headers)
    client.post("/api/records", json={"student_id": sid, "type": "leave", "content": "病假"}, headers=headers)
    client.post("/api/notes", json={"content": "测试速记"}, headers=headers)

    resp = client.get("/api/dashboard/today", headers=headers)
    data = resp.json()["data"]
    assert data["attendance_count"] >= 1
    assert data["leave_count"] >= 1
    assert data["note_count"] >= 1


def test_recent_records(client, headers):
    cid = client.post("/api/classes", json={"name": "初二1班"}, headers=headers).json()["data"]["id"]
    sid = client.post("/api/students", json={"class_id": cid, "name": "李四"}, headers=headers).json()["data"]["id"]
    client.post("/api/records", json={"student_id": sid, "type": "attendance"}, headers=headers)
    client.post("/api/notes", json={"content": "速记1"}, headers=headers)

    resp = client.get("/api/dashboard/recent?limit=10", headers=headers)
    assert resp.status_code == 200
    items = resp.json()["data"]["items"]
    assert len(items) >= 2
    sources = {item["source"] for item in items}
    assert "record" in sources
    assert "note" in sources
