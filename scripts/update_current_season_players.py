import json
import os
import re

def load_official_players():
    """从players.json加载官方球员名单，建立中英文映射"""
    player_map = {}
    with open('public/data/players.json', encoding='utf-8') as f:
        players = json.load(f)
        for p in players:
            name = p['name']
            player_map[name] = name
            # 添加拼音/英文别名映射
            if 'english_name' in p and p['english_name']:
                player_map[p['english_name']] = name
            if 'pinyin' in p and p['pinyin']:
                player_map[p['pinyin']] = name
    return player_map

def find_player_name(name, player_map):
    """查找球员名称，支持多种匹配方式"""
    if not name:
        return name
    
    name = name.strip()
    
    # 精确匹配
    if name in player_map:
        return player_map[name]
    
    # 去除空格匹配
    name_no_space = name.replace(' ', '').replace('-', '').replace('.', '')
    for key in player_map:
        key_no_space = key.replace(' ', '').replace('-', '').replace('.', '')
        if name_no_space == key_no_space:
            return player_map[key]
    
    # 姓氏匹配
    last_name = name.split()[-1]
    for key in player_map:
        if last_name in key or key.split()[-1] in name:
            return player_map[key]
    
    return name

def update_player_name_in_dict(data, player_map, key):
    """更新字典中指定key的球员名称"""
    if key in data and isinstance(data[key], str):
        original = data[key]
        updated = find_player_name(original, player_map)
        if original != updated:
            data[key] = updated
            return True
    return False

def process_team_data(team_data, is_port_team, player_map):
    """处理球队数据中的球员姓名"""
    if not team_data:
        return
    
    # 更新首发球员
    if 'players' in team_data:
        for player in team_data['players']:
            update_player_name_in_dict(player, player_map, 'name')
    
    # 更新替补球员
    if 'substitutes' in team_data:
        for player in team_data['substitutes']:
            update_player_name_in_dict(player, player_map, 'name')
    
    # 更新换人信息
    if 'substitutions' in team_data:
        for sub in team_data['substitutions']:
            update_player_name_in_dict(sub, player_map, 'player')
            update_player_name_in_dict(sub, player_map, 'player_out')
            update_player_name_in_dict(sub, player_map, 'player_in')

def process_events(events, team_side, is_port_team, player_map):
    """处理事件中的球员姓名"""
    if not events:
        return
    
    for event in events:
        # 只处理海港队的事件
        event_team = event.get('team', '')
        is_event_port = (event_team == 'home' and team_side == 'home' and is_port_team) or \
                        (event_team == 'away' and team_side == 'away' and is_port_team)
        
        if is_event_port:
            update_player_name_in_dict(event, player_map, 'player')
            update_player_name_in_dict(event, player_map, 'player_out')
            update_player_name_in_dict(event, player_map, 'player_in')
            update_player_name_in_dict(event, player_map, 'player2')
            update_player_name_in_dict(event, player_map, 'captain')
            update_player_name_in_dict(event, player_map, 'scorer')

def process_match_report(filepath, player_map):
    """处理单个赛事报告文件"""
    print(f"处理: {os.path.basename(filepath)}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 判断海港是主队还是客队
    teams = data.get('teams', data.get('lineups', {}))
    home_name = teams.get('home', {}).get('name', '').strip() if isinstance(teams, dict) else ''
    away_name = teams.get('away', {}).get('name', '').strip() if isinstance(teams, dict) else ''
    
    home_is_port = any(name in home_name for name in ['上海海港', '海港', 'Shanghai Port'])
    away_is_port = any(name in away_name for name in ['上海海港', '海港', 'Shanghai Port'])
    
    # 处理球队数据
    if isinstance(teams, dict):
        if 'home' in teams:
            process_team_data(teams['home'], home_is_port, player_map)
        if 'away' in teams:
            process_team_data(teams['away'], away_is_port, player_map)
    
    # 处理事件数据
    events = data.get('events', [])
    if events:
        process_events(events, 'home', home_is_port, player_map)
        process_events(events, 'away', away_is_port, player_map)
    
    # 处理matchTimeline
    match_timeline = data.get('matchTimeline', [])
    if match_timeline:
        process_events(match_timeline, 'home', home_is_port, player_map)
        process_events(match_timeline, 'away', away_is_port, player_map)
    
    # 处理highlights
    highlights = data.get('highlights', [])
    if highlights:
        process_events(highlights, 'home', home_is_port, player_map)
        process_events(highlights, 'away', away_is_port, player_map)
    
    # 写回文件（保持原有格式）
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"  ✓ 完成")

def main():
    print("=== 当季球员名称汉化更新 ===")
    print("加载官方球员名单...")
    
    player_map = load_official_players()
    print(f"  已加载 {len(player_map)} 个球员名称")
    
    # 处理2026赛季的赛事报告
    match_files = [
        'public/data/2026-05-10-中超-第11轮.json',
        'public/data/2026-05-10-中乙-第8轮.json'
    ]
    
    for filepath in match_files:
        if os.path.exists(filepath):
            process_match_report(filepath, player_map)
        else:
            print(f"  ✗ 文件不存在: {filepath}")
    
    print("\n=== 处理完成 ===")

if __name__ == '__main__':
    main()