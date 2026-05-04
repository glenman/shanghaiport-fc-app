
import csv
import json
import re
from pathlib import Path

SCHEDULE_CSV = r"datafile/上海海港2018一线队中超赛程.csv"
JSON_DIR = r"public/data/history/2018"

TEAM_MAP = {
    "上海海港": ["Shanghai SIPG", "Shanghai Port"],
    "上海上港": ["Shanghai SIPG", "Shanghai Port"],
    "大连一方": ["Dalian Yifang"],
    "上海申花": ["Shanghai Shen", "Shanghai Greenland"],
    "广州富力": ["Guangzhou R&F", "Guangzhou RF"],
    "重庆力帆": ["Chongqing Lifan"],
    "河南建业": ["Henan Jianye"],
    "河北华夏幸福": ["Hebei China Fortune"],
    "天津泰达": ["Tianjin TEDA"],
    "长春亚泰": ["Changchun Yatai"],
    "北京国安": ["Beijing Guoan"],
    "贵州恒丰": ["Guizhou Hengfeng"],
    "江苏苏宁": ["Jiangsu Suning"],
    "山东鲁能": ["Shandong Luneng", "Shandong Taishan"],
    "广州恒大": ["Guangzhou Evergrande"],
    "北京人和": ["Beijing Renhe"],
    "天津权健": ["Tianjin Quanjian"]
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
    
    if "SIPG" in name or "Shanghai" in name and "Port" in name:
        return True
    if "SIPG" in formation:
        return True
    for player in lineup:
        p_name = player.get('name', '')
        if any(kw in p_name for kw in ["Yan Junling", "Hulk", "Oscar", "Elkeson", "Wu Lei", "Cai Huikang"]):
            return True
    return False

def get_opponent_chinese_name(team_data):
    name = team_data.get('name', '').strip()
    formation = team_data.get('formation', '')
    lineup = team_data.get('lineup', [])
    
    if "Opponent" in name:
        # 从formation或者lineup推断
        if formation:
            match = re.search(r'^(.*?)\s*\(', formation)
            if match:
                formation_name = match.group(1).strip()
                # 匹配已知球队
                for cn, en_list in TEAM_MAP.items():
                    for en in en_list:
                        if en in formation_name:
                            return cn
    
    # 检查name直接匹配
    for cn, en_list in TEAM_MAP.items():
        for en in en_list:
            if en in name:
                return cn
    
    # 检查lineup关键球员
    key_players = {
        "上海申花": ["Giovanni Moreno", "Odion Ighalo"],
        "广州恒大": ["Zheng Zhi", "Gao Lin", "Paulinho"],
        "北京国安": ["Zhang Xizhe", "Yu Dabao"],
        "山东鲁能": ["Wu Xinghan", "Hao Junmin"],
        "江苏苏宁": ["Wu Xi", "Teixeira"],
        "广州富力": ["Eran Zahavi"],
    }
    
    for cn, players in key_players.items():
        for player in lineup:
            p_name = player.get('name', '')
            if any(p in p_name for p in players):
                return cn
    
    return "Opponent"

def check_json(json_path, schedule):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        round_num = get_round_from_filename(json_path.name)
        if not round_num or round_num not in schedule:
            return False, "找不到赛程信息"
        
        correct = schedule[round_num]
        
        # 判断哪个是上海海港
        is_home_port = is_shanghai_port_team(data['teams']['home'])
        is_away_port = is_shanghai_port_team(data['teams']['away'])
        
        # 判断应该哪个是上海海港
        should_home_port = correct['home'] in ["上海海港", "上海上港"]
        should_away_port = correct['away'] in ["上海海港", "上海上港"]
        
        # 判断需要交换吗
        needs_swap = False
        if is_home_port and not should_home_port:
            needs_swap = True
        if is_away_port and not should_away_port:
            needs_swap = True
        
        # 获取另一个队名
        current_other_home = get_opponent_chinese_name(data['teams']['home']) if not is_home_port else "上海海港"
        current_other_away = get_opponent_chinese_name(data['teams']['away']) if not is_away_port else "上海海港"
        
        if needs_swap:
            status = "🔄 需要交换主客队"
        else:
            status = "✅ 主客队正确"
        
        return True, {
            'status': status,
            'needs_swap': needs_swap,
            'correct_home': correct['home'],
            'correct_away': correct['away'],
            'is_home_port': is_home_port,
            'is_away_port': is_away_port
        }
    except Exception as e:
        return False, str(e)

def main():
    print("="*80)
    print("2018赛季 主客队信息检查报告 (智能版)")
    print("="*80)
    
    schedule = load_schedule()
    print(f"✅ 加载到 {len(schedule)} 轮赛程！\n")
    
    json_dir = Path(JSON_DIR)
    json_files = sorted(list(json_dir.glob('*.json')))
    
    swap_list = []
    ok_list = []
    problem_list = []
    
    for json_path in json_files:
        ok, info = check_json(json_path, schedule)
        round_n = get_round_from_filename(json_path.name)
        if ok:
            if info['needs_swap']:
                swap_list.append(json_path.name)
                print(f"第 {round_n:2} 轮 {json_path.name}: {info['status']}")
                print(f"    期望: 主队={info['correct_home']}, 客队={info['correct_away']}")
                print(f"    状态: home_is_port={info['is_home_port']}, away_is_port={info['is_away_port']}")
            else:
                ok_list.append(json_path.name)
                print(f"第 {round_n:2} 轮 {json_path.name}: {info['status']}")
        else:
            problem_list.append(json_path.name)
            print(f"第 {round_n:2} 轮 {json_path.name}: ❌ {info}")
    
    print("\n" + "="*80)
    print(f"总结: 总共有 {len(json_files)} 场比赛！")
    print(f"      ✅ 主客队正确: {len(ok_list)} 场")
    print(f"      🔄 需要交换: {len(swap_list)} 场")
    print(f"      ❌ 有问题: {len(problem_list)} 场")
    if swap_list:
        print(f"\n需要交换的轮次: {swap_list}")
    print("="*80)

if __name__ == "__main__":
    main()
