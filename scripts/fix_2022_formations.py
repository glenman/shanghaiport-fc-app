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

    # 检查home和away的formation字段
    if 'teams' in data:
        for team_type in ['home', 'away']:
            if team_type in data['teams']:
                team = data['teams'][team_type]

                if 'formation' in team:
                    formation = team['formation']
                    # 从formation中提取阵型部分，格式如 "Shanghai Port (4-1-4-1)" -> "(4-1-4-1)"
                    match = re.search(r'(\d+-\d+-\d+)', formation)
                    if match:
                        new_formation = f"({match.group(1)})"
                        if formation != new_formation:
                            print(f"{filename} [{team_type}]: {formation} -> {new_formation}")
                            team['formation'] = new_formation
                            modified = True

    # 保存修改后的JSON
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

if not modified:
    print("No files needed modification")

print("Done!")
