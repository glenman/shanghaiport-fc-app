import os
import json
import re

# 轮次和日期对应关系
round_date_map = {
    1: "2019.03.01",
    2: "2019.03.09",
    3: "2019.03.30",
    4: "2019.04.05",
    5: "2019.04.14",
    6: "2019.04.19",
    7: "2019.04.28",
    8: "2019.05.04",
    9: "2019.05.12",
    10: "2019.05.17",
    11: "2019.05.26",
    12: "2019.06.02",
    13: "2019.06.14",
    14: "2019.06.22",
    15: "2019.06.30",
    16: "2019.07.06",
    17: "2019.07.13",
    18: "2019.07.17",
    19: "2019.07.21",
    20: "2019.07.28",
    21: "2019.08.03",
    22: "2019.08.14",
    23: "2019.08.09",
    24: "2019.09.13",
    25: "2019.09.22",
    26: "2019.10.19",
    27: "2019.10.27",
    28: "2019.11.23",
    29: "2019.11.27",
    30: "2019.12.01"
}

# 创建日期到轮次的映射
date_round_map = {date.replace('.', '-'): round_num for round_num, date in round_date_map.items()}

# 2019目录路径
dir_path = r"d:\Workspace\shanghaiport-fc-app\public\data\history\2019"

# 获取所有JSON文件
files = [f for f in os.listdir(dir_path) if f.endswith('.json')]

for filename in files:
    # 提取日期部分
    date_match = re.match(r'(\d{4}-\d{2}-\d{2})', filename)
    if not date_match:
        print(f"Skipping {filename}, no date found")
        continue
    
    file_date = date_match.group(1)
    
    # 查找对应的轮次
    if file_date not in date_round_map:
        print(f"Skipping {filename}, date {file_date} not in mapping")
        continue
    
    correct_round = date_round_map[file_date]
    
    # 构建新文件名
    new_filename = f"{file_date}-中超-第{correct_round}轮.json"
    
    old_path = os.path.join(dir_path, filename)
    new_path = os.path.join(dir_path, new_filename)
    
    # 读取JSON文件
    with open(old_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 更新round字段
    if 'match_info' in data and 'competition' in data['match_info']:
        data['match_info']['competition']['round'] = f"Matchweek {correct_round}"
    else:
        print(f"Warning: {filename} has no match_info.competition.round field")
    
    # 保存修改后的JSON
    with open(old_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 重命名文件
    if old_path != new_path:
        os.rename(old_path, new_path)
        print(f"Renamed: {filename} -> {new_filename}, round updated to {correct_round}")
    else:
        print(f"Updated: {filename}, round updated to {correct_round}")

print("Done!")
