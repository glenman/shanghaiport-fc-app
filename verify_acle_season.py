# -*- coding: utf-8 -*-
"""核对跨年亚冠比赛的赛季归属一致性（一次性校验脚本，非工程文件）"""
import json
from pathlib import Path

DATA = Path('public/data')
issues = []

# ===== 1. history_schedule: 亚冠比赛 season vs 日期年份 =====
hs = json.load(open(DATA / 'history_schedule.json', encoding='utf-8'))
ms = hs['matches']
acle = [m for m in ms if '亚冠' in str(m.get('match_type', ''))]
print('=== 1. 赛程亚冠比赛: %d 场 ===' % len(acle))
cross = []
for m in acle:
    dy = int(str(m.get('date', '0000'))[:4])
    s = str(m.get('season'))
    if s != str(dy):
        cross.append(m)
        if s != str(dy - 1):
            issues.append('赛程 %s: season=%s date=%s 不匹配' % (m.get('match_id'), s, m.get('date')))
print('日期在第2年(跨年)进行的: %d 场, 逐条:' % len(cross))
for m in cross:
    print('  %s %s -> season %s  %s %s' % (m.get('match_id'), m.get('date'), m.get('season'), m.get('match_type'), m.get('round')))
bad = [m for m in ms if '/' in str(m.get('season', ''))]
print('残留跨年标签(/): %d' % len(bad))
if bad:
    issues.append('赛程残留跨年 %d 条' % len(bad))

# ===== 2. bySeason 汇总 =====
print()
print('=== 2. bySeason 汇总核对 ===')
for agg in hs['summary']['bySeason']:
    s = str(agg['season'])
    cnt = sum(1 for m in ms if str(m.get('season')) == s)
    total = agg.get('total', 0)
    if '/' in s:
        issues.append('bySeason 残留跨年 %s' % s)
    if total != cnt:
        issues.append('bySeason %s: total=%d vs 明细%d' % (s, total, cnt))
    if s in ('2025', '2026'):
        print('  %s: total=%d vs 明细=%d %s' % (s, total, cnt, 'OK' if total == cnt else 'MISMATCH'))

# summary 总数
sm = hs['summary']
calc = len([m for m in ms if m.get('result') and str(m.get('win_loss', '')) != ''])
print('  summary.totalMatches=%d vs 实际明细=%d' % (sm['totalMatches'], len(ms)))
if sm['totalMatches'] != len(ms):
    issues.append('summary.totalMatches 不一致')

# ===== 3. goal_details =====
print()
print('=== 3. goal_details 进球记录 ===')
goals = json.load(open(DATA / 'goal_details.json', encoding='utf-8'))
acle_goals = [g for g in goals if '亚冠' in str(g.get('match_type', '')) or '亚冠' in str(g.get('match_name', ''))]
print('亚冠进球: %d 条' % len(acle_goals))

def goal_year(g):
    # 日期字段为 match_date_code (int 如 20260915)
    dc = str(g.get('match_date_code', '00000000'))
    return int(dc[:4])

cross_g = [g for g in acle_goals if str(g.get('season')) != str(goal_year(g))]
for g in cross_g:
    dy = goal_year(g)
    if str(g.get('season')) != str(dy - 1):
        issues.append('进球 %s: season=%s date=%s' % (g.get('id', g.get('match_id')), g.get('season'), g.get('match_date_code')))
badg = [g for g in goals if '/' in str(g.get('season', ''))]
print('日期年份与season不同的亚冠进球: %d 条 (应为第2年进行, season=起始年)' % len(cross_g))
for g in cross_g:
    print('  %s %s %s -> season %s (%s)' % (g.get('id'), g.get('match_date_code'), g.get('goal_player'), g.get('season'), g.get('match_name', g.get('match_type'))))
print('残留跨年标签: %d' % len(badg))
if badg:
    issues.append('进球残留跨年 %d 条' % len(badg))

# ===== 4. player_appearance_details =====
print()
print('=== 4. player_appearance_details 出场明细 ===')
pad = json.load(open(DATA / 'player_appearance_details.json', encoding='utf-8'))
# 结构: {description, ..., players: [{name, seasons: [{season, appearances: [{matchId, ...}]}]}]}
players = pad['players']
bad_nodes = 0
total_apps = 0
for pl in players:
    for snode in pl.get('seasons', []):
        s = str(snode.get('season'))
        if '/' in s:
            bad_nodes += 1
            issues.append('出场明细 %s 残留跨年节点 %s' % (pl.get('name'), s))
        total_apps += len(snode.get('appearances', []))
