import json
import os
import shutil
from pathlib import Path

match_reports_dir = Path('data/match_reports')
history_schedule_file = Path('public/data/history_schedule.json')

with open(history_schedule_file, 'r', encoding='utf-8') as f:
    history_schedule = json.load(f)

date_to_round = {}
for match in history_schedule:
    if match['season'] == '2024' and match['match_type'] == '中超联赛':
        date = match['date']
        round = match['round']
        date_to_round[date] = round

print(f"找到 {len(date_to_round)} 场2024年中超联赛")

for json_file in match_reports_dir.glob('match_2024-*.json'):
    parts = json_file.stem.split('_')
    if len(parts) >= 2:
        date = parts[1]
        
        if date in date_to_round:
            round = date_to_round[date]
            new_name = f"{date}-中超-{round}.json"
            new_path = match_reports_dir / new_name
            
            if not new_path.exists():
                shutil.move(str(json_file), str(new_path))
                print(f"重命名: {json_file.name} -> {new_name}")
            else:
                print(f"跳过: {new_name} 已存在")
        else:
            print(f"未找到日期 {date} 对应的轮次")

print("完成！")
