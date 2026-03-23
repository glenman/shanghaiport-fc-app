
import json
import os

# 读取现有的goal_details.json文件
file_path = "public/data/goal_details.json"
with open(file_path, 'r', encoding='utf-8') as f:
    goal_details = json.load(f)

# 获取最新的ID
latest_id = max(item['id'] for item in goal_details) if goal_details else 0

# 新的进球记录
new_goals = [
    {
        "id": latest_id + 1,
        "season": "2026",
        "match_type": "中超联赛",
        "goal_time": "45+4'",
        "goal_player": "加布里埃尔",
        "assist_player": "杨希",
        "create_player": "—",
        "match_date_code": 20260307,
        "match_name": "中超联赛第1轮",
        "home_team": "上海海港",
        "home_score": 1,
        "away_score": 2,
        "away_team": "河南俱乐部",
        "match_result": "负",
        "remark": "—"
    },
    {
        "id": latest_id + 2,
        "season": "2026",
        "match_type": "中超联赛",
        "goal_time": "47'",
        "goal_player": "让克劳德",
        "assist_player": "李帅",
        "create_player": "—",
        "match_date_code": 20260315,
        "match_name": "中超联赛第2轮",
        "home_team": "上海海港",
        "home_score": 4,
        "away_score": 1,
        "away_team": "青岛西海岸",
        "match_result": "胜",
        "remark": "—"
    },
    {
        "id": latest_id + 3,
        "season": "2026",
        "match_type": "中超联赛",
        "goal_time": "61'",
        "goal_player": "莱昂纳多",
        "assist_player": "蒯纪闻",
        "create_player": "—",
        "match_date_code": 20260315,
        "match_name": "中超联赛第2轮",
        "home_team": "上海海港",
        "home_score": 4,
        "away_score": 1,
        "away_team": "青岛西海岸",
        "match_result": "胜",
        "remark": "—"
    },
    {
        "id": latest_id + 4,
        "season": "2026",
        "match_type": "中超联赛",
        "goal_time": "70'",
        "goal_player": "武磊",
        "assist_player": "—",
        "create_player": "—",
        "match_date_code": 20260315,
        "match_name": "中超联赛第2轮",
        "home_team": "上海海港",
        "home_score": 4,
        "away_score": 1,
        "away_team": "青岛西海岸",
        "match_result": "胜",
        "remark": "—"
    },
    {
        "id": latest_id + 5,
        "season": "2026",
        "match_type": "中超联赛",
        "goal_time": "80'",
        "goal_player": "武磊",
        "assist_player": "安佩姆",
        "create_player": "—",
        "match_date_code": 20260315,
        "match_name": "中超联赛第2轮",
        "home_team": "上海海港",
        "home_score": 4,
        "away_score": 1,
        "away_team": "青岛西海岸",
        "match_result": "胜",
        "remark": "—"
    }
]

# 添加新的进球记录
goal_details.extend(new_goals)

# 保存更新后的文件
with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(goal_details, f, ensure_ascii=False, indent=2)

print(f"成功添加了 {len(new_goals)} 个进球记录")
print(f"最新的ID是: {latest_id + len(new_goals)}")
