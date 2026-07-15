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


def make_score_excel_with_class(rows):
    wb = Workbook()
    ws = wb.active
    ws.append(["姓名", "班级", "物理", "语文"])
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

    def test_confirm_with_class_column(self, client, headers):
        excel = make_score_excel_with_class([
            ["张三", "2班", 95, 88],
            ["李四", "3班", 80, 75],
        ])
        preview = client.post(
            "/api/scores/import/preview",
            files={"file": ("test.xlsx", excel, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            headers=headers,
        )
        data = preview.json()["data"]
        assert data["has_class_column"] is True
        assert data["students"][0]["class_name"] == "2班"

        confirm_body = {
            "exam_name": "期中考试",
            "subject": "物理",
            "grade_prefix": "初二",
            "students": [
                {"name": "张三", "class_name": "2班", "score": data["students"][0]["scores"]["物理"]},
                {"name": "李四", "class_name": "3班", "score": data["students"][1]["scores"]["物理"]},
            ],
        }
        res = client.post("/api/scores/import/confirm", json=confirm_body, headers=headers)
        assert res.status_code == 200
        assert res.json()["data"]["imported_count"] == 2
        assert res.json()["data"]["auto_created_classes"] == 2
        assert res.json()["data"]["auto_created_students"] == 2

        classes = client.get("/api/classes", headers=headers).json()["data"]["items"]
        class_names = [c["name"] for c in classes]
        assert "初二2班" in class_names
        assert "初二3班" in class_names

    def test_confirm_with_full_score(self, client, headers):
        cid, sids = setup_class_and_students(client, headers, ["张三", "李四"])
        confirm_body = {
            "exam_name": "月考",
            "subject": "物理",
            "class_id": cid,
            "full_score": 80,
            "students": [
                {"student_id": sids["张三"], "score": 72},
                {"student_id": sids["李四"], "score": 60},
            ],
        }
        res = client.post("/api/scores/import/confirm", json=confirm_body, headers=headers)
        assert res.status_code == 200
        list_res = client.get(f"/api/scores?student_id={sids['张三']}&subject=物理", headers=headers)
        item = list_res.json()["data"]["items"][0]
        assert item["score"] == 72
        assert item["full_score"] == 80


class TestScoreAnalysis:
    def setup_method(self, method):
        """每个测试前准备好两场考试的数据"""

    def _setup_exam_data(self, client, headers):
        """创建班级+学生,导入两场考试成绩"""
        cid, sids = setup_class_and_students(
            client, headers, ["张三", "李四", "王五", "赵六", "钱七"]
        )
        # 月考1: 5人成绩
        for name, score in [("张三", 80), ("李四", 70), ("王五", 60), ("赵六", 50), ("钱七", 90)]:
            client.post("/api/scores", json={
                "student_id": sids[name], "exam_name": "月考1", "subject": "物理",
                "score": score, "full_score": 100,
            }, headers=headers)
        # 期中: 5人成绩(张三进步,赵六退步)
        for name, score in [("张三", 95), ("李四", 72), ("王五", 65), ("赵六", 40), ("钱七", 88)]:
            client.post("/api/scores", json={
                "student_id": sids[name], "exam_name": "期中", "subject": "物理",
                "score": score, "full_score": 100,
            }, headers=headers)
        return cid, sids

    def test_exam_analysis(self, client, headers):
        cid, sids = self._setup_exam_data(client, headers)
        res = client.get(
            "/api/scores/analysis/exam?exam_name=期中&subject=物理", headers=headers
        )
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["total_students"] == 5
        assert data["full_score"] == 100
        assert data["max_score"] == 95
        assert data["min_score"] == 40
        assert data["avg_score"] == 72.0
        assert "score_ranges" in data
        assert "difficulty" in data
        assert data["difficulty_level"] in ("easy", "moderate", "hard", "very_hard")
        assert len(data["class_comparison"]) >= 1

    def test_exam_analysis_not_found(self, client, headers):
        res = client.get(
            "/api/scores/analysis/exam?exam_name=不存在&subject=物理", headers=headers
        )
        assert res.status_code == 404

    def test_student_trend(self, client, headers):
        cid, sids = self._setup_exam_data(client, headers)
        res = client.get(
            f"/api/scores/analysis/trend?student_id={sids['张三']}&subject=物理",
            headers=headers,
        )
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["student_name"] == "张三"
        assert len(data["exams"]) == 2
        assert data["exams"][0]["exam_name"] == "月考1"
        assert data["exams"][0]["change"] is None
        assert data["exams"][1]["exam_name"] == "期中"
        assert data["exams"][1]["change"] == 15.0
        assert data["exams"][1]["class_avg"] is not None

    def test_student_trend_not_found(self, client, headers):
        res = client.get(
            "/api/scores/analysis/trend?student_id=99999&subject=物理",
            headers=headers,
        )
        assert res.status_code == 404

    def test_class_trend(self, client, headers):
        cid, sids = self._setup_exam_data(client, headers)
        res = client.get(
            f"/api/scores/analysis/class-trend?class_id={cid}&subject=物理",
            headers=headers,
        )
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["class_name"] == "初二1班"
        assert len(data["exams"]) == 2
        assert data["exams"][0]["exam_name"] == "月考1"
        assert data["exams"][0]["avg"] == 70.0
        assert data["exams"][0]["count"] == 5

    def test_ranking(self, client, headers):
        cid, sids = self._setup_exam_data(client, headers)
        res = client.get(
            "/api/scores/analysis/ranking?exam_name=期中&subject=物理",
            headers=headers,
        )
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["exam_name"] == "期中"
        assert data["prev_exam_name"] == "月考1"
        assert len(data["rankings"]) == 5
        assert data["rankings"][0]["score"] == 95
        assert data["rankings"][0]["rank"] == 1
        # 张三从80→95,进步15分,应在进步榜
        improved_names = [t["student_name"] for t in data["top_improved"]]
        assert "张三" in improved_names
        # 赵六从50→40,退步10分,应在退步榜
        declined_names = [t["student_name"] for t in data["top_declined"]]
        assert "赵六" in declined_names

    def test_ranking_by_class(self, client, headers):
        cid, sids = self._setup_exam_data(client, headers)
        res = client.get(
            f"/api/scores/analysis/ranking?exam_name=期中&subject=物理&class_id={cid}",
            headers=headers,
        )
        assert res.status_code == 200
        data = res.json()["data"]
        assert len(data["rankings"]) == 5

    def test_exam_subjects(self, client, headers):
        cid, sids = self._setup_exam_data(client, headers)
        res = client.get("/api/scores/exams/期中/subjects", headers=headers)
        assert res.status_code == 200
        items = res.json()["data"]["items"]
        assert "物理" in items
