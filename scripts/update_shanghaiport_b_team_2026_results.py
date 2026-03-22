import json
import os
from pathlib import Path

schedule_file = Path('public/data/schedule_b.json')

with open(schedule_file, 'r', encoding='utf-8') as f:
    schedule = json.load(f)

updated_matches = []
for match in schedule:
    if match['awayTeam'] == '上海海港B队':
        if match['result'] == '-':
            match['result'] = '1-6'
            match['status'] = '已结束'
            updated_matches.append(match)
            print(f"更新: {match['date']} - {match['homeTeam']} vs {match['awayTeam']} - {match['result']}")

if updated_matches:
    with open(schedule_file, 'w', encoding='utf-8') as f:
        json.dump(schedule, f, ensure_ascii=False, indent=2)
    print(f"已更新 {len(updated_matches)} 场比赛")
else:
    print("没有需要更新的比赛")
