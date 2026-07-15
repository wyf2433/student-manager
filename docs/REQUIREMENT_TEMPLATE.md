# 需求描述模板

> 提需求时复制本模板填写。AI agent 会严格按照本模板理解需求。

---

## Context(背景)

(仓库定位 / 相关模块 / 限制条件)

例:当前后端已有学生 CRUD 接口,需要新增"按班级批量导入学生"功能。
限制:Excel 文件由学校提供,格式不固定,需字段映射。

## Goal(目标)

(一句话说清想要什么效果)

例:支持上传 Excel 文件,解析后返回预览,确认后批量入库。

## Acceptance criteria(验收标准)

- (使用什么命令可以校验结果)

例:
- `curl -X POST .../api/students/import/preview -F file=@test.xlsx` 返回 200 + 学生列表
- `curl -X POST .../api/students/import/confirm -d '{"students":[...]}'` 返回 201 + 导入数量
- `pytest tests/test_import.py` 全部通过

## Constraints(约束)

- 不泄露 secrets
- 最小化改动
- 幂等(重复导入同一文件不产生重复记录)
- 改动不超过 5 个文件

## Delivery(必须交付)

1. 计划(3-7 步,标注每步验证方式)
2. 代码改动
3. 关键 diff
4. 验证通过的输出(测试日志 / curl 输出)
