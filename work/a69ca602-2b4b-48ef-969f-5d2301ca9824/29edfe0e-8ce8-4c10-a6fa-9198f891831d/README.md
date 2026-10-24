# 命令行待办清单

一个只依赖 Python 标准库的命令行待办工具。任务保存在 `todo.py` 同目录的
`todo.json` 中；文件不存在时会自动使用空列表，写入时先创建临时文件再原子替换。

## 运行环境

- Python 3.10 或更高版本
- 测试需要 pytest（运行时不需要）

在成果目录下运行：

```powershell
python todo.py add '写周报'
python todo.py add 'Buy MILK'
python todo.py list
python todo.py done 1
python todo.py search milk
python todo.py remove 1
python -m pytest -q
```

也可以使用绝对路径运行，例如 `python D:\Test\work\a69ca602-2b4b-48ef-969f-5d2301ca9824\29edfe0e-8ce8-4c10-a6fa-9198f891831d\todo.py list`。
无论当前工作目录是什么，数据都会写到脚本所在目录的 `todo.json`。

## 命令

- `add <任务内容>`：新增任务并打印新 ID；`nextId` 只增不减。
- `list`：按 ID 升序列出任务，完成项显示 `[x]`，未完成项显示 `[ ]`。
- `done <id>`：将任务标记为完成；ID 不存在时向 stderr 报错并返回 1。
- `remove <id>`：删除任务；ID 不存在时向 stderr 报错并返回 1。
- `search <关键词>`：按任务内容搜索，忽略大小写；没有结果时打印 `没有匹配的任务`。

## 真实运行记录

以下输出来自 2026-10-24 在成果目录中从空数据开始的实跑。

```text
$ python todo.py add '写周报'
已添加 #1: 写周报
$ python todo.py add 'Buy MILK'
已添加 #2: Buy MILK
$ python todo.py done 1
已完成 #1
$ python todo.py list
[x] 1. 写周报
[ ] 2. Buy MILK
$ python todo.py search milk
[ ] 2. Buy MILK
$ python todo.py done 99
错误：没有 ID 为 99 的任务
（退出码 1）
$ python todo.py remove 99
错误：没有 ID 为 99 的任务
（退出码 1）
$ python -m pytest -q
..........                                                               [100%]
10 passed
```

运行后 `todo.json` 中的 `nextId` 为 3，任务 1 已完成，任务 2 未完成；不存在的 ID
没有改变数据文件。

## remove 不存在 ID 的取舍

我选择像 `done` 一样明确报错：把错误提示写到 stderr，返回退出码 1，并且不保存改动。
这样调用方可以可靠判断删除是否成功，不会把打字错误当成一次成功删除；如果静默成功，
脚本和人工操作都可能误以为目标任务已经不存在。

## 测试覆盖

`test_todo.py` 共 10 个测试，覆盖添加与 ID 递增、查找失败、删除成功和失败、
删除后不复用 ID、大小写不敏感搜索、无搜索结果、中文 JSON 往返保存，以及完整命令层流程。
业务函数只修改或返回内存数据，不打印、不退出进程；命令层负责提示和退出码。
