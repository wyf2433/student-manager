"""学生接口测试"""

from conftest import API_KEY


def _create_class(client, headers, name="初二1班"):
    resp = client.post("/api/classes", json={"name": name, "grade": "初二"}, headers=headers)
    return resp.json()["data"]["id"]


def test_create_student(client, headers):
    cid = _create_class(client, headers)
    resp = client.post(
        "/api/students",
        json={"class_id": cid, "name": "张三", "student_no": "20240101", "gender": "male"},
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json()["data"]["name"] == "张三"


def test_list_students_by_class(client, headers):
    cid = _create_class(client, headers)
    client.post("/api/students", json={"class_id": cid, "name": "李四"}, headers=headers)
    client.post("/api/students", json={"class_id": cid, "name": "王五"}, headers=headers)
    resp = client.get(f"/api/students?class_id={cid}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["total"] >= 2


def test_search_students(client, headers):
    cid = _create_class(client, headers)
    client.post("/api/students", json={"class_id": cid, "name": "张三"}, headers=headers)
    client.post("/api/students", json={"class_id": cid, "name": "张伟"}, headers=headers)
    client.post("/api/students", json={"class_id": cid, "name": "李四"}, headers=headers)
    resp = client.get(f"/api/students?keyword=张", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["total"] >= 2


def test_batch_create(client, headers):
    cid = _create_class(client, headers)
    resp = client.post(
        "/api/students/batch",
        json={
            "students": [
                {"class_id": cid, "name": "赵六"},
                {"class_id": cid, "name": "钱七"},
            ]
        },
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json()["data"]["imported_count"] == 2


def test_update_student(client, headers):
    cid = _create_class(client, headers)
    create = client.post("/api/students", json={"class_id": cid, "name": "孙八"}, headers=headers)
    sid = create.json()["data"]["id"]
    resp = client.put(f"/api/students/{sid}", json={"name": "孙九"}, headers=headers)
    assert resp.json()["data"]["name"] == "孙九"


def test_delete_student(client, headers):
    cid = _create_class(client, headers)
    create = client.post("/api/students", json={"class_id": cid, "name": "周十"}, headers=headers)
    sid = create.json()["data"]["id"]
    resp = client.delete(f"/api/students/{sid}", headers=headers)
    assert resp.status_code == 200


def test_get_student_not_found(client, headers):
    resp = client.get("/api/students/99999", headers=headers)
    assert resp.status_code == 404
