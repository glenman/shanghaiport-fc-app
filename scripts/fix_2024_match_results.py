import json
import os
from pathlib import Path

data_dir = Path('public/data')
history_schedule_file = data_dir / 'history_schedule.json'

with open(history_schedule_file, 'r', encoding='utf-8') as f:
    history_schedule = json.load(f)

result_map = {}
for match in history_schedule:
    if match['season'] == '2024':
        date = match['date']
        result = match['result']
        result_map[date] = result

print(f"找到 {len(result_map)} 场2024年比赛")

for json_file in data_dir.glob('2024-*.json'):
    if json_file.name.startswith('2024-'):
        date = json_file.name.split('-')[0:3]
        date_str = f"{date[0]}-{date[1]}-{date[2]}"
        
        if date_str in result_map:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if data['match']['result'] is None:
                data['match']['result'] = result_map[date_str]
                
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                print(f"更新 {json_file.name}: {result_map[date_str]}")
            else:
                print(f"跳过 {json_file.name}: 已有结果 {data['match']['result']}")

print("完成！")
