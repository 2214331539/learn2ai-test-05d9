'''一个无需第三方运行时依赖的命令行待办清单。'''

import argparse
import json
import os
import sys
import tempfile


DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'todo.json')


def load(path):
    '''读取数据；文件不存在时返回空结构。'''
    if not os.path.exists(path):
        return {'nextId': 1, 'items': []}
    with open(path, encoding='utf-8') as file:
        return json.load(file)


def save(path, data):
    '''先写同目录临时文件，再用 os.replace 原子替换目标文件。'''
    directory = os.path.dirname(os.path.abspath(path))
    fd, tmp_path = tempfile.mkstemp(dir=directory, suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def add_item(data, text):
    '''添加任务并返回新任务；ID 不复用。'''
    item = {'id': data['nextId'], 'text': text, 'done': False}
    data['nextId'] += 1
    data['items'].append(item)
    return item


def find_item(data, item_id):
    '''按 ID 查找任务，找不到时抛出 KeyError。'''
    for item in data['items']:
        if item['id'] == item_id:
            return item
    raise KeyError(f'没有 ID 为 {item_id} 的任务')


def remove_item(data, item_id):
    '''删除指定任务；返回它此前是否存在。'''
    for index, item in enumerate(data['items']):
        if item['id'] == item_id:
            del data['items'][index]
            return True
    return False


def search_items(data, keyword):
    '''按任务内容做大小写不敏感搜索，结果按 ID 排序。'''
    needle = keyword.casefold()
    matches = [item for item in data['items'] if needle in item['text'].casefold()]
    return sorted(matches, key=lambda item: item['id'])


def build_parser():
    parser = argparse.ArgumentParser(prog='todo', description='命令行待办清单')
    sub = parser.add_subparsers(dest='command', required=True)

    p_add = sub.add_parser('add', help='添加任务')
    p_add.add_argument('text')

    sub.add_parser('list', help='列出任务')

    p_done = sub.add_parser('done', help='标记完成')
    p_done.add_argument('id', type=int)

    p_remove = sub.add_parser('remove', help='删除任务')
    p_remove.add_argument('id', type=int)

    p_search = sub.add_parser('search', help='搜索任务')
    p_search.add_argument('keyword')
    return parser


def print_items(items):
    for item in sorted(items, key=lambda entry: entry['id']):
        mark = 'x' if item['done'] else ' '
        item_id = item['id']
        item_text = item['text']
        print(f'[{mark}] {item_id}. {item_text}')


def main(argv=None, path=None):
    args = build_parser().parse_args(argv)
    data_path = DATA_FILE if path is None else path
    data = load(data_path)
    try:
        if args.command == 'add':
            item = add_item(data, args.text)
            save(data_path, data)
            item_id = item['id']
            item_text = item['text']
            print(f'已添加 #{item_id}: {item_text}')
        elif args.command == 'list':
            print_items(data['items'])
        elif args.command == 'done':
            find_item(data, args.id)['done'] = True
            save(data_path, data)
            print(f'已完成 #{args.id}')
        elif args.command == 'remove':
            if not remove_item(data, args.id):
                print(f'错误：没有 ID 为 {args.id} 的任务', file=sys.stderr)
                return 1
            save(data_path, data)
            print(f'已删除 #{args.id}')
        elif args.command == 'search':
            matches = search_items(data, args.keyword)
            if matches:
                print_items(matches)
            else:
                print('没有匹配的任务')
    except KeyError as exc:
        print(f'错误：{exc.args[0]}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
