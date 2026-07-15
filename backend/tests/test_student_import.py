"""学生 Excel 导入测试"""

import io
import pytest
from openpyxl import Workbook
from conftest import API_KEY
from database import get_db, init_db


@pytest.fixture(autouse=True)
def clean_students():
    init_db()
    with get_db() as conn:
        conn.execute("DELETE FROM students")
        conn.execute("DELETE FROM classes")
    yield


def make_student_excel(rows):
    wb = Workbook()
    ws = wb.active
    ws.append(["姓名", "学号", "性别"])
    for r in rows:
        ws.append(r)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


class TestStudentImport:
    def test_preview(self, client, headers):
        excel = make_student_excel([["张三", "001", "男"], ["李四", "002", "女"]])
        res = client.post(
            "/api/students/import/preview",
            files={"file": ("test.xlsx", excel, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            headers=headers,
        )
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["total"] == 2
        assert data["students"][0]["name"] == "张三"
        assert data["students"][0]["gender"] == "男"

    def test_preview_no_name_column(self, client, headers):
        wb = Workbook()
        ws = wb.active
        ws.append(["编号", "学号"])
        ws.append(["001", "张三"])
        buf = io.BytesIO()
        wb.save(buf)
        res = client.post(
            "/api/students/import/preview",
            files={"file": ("test.xlsx", buf.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            headers=headers,
        )
        assert res.status_code == 400

    def test_confirm(self, client, headers):
        create = client.post("/api/classes", json={"name": "初二1班"}, headers=headers)
        cid = create.json()["data"]["id"]
        excel = make_student_excel([["张三", "001", "男"], ["李四", "002", "女"]])
        preview = client.post(
            "/api/students/import/preview",
            files={"file": ("test.xlsx", excel, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            headers=headers,
        )
        students = preview.json()["data"]["students"]
        res = client.post(
            "/api/students/import/confirm",
            json={"class_id": cid, "students": students},
            headers=headers,
        )
        assert res.status_code == 200
        assert res.json()["data"]["imported_count"] == 2

        list_res = client.get(f"/api/students?class_id={cid}", headers=headers)
        assert list_res.json()["data"]["total"] == 2
