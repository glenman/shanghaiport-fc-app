import csv
import json
from pathlib import Path

CSV_FILE = r"datafile\上海海港2019中超联赛比赛结果.csv"
JSON_DIR = r"public\data\history\2019"

def load_csv_data():
    """从CSV加载比赛结果数据"""
    matches = {}
    try:
        with open(CSV_FILE, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                round_num = str(row.get('轮次', '')).strip()
                date = row.get('比赛时间', '').strip().replace('.', '-')
                home = row.get('主队', '').strip()
                away = row.get('客队', '').strip()

                if round_num and date:
                    matches[date] = {
                        'round': round_num,
                        'home': home,
                        'away': away
                    }
                    print(f"第{round_num}轮 ({date}): {home} vs {away}")
        return matches
    except Exception as e:
        print(f"❌ 加载CSV失败: {e}")
        return {}

def get_date_from_filename(filename):
    """从文件名提取日期"""
    import re
    match = re.match(r'(\d{4}-\d{2}-\d{2})-中超-第\d+轮\.json', filename)
    if match:
        return match.group(1)
    return None

def update_json_files(matches):
    """更新JSON文件中的主客队名称"""
    json_dir = Path(JSON_DIR)
    json_files = sorted(list(json_dir.glob('*.json')))

    updated_count = 0
    for json_path in json_files:
        date = get_date_from_filename(json_path.name)
        if not date or date not in matches:
            print(f"⚠️ 找不到匹配: {json_path.name}")
            continue

        match_info = matches[date]

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 更新主队名称
            if 'teams' in data and 'home' in data['teams']:
                old_home = data['teams']['home'].get('name', '')
                data['teams']['home']['name'] = match_info['home']
                data['teams']['home']['full_name'] = match_info['home']

                # 更新formation中的队名
                if 'formation' in data['teams']['home']:
                    formation = data['teams']['home']['formation']
                    # 保留阵型，去除队名
                    import re
                    match = re.search(r'\((\d+[-–]?)*\d+\)', formation)
                    if match:
                        data['teams']['home']['formation'] = match.group(0)

            # 更新客队名称
            if 'teams' in data and 'away' in data['teams']:
                old_away = data['teams']['away'].get('name', '')
                data['teams']['away']['name'] = match_info['away']
                data['teams']['away']['full_name'] = match_info['away']

                # 更新formation中的队名
                if 'formation' in data['teams']['away']:
                    formation = data['teams']['away']['formation']
                    # 保留阵型，去除队名
                    import re
                    match = re.search(r'\((\d+[-–]?)*\d+\)', formation)
                    if match:
                        data['teams']['away']['formation'] = match.group(0)

            # 保存文件
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            updated_count += 1
            print(f"✅ {json_path.name}: {match_info['home']} vs {match_info['away']}")

        except Exception as e:
            print(f"❌ 处理失败 {json_path.name}: {e}")

    return updated_count

def main():
    print("=" * 60)
    print("2019赛季 主客队名称更新")
    print("=" * 60)

    print("\n📋 加载CSV数据...")
    matches = load_csv_data()
    print(f"✅ 加载了 {len(matches)} 场比赛数据\n")

    print("📝 更新JSON文件...")
    updated = update_json_files(matches)

    print("\n" + "=" * 60)
    print(f"✅ 更新完成! 共更新 {updated} 个文件")
    print("=" * 60)

if __name__ == "__main__":
    main()
