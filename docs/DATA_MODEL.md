# 数据模型设计

> 修改本文件前必须停手汇报(数据库 schema 变更是红线)。
> SQLite 单文件,字段类型用 SQLite 原生类型。

## 表结构

### 1. classes(班级)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| name | TEXT NOT NULL | 班级名(如"初二1班") |
| grade | TEXT | 年级(初一/初二/初三) |
| created_at | TEXT | 创建时间(ISO8601) |

### 2. students(学生)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| class_id | INTEGER FK | 关联 classes.id |
| name | TEXT NOT NULL | 姓名 |
| student_no | TEXT | 学号 |
| gender | TEXT | 性别(male/female) |
| created_at | TEXT | 创建时间 |

### 3. records(日常记录:考勤/请假/加扣分)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| student_id | INTEGER FK | 关联 students.id |
| type | TEXT NOT NULL | 类型:attendance/leave/score |
| content | TEXT | 内容描述 |
| value | REAL | 分值(加扣分用,正=加,负=扣) |
| created_at | TEXT | 记录时间 |

- type=attendance:考勤(正常/迟到/缺席)
- type=leave:请假(病假/事假/其他)
- type=score:加扣分(带 value)

### 4. scores(成绩)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| student_id | INTEGER FK | 关联 students.id |
| exam_name | TEXT NOT NULL | 考试名称(如"期中考试") |
| subject | TEXT NOT NULL | 科目(物理/语文/数学...) |
| score | REAL | 分数 |
| created_at | TEXT | 创建时间 |

### 5. traces(工作留痕)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| title | TEXT NOT NULL | 标题 |
| type | TEXT NOT NULL | 类型(见下方枚举) |
| note | TEXT | 备注 |
| image_urls | TEXT | 图片 URL(JSON 数组字符串) |
| student_ids | TEXT | 关联学生 ID(JSON 数组字符串) |
| created_at | TEXT | 创建时间 |

留痕类型枚举:
- classroom_discipline(课堂纪律)
- experiment_record(实验课记录)
- homework_feedback(作业反馈)
- exam_analysis(测验/考试分析)
- student_talk(学生谈话)
- parent_communication(家长沟通)
- other(其他)

### 6. schedule(常规课表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| weekday | INTEGER NOT NULL | 星期(1-7) |
| period | INTEGER NOT NULL | 节次(1-12) |
| subject | TEXT NOT NULL | 科目(默认"物理") |
| class_name | TEXT | 上哪个班的课 |
| created_at | TEXT | 创建时间 |

- 联合唯一:(weekday, period) 防止重复排课

### 7. schedule_override(临时调课)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| date | TEXT NOT NULL | 具体日期(ISO8601) |
| period | INTEGER NOT NULL | 节次 |
| action | TEXT NOT NULL | 类型:change/cancel/substitute/add |
| new_subject | TEXT | 新科目(change/substitute 用) |
| new_class_name | TEXT | 新班级 |
| note | TEXT | 备注(如"教研会") |
| created_at | TEXT | 创建时间 |

调课类型:
- change:改科目(原数学→自习)
- cancel:停课(开会)
- substitute:代课(帮别人上课)
- add:加课(临时多一节)

### 8. homework(作业布置)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| class_id | INTEGER FK | 关联 classes.id |
| content | TEXT NOT NULL | 作业内容 |
| type | TEXT NOT NULL | 类型:daily/experiment_report/review/exam |
| due_date | TEXT | 截止日期 |
| status | TEXT NOT NULL | 状态:active/collected/graded |
| note | TEXT | 备注 |
| created_at | TEXT | 布置日期 |

作业类型:
- daily(日常作业)
- experiment_report(实验报告)
- review(复习提纲)
- exam(试卷)

作业状态流转:active → collected → graded

### 9. quick_notes(速记)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| content | TEXT NOT NULL | 速记内容 |
| student_id | INTEGER FK | 关联学生(可选,可后补关联) |
| created_at | TEXT | 创建时间 |

## 索引建议

- students: (class_id), (name)
- records: (student_id), (created_at), (type)
- scores: (student_id), (exam_name), (subject)
- traces: (type), (created_at)
- schedule: (weekday, period)
- schedule_override: (date)
- homework: (class_id), (status), (due_date)

## 查询示例

### 今日课程(合并常规+调课)

```sql
-- 常规课表
SELECT * FROM schedule WHERE weekday = ?;
-- 今日调课
SELECT * FROM schedule_override WHERE date = ?;
-- 应用层合并:override 覆盖/补充 schedule
```

### 学生详情时间线

```sql
SELECT 'record' AS source, id, type, content, value, created_at
FROM records WHERE student_id = ?
UNION ALL
SELECT 'score' AS source, id, exam_name, subject, score, created_at
FROM scores WHERE student_id = ?
UNION ALL
SELECT 'trace' AS source, id, title, type, note, NULL, created_at
FROM traces WHERE student_ids LIKE ?
ORDER BY created_at DESC;
```
