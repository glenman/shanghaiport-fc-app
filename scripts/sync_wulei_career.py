# -*- coding: utf-8 -*-
"""武磊国家队+留洋数据补充（幂等，可重跑）

数据源: datafile/武磊职业生涯三百球.xlsx
- 进球明细 sheet: 300 球逐条 -> 国家队 36 球 + 留洋 16 球追加到 goal_details.json
- 国家队 sheet: 101 场 A 级赛 -> stats 分项 + appearance 逐场明细
- 留洋 sheet: 126 场西班牙人 -> stats 分项 + appearance 逐场明细
"""
import json
import re
from datetime import datetime, timedelta
import openpyxl

XLSX = 'datafile/武磊职业生涯三百球.xlsx'
GOAL_PATH = 'public/data/goal_details.json'
STATS_PATH = 'public/data/player_history_stats.json'
APP_PATH = 'public/data/player_appearance_details.json'
GH_PATH = 'public/data/goal_history.json'

NT_TYPES = ('世界杯预选赛', '友谊赛', '东亚杯', '亚洲杯', '亚洲杯预选赛', '国家队')
ABROAD_KEEP = ('西甲联赛', '西班牙国王杯', '欧联杯', '西乙联赛')

wb = openpyxl.load_workbook(XLSX, data_only=True)


def xldate(v):
    if isinstance(v, int):
        return (datetime(1899, 12, 30) + timedelta(days=v)).strftime('%Y-%m-%d')
    if isinstance(v, datetime):
        return v.strftime('%Y-%m-%d')
    return str(v).replace('.', '-')


def parse_date(v):
    if isinstance(v, datetime):
        return v.strftime('%Y-%m-%d')
    s = str(v).strip().replace('.', '-')
    return f'{s[0:4]}-{s[4:6]}-{s[6:8]}' if re.fullmatch(r'\d{8}', s) else s


def parse_goal(v):
    """'1(1)' -> (1,1)；2 -> (2,0)；'？' -> (0,0)"""
    s = str(v).strip() if v is not None else ''
    m = re.fullmatch(r'(\d+)(?:\((\d+)\))?', s)
    if not m:
        return 0, 0
    return int(m.group(1)), int(m.group(2) or 0)


def norm_time(t):
    s = str(t).strip().replace('’', "'").replace('`', "'")
    return s if s.endswith("'") else s + "'"


def num(v):
    return v if isinstance(v, (int, float)) else 0


# ---------- 1) 进球明细 -> goal_details ----------
ws = wb['进球明细']
new_goals = []
skipped = []
for row in ws.iter_rows(min_row=2, values_only=True):
    if not row[0]:
        continue
    cat = str(row[1]).strip()
    is_nt = cat in NT_TYPES
    is_abroad = cat in ABROAD_KEEP
    if not is_nt and not is_abroad:
        continue
    if row[6] is None:
        # 明细行缺比赛信息（日期/比分等），跳过 goal_details 收录
        skipped.append((row[0], cat, row[2]))
        continue
    date = xldate(row[6])
    scorer = str(row[3]).strip()
    entry = {
        'season': date[:4],
        'match_type': '国家队' if is_nt else cat,
        'goal_time': norm_time(row[2]),
        'goal_player': '武磊(PK)' if 'PK' in scorer else '武磊',
        'assist_player': str(row[4]).strip() or '—',
        'create_player': str(row[5]).strip() or '—',
        'match_date_code': int(date.replace('-', '')),
        'match_name': str(row[7]).strip(),
        'home_team': str(row[8]).strip(),
        'home_score': num(row[9]),
        'away_score': num(row[10]),
        'away_team': str(row[11]).strip(),
        'match_result': str(row[12]).strip() or '—',
        'remark': str(row[13]).strip() if row[13] else '—',
    }
    new_goals.append(entry)

nt_count = sum(1 for g in new_goals if g['match_type'] == '国家队')
print(f'明细提取: 待追加 {len(new_goals)} 球 (国家队 {nt_count} / 留洋 {len(new_goals) - nt_count}); '
      f'跳过缺比赛信息 {len(skipped)} 球: {skipped}')
print('点球标记(明细 PK 字样):', sum(1 for g in new_goals if g['goal_player'] == '武磊(PK)'), '球')

with open(GOAL_PATH, encoding='utf-8') as f:
    gd = json.load(f)
# 幂等: 先删除此前脚本追加的（id > 原 max 或 match_type 非俱乐部）
CLUB = ('中超', '中甲', '中乙', '足协杯', '亚冠', '超级杯')
removed = [g for g in gd if not any(t in g['match_type'] for t in CLUB)]
gd = [g for g in gd if any(t in g['match_type'] for t in CLUB)]
next_id = max(g['id'] for g in gd) + 1
for g in new_goals:
    g['id'] = next_id
    next_id += 1
