import csv
import json
import os
import re
from pathlib import Path

def load_schedule_from_csv(csv_path):
    """从CSV文件读取赛程数据，建立日期到轮次的映射"""
    date_to_round = {}
    round_to_date = {}

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()

    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        if line.startswith('"') and line.endswith('"'):
            line = line[1:-1]

        parts = line.split(',')
        if len(parts) >= 6:
            round_str = parts[0].strip().replace('Matchweek', '').strip()
            date = parts[1].strip()
            home = parts[4].strip()
            away = parts[5].strip()

            if round_str.isdigit():
                round_num = int(round_str)
                date_to_round[date] = round_num
                round_to_date[round_num] = {'date': date, 'home': home, 'away': away}

    return date_to_round, round_to_date

def extract_date_from_filename(filename):
    """从文件名提取日期"""
    match = re.match(r'(\d{4}-\d{2}-\d{2})', filename)
    if match:
        return match.group(1)
    return None

def extract_current_round(filename):
    """从文件名提取当前轮次"""
    match = re.search(r'第(\d+)轮', filename)
    if match:
        return int(match.group(1))
    return None

def main():
    csv_path = r'd:\Workspace\shanghaiport-fc-app\datafile\上海海港2019一线队中超赛程.csv'
    json_dir = r'd:\Workspace\shanghaiport-fc-app\public\data\history\2019'

    print("加载赛程数据...")
    date_to_round, round_to_date = load_schedule_from_csv(csv_path)
    print(f"已加载 {len(date_to_round)} 个日期-轮次映射")

    print("\n当前文件 vs 正确轮次:")
    print("-" * 80)

    json_files = sorted(Path(json_dir).glob('*.json'))

    for json_path in json_files:
        filename = json_path.name
        current_date = extract_date_from_filename(filename)
        current_round = extract_current_round(filename)

        if current_date and current_date in date_to_round:
            correct_round = date_to_round[current_date]
            status = "✅" if current_round == correct_round else "❌"
            print(f"{status} {filename}")
            print(f"   当前轮次: 第{current_round}轮 → 正确轮次: 第{correct_round}轮")
        else:
            print(f"⚠️  {filename} - 无法匹配日期")

    print("\n开始重命名文件并更新round字段...")

    for json_path in json_files:
        filename = json_path.name
        current_date = extract_date_from_filename(filename)

        if not current_date or current_date not in date_to_round:
            print(f"  跳过: {filename} (无法匹配日期)")
            continue

        correct_round = date_to_round[current_date]

        # 读取JSON文件更新round字段
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 更新round字段
        if 'match_info' in data and 'competition' in data['match_info']:
            old_round = data['match_info']['competition'].get('round', '')
            new_round = f"第{correct_round}轮"
            if old_round != new_round:
                data['match_info']['competition']['round'] = new_round
                print(f"  更新round: {filename} - {old_round} → {new_round}")

        # 保存JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # 构建新文件名
        new_filename = f"{current_date}-中超-第{correct_round}轮.json"
        new_path = json_path.parent / new_filename

        if new_path.exists() and new_path != json_path:
            print(f"  警告: 目标文件已存在，跳过: {new_filename}")
            continue

        if new_path != json_path:
            os.rename(json_path, new_path)
            print(f"  重命名: {filename} → {new_filename}")

    print("\n完成！")

if __name__ == '__main__':
    main()