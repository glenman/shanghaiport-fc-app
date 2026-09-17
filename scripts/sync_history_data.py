#!/usr/bin/env python3
"""
将 team-a 目录下的比赛报告同步到：
  - goal_details.json   （上海海港一线队的每一条进球记录）
  - history_schedule.json（每场比赛的赛程/赛果/教练/裁判/进球者等）

幂等设计：按 (日期, 主队, 客队) 与 (日期码, 进球球员, 进球时间) 去重，可重复运行。
用于 match-result-updater 工作流，每更新一场比赛后同步留存。
"""
import json
import re
from pathlib import Path

BASE_DIR = Path(r'd:\Workspace\shanghaiport-fc-app\public\data')
TEAM_A_DIR = BASE_DIR / 'team-a'
GOAL_DETAILS_PATH = BASE_DIR / 'goal_details.json'
HISTORY_SCHEDULE_PATH = BASE_DIR / 'history_schedule.json'

SHANGHAI_PORT = '上海海港'

# competition 全称 -> match_type 简称
COMPETITION_MAP = {
    '中国足球协会超级联赛': '中超联赛',
    '中国足球协会杯': '足协杯',
    '亚足联冠军精英联赛': '亚冠精英联赛',
    '中国足球协会乙级联赛': '中乙联赛',
    '中国足球协会甲级联赛': '中甲联赛',
    '中国足球协会超级杯': '超级杯',
}


def is_shanghai_port_team(name):
    """判断是否为上海海港一线队（排除富盛经开 B 队）"""
    return name == SHANGHAI_PORT or (name.startswith(SHANGHAI_PORT) and '富盛' not in name)


def parse_result(result):
    """解析赛果字符串，支持 '1-1 (点球 4-3)' 格式。
    返回 (常规时间主队分, 常规时间客队分, 点球主队分, 点球客队分)。
    无点球时点球分返回 None；无法解析时全部返回 None。
    """
    if result is None:
        return None, None, None, None
    s = str(result).strip()
    pen_home = pen_away = None
    m = re.search(r'点球\s*(\d+)\s*-\s*(\d+)', s)
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


def compute_win_loss(is_home, home_score, away_score, pen_home=None, pen_away=None):
    sp = home_score if is_home else away_score
    opp = away_score if is_home else home_score
    # 杯赛淘汰赛点球大战决定胜负
    if pen_home is not None and pen_away is not None:
        sp_pen = pen_home if is_home else pen_away
        opp_pen = pen_away if is_home else pen_home
        if sp_pen > opp_pen:
            return '胜'
        if sp_pen < opp_pen:
            return '负'
        return '平'
    if sp is None or opp is None:
        return '—'
    if sp > opp:
        return '胜'
    if sp < opp:
        return '负'
    return '平'


def format_goal_time(minute, minute_extra):
    extra = f"+{minute_extra}" if minute_extra else ""
    return f"{minute}{extra}'"


def goal_marker(goal_type, is_own_goal, etype=''):
    if is_own_goal or goal_type == 'own_goal':
        return '(OG)'
    if etype == 'penalty_goal' or goal_type in ('penalty', 'penalty_goal'):
        return '(PK)'
    return ''


def extract_goal_events(report):
    events = report.get('matchTimeline') or report.get('highlights') or []
    return [e for e in events if e.get('type') in ('goal', 'penalty_goal')]


def build_history_entry(report):
    m = report.get('match', {})
    home_team = m.get('homeTeam', '')
    away_team = m.get('awayTeam', '')
    is_home = is_shanghai_port_team(home_team)
    is_away = is_shanghai_port_team(away_team)
    if not is_home and not is_away:
        return None

    home_score, away_score, pen_home, pen_away = parse_result(m.get('result', ''))
    match_type = COMPETITION_MAP.get(m.get('competition', ''), '其他赛事')
    round_ = m.get('round', '')

    scorers = {'home': [], 'away': []}
    for e in extract_goal_events(report):
        team = e.get('team', '')
        player = e.get('player', '')
        if not player:
            continue
        marker = goal_marker(e.get('goal_type', ''), e.get('isOwnGoal', False), e.get('type', ''))
        if team == 'home':
            scorers['home'].append(player + marker)
        elif team == 'away':
            scorers['away'].append(player + marker)

    attendance = m.get('attendance')
    if attendance is not None:
        try:
            attendance = int(attendance)
        except (ValueError, TypeError):
            pass

    entry = {
        'season': m.get('season', ''),
        'match_type': match_type,
        'match_name': f"{match_type}{round_}",
        'round': round_,
        'date': m.get('date', ''),
        'home_team': home_team,
        'away_team': away_team,
        'result': m.get('result', ''),
        'win_loss': compute_win_loss(is_home, home_score, away_score, pen_home, pen_away),
        'venue': m.get('venue'),
        'referee': (report.get('officials', {}) or {}).get('referee') or m.get('referee'),
        'home_coach': (report.get('lineups', {}).get('home', {}) or {}).get('manager'),
        'away_coach': (report.get('lineups', {}).get('away', {}) or {}).get('manager'),
        'kickoff_time': m.get('time'),
        'city': m.get('city'),
        'attendance': attendance,
        'scorers': scorers,
    }
    return {k: v for k, v in entry.items() if v is not None}


