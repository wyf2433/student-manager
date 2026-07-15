# 实施计划

> MVP 优先,先跑通核心闭环再迭代增强。
> 每个阶段严格遵循 AGENTS.md 协同规矩:3-7步计划 → diff → 验证。

## 一、概述

| 维度 | 内容 |
|------|------|
| 目标用户 | 初中物理老师(个人使用) |
| 技术栈 | 微信小程序 + 云函数(Node转发) + FastAPI(Python) + SQLite |
| 部署 | ECS 香港(47.239.15.178),纯公网IP,HTTP + API Key |
| AppID | wxe7bfa91a1970e2dc |
| 开发机 | 后端在 Linux 服务器;前端代码服务器写好,Win/Mac 开发者工具打开 |
| 节奏 | MVP 优先 |

## 二、MVP 定义

**目标**:女朋友能在手机上记录学生考勤/请假/加扣分,查看今日概览和学生历史。

| 包含(MVP) | 不包含(后续迭代) |
|------|----------------|
| 学生名册(手动添加) | 课表/调课 |
| 考勤/请假/加扣分记录 | 作业布置 |
| 今日概览 + 最近记录 | 工作留痕/拍照 |
| 学生详情时间线 | Excel成绩导入 |
| 一句话速记 | |

## 三、开发阶段总览

```
MVP(阶段1-5,约6天)            迭代1(阶段6-7,约2.5天)
┌──────────────────┐          ┌──────────────────┐
│ 1.后端基础        │          │ 6.课表+调课       │
│ 2.班级+学生CRUD   │          │ 7.作业布置        │
│ 3.记录+速记       │          └──────────────────┘
│ 4.首页聚合API     │          迭代2(阶段8-9,约3天)
│ 5.小程序首页+学生 │          ┌──────────────────┐
└──────────────────┘          │ 8.工作留痕+图片   │
                              │ 9.Excel成绩导入   │
                              └──────────────────┘
                              收尾(阶段10-11,约2天)
                              ┌──────────────────┐
                              │ 10.云函数+联调    │
                              │ 11.测试+提交审核  │
                              └──────────────────┘
```

## 四、各阶段详细计划

### 阶段 1:后端基础搭建(1天)

**目标**:FastAPI 项目能启动,API Key 认证生效,数据库表初始化。

**产出文件**:
```
backend/
├── main.py              # FastAPI 入口
├── config.py            # .env 配置加载
├── database.py          # SQLite 连接 + init_db(8张表)
├── middleware/
│   ├── __init__.py
│   ├── auth.py          # X-API-Key 校验
│   └── rate_limit.py    # 速率限制
├── requirements.txt
├── .env / .env.example
└── pytest.ini
```

**验收标准**:
```bash
curl -H "X-API-Key: xxx" http://localhost:8000/api/health  # → 200
curl http://localhost:8000/api/health                        # → 401
sqlite3 data/student_manager.db ".tables"                    # → 8张表
```

### 阶段 2:班级 + 学生 CRUD(1.5天)

**产出文件**:
```
backend/
├── models/{__init__,class_model,student_model}.py
├── schemas/{__init__,class_schema,student_schema}.py
├── routers/{__init__,classes,students}.py
├── tests/{conftest,test_classes,test_students}.py
```

**验收标准**:
```bash
curl -X POST -d '{"name":"初二1班","grade":"初二"}' .../api/classes
curl -X POST -d '{"class_id":1,"name":"张三"}' .../api/students
curl .../api/students?class_id=1&keyword=张
pytest tests/test_students.py -v
```

### 阶段 3:日常记录 + 速记(1天)

**产出文件**:
```
backend/
├── models/{record_model,note_model}.py
├── schemas/{record_schema,note_schema}.py
├── routers/{records,notes}.py
├── tests/{test_records,test_notes}.py
```

### 阶段 4:首页聚合 API(0.5天)

**产出文件**:
```
backend/
├── routers/dashboard.py
├── tests/test_dashboard.py
```

**验收标准**:
```bash
curl .../api/dashboard/today    # → 今日记录统计
curl .../api/dashboard/recent    # → 混合记录流
```

### 阶段 5:小程序首页 + 学生模块(2天)

**产出文件**:
```
miniprogram/
├── app.js / app.json / app.wxss
├── utils/{api,format,constants}.js
├── pages/
│   ├── home/           # 首页(概览+速记+最近)
│   ├── students/       # 学生列表
│   ├── student-detail/ # 学生详情(时间线)
│   └── student-add/    # 新增学生
├── components/
│   └── record-form/    # 底部记录表单
└── images/
```

