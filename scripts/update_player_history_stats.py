#!/usr/bin/env python3
"""
全量重算 player_history_stats.json。

数据来源：
1. 基线：datafile/上海海港球员历史出场汇总(2006-2026).xlsx（通过 convert_player_history.read_sheet 读取）
2. 增量：public/data/team-a/*.json 中所有「已结束」的一线队比赛报告

统计口径（覆盖全部 12 个字段）：
- appearances/starts/substitute：首发 = lineups.{role}.players[]；替补出场 = substitutes[]/bench[] 中带 substitutedAt（或 minutes>0）的球员
- minutes：首发取 lineups 中的 minutes；替补按 90 - substitutedAt 估算
- goals：matchTimeline 中 type=goal（非乌龙）与 type=penalty_goal 两种进球事件
- penalties：进球事件中 goal_type 为 penalty/penalty_goal，或 type=penalty_goal
- assists：进球事件的 player2/assist（乌龙球不计）
- yellowCards/redCards：matchTimeline 中 type=yellow_card/red_card
- goalsConceded：对手常规时间进球数，记到当场门将
- cleanSheets：常规时间不失球，记到当场门将
- penaltySaves：对手罚失点球（penalty_missed/penalty_miss 且 team!=role），记到当场门将

幂等设计：每次从 Excel 基线全量重算，不依赖状态文件，重复运行结果一致。
仅统计上海海港一线队（排除上海海港富盛经开 B 队）。
"""

import sys
import json
import re
from pathlib import Path

import openpyxl

BASE_DIR = Path(r'd:\Workspace\shanghaiport-fc-app')
sys.path.insert(0, str(BASE_DIR / 'scripts'))

from convert_player_history import INPUT as EXCEL_INPUT, SHEET_MAP, COMPETITION_KEYS, read_sheet

DATA_DIR = BASE_DIR / 'public' / 'data'
TEAM_A_DIR = DATA_DIR / 'team-a'
STATS_PATH = DATA_DIR / 'player_history_stats.json'

SHANGHAI_PORT = '上海海港'

# 比赛报告 competition 名称 -> player_history_stats 赛事 key
COMPETITION_KEY_MAP = {
    '中国足球协会超级联赛': 'csl',
    '中超联赛': 'csl',
    '中超': 'csl',
    '中国足球协会杯': 'cfa',
    '足协杯': 'cfa',
    '亚足联冠军精英联赛': 'acle',
    '亚冠精英联赛': 'acle',
    '亚冠精英': 'acle',
    '亚冠联赛': 'acle',
    '中国足球协会乙级联赛': 'c2l',
    '中乙联赛': 'c2l',
    '中乙': 'c2l',
    '中国足球协会甲级联赛': 'c1l',
    '中甲联赛': 'c1l',
    '中甲': 'c1l',
    '中国足球协会超级杯': 'supercup',
    '超级杯': 'supercup',
}

# 报告/标准名 -> player_history_stats.json（Excel）中的名字
ALIAS_MAP = {
    '让克劳德': '克劳德',
    '维塔尔': '马特乌斯·维塔尔',
    '吾米提江': '吾米提江.玉苏普',
}

# 门将位置标识
GK_POSITIONS = ('门将', '守门员', 'GK')

# 普通字段：所有球员都累加
NORMAL_FIELDS = [
    'appearances', 'starts', 'substitute', 'minutes',
    'goals', 'penalties', 'assists', 'yellowCards', 'redCards',
]

# 门将专属字段：仅门将累加，非门将保持 None
GK_FIELDS = ['goalsConceded', 'cleanSheets', 'penaltySaves']


def is_first_team(name):
    """判断是否为上海海港一线队（排除富盛经开 B 队）"""
    if not name:
        return False
    return name == SHANGHAI_PORT or (name.startswith(SHANGHAI_PORT) and '富盛' not in name)


def get_role(home_team, away_team):
    """返回上海海港一线队在本场比赛中的角色（home/away/None）"""
    if is_first_team(home_team):
        return 'home'
    if is_first_team(away_team):
        return 'away'
    return None


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def to_int(value):
    if isinstance(value, int):
        return value
    if value is None:
        return 0
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0


def parse_result(result):
    """解析赛果字符串，支持 '1-1 (点球 4-3)'。
    返回 (常规时间主队分, 常规时间客队分, 点球主队分, 点球客队分)。
    """
    if result is None:
        return None, None, None, None
    s = str(result).strip()
    pen_home = pen_away = None
    m = re.search(r'点球\s*(\d+)\s*[-–]\s*(\d+)', s)
    if m:
        pen_home, pen_away = int(m.group(1)), int(m.group(2))
        s = s.split('(')[0].strip()
    parts = s.split('-')
    if len(parts) != 2:
        return None, None, None, None
    try:
        return int(parts[0]), int(parts[1]), pen_home, pen_away
    except ValueError:
        return None, None, None, None


