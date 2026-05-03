import os
import json

# 轮次和日期对应关系（使用正确的对应）
round_date_map = {
    1: "2017-03-04",
    2: "2017-03-10",
    3: "2017-04-01",
    4: "2017-04-07",
    5: "2017-04-15",
    6: "2017-04-21",
    7: "2017-04-30",
    8: "2017-05-06",
    9: "2017-05-14",
    10: "2017-05-20",
    11: "2017-05-27",
    12: "2017-06-03",
    13: "2017-06-18",
    14: "2017-06-25",
    15: "2017-07-01",
    16: "2017-07-09",
    17: "2017-07-15",
    18: "2017-07-22",
    19: "2017-07-30",
    20: "2017-08-06",
    21: "2017-08-10",
    22: "2017-08-13",
    23: "2017-08-19",
    24: "2017-09-09",
    25: "2017-09-16",
    26: "2017-09-22",
    27: "2017-10-14",
    28: "2017-10-22",
    29: "2017-10-29",
    30: "2017-11-04"
}

# 创建日期到轮次的映射
date_round_map = {date: round_num for round_num, date in round_date_map.items()}

# 2017目录路径
dir_path = r"d:\Workspace\shanghaiport-fc-app\public\data\history\2017"

# 获取所有JSON文件
files = [f for f in os.listdir(dir_path) if f.endswith('.json')]

for filename in files:
    # 提取日期部分 (格式: 2017-03-04-中超-第X轮.json)
    parts = filename.split('-')
    if len(parts) < 3:
        print(f"Skipping {filename}, invalid format")
        continue

    # 日期在前3个部分: 2017-03-04
    file_date = f"{parts[0]}-{parts[1]}-{parts[2]}"

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
        print(f"No change needed: {filename}")

print("Done!")
