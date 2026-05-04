
import csv
import json
import re
from pathlib import Path

SCHEDULE_CSV = r"datafile/上海海港2018一线队中超赛程.csv"
JSON_DIR = r"public/data/history/2018"

TEAM_MAP_EN = {
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

def get_team_name_candidates(team_data):
    name = team_data.get('name', '').strip()
    formation = team_data.get('formation', '')
    lineup = team_data.get('lineup', [])
    
    candidates = [name]
    if formation:
        match = re.search(r'^(.*?)\s*\(', formation)
        if match:
            candidates.append(match.group(1).strip())
    return candidates

def matches_team_name(candidates, target_chinese):
    target_english_list = TEAM_MAP_EN.get(target_chinese, [])
    for candidate in candidates:
        c_lower = candidate.lower()
        for target in target_english_list:
            if target.lower() in c_lower:
                return True
    return False

def is_shanghai_port(team_data):
    return matches_team_name(get_team_name_candidates(team_data), "上海海港")

def check_json(json_path, schedule):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        round_num = get_round_from_filename(json_path.name)
        if not round_num or round_num not in schedule:
            return False, "找不到赛程信息"
        
        correct = schedule[round_num]
        
        home_candidates = get_team_name_candidates(data['teams']['home'])
        away_candidates = get_team_name_candidates(data['teams']['away'])
        
        home_is_correct = matches_team_name(home_candidates, correct['home'])
        away_is_correct = matches_team_name(away_candidates, correct['away'])
        
        home_is_opponent = any('opponent' in c.lower() for c in home_candidates)
        away_is_opponent = any('opponent' in c.lower() for c in away_candidates)
        
        needs_swap = False
        if home_is_correct and away_is_correct:
            status = "✅ 主客队正确"
        elif (matches_team_name(home_candidates, correct['away']) and 
              matches_team_name(away_candidates, correct['home'])):
            status = "🔄 需要交换主客队"
            needs_swap = True
        else:
            status = "❌ 队名匹配有问题"
        
        return True, {
            'status': status,
            'needs_swap': needs_swap,
            'correct': correct,
            'current_home': home_candidates[0],
            'current_away': away_candidates[0]
        }
    except Exception as e:
        return False, str(e)

def main():
    print("="*80)
    print("2018赛季 主客队信息检查报告")
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
        if ok:
            if info['needs_swap']:
                swap_list.append(json_path.name)
                print(f"第 {get_round_from_filename(json_path.name):2} 轮 {json_path.name}: {info['status']}")
                print(f"    期望 主队={info['correct']['home']}, 客队={info['correct']['away']}")
                print(f"    当前 主队={info['current_home']}, 客队={info['current_away']}")
            else:
                ok_list.append(json_path.name)
                print(f"第 {get_round_from_filename(json_path.name):2} 轮 {json_path.name}: {info['status']}")
        else:
            problem_list.append(json_path.name)
            print(f"第 {get_round_from_filename(json_path.name):2} 轮 {json_path.name}: ❌ {info}")
    
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
