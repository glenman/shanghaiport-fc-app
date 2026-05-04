
import csv
import json
import re
from pathlib import Path

SCHEDULE_CSV = r"datafile/上海海港2018一线队中超赛程.csv"
JSON_DIR = r"public/data/history/2018"

TEAM_MAP = {
    "上海海港": "上海海港",
    "上海上港": "上海海港",
    "大连一方": "大连一方",
    "上海申花": "上海申花",
    "广州富力": "广州富力",
    "重庆力帆": "重庆力帆",
    "河南建业": "河南建业",
    "河北华夏幸福": "河北华夏幸福",
    "河北华夏": "河北华夏幸福",
    "天津泰达": "天津泰达",
    "长春亚泰": "长春亚泰",
    "北京国安": "北京国安",
    "贵州恒丰": "贵州恒丰",
    "江苏苏宁": "江苏苏宁",
    "山东鲁能": "山东鲁能",
    "广州恒大": "广州恒大",
    "北京人和": "北京人和",
    "天津权健": "天津权健"
}

def load_schedule():
    schedule = {}
    with open(SCHEDULE_CSV, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            round_num = str(row['轮次']).strip()
            schedule[round_num] = {
                'home': row['主队'].strip(),
                'away': row['客队'].strip()
            }
    return schedule

def get_round_from_filename(filename):
    match = re.match(r'\d{4}-\d{2}-\d{2}-中超-第(\d+)轮\.json', filename)
    if match:
        return match.group(1)
    return None

def is_shanghai_port_team(team_data):
    name = team_data.get('name', '').strip()
    formation = team_data.get('formation', '')
    lineup = team_data.get('lineup', [])
    
    if "SIPG" in name or "Shanghai" in name and "Port" in name or name in ["上海海港", "上海上港"]:
        return True
    if "SIPG" in formation:
        return True
    for player in lineup:
        p_name = player.get('name', '')
        if "Yan Junling" in p_name or "Hulk" in p_name or "Oscar" in p_name or "Elkeson" in p_name:
            return True
    return False

def check_and_fix_json(json_path, schedule):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        round_num = get_round_from_filename(json_path.name)
        if not round_num or round_num not in schedule:
            return False
        
        correct = schedule[round_num]
        
        # 判断当前主客队哪个是上海海港
        is_home_port = is_shanghai_port_team(data['teams']['home'])
        is_away_port = is_shanghai_port_team(data['teams']['away'])
        
        # 判断应该哪个是上海海港
        should_home_be_port = correct['home'] in ["上海海港", "上海上港"]
        
        needs_swap = False
        if should_home_be_port and not is_home_port:
            needs_swap = True
        if not should_home_be_port and is_home_port:
            needs_swap = True
        
        if needs_swap:
            print(f"🔄 {json_path.name}: 需要交换主客队！")
            
            # 交换主客队
            data['teams']['home'], data['teams']['away'] = data['teams']['away'], data['teams']['home']
            
            # 更新事件中的team字段
            for event in data.get('events', []):
                if 'team' in event:
                    if event['team'] == 'home':
                        event['team'] = 'away'
                    elif event['team'] == 'away':
                        event['team'] = 'home'
            
            # 更新换人信息中的team字段
            for team_key in ['home', 'away']:
                team = data['teams'][team_key]
                for sub in team.get('substitutions', []):
                    if 'team' in sub:
                        if sub['team'] == 'home':
                            sub['team'] = 'away'
                        elif sub['team'] == 'away':
                            sub['team'] = 'home'
        
        # 更新队名显示
        correct_home_name = TEAM_MAP.get(correct['home'], correct['home'])
        correct_away_name = TEAM_MAP.get(correct['away'], correct['away'])
        
        data['teams']['home']['name'] = correct_home_name
        data['teams']['home']['full_name'] = correct_home_name
        data['teams']['away']['name'] = correct_away_name
        data['teams']['away']['full_name'] = correct_away_name
        
        # 保存文件
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        if needs_swap:
            print(f"✅ {json_path.name}: 已交换并修正！")
        else:
            print(f"✅ {json_path.name}: 已检查并更新队名！")
        
        return True
    except Exception as e:
        print(f"❌ {json_path.name}: 处理失败！ {e}")
        return False

def main():
    print("="*60)
    print("2018赛季 主客队信息检查与修正")
    print("="*60)
    
    schedule = load_schedule()
    print(f"✅ 加载到 {len(schedule)} 轮赛程！\n")
    
    json_dir = Path(JSON_DIR)
    json_files = sorted(list(json_dir.glob('*.json')))
    
    success = 0
    for json_path in json_files:
        if check_and_fix_json(json_path, schedule):
            success +=1
    
    print("\n" + "="*60)
    print(f"完成！ 处理 {len(json_files)} 个文件， 成功 {success}！")
    print("="*60)

if __name__ == "__main__":
    main()
