---
id: 29edfe0e-8ce8-4c10-a6fa-9198f891831d
title: 补完你的命令行待办清单
dueAt: 2026-11-07T23:59:00+08:00
---

# 补完你的命令行待办清单

阅读 `materials/python-cli-todo.md`，以 `materials/starter/todo.py` 为起点，完成一个能真正用起来的命令行待办工具。不许引入第三方运行时依赖（`pytest` 只用于测试）。

## 要交付的东西

在你的成果目录里至少包含：

- `todo.py`：完整可运行的工具
- `test_todo.py`：至少 3 个测试，覆盖添加、查找失败、删除
- `README.md`：运行方法、一条真实运行记录、你对 `remove` 不存在 ID 时的取舍说明

成果统一放在 `work/<你的用户UUID>/29edfe0e-8ce8-4c10-a6fa-9198f891831d/`，不要修改 `materials/` 或 `assignments/`。

## 功能要求

1. `add "任务内容"`：新增任务，打印新 ID，`nextId` 递增。
2. `list`：按 ID 从小到大列出，完成的显示 `[x]`，未完成的显示 `[ ]`。
3. `done <id>`：把任务标记为完成；ID 不存在时提示错误并以非 0 退出码结束。
4. `remove <id>`：删除任务；ID 不存在时的行为由你决定，但必须在 README 里写明理由。
5. 数据保存在脚本同目录的 `todo.json`，文件不存在时自动创建空结构，中文不乱码。
6. 写入采用「临时文件 + 替换」，不允许直接覆盖写。
7. 额外加一个 `search <关键词>` 子命令：大小写不敏感，匹配任务内容，无结果时打印「没有匹配的任务」。

## 自测清单

在成果目录里依次执行，确认输出符合预期：

```bash
python todo.py add "写周报"
python todo.py add "Buy MILK"
python todo.py done 1
python todo.py list
python todo.py search milk
python todo.py done 99   # 应报错，退出码非 0
python -m pytest -q
```

`todo.json` 里应当看到 `nextId` 继续增长，且 `done 1` 之后任务 1 是已完成状态，删除任务不会让 ID 被复用。

## 评分关注点

- 核心命令可用，边界情况有明确反馈（40%）
- 分层清楚，业务函数不打印、不退出进程，便于测试（25%）
- 测试真能发现问题，而不是只调用一次函数（20%）
- README 能让人从零跑起来，取舍说明有理由（15%）

