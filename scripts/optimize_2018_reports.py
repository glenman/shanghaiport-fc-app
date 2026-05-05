import csv
import json
import re
from pathlib import Path

SEASON = "2018"
ROSTER_CSV = r"datafile/上海海港2018一线队大名单.csv"
SCHEDULE_CSV = r"datafile/上海海港2018一线队中超赛程.csv"
JSON_DIR = r"public/data/history/2018"

TEAM_NAME_MAP = {
    "Shanghai SIPG": "上海海港",
    "Shanghai Port": "上海海港",
    "Shanghai Shenhua": "上海绿地",
    "Shanghai Greenland": "上海绿地",
    "Dalian Yifang": "大连一方",
    "Guangzhou R&F": "广州富力",
    "Chongqing Lifan": "重庆力帆",
    "Henan Jianye": "河南建业",
    "Hebei China Fortune": "河北华夏幸福",
    "Tianjin TEDA": "天津泰达",
    "Changchun Yatai": "长春亚泰",
    "Beijing Guoan": "北京国安",
    "Guizhou Hengfeng": "贵州恒丰",
    "Jiangsu Suning": "江苏苏宁",
    "Shandong Luneng": "山东泰山",
    "Guangzhou Evergrande": "广州恒大",
    "Beijing Renhe": "北京人和",
    "Tianjin Quanjian": "天津权健",
}

VENUE_NAME_MAP = {
    "Hongkou Stadium": "虹口足球场",
    "Tianhe Stadium": "天河体育场",
    "Workers Stadium": "工人体育场",
    "Shanghai Stadium": "上海体育场",
    "Yuanshen Stadium": "源深体育场",
}

