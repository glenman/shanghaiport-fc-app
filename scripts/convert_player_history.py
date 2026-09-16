#!/usr/bin/env python3
"""
将《上海海港球员历史出场汇总(2006-2026).xlsx》转换为按球员组织的 JSON
每个球员包含：基本信息(name/birthDate/position/nationality)
             + 汇总(summary) + 各赛事(c2l/c1l/csl/cfa/acle/supercup)统计
字段名用英文，进球(点球)拆分为 goals + penalties 两个字段
"""
import openpyxl
import json
import re
from datetime import datetime, date

INPUT = 'datafile/上海海港球员历史出场汇总(2006-2026).xlsx'
OUTPUT = 'public/data/player_history_stats.json'

# sheet 名 → JSON key
SHEET_MAP = {
    '汇总': 'summary',
    '中乙联赛': 'c2l',
    '中甲联赛': 'c1l',
    '中超联赛': 'csl',
    '足协杯': 'cfa',
    '亚冠联赛(含资格赛)': 'acle',
    '超级杯': 'supercup',
}

# 赛事类型 key（除 summary 外）
COMPETITION_KEYS = ['c2l', 'c1l', 'csl', 'cfa', 'acle', 'supercup']

# 球员名标准化（Excel 数据源错别字修正）
NAME_ALIASES = {'莱昂那多': '莱昂纳多'}
# 数字姓名修正（Excel 中姓名列被误填为号码，按出生日期匹配）
NAME_FIX = {93: '王玉龙'}


def parse_goals(value):
    """解析进球(点球)列，返回 (goals, penalties)"""
    if value is None:
        return None, None
    if isinstance(value, (int, float)):
        return int(value), 0
    s = str(value).strip()
    m = re.match(r'^(\d+)\((\d+)\)$', s)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None, None


def clean_value(value):
    """清洗单元格值，未知/不适用/空值统一为 None，日期转字符串"""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d')
    if isinstance(value, date):
        return value.strftime('%Y-%m-%d')
    if isinstance(value, str):
        s = value.strip()
        if s in ('？', '—', ''):
            return None
        return s
    return value


def normalize_name(value):
    """标准化球员姓名"""
    if isinstance(value, (int, float)):
        return NAME_FIX.get(int(value), str(int(value)))
    name = str(value).strip()
    return NAME_ALIASES.get(name, name)


def read_sheet(ws):
    """读取一个 sheet，返回 {name: {'meta': {...}, 'stats': {...}}}"""
    result = {}
    for row in ws.iter_rows(min_row=3, values_only=True):
        if row is None or len(row) < 2 or row[1] is None:
            continue
        name = normalize_name(row[1])
        if not name:
            continue
        goals, penalties = parse_goals(row[9])
        result[name] = {
            'birthDate': clean_value(row[2]),
            'position': clean_value(row[3]),
            'nationality': clean_value(row[4]),
            'stats': {
                'appearances': clean_value(row[5]),
                'starts': clean_value(row[6]),
                'substitute': clean_value(row[7]),
                'minutes': clean_value(row[8]),
                'goals': goals,
                'penalties': penalties,
                'assists': clean_value(row[10]),
                'yellowCards': clean_value(row[11]),
                'redCards': clean_value(row[12]),
                'goalsConceded': clean_value(row[13]),
                'cleanSheets': clean_value(row[14]),
                'penaltySaves': clean_value(row[15]),
            },
        }
    return result


def main():
    wb = openpyxl.load_workbook(INPUT, data_only=True)
    sheets = {SHEET_MAP.get(ws.title, ws.title): read_sheet(ws) for ws in wb.worksheets}

    summary = sheets['summary']
    players = []
    for name, meta in summary.items():
        player = {
            'name': name,
            'birthDate': meta['birthDate'],
            'position': meta['position'],
            'nationality': meta['nationality'],
            'summary': meta['stats'],
        }
        for key in COMPETITION_KEYS:
            player[key] = sheets[key][name]['stats'] if name in sheets[key] else None
        players.append(player)

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump({'players': players}, f, ensure_ascii=False, indent=2)

    print(f'总球员数: {len(players)}')
    for key in COMPETITION_KEYS:
        non_null = sum(1 for p in players if p[key] is not None)
        print(f'{key}: {non_null} 名球员有数据')


if __name__ == '__main__':
    main()
