import json
import os
import re
import sys

def load_players(filepath):
    """加载球员名单"""
    player_map = {}
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            players = json.load(f)
            for p in players:
                name = p['name']
                player_map[name] = name
                # 添加拼音/英文别名映射
                if 'english_name' in p and p['english_name']:
                    player_map[p['english_name']] = name
                if 'pinyin' in p and p['pinyin']:
                    player_map[p['pinyin']] = name
    
    # 添加常见别名映射
    alias_map = {
        '乌米提江·玉素甫': '吾米提江',
        '乌米提江': '吾米提江',
        '莱奥': '莱昂纳多',
        '莱昂纳多·席尔瓦': '莱昂纳多',
        '布朗宁': '蒋光太',
        'Tyias Browning': '蒋光太',
        '马修·奥尔': '让克劳德',
        'Matthew Orr': '让克劳德',
        '科乔·阿齐安贝': '让克劳德',
        'Kodjo Aziangbe': '让克劳德',
        '吕永涛': '卢永涛'
    }
    for alias, correct_name in alias_map.items():
        if correct_name in player_map:
            player_map[alias] = correct_name
    
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

def normalize_venue(venue):
    """场地名称标准化"""
    venue_map = {
        'SAIC Motor Pudong Arena': '上汽浦东足球场',
        'Worker Stadium': '工人体育场',
        'Workers Stadium': '工人体育场'
    }
    return venue_map.get(venue, venue)

def normalize_competition(competition):
    """赛事名称标准化"""
    comp_map = {
        'Chinese Super League': '中国足球协会超级联赛',
        'CSL': '中国足球协会超级联赛'
    }
    return comp_map.get(competition, competition)

def process_team_data(team_data, is_port_team, player_map):
    """处理球队数据中的球员姓名"""
    if not team_data:
        return 0
    
    updated_count = 0
    
    # 更新首发球员
    if 'players' in team_data:
        for player in team_data['players']:
            if update_player_name_in_dict(player, player_map, 'name'):
                updated_count += 1
    
    # 更新替补球员
    if 'substitutes' in team_data:
        for player in team_data['substitutes']:
            if update_player_name_in_dict(player, player_map, 'name'):
                updated_count += 1
    
    # 更新换人信息
    if 'substitutions' in team_data:
        for sub in team_data['substitutions']:
            if update_player_name_in_dict(sub, player_map, 'player'):
                updated_count += 1
            if update_player_name_in_dict(sub, player_map, 'player_out'):
                updated_count += 1
            if update_player_name_in_dict(sub, player_map, 'player_in'):
                updated_count += 1
            # 支持驼峰格式（matchTimeline中使用）
            if update_player_name_in_dict(sub, player_map, 'playerOut'):
                updated_count += 1
            if update_player_name_in_dict(sub, player_map, 'playerIn'):
                updated_count += 1
    
    return updated_count

def process_events(events, team_side, is_port_team, player_map):
    """处理事件中的球员姓名"""
    if not events:
        return 0
    
    updated_count = 0
    
    for event in events:
        # 只处理海港队的事件
        event_team = event.get('team', '')
        is_event_port = (event_team == 'home' and team_side == 'home' and is_port_team) or \
                        (event_team == 'away' and team_side == 'away' and is_port_team)
        
        if is_event_port:
            if update_player_name_in_dict(event, player_map, 'player'):
                updated_count += 1
            if update_player_name_in_dict(event, player_map, 'player_out'):
                updated_count += 1
            if update_player_name_in_dict(event, player_map, 'player_in'):
                updated_count += 1
            # 支持驼峰格式（matchTimeline中使用）
            if update_player_name_in_dict(event, player_map, 'playerOut'):
                updated_count += 1
            if update_player_name_in_dict(event, player_map, 'playerIn'):
                updated_count += 1
            if update_player_name_in_dict(event, player_map, 'player2'):
                updated_count += 1
            if update_player_name_in_dict(event, player_map, 'captain'):
                updated_count += 1
            if update_player_name_in_dict(event, player_map, 'scorer'):
                updated_count += 1
    
    return updated_count

