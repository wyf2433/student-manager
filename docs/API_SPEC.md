# API 规范

> 所有接口必须遵循本规范。

## 通用约定

### Base URL

```
http://<香港服务器公网IP>:8000/api
```

### 认证

所有请求必须携带请求头:
```
X-API-Key: <你的API Key>
```

无 Key 或 Key 错误 → `401 Unauthorized`

### 统一响应格式

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

- `code=0` 表示成功,非 0 表示错误
- `data` 为实际数据,列表用数组,分页用对象
- 错误时 `data` 为 null,`message` 描述错误原因

### 分页格式

```json
{
  "code": 0,
  "data": {
    "items": [],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

### HTTP 方法

| 方法 | 用途 |
|------|------|
| GET | 查询(列表/详情) |
| POST | 新增 |
| PUT | 全量更新 |
| PATCH | 部分更新 |
| DELETE | 删除 |

### 状态码

| 码 | 含义 |
|----|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证/API Key 错误 |
| 404 | 资源不存在 |
| 422 | 校验失败 |
| 429 | 请求过快(速率限制) |
| 500 | 服务器错误(生产环境不返回堆栈) |

## API 清单

### 班级管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/classes` | 班级列表 |
| POST | `/api/classes` | 新增班级 |
| PUT | `/api/classes/{id}` | 更新班级 |
| DELETE | `/api/classes/{id}` | 删除班级 |

### 学生管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/students` | 学生列表(支持 class_id 筛选、关键词搜索) |
| GET | `/api/students/{id}` | 学生详情 |
| POST | `/api/students` | 新增学生 |
| POST | `/api/students/batch` | 批量新增 |
| PUT | `/api/students/{id}` | 更新学生 |
| DELETE | `/api/students/{id}` | 删除学生 |

### 日常记录

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/records` | 记录列表(支持 student_id/type 筛选) |
| POST | `/api/records` | 新增记录(考勤/请假/加扣分) |
| DELETE | `/api/records/{id}` | 删除记录 |

### 成绩管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/scores` | 成绩列表(支持 student_id/exam_name/subject 筛选) |
| GET | `/api/scores/exams` | 考试名称列表 |
| GET | `/api/scores/exams/{exam_name}/subjects` | 某场考试的科目列表 |
| POST | `/api/scores` | 新增单条成绩(支持 full_score) |
| POST | `/api/scores/import/preview` | Excel 导入预览 |
| POST | `/api/scores/import/confirm` | Excel 导入确认(支持 full_score/grade_prefix) |
| DELETE | `/api/scores/{id}` | 删除成绩 |
| GET | `/api/scores/analysis/exam` | 单次考试分析(均分/中位数/标准差/分数段/难度/班级对比) |
| GET | `/api/scores/analysis/trend` | 学生个人多次成绩趋势(含班级均分+进退步) |
| GET | `/api/scores/analysis/class-trend` | 班级多次考试成绩趋势 |
| GET | `/api/scores/analysis/ranking` | 排行榜+进步/退步榜TOP5 |

### 工作留痕

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/traces` | 留痕列表(支持 type 筛选) |
| GET | `/api/traces/{id}` | 留痕详情 |
| POST | `/api/traces` | 新增留痕 |
| PUT | `/api/traces/{id}` | 更新留痕 |
| DELETE | `/api/traces/{id}` | 删除留痕 |
| POST | `/api/upload/image` | 上传图片(返回 URL) |

### 课表管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/schedule` | 课表列表(支持 weekday 筛选) |
| GET | `/api/schedule/today` | 今日课程(合并常规+调课) |
| POST | `/api/schedule` | 新增课表项 |
| PUT | `/api/schedule/{id}` | 更新课表项 |
| DELETE | `/api/schedule/{id}` | 删除课表项 |

### 临时调课

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/schedule/overrides` | 调课列表(支持 date 筛选) |
| POST | `/api/schedule/overrides` | 新增调课 |
| DELETE | `/api/schedule/overrides/{id}` | 删除调课 |

### 作业管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/homework` | 作业列表(支持 class_id/status 筛选) |
| GET | `/api/homework/today` | 今日作业 |
| POST | `/api/homework` | 布置作业 |
| PATCH | `/api/homework/{id}/status` | 更新作业状态 |
| DELETE | `/api/homework/{id}` | 删除作业 |

### 速记

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/notes` | 速记列表 |
| POST | `/api/notes` | 新增速记 |
| PATCH | `/api/notes/{id}` | 关联学生 |
| DELETE | `/api/notes/{id}` | 删除速记 |

### 首页聚合

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/dashboard/today` | 今日概览(课程+作业+记录统计) |
| GET | `/api/dashboard/recent` | 最近记录列表(混合流) |

## Excel 导入流程

```
1. POST /api/scores/import/preview  (multipart/form-data, file=xxx.xlsx)
   → 返回: {exam_name, subjects[], students[{name, scores{subject:score}}], field_mapping}
   
2. 用户确认字段映射(前端展示)

3. POST /api/scores/import/confirm  (JSON, {exam_name, subject, mapping, students[]})
   → 返回: {imported_count}
```

## 速率限制

- 全局:60 次/分钟
- 导入接口:5 次/分钟
- 超限返回 429 + `Retry-After` 头
