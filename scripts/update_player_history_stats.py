#!/usr/bin/env python3
"""
根据 team-a 目录下的比赛报告，更新 player_history_stats.json 中球员的出场/首发/替补统计。

统计口径：
- 首发（starts）：lineups.{role}.players[] 中的球员
- 替补出场（substitute）：lineups.{role}.substitutes[]（或 bench[]）中带 substitutedAt 字段的球员
- 出场（appearances）= 首发 + 替补出场

名字匹配：
- 优先精确匹配 player_history_stats.json 中的名字
- 其次走 ALIAS_MAP（报告/标准名 -> Excel 文件名）
- 都不匹配则自动新建球员条目（position/nationality 取自比赛报告 lineups）

幂等设计：
- 使用 scripts/player_history_sync_state.json 记录已处理的比赛（按「日期|主队|客队」去重），
  重复运行不会重复统计。

用于 match-result-updater 工作流，每更新一场比赛后同步球员出场数据。
仅统计上海海港一线队（排除上海海港富盛经开 B 队）。

注意：本脚本只更新 appearances/starts/substitute 三个字段，不改动 minutes/goals/assists 等字段。
"""

import json
from pathlib import Path

BASE_DIR = Path(r'd:\Workspace\shanghaiport-fc-app')
DATA_DIR = BASE_DIR / 'public' / 'data'
TEAM_A_DIR = DATA_DIR / 'team-a'
STATS_PATH = DATA_DIR / 'player_history_stats.json'
STATE_PATH = BASE_DIR / 'scripts' / 'player_history_sync_state.json'

SHANGHAI_PORT = '上海海港'

# player_history_stats.json 中各赛事字段（除 summary 外）
COMPETITION_KEYS = ['c2l', 'c1l', 'csl', 'cfa', 'acle', 'supercup']

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
    '亚冠联赛': 'acle',  # 旧亚冠（含资格赛）
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


def load_state():
    if STATE_PATH.exists():
        data = load_json(STATE_PATH)
        return set(data.get('processed_matches', []))
    return set()


def save_state(processed):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_PATH, 'w', encoding='utf-8') as f:
        json.dump({'processed_matches': sorted(processed)}, f, ensure_ascii=False, indent=2)


def new_stats():
    """新建赛事统计字典的默认值（只关心出场字段，其余置空/0）"""
    return {
        'appearances': 0,
        'starts': 0,
        'substitute': 0,
        'minutes': None,
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
    player = {
        'name': name,
        'birthDate': None,
        'position': position,
        'nationality': nationality,
        'summary': new_stats(),
    }
    for key in COMPETITION_KEYS:
        player[key] = None
    return player


def to_int(value):
    if isinstance(value, int):
        return value
    if value is None:
        return 0
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0


def extract_appearances(report, role):
    """返回 (首发名单, 替补出场名单)，每项为 dict(name/position/nationality)"""
    team = (report.get('lineups', {}) or {}).get(role, {}) or {}

    starters = []
    for p in team.get('players', []):
        name = p.get('name')
        if name:
            starters.append({
                'name': name,
                'position': p.get('position'),
                'nationality': p.get('nationality'),
            })

    subs_on = []
    for p in (team.get('substitutes', []) or team.get('bench', [])):
        name = p.get('name')
        if not name:
            continue
        # 替补出场：带 substitutedAt 字段；兼容带 minutes 且 >0 的情况
        if p.get('substitutedAt') is not None or (isinstance(p.get('minutes'), (int, float)) and p.get('minutes') > 0):
            subs_on.append({
                'name': name,
                'position': p.get('position'),
                'nationality': p.get('nationality'),
            })

    return starters, subs_on


def resolve_player(name, player_map, players, meta):
    """按 精确 -> 别名 -> 新建 的顺序返回球员条目"""
    if name in player_map:
        return player_map[name]
    std = ALIAS_MAP.get(name)
    if std and std in player_map:
        return player_map[std]
    player = new_player(name, meta.get('position'), meta.get('nationality'))
    player_map[name] = player
    players.append(player)
    return player


def increment(player, comp_key, is_start):
    """对某球员的 summary 和指定赛事 key 累加一次出场（首发或替补）"""
    # 汇总
    summary = player.setdefault('summary', new_stats())
    summary['appearances'] = to_int(summary.get('appearances')) + 1
    if is_start:
        summary['starts'] = to_int(summary.get('starts')) + 1
    else:
        summary['substitute'] = to_int(summary.get('substitute')) + 1

    # 分赛事
    if player.get(comp_key) is None:
        player[comp_key] = new_stats()
    comp = player[comp_key]
    comp['appearances'] = to_int(comp.get('appearances')) + 1
    if is_start:
        comp['starts'] = to_int(comp.get('starts')) + 1
    else:
        comp['substitute'] = to_int(comp.get('substitute')) + 1


def main():
    data = load_json(STATS_PATH)
    players = data['players']
    player_map = {p['name']: p for p in players}

    processed = load_state()

    report_files = sorted(p for p in TEAM_A_DIR.glob('*.json') if '-MO' not in p.stem)

    new_processed = 0
    updated_players = set()
    warnings = []

    for path in report_files:
        report = load_json(path)
        m = report.get('match', {})
        if m.get('status') != '已结束':
            continue

        home = m.get('homeTeam', '')
        away = m.get('awayTeam', '')
        role = get_role(home, away)
        if not role:
            continue

        match_key = f"{m.get('date', '')}|{home}|{away}"
        if match_key in processed:
            continue

        comp_key = COMPETITION_KEY_MAP.get(m.get('competition', ''), '')
        if comp_key not in COMPETITION_KEYS:
            warnings.append(f"跳过未知赛事类型: {path.name} -> {m.get('competition', '')}")
            continue

        starters, subs_on = extract_appearances(report, role)

        for meta in starters:
            player = resolve_player(meta['name'], player_map, players, meta)
            increment(player, comp_key, is_start=True)
            updated_players.add(meta['name'])

        for meta in subs_on:
            player = resolve_player(meta['name'], player_map, players, meta)
            increment(player, comp_key, is_start=False)
            updated_players.add(meta['name'])

        processed.add(match_key)
        new_processed += 1

    save_state(processed)

    if updated_players:
        with open(STATS_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"新增处理比赛: {new_processed}")
    print(f"更新球员数: {len(updated_players)}")

    for w in warnings:
        print(f"警告: {w}")


if __name__ == '__main__':
    main()
