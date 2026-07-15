"""成绩数据访问层"""

import math

from database import get_db


def create_score(
    student_id: int, exam_name: str, subject: str, score: float = None, full_score: float = 100
) -> dict:
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO scores (student_id, exam_name, subject, score, full_score) "
            "VALUES (?, ?, ?, ?, ?)",
            (student_id, exam_name, subject, score, full_score),
        )
        row = conn.execute("SELECT * FROM scores WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return dict(row)


def list_scores(student_id: int = None, exam_name: str = None, subject: str = None) -> list:
    sql = "SELECT * FROM scores WHERE 1=1"
    params = []
    if student_id:
        sql += " AND student_id = ?"
        params.append(student_id)
    if exam_name:
        sql += " AND exam_name = ?"
        params.append(exam_name)
    if subject:
        sql += " AND subject = ?"
        params.append(subject)
    sql += " ORDER BY created_at DESC, id DESC"
    with get_db() as conn:
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]


def batch_create_scores(scores: list[dict]) -> int:
    with get_db() as conn:
        for s in scores:
            conn.execute(
                "INSERT INTO scores (student_id, exam_name, subject, score, full_score) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    s["student_id"],
                    s["exam_name"],
                    s["subject"],
                    s.get("score"),
                    s.get("full_score", 100),
                ),
            )
        return len(scores)


def delete_score(score_id: int) -> bool:
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM scores WHERE id = ?", (score_id,))
        return cursor.rowcount > 0


def get_exam_names() -> list:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT DISTINCT exam_name FROM scores ORDER BY exam_name"
        ).fetchall()
        return [r["exam_name"] for r in rows]


def get_exam_subjects(exam_name: str) -> list:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT DISTINCT subject FROM scores WHERE exam_name = ? ORDER BY subject",
            (exam_name,),
        ).fetchall()
        return [r["subject"] for r in rows]


# ── 分析查询 ──