def new_stats():
    """新建赛事统计字典的默认值"""
    return {
        'appearances': 0,
        'starts': 0,
        'substitute': 0,
        'minutes': 0,
        'goals': 0,
        'penalties': 0,
        'assists': 0,
        'yellowCards': 0,
        'redCards': 0,
        'goalsConceded': None,
        'cleanSheets': None,
        'penaltySaves': None,
    }


def new_player(name, position, nationality):
    """新建球员条目（Excel 里尚不存在的新援）"""
    return {
        'name': name,
        'birthDate': None,
        'position': position,
        'nationality': nationality,
        'summary': new_stats(),
        **{k: None for k in COMPETITION_KEYS},
    }


def is_goalkeeper(player):
    return player.get('position') in GK_POSITIONS


def build_baseline():
    """从 Excel 读取基线球员列表（结构与 convert_player_history 输出一致）"""
    wb = openpyxl.load_workbook(EXCEL_INPUT, data_only=True)
    sheets = {SHEET_MAP.get(ws.title, ws.title): read_sheet(ws) for ws in wb.worksheets}
    summary = sheets['summary']

    players = []
    for name, meta in summary.items():
        player = {
            'name': name,
            'birthDate': meta['birthDate'],
            'position': meta['position'],
            'nationality': meta['nationality'],
            'summary': dict(meta['stats']),
        }
        for key in COMPETITION_KEYS:
            player[key] = dict(sheets[key][name]['stats']) if name in sheets[key] else None
        players.append(player)
    return players


def resolve_player(name, player_map, players, position=None, nationality=None):
    """按 精确 -> 别名 -> 新建 的顺序返回球员条目"""
    if name in player_map:
        return player_map[name]
    std = ALIAS_MAP.get(name)
    if std and std in player_map:
        return player_map[std]
    player = new_player(name, position, nationality)
    player_map[name] = player
    players.append(player)
    return player


def add_field(player, comp_key, field, delta):
    """对某球员的 summary 和指定赛事 key 累加普通字段"""
    s = player.setdefault('summary', new_stats())
    s[field] = to_int(s.get(field)) + delta

    if player.get(comp_key) is None:
        player[comp_key] = new_stats()
    c = player[comp_key]
    c[field] = to_int(c.get(field)) + delta


def add_gk_field(player, comp_key, field, delta):
    """对门将专属字段累加（非门将保持 None）"""
    if not is_goalkeeper(player):
        return
    s = player.setdefault('summary', new_stats())
    s[field] = to_int(s.get(field)) + delta

    if player.get(comp_key) is None:
        player[comp_key] = new_stats()
    c = player[comp_key]
    c[field] = to_int(c.get(field)) + delta


def get_goalkeeper(report, role):
    """返回当场上海海港首发门将（优先）或替补出场门将"""
    team = (report.get('lineups', {}) or {}).get(role, {}) or {}
    for p in team.get('players', []):
        if p.get('position') in GK_POSITIONS and p.get('name'):
            return p.get('name')
    for p in (team.get('substitutes', []) or team.get('bench', [])):
        if p.get('position') in GK_POSITIONS and p.get('name'):
            if p.get('substitutedAt') is not None or (isinstance(p.get('minutes'), (int, float)) and p.get('minutes') > 0):
                return p.get('name')
    return None


def count_conceded(report, role):
    """返回上海海港常规时间失球数（点球大战不计）"""
    result = report.get('match', {}).get('result', '')
    home_score, away_score, _pen_home, _pen_away = parse_result(result)
    if home_score is None or away_score is None:
        return 0
    return away_score if role == 'home' else home_score


def count_penalty_saves(report, role):
    """返回上海海港门将扑出（对手罚失）点球数"""
    count = 0
    for e in report.get('matchTimeline', []):
        if e.get('type') in ('penalty_missed', 'penalty_miss') and e.get('team') != role:
            count += 1
    return count


