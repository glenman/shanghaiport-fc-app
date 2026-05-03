import os
import json
import re

# 2022目录路径
dir_path = r"d:\Workspace\shanghaiport-fc-app\public\data\history\2022"

# 获取所有JSON文件
files = [f for f in os.listdir(dir_path) if f.endswith('.json')]

for filename in files:
    file_path = os.path.join(dir_path, filename)

    # 读取JSON文件
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    modified = False

    # 检查home和away的name字段
    if 'teams' in data:
        for team_type in ['home', 'away']:
            if team_type in data['teams']:
                team = data['teams'][team_type]

                # 如果name是"Opponent"或者name与formation中的球队名不匹配，从formation中提取球队名称
                if 'formation' in team:
                    formation = team['formation']
                    # 从formation中提取球队名称，格式如 "Wuhan Zall (4-3-3)"
                    match = re.match(r'^(.+?)\s*\(', formation)
                    if match:
                        team_name_from_formation = match.group(1).strip()

                        # 如果name是"Opponent"，直接替换
                        if team.get('name') == 'Opponent':
                            team['name'] = team_name_from_formation
                            print(f"{filename} [{team_type}]: Opponent -> {team_name_from_formation}")
                            modified = True
                        # 如果name与formation中的名称不匹配，也需要更新
                        elif team.get('name') != team_name_from_formation:
                            old_name = team.get('name')
                            team['name'] = team_name_from_formation
                            print(f"{filename} [{team_type}]: {old_name} -> {team_name_from_formation}")
                            modified = True

    # 保存修改后的JSON
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

if not modified:
    print("No files needed modification")

print("Done!")
