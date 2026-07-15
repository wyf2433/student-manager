# AGENTS.md — 学生管理类 App(初中物理老师端)

> 本文件是 AI coding agent 的核心规则文件,开发时必须随时参阅。
> 规范来源:how-to-vibecoding 工程方法论 + 本项目实际约束。

## Project(项目定位)

- **名称**:学生管理类 App(初中物理老师端)
- **目标用户**:初中物理老师(个人使用,女朋友专用)
- **微信 AppID**:wxe7bfa91a1970e2dc
- **后端公网地址**:http://47.239.25.178
- **技术栈**:
  - 前端:微信原生小程序(AppID: wxe7bfa91a1970e2dc)
  - 网关:微信云函数(Node.js,薄转发层,免备案)
  - 后端:Python FastAPI(部署于 ECS 47.239.25.178)
  - 数据库:SQLite
  - 部署:香港服务器(纯公网 IP,无域名,HTTP + API Key)
- **学科上下文**:初中物理(初一无物理课,初二/初三有)
- **密钥管理**:所有密钥在 `backend/.env`(gitignored),上传密钥在 `/home/wyf/weixinkey`(不复制进仓库)

## How to run(运行方式)

- **Backend**:`cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 --reload`
- **Mini-program**:微信开发者工具打开 `miniprogram/` 目录
- **Cloud function**:部署到微信云开发,配置后端公网 IP
- **Test**:`cd backend && pytest`
- **Lint**:`cd backend && ruff check .`

## Collaboration rules(协同规矩)

1. **动手前先给 3-7 步计划**,标注每一步怎么验证。
2. **改完必须贴 diff**,不要只给总结。
3. **收工前自觉跑 lint、test、build**;跑不了的说明原因。
4. **任何情况都不许泄露 secrets**(.env、key、token、API Key、credentials)。
5. **最小化改动**,不要为了美观重构大片代码。
6. **修改方案做到幂等**:无论跑几次都不该搞出重复追加、文本反复插入导致的破相。
7. **不迷信 unified diff 通用性**:工具执行失败,立刻切换降维方案——给出整个函数/模块的完整替换,或采用"查找且批量替换"式方案协助落盘。

## Stop conditions(什么时候必须停手)

遇到以下情况立刻停手汇报,不许硬撑:

- 要引入新依赖或做大版本升级。
- 改动超过 5 个文件。
- 连续 2 次排错失败找不到原因。
- 涉及数据库 schema 变更(需先更新 `docs/DATA_MODEL.md`)。
- 涉及 API Key / 认证逻辑修改。
- 涉及删除操作或重建根目录。

## 角色约束

### Builder(实现者)
- 职责:只做实现,最小改动。
- 禁止:自行修改测试基线、重构无关代码。
- 交付:diff + 通过验证的输出。

### Verifier(审查者)
- 职责:只做审查,不写实现。
- 必须交付:风险清单、未覆盖边界、逐条 diff 结论。
- 禁止:在没有验证结果时宣称"应该没问题"。

## 安全红线(本项目特有)

后端暴露在公网 IP,安全是重中之重:

1. **所有接口必须校验 `X-API-Key` 请求头**,无 Key 或 Key 错误直接返回 401。
2. **API Key 只存环境变量**(`.env`),禁止硬编码进任何源文件。
3. **云函数转发时必须携带 API Key**(从云函数环境变量读取)。
4. **SQL 参数化查询**:使用 `?` 占位符,禁止 f-string / 字符串拼接 SQL。
5. **文件上传校验**:校验 MIME 类型 + 文件大小(Excel ≤ 10MB,图片 ≤ 5MB)。
6. **CORS 限制来源**:仅允许微信云函数来源。
7. **速率限制**:防止暴力调用(建议 60 次/分钟)。
8. **错误信息脱敏**:生产环境不返回堆栈详情,只返回错误码 + 简短消息。

## 需求描述规范

提需求时请遵循 `docs/REQUIREMENT_TEMPLATE.md` 模板,包含:
- Context(背景)
- Goal(目标)
- Acceptance criteria(验收标准)
- Constraints(约束)
- Delivery(必须交付)

## 排障规范

遇到 Bug 时,严格遵循 `skills/bugfix.md` 中定义的流程卡片。

## 文件结构

```
student-manager/
├── AGENTS.md                  ← 本文件(核心规则)
├── .context/                  ← 跨设备同步与进展追踪
│   ├── SUMMARY.md
│   ├── task_progress.md
│   ├── sync_meta.json
│   └── .gitattributes
├── docs/                      ← 设计文档与规范
│   ├── REQUIREMENT_TEMPLATE.md
│   ├── DATA_MODEL.md
│   ├── API_SPEC.md
│   └── SECURITY.md
├── skills/                    ← Skills 流程卡
│   └── bugfix.md
├── backend/                   ← Python FastAPI 后端
├── miniprogram/               ← 微信小程序前端
└── .gitignore
```

## 开发阶段(参考)

1. 后端搭建:FastAPI + SQLite + 数据模型
2. 核心 CRUD 接口(学生/记录/留痕)
3. Excel 导入解析 + 预览接口
4. 小程序前端:首页(课程+作业+速记+概览)
5. 小程序前端:学生模块(列表+详情+时间线)
6. 课表 + 临时调课
7. 作业布置 + 状态流转
8. 云函数转发层 + 联调
9. 测试 + 优化 + 提交审核