def process_report(report, role, comp_key, player_map, players):
    """累加一场比赛对全部球员、全部字段的增量"""
    team = (report.get('lineups', {}) or {}).get(role, {}) or {}

    # 1. 首发球员：starts + appearances + minutes
    for p in team.get('players', []):
        name = p.get('name')
        if not name:
            continue
        player = resolve_player(name, player_map, players, p.get('position'), p.get('nationality'))
        add_field(player, comp_key, 'starts', 1)
        add_field(player, comp_key, 'appearances', 1)
        minutes = to_int(p.get('minutes'))
        if minutes > 0:
            add_field(player, comp_key, 'minutes', minutes)

    # 2. 替补出场：substitute + appearances + minutes（估算）
    for p in (team.get('substitutes', []) or team.get('bench', [])):
        name = p.get('name')
        if not name:
            continue
        sub_at = p.get('substitutedAt')
        has_minutes = isinstance(p.get('minutes'), (int, float)) and p.get('minutes') > 0
        if sub_at is None and not has_minutes:
            continue
        player = resolve_player(name, player_map, players, p.get('position'), p.get('nationality'))
        add_field(player, comp_key, 'substitute', 1)
        add_field(player, comp_key, 'appearances', 1)
        if has_minutes:
            add_field(player, comp_key, 'minutes', to_int(p.get('minutes')))
        elif sub_at is not None:
            sa = to_int(sub_at)
            # 加时赛（substitutedAt > 90）按 120 分钟估算，常规时间按 90 分钟估算
            total = 120 if sa > 90 else 90
            add_field(player, comp_key, 'minutes', max(0, total - sa))

    # 3. 事件：进球/助攻/点球/黄牌/红牌
    for e in report.get('matchTimeline', []):
        if e.get('team') != role:
            continue
        etype = e.get('type')

        if etype == 'goal':
            is_own = e.get('goal_type') == 'own_goal' or e.get('isOwnGoal')
            if is_own:
                continue
            scorer = e.get('player')
            if scorer:
                player = resolve_player(scorer, player_map, players)
                add_field(player, comp_key, 'goals', 1)
                if e.get('goal_type') in ('penalty', 'penalty_goal'):
                    add_field(player, comp_key, 'penalties', 1)
                assist = e.get('player2') or e.get('assist')
                if assist:
                    aplayer = resolve_player(assist, player_map, players)
                    add_field(aplayer, comp_key, 'assists', 1)
        elif etype == 'penalty_goal':
            scorer = e.get('player')
            if scorer:
                player = resolve_player(scorer, player_map, players)
                add_field(player, comp_key, 'goals', 1)
                add_field(player, comp_key, 'penalties', 1)
        elif etype == 'yellow_card':
            pname = e.get('player')
            if pname:
                player = resolve_player(pname, player_map, players)
                add_field(player, comp_key, 'yellowCards', 1)
        elif etype == 'red_card':
            pname = e.get('player')
            if pname:
                player = resolve_player(pname, player_map, players)
                add_field(player, comp_key, 'redCards', 1)

    # 4. 门将字段
    gk_name = get_goalkeeper(report, role)
    if gk_name:
        gk = resolve_player(gk_name, player_map, players)
        conceded = count_conceded(report, role)
        if conceded > 0:
            add_gk_field(gk, comp_key, 'goalsConceded', conceded)
        else:
            add_gk_field(gk, comp_key, 'cleanSheets', 1)
        saves = count_penalty_saves(report, role)
        if saves > 0:
            add_gk_field(gk, comp_key, 'penaltySaves', saves)


def main():
    players = build_baseline()
    player_map = {p['name']: p for p in players}

    report_files = sorted(p for p in TEAM_A_DIR.glob('*.json') if '-MO' not in p.stem)

    processed = 0
    skipped_competition = []
    skipped_no_role = []

    for path in report_files:
        report = load_json(path)
        m = report.get('match', {})
        if m.get('status') != '已结束':
            continue

        home = m.get('homeTeam', '')
        away = m.get('awayTeam', '')
        role = get_role(home, away)
        if not role:
            skipped_no_role.append(path.name)
            continue

        comp_key = COMPETITION_KEY_MAP.get(m.get('competition', ''), '')
        if comp_key not in COMPETITION_KEYS:
            skipped_competition.append(f"{path.name} -> {m.get('competition', '')}")
            continue

        process_report(report, role, comp_key, player_map, players)
        processed += 1

    # 清理新球员中可能残留的 None 字段值（保持与 Excel 基线风格一致）
    for p in players:
        for comp_key in ['summary'] + COMPETITION_KEYS:
            stats = p.get(comp_key)
            if not isinstance(stats, dict):
                continue
            for field in NORMAL_FIELDS:
                if stats.get(field) is None:
                    stats[field] = 0

    with open(STATS_PATH, 'w', encoding='utf-8') as f:
        json.dump({'players': players}, f, ensure_ascii=False, indent=2)

    print(f"处理已结束一线队比赛: {processed} 场")
    print(f"球员总数: {len(players)}")
    if skipped_competition:
        print("跳过未知赛事类型:")
        for s in skipped_competition:
            print(f"  - {s}")
    if skipped_no_role:
        print("跳过无法判定一线队角色:")
        for s in skipped_no_role:
            print(f"  - {s}")


if __name__ == '__main__':
    main()
