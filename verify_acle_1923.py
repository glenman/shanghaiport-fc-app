# -*- coding: utf-8 -*-
"""单独核对 2019-2023 疫情区间各赛季亚冠比赛的跨年归属"""
import json

hs = json.load(open('public/data/history_schedule.json', encoding='utf-8'))
ms = hs['matches']

for yr in ('2019', '2020', '2021', '2022', '2023'):
    ac = [m for m in ms if str(m.get('season')) == yr and '亚冠' in str(m.get('match_type', ''))]
    if not ac:
        print('%s 赛季: 无亚冠比赛记录' % yr)
        continue
    print('%s 赛季亚冠 %d 场:' % (yr, len(ac)))
    for m in ac:
        dy = str(m.get('date', ''))[:4]
        flag = '  <-- 跨年(第2年进行)' if dy != yr else ''
        print('  %s %s %s %s %s %s%s' % (
            m['match_id'], m.get('date'), m.get('match_type'), m.get('round'),
            m.get('result', ''), m.get('win_loss', ''), flag))
    print()

# 出场明细与进球记录在这两个赛季的亚冠归属
pad = json.load(open('public/data/player_appearance_details.json', encoding='utf-8'))
mid_map = {m.get('match_id'): m for m in ms}
for yr in ('2021', '2022'):
    cnt = 0
    bad = 0
    for pl in pad['players']:
        for snode in pl.get('seasons', []):
            for rec in snode.get('appearances', []):
                m = mid_map.get(rec.get('matchId'))
                if m and '亚冠' in str(m.get('match_type', '')) and str(m.get('season')) == yr:
                    cnt += 1
                    if str(snode.get('season')) != yr:
                        bad += 1
    print('%s 赛季亚冠出场记录: %d 条, 节点season不一致: %d' % (yr, cnt, bad))

goals = json.load(open('public/data/goal_details.json', encoding='utf-8'))
for yr in ('2021', '2022'):
    gy = [g for g in goals if str(g.get('season')) == yr and '亚冠' in str(g.get('match_type', ''))]
    cross = [g for g in gy if str(str(g.get('match_date_code'))[:4]) != yr]
    print('%s 赛季亚冠进球: %d 条, 其中日期在第2年的: %d (season均已=%s)' % (yr, len(gy), len(cross), yr))
