import json

import pytest

from todo import add_item, find_item, load, main, remove_item, save, search_items


def test_add_increases_next_id_and_preserves_text():
    data = {'nextId': 4, 'items': []}

    item = add_item(data, '写周报')

    assert item == {'id': 4, 'text': '写周报', 'done': False}
    assert data['nextId'] == 5
    assert data['items'] == [item]


def test_find_missing_item_raises_key_error():
    data = {'nextId': 1, 'items': []}

    with pytest.raises(KeyError, match='99'):
        find_item(data, 99)


def test_remove_reports_result_and_never_reuses_id():
    data = {'nextId': 1, 'items': []}
    first = add_item(data, '买牛奶')
    add_item(data, '写周报')

    assert remove_item(data, first['id']) is True
    assert remove_item(data, 99) is False
    assert [item['id'] for item in data['items']] == [2]
    assert data['nextId'] == 3


def test_search_is_case_insensitive_and_sorted_by_id():
    data = {'nextId': 1, 'items': []}
    add_item(data, 'Buy MILK')
    add_item(data, '整理报告')
    add_item(data, 'buy milk again')

    assert [item['id'] for item in search_items(data, 'milk')] == [1, 3]


def test_search_returns_empty_list_when_nothing_matches():
    data = {'nextId': 1, 'items': []}
    add_item(data, '写周报')

    assert search_items(data, '牛奶') == []


def test_save_and_load_round_trip_preserves_chinese(tmp_path):
    path = tmp_path / 'todo.json'
    data = {'nextId': 2, 'items': [{'id': 1, 'text': '中文不乱码', 'done': True}]}

    save(path, data)

    assert load(path) == data
    assert '中文不乱码' in path.read_text(encoding='utf-8')
    assert list(tmp_path.glob('*.tmp')) == []


def test_main_add_done_list_and_search(tmp_path, capsys):
    path = tmp_path / 'todo.json'

    assert main(['add', '写周报'], path=path) == 0
    assert main(['add', 'Buy MILK'], path=path) == 0
    assert main(['done', '1'], path=path) == 0
    assert main(['list'], path=path) == 0
    assert main(['search', 'milk'], path=path) == 0

    output = capsys.readouterr().out
    assert '已添加 #1' in output
    assert '已完成 #1' in output
    assert '[x] 1. 写周报' in output
    assert '[ ] 2. Buy MILK' in output
    assert json.loads(path.read_text(encoding='utf-8'))['nextId'] == 3


def test_main_done_missing_returns_error_and_does_not_save(tmp_path, capsys):
    path = tmp_path / 'todo.json'

    assert main(['done', '99'], path=path) == 1

    captured = capsys.readouterr()
    assert '没有 ID 为 99 的任务' in captured.err
    assert not path.exists()


def test_main_search_without_matches_prints_message(tmp_path, capsys):
    path = tmp_path / 'todo.json'
    main(['add', '写周报'], path=path)
    capsys.readouterr()

    assert main(['search', '牛奶'], path=path) == 0

    assert capsys.readouterr().out.strip() == '没有匹配的任务'


def test_main_remove_missing_returns_nonzero(tmp_path, capsys):
    path = tmp_path / 'todo.json'

    assert main(['remove', '7'], path=path) == 1

    assert '没有 ID 为 7 的任务' in capsys.readouterr().err
    assert not path.exists()
