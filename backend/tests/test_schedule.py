"""课表 + 调课测试"""

from datetime import date
import pytest
from conftest import API_KEY
from database import get_db


@pytest.fixture(autouse=True)
def clean_schedule():
    from database import init_db
    init_db()
    with get_db() as conn:
        conn.execute("DELETE FROM schedule")
        conn.execute("DELETE FROM schedule_override")
    yield


class TestSchedule:
    def test_create_schedule(self, client, headers):
        res = client.post("/api/schedule", json={"weekday": 1, "period": 1, "subject": "物理", "class_name": "初二1班"}, headers=headers)
        assert res.status_code == 201
        data = res.json()
        assert data["code"] == 0
        assert data["data"]["weekday"] == 1
        assert data["data"]["subject"] == "物理"

    def test_create_duplicate(self, client, headers):
        client.post("/api/schedule", json={"weekday": 1, "period": 2, "subject": "物理"}, headers=headers)
        res = client.post("/api/schedule", json={"weekday": 1, "period": 2, "subject": "数学"}, headers=headers)
        assert res.status_code == 409

    def test_list_schedule(self, client, headers):
        client.post("/api/schedule", json={"weekday": 2, "period": 1, "subject": "物理"}, headers=headers)
        client.post("/api/schedule", json={"weekday": 2, "period": 2, "subject": "物理"}, headers=headers)
        client.post("/api/schedule", json={"weekday": 3, "period": 1, "subject": "物理"}, headers=headers)
        res = client.get("/api/schedule", headers=headers)
        assert res.json()["data"]["total"] == 3

    def test_list_by_weekday(self, client, headers):
        client.post("/api/schedule", json={"weekday": 2, "period": 1, "subject": "物理"}, headers=headers)
        client.post("/api/schedule", json={"weekday": 3, "period": 1, "subject": "物理"}, headers=headers)
        res = client.get("/api/schedule?weekday=2", headers=headers)
        items = res.json()["data"]["items"]
        assert len(items) == 1
        assert items[0]["weekday"] == 2

    def test_update_schedule(self, client, headers):
        res = client.post("/api/schedule", json={"weekday": 1, "period": 3, "subject": "物理"}, headers=headers)
        sid = res.json()["data"]["id"]
        res = client.put(f"/api/schedule/{sid}", json={"subject": "数学", "class_name": "初三2班"}, headers=headers)
        assert res.json()["data"]["subject"] == "数学"
        assert res.json()["data"]["class_name"] == "初三2班"

    def test_delete_schedule(self, client, headers):
        res = client.post("/api/schedule", json={"weekday": 1, "period": 4, "subject": "物理"}, headers=headers)
        sid = res.json()["data"]["id"]
        res = client.delete(f"/api/schedule/{sid}", headers=headers)
        assert res.json()["code"] == 0
        res = client.get("/api/schedule", headers=headers)
        assert res.json()["data"]["total"] == 0


class TestOverride:
    def test_create_override(self, client, headers):
        res = client.post("/api/schedule/overrides", json={
            "date": "2026-07-15", "period": 1, "action": "cancel", "note": "开会"
        }, headers=headers)
        assert res.status_code == 201
        assert res.json()["data"]["action"] == "cancel"

    def test_list_overrides(self, client, headers):
        client.post("/api/schedule/overrides", json={"date": "2026-07-15", "period": 1, "action": "cancel"}, headers=headers)
        client.post("/api/schedule/overrides", json={"date": "2026-07-16", "period": 2, "action": "change", "new_subject": "自习"}, headers=headers)
        res = client.get("/api/schedule/overrides", headers=headers)
        assert res.json()["data"]["total"] == 2

    def test_list_overrides_by_date(self, client, headers):
        client.post("/api/schedule/overrides", json={"date": "2026-07-15", "period": 1, "action": "cancel"}, headers=headers)
        client.post("/api/schedule/overrides", json={"date": "2026-07-16", "period": 2, "action": "change", "new_subject": "自习"}, headers=headers)
        res = client.get("/api/schedule/overrides?date=2026-07-15", headers=headers)
        assert len(res.json()["data"]["items"]) == 1

    def test_delete_override(self, client, headers):
        res = client.post("/api/schedule/overrides", json={"date": "2026-07-15", "period": 1, "action": "cancel"}, headers=headers)
        oid = res.json()["data"]["id"]
        res = client.delete(f"/api/schedule/overrides/{oid}", headers=headers)
        assert res.json()["code"] == 0


class TestTodaySchedule:
    def test_today_empty(self, client, headers):
        res = client.get("/api/schedule/today", headers=headers)
        data = res.json()["data"]
        assert data["items"] == []

    def test_today_with_regular(self, client, headers):
        today = date.today()
        weekday = today.isoweekday()
        client.post("/api/schedule", json={"weekday": weekday, "period": 1, "subject": "物理", "class_name": "初二1班"}, headers=headers)
        client.post("/api/schedule", json={"weekday": weekday, "period": 2, "subject": "物理", "class_name": "初二2班"}, headers=headers)
        res = client.get("/api/schedule/today", headers=headers)
        items = res.json()["data"]["items"]
        assert len(items) == 2

    def test_today_with_cancel(self, client, headers):
        today = date.today()
        weekday = today.isoweekday()
        date_str = today.isoformat()
        client.post("/api/schedule", json={"weekday": weekday, "period": 1, "subject": "物理"}, headers=headers)
        client.post("/api/schedule", json={"weekday": weekday, "period": 2, "subject": "物理"}, headers=headers)
        client.post("/api/schedule/overrides", json={"date": date_str, "period": 1, "action": "cancel"}, headers=headers)
        res = client.get("/api/schedule/today", headers=headers)
        items = res.json()["data"]["items"]
        assert len(items) == 1
        assert items[0]["period"] == 2

    def test_today_with_change(self, client, headers):
        today = date.today()
        weekday = today.isoweekday()
        date_str = today.isoformat()
        client.post("/api/schedule", json={"weekday": weekday, "period": 1, "subject": "物理"}, headers=headers)
        client.post("/api/schedule/overrides", json={
            "date": date_str, "period": 1, "action": "change", "new_subject": "自习"
        }, headers=headers)
        res = client.get("/api/schedule/today", headers=headers)
        items = res.json()["data"]["items"]
        assert len(items) == 1
        assert items[0]["subject"] == "自习"
        assert items[0]["is_overridden"] is True

    def test_today_with_add(self, client, headers):
        today = date.today()
        weekday = today.isoweekday()
        date_str = today.isoformat()
        client.post("/api/schedule", json={"weekday": weekday, "period": 1, "subject": "物理"}, headers=headers)
        client.post("/api/schedule/overrides", json={
            "date": date_str, "period": 3, "action": "add", "new_subject": "辅导"
        }, headers=headers)
        res = client.get("/api/schedule/today", headers=headers)
        items = res.json()["data"]["items"]
        assert len(items) == 2
        assert items[1]["subject"] == "辅导"
