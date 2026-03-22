import json
from pathlib import Path

schedule_file = Path('public/data/schedule_b.json')

with open(schedule_file, 'r', encoding='utf-8') as f:
    schedule = json.load(f)

for match in schedule:
    if match['round'] == '第1轮' and match['date'] == '2026-03-22':
        match['result'] = '1-6'
        match['status'] = '已结束'
        print(f"更新: {match['date']} - {match['homeTeam']} vs {match['awayTeam']} - {match['result']}")

with open(schedule_file, 'w', encoding='utf-8') as f:
    json.dump(schedule, f, ensure_ascii=False, indent=2)

print("更新完成！")
