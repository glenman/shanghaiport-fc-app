# -*- coding: utf-8 -*-
"""扫描所有比赛: 找出日期年份 != 赛季年份的记录, 核对跨年归属是否正确"""
import json

hs = json.load(open('public/data/history_schedule.json', encoding='utf-8'))
ms = hs['matches']

print('=== 全部 702 场中: 日期年份 != season 的比赛 ===')
cross = []
for m in ms:
    dy = int(str(m.get('date', '0000'))[:4])
    s = str(m.get('season'))
    if str(dy) != s:
        cross.append((m, dy, s))

print('共 %d 场, 逐条:' % len(cross))
for m, dy, s in cross:
    correct = (s == str(dy - 1))  # 规则: 归属起始年 = 日期年 - 1
    print('  %s %s %s %-22s %s %s %s %s %s' % (
        m['match_id'], m.get('date'), s, '%s %s' % (m.get('match_type', ''), m.get('round', '')),
        m.get('home_team'), m.get('result'), m.get('away_team'),
        m.get('win_loss', ''), 'OK' if correct else '!!!错误'))

# 按类型统计
print()
print('=== 按赛事类型统计跨年场次 ===')
by_type = {}
for m, dy, s in cross:
    by_type.setdefault(str(m.get('match_type', '')), []).append(m)
for t, lst in by_type.items():
    print('  %s: %d 场' % (t, len(lst)))

# 出场明细交叉验证: 日期年 != season 的比赛的出场记录是否挂在起始年节点
pad = json.load(open('public/data/player_appearance_details.json', encoding='utf-8'))
mid_map = {m.get('match_id'): m for m in ms}
print()
print('=== 出场明细对这 %d 场比赛的归属核对 ===' % len(cross))
bad = 0
total = 0
for m, dy, s in cross:
    cnt = 0
    for pl in pad['players']:
        for snode in pl.get('seasons', []):
            for rec in snode.get('appearances', []):
                if rec.get('matchId') == m['match_id']:
                    cnt += 1
                    if str(snode.get('season')) != s:
                        bad += 1
                        if bad <= 10:
                            print('  !!! %s %s: 出场挂在 %s 节点, 比赛season=%s' % (pl.get('name'), m['match_id'], snode.get('season'), s))
    total += cnt
print('这些比赛共 %d 条出场记录, 挂错赛季节点: %d' % (total, bad))

# 进球记录同样核对
goals = json.load(open('public/data/goal_details.json', encoding='utf-8'))
print()
print('=== 进球记录归属核对(日期年 != season) ===')
gbad = 0
gtotal = 0
for g in goals:
    dy = int(str(g.get('match_date_code', 0))[:4])
    s = str(g.get('season'))
    if str(dy) != s:
        gtotal += 1
        if s != str(dy - 1):
            gbad += 1
            if gbad <= 10:
                print('  !!! 进球 %s %s %s: season=%s 应为 %s' % (g.get('id'), g.get('match_date_code'), g.get('goal_player'), s, dy - 1))
print('日期年与season不同的进球: %d 条, 归属错误: %d' % (gtotal, gbad))

print()
errs = [x for x in cross if x[1] and str(x[2]) != str(x[1] - 1)]
if not errs and bad == 0 and gbad == 0:
    print('ALL OK: 所有跨年比赛(含非亚冠)均正确归属起始年赛季')
else:
    print('存在 %d 场归属错误' % len(errs))
