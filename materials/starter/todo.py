"""命令行待办清单起步文件：补完标有 TODO 的函数即可。"""

import argparse
import json
import os
import sys
import tempfile

DATA_FILE = "todo.json"


def load(path):
    """读取数据；文件不存在时返回空结构。"""
    if not os.path.exists(path):
        return {"nextId": 1, "items": []}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, data):
    """原子写入，避免中途失败损坏原文件。"""
    directory = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(dir=directory, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def add_item(data, text):
    """添加任务，返回新任务。TODO"""
    raise NotImplementedError


def find_item(data, item_id):
    """按 ID 查找任务，找不到时抛 KeyError。TODO"""
    raise NotImplementedError


def remove_item(data, item_id):
    """删除任务，返回是否真的删掉了。TODO"""
    raise NotImplementedError


def build_parser():
    parser = argparse.ArgumentParser(prog="todo", description="命令行待办清单")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="添加任务")
    p_add.add_argument("text")

    sub.add_parser("list", help="列出任务")

    p_done = sub.add_parser("done", help="标记完成")
    p_done.add_argument("id", type=int)

    p_remove = sub.add_parser("remove", help="删除任务")
    p_remove.add_argument("id", type=int)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    data = load(DATA_FILE)
    try:
        if args.command == "add":
            item = add_item(data, args.text)
            save(DATA_FILE, data)
            print(f"已添加 #{item['id']}: {item['text']}")
        elif args.command == "list":
            for item in data["items"]:
                mark = "x" if item["done"] else " "
                print(f"[{mark}] {item['id']}. {item['text']}")
        elif args.command == "done":
            find_item(data, args.id)["done"] = True
            save(DATA_FILE, data)
            print(f"已完成 #{args.id}")
        elif args.command == "remove":
            removed = remove_item(data, args.id)
            save(DATA_FILE, data)
            print(f"已删除 #{args.id}" if removed else f"没有 #{args.id}")
    except KeyError as exc:
        print(f"错误：{exc.args[0]}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