print('球员数: %d, 跨年残留节点: %d, 总出场: %d (汇总字段=%s)' % (
    len(players), bad_nodes, total_apps, pad.get('totalAppearanceEntries')))

# 亚冠出场记录的 season vs 比赛 season 交叉核对（通过 matchId 映射赛程）
mid_map = {m.get('match_id'): m for m in ms}
mismatch_app = 0
acle_app = 0
missing_cnt = 0
for pl in players:
    for snode in pl.get('seasons', []):
        s = str(snode.get('season'))
        for rec in snode.get('appearances', []):
            mid = rec.get('matchId') or rec.get('match_id')
            m = mid_map.get(mid)
            if m is None:
                missing_cnt += 1
                continue
            if '亚冠' in str(m.get('match_type', '')):
                acle_app += 1
                if str(m.get('season')) != s:
                    mismatch_app += 1
                    if mismatch_app <= 8:
                        issues.append('出场明细 %s %s: 节点season=%s 比赛season=%s (%s %s)' % (
                            pl.get('name'), mid, s, m.get('season'), m.get('date'), m.get('match_type')))
print('亚冠出场记录: %d 条, 与赛程season不一致: %d, matchId无匹配: %d' % (acle_app, mismatch_app, missing_cnt))
if missing_cnt:
    issues.append('出场明细有 %d 条 matchId 无法匹配赛程' % missing_cnt)

# ===== 5. seasons.json =====
print()
print('=== 5. seasons.json 赛季汇总 ===')
ss = json.load(open(DATA / 'seasons.json', encoding='utf-8'))
bads = [s for s in ss if '/' in str(s.get('season', ''))]
print('跨年残留: %d' % len(bads))
if bads:
    issues.append('seasons.json 残留跨年 %d 条' % len(bads))
# 2026 亚冠精英条目的场次 vs 赛程明细
entry = [s for s in ss if s.get('season') == '2026' and '亚冠' in str(s.get('league', ''))]
if entry:
    e = entry[0]
    cnt = sum(1 for m in ms if str(m.get('season')) == '2026' and '亚冠' in str(m.get('match_type', '')))
    print('2026亚冠精英条目: matches=%s vs 赛程明细=%d' % (e.get('matches'), cnt))
    if e.get('matches') != cnt:
        issues.append('2026亚冠 seasons.json matches=%s vs %d' % (e.get('matches'), cnt))

# ===== 6. 比赛报告文件 =====
print()
print('=== 6. 比赛报告文件(team-a) ===')
files = sorted((DATA / 'team-a').glob('*.json'))
report_bad = []
for f in files:
    try:
        d = json.load(open(f, encoding='utf-8'))
    except Exception as ex:
        report_bad.append('%s 解析失败 %s' % (f.name, ex))
        continue
    s = str(d.get('season', ''))
    if '/' in s:
        report_bad.append('%s season=%s' % (f.name, s))
print('报告文件: %d 个, 残留跨年: %d' % (len(files), len(report_bad)))
for b in report_bad:
    issues.append('报告 ' + b)

# ===== 7. dist 同步检查 =====
print()
print('=== 7. dist 构建产物同步 ===')
for f in ['history_schedule.json', 'goal_details.json', 'player_appearance_details.json', 'seasons.json']:
    p1 = DATA / f
    p2 = Path('dist/data') / f
    if p2.exists():
        same = p1.read_bytes() == p2.read_bytes()
        print('  %s: %s' % (f, 'OK' if same else 'DIFF'))
        if not same:
            issues.append('dist/%s 与 public 不同步' % f)
    else:
        issues.append('dist/data/%s 缺失' % f)
# 报告文件
pub_reports = {f.name for f in (DATA / 'team-a').glob('*.json')}
dist_reports = {f.name for f in Path('dist/data/team-a').glob('*.json')}
diff_reports = pub_reports - dist_reports
print('  team-a 报告: public=%d dist=%d, 差异=%s' % (len(pub_reports), len(dist_reports), diff_reports or '无'))
if diff_reports:
    issues.append('dist报告缺 %s' % diff_reports)

print()
print('=' * 50)
if issues:
    print('发现问题 %d 个:' % len(issues))
    for i in issues[:30]:
        print(' -', i)
else:
    print('ALL OK: 跨年比赛全部正确归属到起始年赛季')