gd.extend(new_goals)
print(f'goal_details: 移除旧追加 {len(removed)} 条, 新增 {len(new_goals)} 条, 总数 {len(gd)}')
with open(GOAL_PATH, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(gd, f, ensure_ascii=False, indent=2)
    f.write('\n')

# ---------- 2) 国家队/留洋 出场汇总 ----------
def load_rows(sheet):
    ws = wb[sheet]
    out = []
    for row in ws.iter_rows(min_row=3, values_only=True):
        if not row[0] or str(row[0]).strip() in ('序号', '合计', '赛事类别'):
            continue
        out.append(row)
    return out

nt_rows = load_rows('国家队')
ab_rows = load_rows('留洋')
print(f'国家队 {len(nt_rows)} 场, 留洋 {len(ab_rows)} 场')


def make_appearances(rows, is_nt):
    apps = []
    agg = dict(appearances=0, starts=0, substitute=0, minutes=0, goals=0,
               penaltyGoals=0, assists=0, yellowCards=0, redCards=0)
    for r in rows:
        if is_nt:
            date, comp, opp = parse_date(r[2]), str(r[1]).strip(), str(r[3]).strip()
            g, p = parse_goal(r[10])
            a, yc, rc, mins = num(r[11]), num(r[13]), num(r[14]), num(r[9])
        else:
            date, comp, opp = parse_date(r[2]), str(r[0]).strip(), str(r[3]).strip()
            g, p = num(r[10]), 0
            a, yc, rc, mins = num(r[11]), num(r[13]), num(r[14]), num(r[9])
        started = num(r[7]) == 1
        status = '首发' if started else '替补'
        entry = {'date': date, 'competition': comp, 'opponent': opp,
                 'score': f'{num(r[4])}-{num(r[5])}', 'status': status, 'minutes': mins}
        if g:
            entry['goals'] = g
            if p:
                entry['penaltyGoals'] = p
        if a:
            entry['assists'] = a
        if yc:
            entry['yellowCards'] = yc
        if rc:
            entry['redCards'] = rc
        apps.append(entry)
        agg['appearances'] += 1
        agg['starts'] += 1 if started else 0
        agg['substitute'] += 0 if started else 1
        agg['minutes'] += mins
        agg['goals'] += g
        agg['penaltyGoals'] += p
        agg['assists'] += a
        agg['yellowCards'] += yc
        agg['redCards'] += rc
    return apps, agg

nt_apps, nt_agg = make_appearances(nt_rows, True)
ab_apps, ab_agg = make_appearances(ab_rows, False)
print('国家队汇总:', json.dumps(nt_agg, ensure_ascii=False))
print('留洋汇总:', json.dumps(ab_agg, ensure_ascii=False))


def stat_block(agg):
    return {
        'appearances': agg['appearances'], 'starts': agg['starts'], 'substitute': agg['substitute'],
        'minutes': agg['minutes'], 'goals': agg['goals'], 'penalties': agg['penaltyGoals'],
        'assists': agg['assists'], 'yellowCards': agg['yellowCards'], 'redCards': agg['redCards'],
        'goalsConceded': None, 'cleanSheets': None, 'penaltySaves': None,
    }


# ---------- 3) player_history_stats ----------
with open(STATS_PATH, encoding='utf-8') as f:
    stats = json.load(f)
players = stats if isinstance(stats, list) else stats.get('players', [])
wu = next(p for p in players if p['name'] == '武磊')
wu['nationalTeam'] = stat_block(nt_agg)
wu['espanyol'] = stat_block(ab_agg)
with open(STATS_PATH, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(stats, f, ensure_ascii=False, indent=2)
    f.write('\n')
print('player_history_stats: 武磊 +nationalTeam/+espanyol')

# ---------- 4) player_appearance_details ----------
with open(APP_PATH, encoding='utf-8') as f:
    app = json.load(f)
wud = next(p for p in app['players'] if p['name'] == '武磊')
wud['otherCareer'] = {
    'nationalTeam': {
        'team': '中国国家男子足球队',
        'period': '2010-2026',
        'summary': nt_agg,
        'appearances': nt_apps,
    },
    'espanyol': {
        'team': '皇家西班牙人',
        'period': '2019-2022',
        'summary': ab_agg,
        'appearances': ab_apps,
    },
}
with open(APP_PATH, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(app, f, ensure_ascii=False, indent=2)
    f.write('\n')
print('player_appearance_details: 武磊 +otherCareer(国家队/西班牙人)')

# ---------- 5) goal_history ----------
with open(GH_PATH, encoding='utf-8') as f:
    gh = json.load(f)
wu_gh = next(x for x in gh if x['球员'] == '武磊')
wu_gh['国家队进球'] = nt_agg['goals']
wu_gh['留洋进球(西班牙人)'] = ab_agg['goals']
with open(GH_PATH, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(gh, f, ensure_ascii=False, indent=2)
    f.write('\n')
print('goal_history: 武磊行 +国家队进球/+留洋进球')