def process_match_report(filepath, first_team_players, b_team_players):
    """处理单个赛事报告文件"""
    filename = os.path.basename(filepath)
    print(f"\n处理: {filename}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    total_updates = 0
    
    # 判断赛事类型和海港队位置
    lineups = data.get('lineups', data.get('teams', {}))
    home_name = lineups.get('home', {}).get('name', '')
    away_name = lineups.get('away', {}).get('name', '')
    
    is_b_team = '富盛' in home_name or '富盛' in away_name
    is_first_team = '上海海港' in home_name or '上海海港' in away_name
    
    home_is_port = '上海海港' in home_name or '海港富盛' in home_name
    away_is_port = '上海海港' in away_name or '海港富盛' in away_name
    
    # 确定使用哪个球员名单
    if is_b_team:
        player_map = b_team_players
        team_type = 'B队'
    else:
        player_map = first_team_players
        team_type = '一线队'
    
    print(f"  球队类型: {team_type}")
    
    # 1. 场地名称汉化
    if 'match' in data and 'venue' in data['match']:
        original_venue = data['match']['venue']
        new_venue = normalize_venue(original_venue)
        if original_venue != new_venue:
            data['match']['venue'] = new_venue
            total_updates += 1
            print(f"  场地名称: {original_venue} → {new_venue}")
    
    # 2. 赛事名称标准化
    if 'match' in data and 'competition' in data['match']:
        original_comp = data['match']['competition']
        new_comp = normalize_competition(original_comp)
        if original_comp != new_comp:
            data['match']['competition'] = new_comp
            total_updates += 1
            print(f"  赛事名称: {original_comp} → {new_comp}")
    
    # 3. 球员名称标准化
    # 处理球队数据
    if isinstance(lineups, dict):
        if 'home' in lineups:
            total_updates += process_team_data(lineups['home'], home_is_port, player_map)
        if 'away' in lineups:
            total_updates += process_team_data(lineups['away'], away_is_port, player_map)
    
    # 处理事件数据
    for events_key in ['events', 'matchTimeline', 'highlights']:
        events = data.get(events_key, [])
        if events:
            total_updates += process_events(events, 'home', home_is_port, player_map)
            total_updates += process_events(events, 'away', away_is_port, player_map)
    
    # 4. 时间线描述标准化
    if 'matchTimeline' in data:
        for event in data['matchTimeline']:
            if 'description' in event:
                # 这里可以添加描述标准化逻辑
                pass
    
    # 写回文件（保持原有格式）
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    if total_updates > 0:
        print(f"  ✓ 完成，共更新 {total_updates} 处")
    else:
        print(f"  ✓ 完成，无需更新")
    
    return total_updates

def main():
    print("=== 赛事报告汉化和标准化处理 ===")
    
    # 加载球员名单
    print("\n加载球员名单...")
    first_team_players = load_players('public/data/players.json')
    b_team_players = load_players('public/data/players_b.json')
    print(f"  一线队球员: {len(first_team_players)} 人")
    print(f"  B队球员: {len(b_team_players)} 人")
    
    # 确定要处理的文件
    match_files = []
    
    if len(sys.argv) > 1:
        # 通过参数指定文件
        for filepath in sys.argv[1:]:
            if os.path.exists(filepath):
                match_files.append(filepath)
            else:
                print(f"  警告: 文件不存在 {filepath}")
    else:
        # 默认处理最新的2026赛季赛事报告
        match_files = [
            'public/data/2026-05-10-中超-第11轮.json',
            'public/data/2026-05-10-中乙-第8轮.json'
        ]
    
    if not match_files:
        print("\n未找到要处理的赛事报告文件")
        return
    
    # 处理文件
    total_updates = 0
    for filepath in match_files:
        if os.path.exists(filepath):
            total_updates += process_match_report(filepath, first_team_players, b_team_players)
    
    print(f"\n=== 全部完成，共更新 {total_updates} 处 ===")

if __name__ == '__main__':
    main()
