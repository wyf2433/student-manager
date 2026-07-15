"""SQLite 数据库连接与初始化"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path

from config import DB_PATH

SQL_PATH = DB_PATH


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(SQL_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def get_db():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    Path(SQL_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                grade TEXT,
                created_at TEXT DEFAULT (datetime('now', 'localtime'))
            );

            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                student_no TEXT,
                gender TEXT,
                created_at TEXT DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_students_class_id ON students(class_id);
            CREATE INDEX IF NOT EXISTS idx_students_name ON students(name);

            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                content TEXT,
                value REAL,
                created_at TEXT DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_records_student_id ON records(student_id);
            CREATE INDEX IF NOT EXISTS idx_records_type ON records(type);
            CREATE INDEX IF NOT EXISTS idx_records_created_at ON records(created_at);

            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                exam_name TEXT NOT NULL,
                subject TEXT NOT NULL,
                score REAL,
                created_at TEXT DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_scores_student_id ON scores(student_id);
            CREATE INDEX IF NOT EXISTS idx_scores_exam ON scores(exam_name);

            CREATE TABLE IF NOT EXISTS traces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                type TEXT NOT NULL,
                note TEXT,
                image_urls TEXT,
                student_ids TEXT,
                created_at TEXT DEFAULT (datetime('now', 'localtime'))
            );
            CREATE INDEX IF NOT EXISTS idx_traces_type ON traces(type);
            CREATE INDEX IF NOT EXISTS idx_traces_created_at ON traces(created_at);

            CREATE TABLE IF NOT EXISTS schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                weekday INTEGER NOT NULL,
                period INTEGER NOT NULL,
                subject TEXT NOT NULL,
                class_name TEXT,
                created_at TEXT DEFAULT (datetime('now', 'localtime')),
                UNIQUE(weekday, period)
            );

            CREATE TABLE IF NOT EXISTS schedule_override (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                period INTEGER NOT NULL,
                action TEXT NOT NULL,
                new_subject TEXT,
                new_class_name TEXT,
                note TEXT,
                created_at TEXT DEFAULT (datetime('now', 'localtime'))
            );
            CREATE INDEX IF NOT EXISTS idx_override_date ON schedule_override(date);

            CREATE TABLE IF NOT EXISTS homework (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                type TEXT NOT NULL,
                due_date TEXT,
                status TEXT NOT NULL DEFAULT 'active',
                note TEXT,
                created_at TEXT DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_homework_class_id ON homework(class_id);
            CREATE INDEX IF NOT EXISTS idx_homework_status ON homework(status);

            CREATE TABLE IF NOT EXISTS quick_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                student_id INTEGER,
                created_at TEXT DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE SET NULL
            );
            CREATE INDEX IF NOT EXISTS idx_notes_created_at ON quick_notes(created_at);
            """
        )

        _migrate_scores_full_score(conn)
        conn.commit()
    finally:
        conn.close()


def _migrate_scores_full_score(conn):
    """幂等迁移:为 scores 表添加 full_score 列(默认 100)"""
    cols = [r[1] for r in conn.execute("PRAGMA table_info(scores)").fetchall()]
    if "full_score" not in cols:
        conn.execute("ALTER TABLE scores ADD COLUMN full_score REAL DEFAULT 100")
