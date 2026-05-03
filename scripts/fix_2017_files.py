import os
import json
import re

# 2017目录路径
dir_path = r"d:\Workspace\shanghaiport-fc-app\public\data\history\2017"

# 获取所有JSON文件
files = [f for f in os.listdir(dir_path) if f.endswith('.json')]

# 需要修正的文件映射：文件名中的轮次 -> 正确的轮次
# 第19轮到第30轮的文件名错误地显示为第1轮到第12轮
round_correction = {
    1: 19,   # 2017-07-30-中超-第1轮.json -> 第19轮
    2: 20,   # 2017-08-06-中超-第2轮.json -> 第20轮
    3: 21,   # 2017-08-10-中超-第3轮.json -> 第21轮
    4: 22,   # 2017-08-13-中超-第4轮.json -> 第22轮
    5: 23,   # 2017-08-19-中超-第5轮.json -> 第23轮
    6: 24,   # 2017-09-09-中超-第6轮.json -> 第24轮
    7: 25,   # 2017-09-16-中超-第7轮.json -> 第25轮
    8: 26,   # 2017-09-22-中超-第8轮.json -> 第26轮
    9: 27,   # 2017-10-14-中超-第9轮.json -> 第27轮
    10: 28,  # 2017-10-22-中超-第10轮.json -> 第28轮
    11: 29,  # 2017-10-29-中超-第11轮.json -> 第29轮
    12: 30   # 2017-11-04-中超-第12轮.json -> 第30轮
}

for filename in files:
    # 检查文件名中是否包含错误的轮次（第1轮到第12轮）
    match = re.search(r'第(\d+)轮', filename)
    if not match:
        print(f"Skipping {filename}, no round found")
        continue

    file_round = int(match.group(1))

    # 检查是否需要修正
    if file_round in round_correction:
        correct_round = round_correction[file_round]

        # 提取日期部分
        date_match = re.match(r'(\d{4}-\d{2}-\d{2})', filename)
        if not date_match:
            print(f"Skipping {filename}, no date found")
            continue

        file_date = date_match.group(1)

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
        os.rename(old_path, new_path)
        print(f"Renamed: {filename} -> {new_filename}, round updated to {correct_round}")
    else:
        # 文件名正确，只需要更新内部的round字段（确保一致性）
        old_path = os.path.join(dir_path, filename)

        with open(old_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if 'match_info' in data and 'competition' in data['match_info']:
            current_round = data['match_info']['competition']['round']
            # 检查是否需要更新
            if f"Matchweek {file_round}" != current_round:
                data['match_info']['competition']['round'] = f"Matchweek {file_round}"
                with open(old_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"Updated: {filename}, round updated to Matchweek {file_round}")
            else:
                print(f"No change needed: {filename}")
        else:
            print(f"Warning: {filename} has no match_info.competition.round field")

print("Done!")
