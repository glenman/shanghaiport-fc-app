#!/usr/bin/env python3
import sqlite3
import json
import re

# 连接数据库
conn = sqlite3.connect('football.db')
cursor = conn.cursor()

# 查询所有比赛信息
query = """
SELECT DISTINCT season, match_type, match_name, match_date_code, home_team, away_team, home_score, away_score, match_result 
FROM goal_details 
ORDER BY season DESC, match_date_code DESC
"""

cursor.execute(query)
matches = cursor.fetchall()

# 处理比赛数据
history_schedule = []

for match in matches:
    season, match_type, match_name, match_date_code, home_team, away_team, home_score, away_score, match_result = match
    
    # 从match_date_code提取日期 (格式: YYYYMMDD)
    date_str = str(match_date_code)
    if len(date_str) == 8:
        date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    else:
        date = ""
    
    # 从match_name提取轮次
    round_match = re.search(r'第[\d一]+轮', match_name)
    round_info = round_match.group(0) if round_match else ""
    
    # 生成赛果
    result = f"{home_score}-{away_score}"
    
    # 创建比赛记录
    match_record = {
        "season": season,
        "match_type": match_type,
        "match_name": match_name,
        "round": round_info,
        "date": date,
        "home_team": home_team,
        "away_team": away_team,
        "result": result
    }
    
    history_schedule.append(match_record)

# 保存为JSON文件
with open('data/history_schedule.json', 'w', encoding='utf-8') as f:
    json.dump(history_schedule, f, ensure_ascii=False, indent=2)

print(f"生成历史赛程JSON文件成功，包含 {len(history_schedule)} 场比赛")

# 关闭数据库连接
conn.close()