def load_roster():
    """从CSV加载球员名单"""
    player_map = {}
    try:
        with open(ROSTER_CSV, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name_cn = row.get('中文名称', '').strip()
                name_en = row.get('英文名称', '').strip()
                if name_cn and name_en:
                    player_map[name_en] = name_cn
                    player_map[name_en.replace('á', 'a').replace('ó', 'o')] = name_cn
        print(f"✅ 已加载 {len(player_map)} 位球员信息")
        return player_map
    except Exception as e:
        print(f"❌ 加载球员名单失败: {e}")
        return {}

def load_schedule():
    """从CSV加载赛程信息"""
    schedule = {}
    try:
        with open(SCHEDULE_CSV, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                round_num = str(row.get('轮次', '')).strip()
                home = row.get('主队', '').strip()
                away = row.get('客队', '').strip()
                if round_num:
                    schedule[round_num] = {'home': home, 'away': away}
        print(f"✅ 已加载 {len(schedule)} 场比赛赛程")
        return schedule
    except Exception as e:
        print(f"❌ 加载赛程失败: {e}")
        return {}

def normalize_team_name(name):
    """标准化球队名称"""
    name = name.strip()
    for old, new in TEAM_NAME_MAP.items():
        if old in name:
            return new
    return name

def normalize_player_name(name, player_map):
    """标准化球员名称"""
    name = name.strip()
    if name in player_map:
        return player_map[name]
    for en, cn in player_map.items():
        if en in name:
            return cn
    return name

def normalize_competition_name(name):
    """标准化赛事名称"""
    name = name.strip()
    if "Chinese Super League" in name:
        return "中国足球协会超级联赛"
    return name

def normalize_venue_name(name):
    """标准化场地名称"""
    name = name.strip()
    for old, new in VENUE_NAME_MAP.items():
        if old in name:
            return new
    return name

def clean_formation(formation):
    """清理Formation中的队名"""
    match = re.search(r'\((\d+[-–]?)*\d+\)', formation)
    if match:
        return match.group(0)
    return formation

def get_round_from_filename(filename):
    """从文件名提取轮次"""
    match = re.match(r'\d{4}-\d{2}-\d{2}-中超-第(\d+)轮\.json', filename)
    if match:
        return match.group(1)
    return None

def is_shanghai_port_team(team_data):
    """判断是否是上海海港队"""
    name = team_data.get('name', '').strip()
    formation = team_data.get('formation', '')
    lineup = team_data.get('lineup', [])

    if "SIPG" in name or "Port" in name:
        return True
    if "SIPG" in formation:
        return True
    for player in lineup:
        p_name = player.get('name', '')
        if any(kw in p_name for kw in ["Yan Junling", "Hulk", "Oscar", "Elkeson", "Wu Lei"]):
            return True
    return False

def process_file(json_path, player_map, schedule):
    """处理单个JSON文件"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        round_num = get_round_from_filename(json_path.name)

        # 判断哪个是上海海港队
        is_home_port = is_shanghai_port_team(data['teams']['home'])
        is_away_port = is_shanghai_port_team(data['teams']['away'])

        # 交换主客队
        should_swap = False
        if round_num and round_num in schedule:
            sched = schedule[round_num]
            correct_home_is_port = "上海海港" in sched['home'] or "上海上港" in sched['home']
            current_home_is_port = is_home_port
            if correct_home_is_port != current_home_is_port:
                should_swap = True

        if should_swap:
            data['teams']['home'], data['teams']['away'] = data['teams']['away'], data['teams']['home']
            is_home_port, is_away_port = is_away_port, is_home_port
            # 更新事件team字段
            for event in data.get('events', []):
                if 'team' in event:
                    if event['team'] == 'home':
                        event['team'] = 'away'
                    elif event['team'] == 'away':
                        event['team'] = 'home'
            # 更新换人信息
            for team_key in ['home', 'away']:
                for sub in data['teams'][team_key].get('substitutions', []):
                    if 'team' in sub:
                        if sub['team'] == 'home':
                            sub['team'] = 'away'
                        elif sub['team'] == 'away':
                            sub['team'] = 'home'

        # 更新队名
        if round_num and round_num in schedule:
            sched = schedule[round_num]
            data['teams']['home']['name'] = normalize_team_name(sched['home'])
            data['teams']['home']['full_name'] = normalize_team_name(sched['home'])
            data['teams']['away']['name'] = normalize_team_name(sched['away'])
            data['teams']['away']['full_name'] = normalize_team_name(sched['away'])

        # 清理Formation
        for team_key in ['home', 'away']:
            if 'formation' in data['teams'][team_key]:
                data['teams'][team_key]['formation'] = clean_formation(data['teams'][team_key]['formation'])

        # 汉化上海海港球员
        for team_key in ['home', 'away']:
            team = data['teams'][team_key]
            should_process = (team_key == 'home' and is_home_port) or (team_key == 'away' and is_away_port)

            if should_process:
                for player in team.get('lineup', []):
                    player['name'] = normalize_player_name(player['name'], player_map)
                    if player.get('country') == 'Unknown':
                        player['country'] = '中国'

                for player in team.get('substitutes', []):
                    player['name'] = normalize_player_name(player['name'], player_map)
                    if player.get('country') == 'Unknown':
                        player['country'] = '中国'

                if 'coach' in team:
                    team['coach'] = normalize_player_name(team['coach'], player_map)
                if 'captain' in team:
                    team['captain'] = normalize_player_name(team['captain'], player_map)

                for sub in team.get('substitutions', []):
                    if 'player' in sub:
                        sub['player'] = normalize_player_name(sub['player'], player_map)
                    if 'player_out' in sub:
                        sub['player_out'] = normalize_player_name(sub['player_out'], player_map)

        # 汉化事件球员
        for event in data.get('events', []):
            if 'player' in event:
                event['player'] = normalize_player_name(event['player'], player_map)
            if 'player2' in event:
                event['player2'] = normalize_player_name(event['player2'], player_map)
            if 'player_out' in event:
                event['player_out'] = normalize_player_name(event['player_out'], player_map)

        # 汉化联赛名称
        if 'competition' in data.get('match_info', {}):
            comp = data['match_info']['competition']
            if 'name' in comp:
                comp['name'] = normalize_competition_name(comp['name'])
            if 'season' in comp:
                comp['season'] = SEASON
            if 'round' in comp:
                comp['round'] = f"第{round_num}轮"

        # 汉化场地
        if 'venue' in data.get('match_info', {}):
            venue = data['match_info']['venue']
            if 'name' in venue:
                venue['name'] = normalize_venue_name(venue['name'])

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return True
    except Exception as e:
        print(f"❌ 处理失败 {json_path.name}: {e}")
        return False

def main():
    print("=" * 60)
    print(f"{SEASON}赛季赛事报告优化处理")
    print("=" * 60)

    player_map = load_roster()
    schedule = load_schedule()

    json_dir = Path(JSON_DIR)
    json_files = sorted(list(json_dir.glob('*.json')))

    print(f"\n开始处理 {len(json_files)} 个文件...")

    success_count = 0
    for json_path in json_files:
        if process_file(json_path, player_map, schedule):
            success_count += 1
            print(f"  ✅ {json_path.name}")

    print("\n" + "=" * 60)
    print(f"处理完成! 成功 {success_count}/{len(json_files)}")
    print("=" * 60)

if __name__ == '__main__':
    main()
