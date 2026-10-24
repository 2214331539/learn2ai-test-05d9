# 用 Python 写一个命令行待办清单

这节课用一个不到 150 行的小工具，把「读参数 → 改数据 → 存文件 → 输出结果」这条链路走一遍。它不需要任何第三方库，但覆盖了日常开发里最常见的几个动作。

## 学完能做到

- 用 `argparse` 把命令行输入拆成子命令和参数
- 用 JSON 文件保存结构化数据，并做到写入不损坏原文件
- 对「文件不存在」「ID 不存在」「参数缺失」给出明确提示和退出码
- 用 `pytest` 为业务函数写最小测试，不依赖终端交互

## 1. 环境

```bash
python --version   # 3.10 及以上
pip install pytest # 可选，跑测试时用
```

课程里不引入框架。工具最终长这样：

```bash
python todo.py add "写周报"
python todo.py list
python todo.py done 1
python todo.py remove 1
```

## 2. 先定数据格式

程序把任务存在 `todo.json`，结构固定为一个对象：

```json
{
  "nextId": 3,
  "items": [
    {"id": 1, "text": "写周报", "done": false},
    {"id": 2, "text": "买牛奶", "done": true}
  ]
}
```

两个约定值得提前想清楚：

1. `nextId` 单调递增，删掉任务后也不回退，避免 ID 被复用。
2. `items` 为空时返回 `[]` 而不是 `null`，下游代码不用到处判空。

## 3. 拆出三层

把代码分成三层，测试会容易很多：

| 层 | 职责 | 例子 |
| --- | --- | --- |
| 存储层 | 读写 JSON 文件 | `load(path)` / `save(path, data)` |
| 业务层 | 增删改查，只碰内存数据 | `add_item(data, text)` |
| 命令层 | 解析参数、打印结果、决定退出码 | `main(argv)` |

命令层不写业务逻辑，业务层不 `print`，存储层不关心任务是什么。这条边界守住了，后面加功能只是加函数。

## 4. 存储：写入要原子

直接 `open(path, "w")` 覆盖写有个风险：写到一半程序崩了，原文件就空了。稳妥做法是先写临时文件，再替换：

```python
import json, os, tempfile

def load(path):
    if not os.path.exists(path):
        return {"nextId": 1, "items": []}
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def save(path, data):
    directory = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(dir=directory, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)   # 同一文件系统内是原子操作
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
```

`ensure_ascii=False` 让中文按原样写入，`indent=2` 让文件可以直接用编辑器看。

## 5. 业务：函数只改数据

```python
def add_item(data, text):
    item = {"id": data["nextId"], "text": text, "done": False}
    data["nextId"] += 1
    data["items"].append(item)
    return item

def find_item(data, item_id):
    for item in data["items"]:
        if item["id"] == item_id:
            return item
    raise KeyError(f"没有 ID 为 {item_id} 的任务")
```

业务函数返回结果或抛自己的异常，不打印、不 `sys.exit`。这样测试里可以直接断言返回值。

## 6. 命令：子命令用 subparsers

```python
import argparse

def build_parser():
    parser = argparse.ArgumentParser(prog="todo", description="命令行待办清单")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="添加任务")
    p_add.add_argument("text")

    sub.add_parser("list", help="列出任务")

    p_done = sub.add_parser("done", help="标记完成")
    p_done.add_argument("id", type=int)

    p_rm = sub.add_parser("remove", help="删除任务")
    p_rm.add_argument("id", type=int)
    return parser
```

`dest="command"` 决定后面用 `args.command` 分发；`required=True` 让不带子命令时直接报错，省掉一次手写判断。

分发时用字典代替长串 `if/elif`：

```python
def main(argv=None):
    args = build_parser().parse_args(argv)
    data = load("todo.json")
    try:
        if args.command == "add":
            item = add_item(data, args.text)
            save("todo.json", data)
            print(f"已添加 #{item['id']}: {item['text']}")
        elif args.command == "list":
            for item in data["items"]:
                mark = "x" if item["done"] else " "
                print(f"[{mark}] {item['id']}. {item['text']}")
        elif args.command == "done":
            find_item(data, args.id)["done"] = True
            save("todo.json", data)
            print(f"已完成 #{args.id}")
        elif args.command == "remove":
            data["items"] = [i for i in data["items"] if i["id"] != args.id]
            save("todo.json", data)
            print(f"已删除 #{args.id}")
    except KeyError as exc:
        print(f"错误：{exc.args[0]}")
        return 1
    return 0
```

`remove` 这里即使 ID 不存在也不会报错——这是需要你判断的地方：静默成功还是提示「不存在」？两种都说得通，但要在文档里写清楚。

## 7. 退出码与错误信息

命令行工具的错误要能被脚本判断：

- 正常结束：`return 0`
- 用户输入有问题：`return 1`，提示写到 `stderr`
- 不要用 `except Exception: pass` 把问题吞掉

```python
import sys

if __name__ == "__main__":
    sys.exit(main())
```

## 8. 测试：绕开终端

业务函数不碰 `print`，测试就很短：

```python
# test_todo.py
from todo import add_item, find_item

def test_add_increases_next_id():
    data = {"nextId": 1, "items": []}
    add_item(data, "写周报")
    assert data["nextId"] == 2
    assert data["items"][0]["text"] == "写周报"

def test_find_missing_raises():
    data = {"nextId": 1, "items": []}
    try:
        find_item(data, 99)
    except KeyError:
        pass
    else:
        raise AssertionError("应当抛出 KeyError")
```

运行：

```bash
python -m pytest -q
```

## 9. 常见坑

- Windows 下直接用 `>` 重定向输出中文会乱码：先设 `PYTHONUTF8=1`，或代码里统一 `encoding="utf-8"`。
- 相对路径取的是「当前工作目录」，不是脚本所在目录；调试时用 `os.path.abspath` 打印确认。
- `argparse` 的 `type=int` 遇到 `abc` 会自己报错退出，不需要你再捕获。
- 文件里已有数据时不要忘记 `nextId` 递增，否则会出现重复 ID。

## 10. 起步文件

`materials/starter/todo.py` 是一个可运行的空壳，四个子命令都已接好，业务函数留了 `TODO`。可以直接复制到自己的成果目录里补完。

