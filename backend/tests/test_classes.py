"""班级接口测试"""

from conftest import API_KEY


def test_create_class(client, headers):
    resp = client.post("/api/classes", json={"name": "初二1班", "grade": "初二"}, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["code"] == 0
    assert data["data"]["name"] == "初二1班"


def test_list_classes(client, headers):
    client.post("/api/classes", json={"name": "初三2班", "grade": "初三"}, headers=headers)
    resp = client.get("/api/classes", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 0
    assert len(data["data"]["items"]) >= 1


def test_update_class(client, headers):
    create = client.post("/api/classes", json={"name": "初一1班"}, headers=headers)
    cid = create.json()["data"]["id"]
    resp = client.put(f"/api/classes/{cid}", json={"name": "初一2班"}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["name"] == "初一2班"


def test_delete_class(client, headers):
    create = client.post("/api/classes", json={"name": "待删除班"}, headers=headers)
    cid = create.json()["data"]["id"]
    resp = client.delete(f"/api/classes/{cid}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["code"] == 0


def test_no_api_key(client):
    resp = client.get("/api/classes")
    assert resp.status_code == 401