**MVP 里程碑**:女朋友可真机预览体验核心功能。

### 阶段 6:课表 + 临时调课(1.5天)

后端: schedule_model + schedule_merger + routers/schedule.py
前端: pages/schedule + pages/schedule-edit + pages/schedule-override + 首页今日课程卡片

### 阶段 7:作业布置(1天)

后端: homework_model + routers/homework.py
前端: pages/homework + pages/homework-add + 首页今日作业卡片

### 阶段 8:工作留痕 + 图片上传(1.5天)

后端: trace_model + routers/traces.py + routers/upload.py
前端: pages/trace-add(拍照/相册+表单)

### 阶段 9:Excel 成绩导入(1.5天)

后端: services/excel_parser.py + routers/scores.py(import/preview + import/confirm)
前端: pages/score-import(选文件→预览→确认映射→导入)

### 阶段 10:云函数 + 联调(0.5天)

```
cloudfunctions/proxy/
├── index.js         # 转发层(携带API Key)
├── package.json
└── config.json
```

### 阶段 11:测试 + 优化 + 提交(1.5天)

- pytest 覆盖率 > 80%
- ruff check 零警告
- 真机全流程测试
- 部署到 ECS(systemd 守护)
- 提交微信审核

## 五、后端目录结构(完整)

```
backend/
├── main.py                      # FastAPI 入口
├── config.py                    # .env 配置加载
├── database.py                  # SQLite 连接 + init_db
├── middleware/
│   ├── auth.py                  # X-API-Key 校验
│   └── rate_limit.py            # 速率限制
├── models/                      # 数据访问层(SQL参数化)
├── schemas/                     # Pydantic 请求/响应模型
├── routers/                     # API 路由
├── services/                    # 业务逻辑(excel_parser, schedule_merger)
├── tests/                       # pytest 测试
├── data/                        # SQLite (gitignored)
├── uploads/                     # 上传文件 (gitignored)
├── requirements.txt
├── .env / .env.example
└── pytest.ini
```

## 六、小程序页面清单

| 页面 | 路径 | 阶段 |
|------|------|------|
| 首页 | pages/home/ | MVP |
| 学生列表 | pages/students/ | MVP |
| 学生详情 | pages/student-detail/ | MVP |
| 新增学生 | pages/student-add/ | MVP |
| 课表 | pages/schedule/ | 迭代1 |
| 课表录入 | pages/schedule-edit/ | 迭代1 |
| 调课 | pages/schedule-override/ | 迭代1 |
| 作业列表 | pages/homework/ | 迭代1 |
| 布置作业 | pages/homework-add/ | 迭代1 |
| 新增留痕 | pages/trace-add/ | 迭代2 |
| 成绩导入 | pages/score-import/ | 迭代2 |

## 七、部署指南(ECS)

```bash
ssh ecs
cd /opt && git clone <repo> student-manager
cd student-manager/backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # 编辑填入真实 API_KEY
uvicorn main:app --host 0.0.0.0 --port 8000

# systemd 守护
# /etc/systemd/system/student-manager.service
[Unit]
Description=Student Manager API
After=network.target
[Service]
WorkingDirectory=/opt/student-manager/backend
ExecStart=/opt/student-manager/backend/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
[Install]
WantedBy=multi-user.target

# 防火墙
ufw allow 8000/tcp
```

## 八、工时汇总

| 阶段 | 工时 | 累计 |
|------|------|------|
| 1.后端基础 | 1天 | 1天 |
| 2.班级+学生 | 1.5天 | 2.5天 |
| 3.记录+速记 | 1天 | 3.5天 |
| 4.首页聚合API | 0.5天 | 4天 |
| 5.小程序MVP | 2天 | 6天 |
| **MVP里程碑** | | **6天** |
| 6.课表+调课 | 1.5天 | 7.5天 |
| 7.作业布置 | 1天 | 8.5天 |
| 8.工作留痕 | 1.5天 | 10天 |
| 9.Excel导入 | 1.5天 | 11.5天 |
| 10.云函数 | 0.5天 | 12天 |
| 11.测试+提交 | 1.5天 | 13.5天 |

## 九、风险评估

| 风险 | 概率 | 应对 |
|------|------|------|
| 微信审核被拒 | 中 | 个人主体选"工具-效率"类目 |
| ECS内存不足(1.6G) | 低 | FastAPI+SQLite轻量,够用 |
| Excel格式不固定 | 高 | 字段映射让用户确认 |
| 云函数冷启动延迟 | 中 | 预热+前端loading |
