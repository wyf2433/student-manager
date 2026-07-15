"""成绩测试"""

import io
import pytest
from openpyxl import Workbook
from conftest import API_KEY
from database import get_db, init_db


@pytest.fixture(autouse=True)
def clean_scores():
    init_db()
    with get_db() as conn:
        conn.execute("DELETE FROM scores")
        conn.execute("DELETE FROM students")
        conn.execute("DELETE FROM classes")
    yield


def setup_class_and_students(client, headers, names):
    create = client.post("/api/classes", json={"name": "初二1班"}, headers=headers)
    cid = create.json()["data"]["id"]
    student_ids = {}
    for name in names:
        res = client.post("/api/students", json={"class_id": cid, "name": name}, headers=headers)
        student_ids[name] = res.json()["data"]["id"]
    return cid, student_ids


def make_score_excel(rows):
    wb = Workbook()
    ws = wb.active
    ws.append(["姓名", "物理", "语文", "数学"])
    for r in rows:
        ws.append(r)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


class TestScoreCRUD:
    def test_create(self, client, headers):
        cid, sids = setup_class_and_students(client, headers, ["张三"])
        res = client.post("/api/scores", json={
            "student_id": sids["张三"], "exam_name": "期中", "subject": "物理", "score": 95
        }, headers=headers)
        assert res.status_code == 201
        assert res.json()["data"]["score"] == 95

    def test_list_by_student(self, client, headers):
        cid, sids = setup_class_and_students(client, headers, ["张三", "李四"])
        client.post("/api/scores", json={"student_id": sids["张三"], "exam_name": "期中", "subject": "物理", "score": 90}, headers=headers)
        client.post("/api/scores", json={"student_id": sids["李四"], "exam_name": "期中", "subject": "物理", "score": 85}, headers=headers)
        res = client.get(f"/api/scores?student_id={sids['张三']}", headers=headers)
        items = res.json()["data"]["items"]
        assert len(items) == 1
        assert items[0]["score"] == 90

    def test_list_exams(self, client, headers):
        cid, sids = setup_class_and_students(client, headers, ["张三"])
        client.post("/api/scores", json={"student_id": sids["张三"], "exam_name": "期中", "subject": "物理", "score": 90}, headers=headers)
        client.post("/api/scores", json={"student_id": sids["张三"], "exam_name": "期末", "subject": "物理", "score": 88}, headers=headers)
        res = client.get("/api/scores/exams", headers=headers)
        items = res.json()["data"]["items"]
        assert "期中" in items
        assert "期末" in items

    def test_delete(self, client, headers):
        cid, sids = setup_class_and_students(client, headers, ["张三"])
        res = client.post("/api/scores", json={"student_id": sids["张三"], "exam_name": "期中", "subject": "物理", "score": 90}, headers=headers)
        sid = res.json()["data"]["id"]
        res = client.delete(f"/api/scores/{sid}", headers=headers)
        assert res.json()["code"] == 0


class TestScoreImport:
    def test_preview(self, client, headers):
        excel = make_score_excel([["张三", 95, 88, 92], ["李四", 80, 75, 85]])
        res = client.post(
            "/api/scores/import/preview",
            files={"file": ("test.xlsx", excel, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            headers=headers,
        )
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["total_students"] == 2
        assert "物理" in data["subjects"]
        assert data["students"][0]["scores"]["物理"] == 95

    def test_confirm(self, client, headers):
        cid, sids = setup_class_and_students(client, headers, ["张三", "李四"])
        excel = make_score_excel([["张三", 95, 88], ["李四", 80, 75]])
        preview = client.post(
            "/api/scores/import/preview",
            files={"file": ("test.xlsx", excel, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            headers=headers,
        )
        students_data = preview.json()["data"]["students"]
        confirm_body = {
            "exam_name": "期中考试",
            "subject": "物理",
            "class_id": cid,
            "students": [
                {"student_id": sids["张三"], "score": students_data[0]["scores"]["物理"]},
                {"student_id": sids["李四"], "score": students_data[1]["scores"]["物理"]},
            ],
        }
        res = client.post("/api/scores/import/confirm", json=confirm_body, headers=headers)
        assert res.status_code == 200
        assert res.json()["data"]["imported_count"] == 2
        assert res.json()["data"]["auto_created_students"] == 0

        list_res = client.get(f"/api/scores?student_id={sids['张三']}&subject=物理", headers=headers)
        assert list_res.json()["data"]["items"][0]["score"] == 95

    def test_confirm_auto_create(self, client, headers):
        cid = client.post("/api/classes", json={"name": "初二1班"}, headers=headers).json()["data"]["id"]
        excel = make_score_excel([["王五", 90], ["赵六", 85]])
        preview = client.post(
            "/api/scores/import/preview",
            files={"file": ("test.xlsx", excel, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            headers=headers,
        )
        students_data = preview.json()["data"]["students"]
        confirm_body = {
            "exam_name": "期中考试",
            "subject": "物理",
            "class_id": cid,
            "students": [
                {"name": "王五", "score": students_data[0]["scores"]["物理"]},
                {"name": "赵六", "score": students_data[1]["scores"]["物理"]},
            ],
        }
        res = client.post("/api/scores/import/confirm", json=confirm_body, headers=headers)
        assert res.status_code == 200
        assert res.json()["data"]["imported_count"] == 2
        assert res.json()["data"]["auto_created_students"] == 2

        list_res = client.get(f"/api/students?class_id={cid}", headers=headers)
        assert list_res.json()["data"]["total"] == 2
