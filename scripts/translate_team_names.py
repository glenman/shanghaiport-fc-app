import os
import json
import re

HISTORY_SCHEDULE_PATH = '../public/data/history_schedule.json'
HISTORY_2025_DIR = '../public/data/history/2025'

TEAM_TRANSLATIONS = {
    'Shanghai Port': '上海海港',
    'Shanghai SIPG': '上海海港',
    'Shanghai Haigang': '上海海港',
    'Tianjin Jinmen Tiger': '天津津门虎',
    'Tianjin TEDA': '天津津门虎',
    'Henan': '河南俱乐部酒祖杜康',
    'Henan Jianye': '河南俱乐部酒祖杜康',
    'Songshan Longmen': '河南俱乐部酒祖杜康',
    'Shenzhen FC': '深圳新鹏城',
    'Shenzhen': '深圳新鹏城',
    '深圳鹏城': '深圳新鹏城',
    'Changchun Yatai': '长春亚泰',
    'Qingdao West Coast': '青岛西海岸',
    'Qingdao Hainiu': '青岛海牛',
    'Meizhou Hakka': '梅州客家',
    'Chengdu Rongcheng': '成都蓉城',
    'Chengdu Better City': '成都蓉城',
    'Yunnan Yukun': '云南玉昆',
    'Beijing Guoan': '北京国安',
    'Wuhan Three Towns': '武汉三镇',
    'Shandong Taishan': '山东泰山',
    'Shandong Luneng': '山东泰山',
    'Shanghai Shenhua': '上海申花',
    'Dalian Pro': '大连英博海发',
    'Dalian Yingbo': '大连英博海发',
    'Zhejiang Professional': '浙江俱乐部绿城',
    'Zhejiang Greentown': '浙江俱乐部绿城',
    'Zhejiang': '浙江俱乐部绿城',
    'Suzhou Dongwu': '苏州东吴',
    'Vissel Kobe': '神户胜利船',
    'Yokohama F. Marinos': '横滨水手',
    'Guangzhou FC': '广州队',
    'Guangzhou Evergrande': '广州队',
    'Sanfrecce Hiroshima': '广岛三箭',
    'Buriram United': '武里南联',
    'FC Seoul': '首尔FC',
    'Johor Darul Ta\'zim': '柔佛新山',
    'Machida Zelvia': '町田泽维亚',
    'Gwangju FC': '光州FC',
    'Shenzhen Ruby': '深圳新鹏城',
    'Shenzhen Pengcheng': '深圳新鹏城',
    'Nantong Zhiyun': '南通支云',
    'Cangzhou Mighty Lions': '沧州雄狮',
    'Qingdao Youth Island': '青岛西海岸',
}

def load_history_schedule():
    with open(HISTORY_SCHEDULE_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_team_names_by_date(schedule):
    teams_by_date = {}
    for match in schedule:
        if match['season'] == '2025':
            date = match['date']
            teams_by_date[date] = {
                'home': match['home_team'],
                'away': match['away_team']
            }
    return teams_by_date

def translate_team_name(name, teams_by_date=None, date=None):
    if teams_by_date and date:
        if date in teams_by_date:
            return teams_by_date[date]['home'] if name.lower() in ['home', 'henan', 'tianjin jinmen tiger'] else teams_by_date[date]['away']
    
    if name in TEAM_TRANSLATIONS:
        return TEAM_TRANSLATIONS[name]
    
    for eng, chn in TEAM_TRANSLATIONS.items():
        if eng.lower() in name.lower() or name.lower() in eng.lower():
            return chn
    
    return name

def extract_date_from_filename(filename):
    match = re.match(r'(\d{4}-\d{2}-\d{2})', filename)
    if match:
        return match.group(1)
    return None

def update_json_file(filepath, teams_by_date):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    filename = os.path.basename(filepath)
    date = extract_date_from_filename(filename)
    
    changes = []
    
    if 'match' in data:
        match_info = data['match']
        
        if 'homeTeam' in match_info:
            old_name = match_info['homeTeam']
            if date and date in teams_by_date:
                new_name = teams_by_date[date]['home']
            else:
                new_name = translate_team_name(old_name)
            
            if old_name != new_name and not re.match(r'^[\u4e00-\u9fff]', old_name):
                match_info['homeTeam'] = new_name
                changes.append(f'homeTeam: {old_name} -> {new_name}')
        
        if 'awayTeam' in match_info:
            old_name = match_info['awayTeam']
            if date and date in teams_by_date:
                new_name = teams_by_date[date]['away']
            else:
                new_name = translate_team_name(old_name)
            
            if old_name != new_name and not re.match(r'^[\u4e00-\u9fff]', old_name):
                match_info['awayTeam'] = new_name
                changes.append(f'awayTeam: {old_name} -> {new_name}')
    
    if 'lineups' in data:
        for side in ['home', 'away']:
            if side in data['lineups']:
                lineup = data['lineups'][side]
                if 'name' in lineup:
                    old_name = lineup['name']
                    if date and date in teams_by_date:
                        new_name = teams_by_date[date][side]
                    else:
                        new_name = translate_team_name(old_name)
                    
                    if old_name != new_name and not re.match(r'^[\u4e00-\u9fff]', old_name):
                        lineup['name'] = new_name
                        changes.append(f'lineups.{side}.name: {old_name} -> {new_name}')
    
    if 'summary' in data:
        summary = data['summary']
        for eng, chn in TEAM_TRANSLATIONS.items():
            if eng in summary:
                data['summary'] = summary.replace(eng, chn)
                changes.append(f'summary: {eng} -> {chn}')
                summary = data['summary']
    
    if changes:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    return changes

def main():
    schedule = load_history_schedule()
    teams_by_date = get_team_names_by_date(schedule)
    
    print("=== 球队名称翻译 ===\n")
    
    files = sorted([f for f in os.listdir(HISTORY_2025_DIR) if f.endswith('.json')])
    
    total_changes = 0
    
    for filename in files:
        filepath = os.path.join(HISTORY_2025_DIR, filename)
        changes = update_json_file(filepath, teams_by_date)
        
        if changes:
            print(f"\n📄 {filename}")
            for change in changes:
                print(f"   ✓ {change}")
            total_changes += len(changes)
    
    print(f"\n\n=== 完成 ===")
    print(f"共更新 {total_changes} 处")

if __name__ == '__main__':
    main()