def get_exam_analysis(exam_name: str, subject: str) -> dict:
    """单次考试分析:均分/中位数/标准差/分数段/难度/班级对比"""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT s.score, s.full_score, st.class_id, c.name AS class_name "
            "FROM scores s "
            "JOIN students st ON s.student_id = st.id "
            "LEFT JOIN classes c ON st.class_id = c.id "
            "WHERE s.exam_name = ? AND s.subject = ? AND s.score IS NOT NULL",
            (exam_name, subject),
        ).fetchall()

        if not rows:
            return None

        scores = [r["score"] for r in rows]
        full_score = rows[0]["full_score"] or 100
        n = len(scores)
        avg = sum(scores) / n
        sorted_scores = sorted(scores)
        median = sorted_scores[n // 2] if n % 2 == 1 else (sorted_scores[n // 2 - 1] + sorted_scores[n // 2]) / 2
        variance = sum((x - avg) ** 2 for x in scores) / n
        std_dev = math.sqrt(variance)

        pass_line = full_score * 0.6
        excellent_line = full_score * 0.9
        pass_count = sum(1 for s in scores if s >= pass_line)
        excellent_count = sum(1 for s in scores if s >= excellent_line)

        difficulty_ratio = avg / full_score if full_score > 0 else 0
        if difficulty_ratio > 0.85:
            difficulty_label, difficulty_level = "偏易", "easy"
        elif difficulty_ratio > 0.7:
            difficulty_label, difficulty_level = "适中", "moderate"
        elif difficulty_ratio > 0.5:
            difficulty_label, difficulty_level = "偏难", "hard"
        else:
            difficulty_label, difficulty_level = "过难", "very_hard"

        ranges = [
            (0, pass_line, "0-59" if full_score == 100 else "不及格"),
            (pass_line, full_score * 0.7, "60-69" if full_score == 100 else "及格"),
            (full_score * 0.7, full_score * 0.8, "70-79" if full_score == 100 else "中等"),
            (full_score * 0.8, excellent_line, "80-89" if full_score == 100 else "良好"),
            (excellent_line, full_score + 1, "90-100" if full_score == 100 else "优秀"),
        ]
        score_ranges = {}
        for lo, hi, label in ranges:
            cnt = sum(1 for s in scores if lo <= s < hi)
            score_ranges[label] = {"count": cnt, "percent": round(cnt / n * 100, 1)}

        class_map = {}
        for r in rows:
            cn = r["class_name"] or "未分班"
            if cn not in class_map:
                class_map[cn] = []
            class_map[cn].append(r["score"])

        class_comparison = []
        for cn, cls_scores in sorted(class_map.items()):
            cn_n = len(cls_scores)
            cls_avg = sum(cls_scores) / cn_n
            cls_pass = sum(1 for s in cls_scores if s >= pass_line)
            class_comparison.append({
                "class_name": cn,
                "avg": round(cls_avg, 1),
                "pass_rate": round(cls_pass / cn_n * 100, 1),
                "count": cn_n,
            })

        return {
            "exam_name": exam_name,
            "subject": subject,
            "full_score": full_score,
            "total_students": n,
            "avg_score": round(avg, 1),
            "max_score": max(scores),
            "min_score": min(scores),
            "median_score": round(median, 1),
            "std_dev": round(std_dev, 1),
            "pass_rate": round(pass_count / n * 100, 1),
            "excellent_rate": round(excellent_count / n * 100, 1),
            "difficulty": difficulty_label,
            "difficulty_level": difficulty_level,
            "difficulty_ratio": round(difficulty_ratio, 2),
            "score_ranges": score_ranges,
            "class_comparison": class_comparison,
        }


def get_student_trend(student_id: int, subject: str = None) -> dict:
    """学生个人多次成绩趋势(含班级均分对比 + 进退步)
    返回 {student_name, subjects[], current_subject, exams[]} — exams 仅含同一科目
    """
    with get_db() as conn:
        all_rows = conn.execute(
            "SELECT s.id, s.exam_name, s.subject, s.score, s.full_score, s.created_at, "
            "st.name AS student_name, st.class_id "
            "FROM scores s JOIN students st ON s.student_id = st.id "
            "WHERE s.student_id = ? AND s.score IS NOT NULL "
            "ORDER BY s.created_at ASC, s.id ASC",
            (student_id,),
        ).fetchall()

        if not all_rows:
            return None

        student_name = all_rows[0]["student_name"]
        class_id = all_rows[0]["class_id"]
        subjects = sorted(set(r["subject"] for r in all_rows))

        if not subject:
            subject = subjects[0]

        rows = [r for r in all_rows if r["subject"] == subject]

        exams = []
        prev_score = None
        for r in rows:
            change = None
            if prev_score is not None:
                change = round(r["score"] - prev_score, 1)
            prev_score = r["score"]

            class_avg = None
            if class_id:
                avg_row = conn.execute(
                    "SELECT AVG(s2.score) AS avg_score "
                    "FROM scores s2 JOIN students st2 ON s2.student_id = st2.id "
                    "WHERE s2.exam_name = ? AND s2.subject = ? AND st2.class_id = ? "
                    "AND s2.score IS NOT NULL",
                    (r["exam_name"], r["subject"], class_id),
                ).fetchone()
                if avg_row and avg_row["avg_score"] is not None:
                    class_avg = round(avg_row["avg_score"], 1)

            date_str = (r["created_at"] or "")[:10]
            exams.append({
                "exam_name": r["exam_name"],
                "subject": r["subject"],
                "score": r["score"],
                "full_score": r["full_score"] or 100,
                "class_avg": class_avg,
                "change": change,
                "date": date_str,
            })

        return {
            "student_name": student_name,
            "subjects": subjects,
            "current_subject": subject,
            "exams": exams,
        }


def get_class_trend(class_id: int, subject: str = None) -> dict:
    """班级多次考试成绩趋势"""
    with get_db() as conn:
        class_row = conn.execute("SELECT name FROM classes WHERE id = ?", (class_id,)).fetchone()
        if not class_row:
            return None
        class_name = class_row["name"]

        if subject:
            rows = conn.execute(
                "SELECT s.exam_name, s.subject, s.score, s.full_score "
                "FROM scores s JOIN students st ON s.student_id = st.id "
                "WHERE st.class_id = ? AND s.subject = ? AND s.score IS NOT NULL "
                "ORDER BY s.created_at ASC, s.id ASC",
                (class_id, subject),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT s.exam_name, s.subject, s.score, s.full_score "
                "FROM scores s JOIN students st ON s.student_id = st.id "
                "WHERE st.class_id = ? AND s.score IS NOT NULL "
                "ORDER BY s.created_at ASC, s.id ASC",
                (class_id,),
            ).fetchall()

        if not rows:
            return {"class_name": class_name, "subject": subject, "exams": []}

        exam_map = {}
        for r in rows:
            key = (r["exam_name"], r["subject"])
            if key not in exam_map:
                exam_map[key] = []
            exam_map[key].append(r["score"])

        full_score = rows[0]["full_score"] or 100
        pass_line = full_score * 0.6
        excellent_line = full_score * 0.9

        exams = []
        for (exam_name, subj), sc_list in exam_map.items():
            n = len(sc_list)
            avg = sum(sc_list) / n
            pass_count = sum(1 for s in sc_list if s >= pass_line)
            exc_count = sum(1 for s in sc_list if s >= excellent_line)
            exams.append({
                "exam_name": exam_name,
                "subject": subj,
                "avg": round(avg, 1),
                "pass_rate": round(pass_count / n * 100, 1),
                "excellent_rate": round(exc_count / n * 100, 1),
                "count": n,
            })

        return {
            "class_name": class_name,
            "subject": subject,
            "exams": exams,
        }


def get_ranking(exam_name: str, subject: str, class_id: int = None) -> dict:
    """单次考试排行榜 + 进步/退步榜"""
    with get_db() as conn:
        if class_id:
            rows = conn.execute(
                "SELECT s.student_id, s.score, s.full_score, st.name AS student_name, "
                "c.name AS class_name, st.class_id "
                "FROM scores s JOIN students st ON s.student_id = st.id "
                "LEFT JOIN classes c ON st.class_id = c.id "
                "WHERE s.exam_name = ? AND s.subject = ? AND st.class_id = ? "
                "AND s.score IS NOT NULL "
                "ORDER BY s.score DESC",
                (exam_name, subject, class_id),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT s.student_id, s.score, s.full_score, st.name AS student_name, "
                "c.name AS class_name, st.class_id "
                "FROM scores s JOIN students st ON s.student_id = st.id "
                "LEFT JOIN classes c ON st.class_id = c.id "
                "WHERE s.exam_name = ? AND s.subject = ? AND s.score IS NOT NULL "
                "ORDER BY s.score DESC",
                (exam_name, subject),
            ).fetchall()

        if not rows:
            return None

        full_score = rows[0]["full_score"] or 100
        rankings = []
        prev_exam = conn.execute(
            "SELECT s.exam_name, MIN(s.created_at) AS first_created, MIN(s.id) AS first_id "
            "FROM scores s WHERE s.subject = ? AND s.score IS NOT NULL "
            "GROUP BY s.exam_name "
            "ORDER BY first_created DESC, first_id DESC",
            (subject,),
        ).fetchall()

        exam_order = [r["exam_name"] for r in prev_exam]
        current_idx = exam_order.index(exam_name) if exam_name in exam_order else -1
        prev_exam_name = exam_order[current_idx + 1] if current_idx >= 0 and current_idx + 1 < len(exam_order) else None

        prev_scores = {}
        if prev_exam_name:
            prev_rows = conn.execute(
                "SELECT student_id, score FROM scores "
                "WHERE exam_name = ? AND subject = ? AND score IS NOT NULL",
                (prev_exam_name, subject),
            ).fetchall()
            prev_scores = {r["student_id"]: r["score"] for r in prev_rows}

        for rank, r in enumerate(rows, 1):
            change = None
            if r["student_id"] in prev_scores:
                change = round(r["score"] - prev_scores[r["student_id"]], 1)
            rankings.append({
                "rank": rank,
                "student_id": r["student_id"],
                "student_name": r["student_name"],
                "class_name": r["class_name"] or "未分班",
                "score": r["score"],
                "change": change,
            })

        changes = [r for r in rankings if r["change"] is not None]
        top_improved = sorted(changes, key=lambda x: x["change"], reverse=True)[:5]
        top_declined = sorted(changes, key=lambda x: x["change"])[:5]

        return {
            "exam_name": exam_name,
            "subject": subject,
            "full_score": full_score,
            "prev_exam_name": prev_exam_name,
            "rankings": rankings,
            "top_improved": top_improved,
            "top_declined": top_declined,
        }
