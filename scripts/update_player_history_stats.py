#!/usr/bin/env python3
"""
更新 player_history_stats.json（默认增量模式，--full 为全量重算）。

【增量模式（默认）】
- 基线：当前 player_history_stats.json 文件本身（基线留存见 datafile/baseline-<日期>/）
- 只处理「文件日期 > scripts/update_state.json 的 baselineDate 且已结束且未在 processed 清单」的
  team-a 新报告，逐场累加，绝不重算/覆盖既有数据
- 已处理文件记录于 update_state.json 的 processed 清单，防止重复累计

【全量重算 --full（仅数据修复用，会覆盖文件）】
- Excel 基线 + 全部 team-a 已结束报告重算；重算后自动恢复 BIRTH_FIX 生日修正与 short_name

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
    # 历史名单错别字（2007 中乙名单“柏佳俊”，实名柏佳骏，生日相同）
    '柏佳俊': '柏佳骏',
    # 报告/名单简写 -> 全名
    '阿布拉汗': '阿布拉汗·哈力克',
}

# 已人工确认的生日修正（覆盖 Excel 基线中的笔误）
BIRTH_FIX = {
    '张俊杰': '2006-10-15',
    '米格尔·坎波斯': '1996-08-19',
    '豪梅·格劳': '1997-05-05',
    '曹赟定': '1989-11-22',
    '明天': '1995-04-08',
    '李小龙': '1989-09-20',
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

# 基线 Excel 已包含以下比赛，team-a 中重复，跳过避免重复累计
EXCLUDE_FILENAME_PATTERNS = ['超级杯', '中超-第1轮']


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


def apply_known_fixes(players):
    """重算后恢复人工确认的修正：
    1) BIRTH_FIX 生日覆盖（Excel 基线笔误）
    2) 保留现有 stats 文件中的 short_name（外援短名映射）
    """
    prev_short = {}
    if STATS_PATH.exists():
        try:
            with open(STATS_PATH, 'r', encoding='utf-8') as f:
                prev = json.load(f)
            prev_short = {p['name']: p.get('short_name') for p in prev.get('players', [])
                          if p.get('short_name')}
        except Exception:
            prev_short = {}
    for p in players:
        if p['name'] in BIRTH_FIX:
            p['birthDate'] = BIRTH_FIX[p['name']]
        if p['name'] in prev_short:
            fixed = {'name': p['name'], 'short_name': prev_short[p['name']]}
            fixed.update({k: v for k, v in p.items() if k != 'name'})
            p.clear()
            p.update(fixed)


def main(full=False):
    import update_state

    baseline = update_state.init_baseline()
    done = update_state.get_processed('update_player_history_stats.py')

    if full:
        # 全量重算（仅数据修复用）：Excel 基线 + 全部 team-a 报告（排除与基线重复的比赛）
        players = build_baseline()
        player_map = {p['name']: p for p in players}
        todo = [p for p in sorted(TEAM_A_DIR.glob('*.json'), key=lambda x: x.name)
                if '-MO' not in p.stem
                and not any(pat in p.name for pat in EXCLUDE_FILENAME_PATTERNS)]
        todo_names = set()
    else:
        # 增量模式（默认）：以现有 stats 文件为基线，只处理基线日之后且未处理过的新报告
        if not STATS_PATH.exists():
            print('缺少 player_history_stats.json，请先执行 --full 全量重算')
            return
        with open(STATS_PATH, 'r', encoding='utf-8') as f:
            players = json.load(f)['players']
        player_map = {p['name']: p for p in players}
        todo = []
        todo_names = set()
        for p in sorted(TEAM_A_DIR.glob('*.json'), key=lambda x: x.name):
            if '-MO' in p.stem or p.name in done:
                continue
            if p.stem[:10] <= baseline:
                continue
            todo.append(p)
            todo_names.add(p.name)
        if not todo:
            print(f'增量模式：基线日 {baseline} 之后无新比赛，跳过（如需重建请加 --full）')
            update_state.record_run('update_player_history_stats.py')
            return
        print(f'增量模式：基线日 {baseline}，待处理新报告 {len(todo)} 个')

    processed = 0
    skipped_competition = []
    skipped_no_role = []

    for path in todo:
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
        if todo_names:
            todo_names.discard(path.name)  # 未真正累计的（跳过）不入账
    # 注：todo_names 在循环中移除成功处理的文件；跳过的文件不记入 processed 清单，
    # 以便其状态修正（如报告更新为已结束）后可再次被处理。

    # 清理新球员中可能残留的 None 字段值（保持与 Excel 基线风格一致）
    for p in players:
        for comp_key in ['summary'] + COMPETITION_KEYS:
            stats = p.get(comp_key)
            if not isinstance(stats, dict):
                continue
            for field in NORMAL_FIELDS:
                if stats.get(field) is None:
                    stats[field] = 0

    apply_known_fixes(players)

    with open(STATS_PATH, 'w', encoding='utf-8') as f:
        json.dump({'players': players}, f, ensure_ascii=False, indent=2)

    handled = [p.name for p in todo if p.name not in todo_names]
    lm = update_state.record_run('update_player_history_stats.py', processed_files=handled)
    if lm:
        print(f"状态已记录 (scripts/update_state.json): 更新至 {lm['date']} {lm['competition']} "
              f"{lm['round']} ({lm.get('matchId')})")

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
    import sys
    main(full='--full' in sys.argv)