def build_goal_entries(report):
    m = report.get('match', {})
    home_team = m.get('homeTeam', '')
    away_team = m.get('awayTeam', '')
    is_home = is_shanghai_port_team(home_team)
    is_away = is_shanghai_port_team(away_team)
    if not is_home and not is_away:
        return []

    home_score, away_score, pen_home, pen_away = parse_result(m.get('result', ''))
    match_type = COMPETITION_MAP.get(m.get('competition', ''), '其他赛事')
    round_ = m.get('round', '')
    match_date_code = int(str(m.get('date', '')).replace('-', ''))
    match_result = compute_win_loss(is_home, home_score, away_score, pen_home, pen_away)

    sp_team = 'home' if is_home else 'away'
    goals = []
    for e in extract_goal_events(report):
        if e.get('team') != sp_team:
            continue
        player = e.get('player', '')
        if not player:
            continue
        marker = goal_marker(e.get('goal_type', ''), e.get('isOwnGoal', False), e.get('type', ''))
        assist = e.get('player2') or e.get('assist') or '—'
        if marker == '(OG)':
            assist = '—'  # 乌龙球不计助攻

        goals.append({
            'season': m.get('season', ''),
            'match_type': match_type,
            'goal_time': format_goal_time(e.get('minute', 0), e.get('minute_extra', 0)),
            'goal_player': player + marker,
            'assist_player': assist,
            'create_player': '—',
            'match_date_code': match_date_code,
            'match_name': f"{match_type}{round_}",
            'home_team': home_team,
            'home_score': home_score,
            'away_score': away_score,
            'away_team': away_team,
            'match_result': match_result,
            'remark': '—',
        })
    return goals


def main():
    with open(GOAL_DETAILS_PATH, 'r', encoding='utf-8') as f:
        goal_details = json.load(f)
    with open(HISTORY_SCHEDULE_PATH, 'r', encoding='utf-8') as f:
        history_schedule = json.load(f)

    existing_sched = {(m.get('date'), m.get('home_team'), m.get('away_team')) for m in history_schedule}
    existing_goals = {(g.get('match_date_code'), g.get('goal_player'), g.get('goal_time')) for g in goal_details}
    max_goal_id = max((g.get('id', 0) for g in goal_details), default=0)

    report_files = sorted(p for p in TEAM_A_DIR.glob('*.json') if '-MO' not in p.stem)

    new_sched = 0
    new_goals = 0

    for path in report_files:
        with open(path, 'r', encoding='utf-8') as f:
            report = json.load(f)

        entry = build_history_entry(report)
        if entry:
            key = (entry['date'], entry['home_team'], entry['away_team'])
            if key not in existing_sched:
                history_schedule.append(entry)
                existing_sched.add(key)
                new_sched += 1

        for g in build_goal_entries(report):
            key = (g['match_date_code'], g['goal_player'], g['goal_time'])
            if key not in existing_goals:
                max_goal_id += 1
                g['id'] = max_goal_id
                goal_details.append(g)
                existing_goals.add(key)
                new_goals += 1

    history_schedule.sort(key=lambda m: (m.get('date', ''), m.get('match_name', ''), m.get('home_team', '')))

    with open(HISTORY_SCHEDULE_PATH, 'w', encoding='utf-8') as f:
        json.dump(history_schedule, f, ensure_ascii=False, indent=2)
    with open(GOAL_DETAILS_PATH, 'w', encoding='utf-8') as f:
        json.dump(goal_details, f, ensure_ascii=False, indent=2)

    print(f'新增比赛记录（history_schedule）: {new_sched}')
    print(f'新增进球记录（goal_details）: {new_goals}')
    print(f'goal_details 最新 ID: {max_goal_id}')


if __name__ == '__main__':
    main()
