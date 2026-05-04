import csv
import json
import re
from pathlib import Path

SCHEDULE_CSV = r"datafile\上海海港2018一线队中超赛程.csv"
JSON_DIR = r"public\data\history\2018"

def load_schedule(csv_path):
    """从CSV加载赛程信息"""
    schedule = {}
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                date = row.get('比赛日期', '').strip()
                round_num = row.get('轮次', '').strip()
                if date and round_num:
                    schedule[date] = round_num
        print(f"✅ 已加载 {len(schedule)} 场比赛赛程")
        return schedule
    except Exception as e:
        print(f"❌ 加载赛程失败: {e}")
        return {}

def check_and_rename(schedule):
    """检查并重命名文件"""
    json_dir = Path(JSON_DIR)
    json_files = sorted(list(json_dir.glob('*.json')))
    
    rename_list = []
    
    for json_path in json_files:
        # 从文件名提取日期和轮次
        match = re.match(r'(\d{4}-\d{2}-\d{2})-中超-第(\d+)轮\.json', json_path.name)
        if match:
            file_date = match.group(1)
            file_round = match.group(2)
            
            if file_date in schedule:
                correct_round = schedule[file_date]
                if file_round != correct_round:
                    new_name = f"{file_date}-中超-第{correct_round}轮.json"
                    new_path = json_dir / new_name
                    rename_list.append((json_path, new_path))
    
    if rename_list:
        print(f"\n发现 {len(rename_list)} 个文件需要重命名：")
        for old, new in rename_list:
            print(f"  {old.name} -> {new.name}")
        
        confirm = input("\n是否继续重命名？(y/n) ").lower()
        if confirm == 'y':
            for old, new in rename_list:
                old.rename(new)
                print(f"  ✅ {new.name}")
        else:
            print("取消操作")
    else:
        print("✅ 所有文件名轮次正确，无需重命名")

def update_round_in_json(schedule):
    """更新JSON文件中的round字段"""
    json_dir = Path(JSON_DIR)
    json_files = sorted(list(json_dir.glob('*.json')))
    
    updated_count = 0
    for json_path in json_files:
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            date = data['match_info']['date']
            if date in schedule:
                correct_round = schedule[date]
                if 'competition' in data['match_info']:
                    comp = data['match_info']['competition']
                    if 'round' in comp:
                        round_val = comp['round']
                        match_round = re.search(r'Matchweek\s*(\d+)', round_val)
                        if match_round:
                            comp['round'] = f"第{correct_round}轮"
                            with open(json_path, 'w', encoding='utf-8') as f:
                                json.dump(data, f, ensure_ascii=False, indent=2)
                            updated_count += 1
        except Exception as e:
            print(f"❌ 处理 {json_path.name} 失败: {e}")
    
    print(f"\n✅ 已更新 {updated_count} 个JSON文件的round字段")

def main():
    print("=" * 60)
    print("2018赛季文件名和轮次检查修正")
    print("=" * 60)
    
    schedule = load_schedule(SCHEDULE_CSV)
    check_and_rename(schedule)
    update_round_in_json(schedule)

if __name__ == '__main__':
    main()