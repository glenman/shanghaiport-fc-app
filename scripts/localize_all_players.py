#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用球员姓名汉化脚本 - 处理所有层级的球员姓名字段
功能：递归遍历JSON结构，汉化所有球员姓名字段，并修复换人信息
"""

import csv
import json
import re
from pathlib import Path
import sys

PLAYER_FIELDS = ['name', 'player', 'player_out', 'player_in', 'player2', 'captain', 'scorer']

SHANGHAI_PORT_NAMES = ["Shanghai Port", "Shanghai Port FC", "SIPG", "上海海港", "上海上港", "上海东亚"]

def load_player_map(csv_path: str) -> dict:
    """从CSV文件加载球员映射"""
    player_map = {}
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name_en = row.get('英文名称', '').strip()
            name_cn = row.get('中文名称', '').strip()
            position = row.get('位置', '').strip()
            
            if name_en and name_cn:
                player_map[name_en] = {'name': name_cn, 'position': position}
                player_map[name_en.replace(' ', '')] = {'name': name_cn, 'position': position}
                player_map[name_en.lower()] = {'name': name_cn, 'position': position}
                player_map[name_cn] = {'name': name_cn, 'position': position}
    return player_map

def translate_player_name(name: str, player_map: dict) -> str:
    """翻译球员姓名"""
    if not name:
        return name
    
    if re.search(r'[\u4e00-\u9fff]', name):
        return name
    
    if name in player_map:
        return player_map[name]['name']
    
    name_no_space = name.replace(' ', '')
    if name_no_space in player_map:
        return player_map[name_no_space]['name']
    
    name_lower = name.lower()
    if name_lower in player_map:
        return player_map[name_lower]['name']
    
    return name

def is_port_team(team_name: str) -> bool:
    """判断是否是上海海港队"""
    if not team_name:
        return False
    team_name_lower = team_name.lower()
    for port_name in SHANGHAI_PORT_NAMES:
        if port_name.lower() in team_name_lower:
            return True
    return False

def process_data(data, is_port_side: bool, player_map: dict):
    """递归处理数据，汉化球员姓名"""
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if key in PLAYER_FIELDS and is_port_side:
                if isinstance(value, str):
                    result[key] = translate_player_name(value, player_map)
                else:
                    result[key] = process_data(value, is_port_side, player_map)
            else:
                result[key] = process_data(value, is_port_side, player_map)
        return result
    elif isinstance(data, list):
        return [process_data(item, is_port_side, player_map) for item in data]
    else:
        return data

def fill_substitutions_player_in(substitutions, substitution_map, team_side, is_port_team, player_map):
    """补充 substitutions 中的 player_in 字段并汉化球员姓名"""
    if not substitutions or not substitution_map:
        return substitutions
    
    filled_substitutions = []
    used_indices = {}
    
    for sub in substitutions:
        minute = sub.get('minute', 0)
        player_out = sub.get('player_out', '')
        player_in = sub.get('player_in', '')
        
        if is_port_team:
            player_out = translate_player_name(player_out, player_map)
        
        if not player_in and minute in substitution_map:
            minute_subs = substitution_map[minute]
            
            if len(minute_subs) == 1:
                player_in = minute_subs[0].get('player_in', '')
            else:
                found = False
                for idx, s in enumerate(minute_subs):
                    key = f"{minute}_{idx}"
                    if key in used_indices:
                        continue
                    
                    s_player_out = s.get('player_out', '')
                    if player_out and s_player_out:
                        p_out_normalized = player_out.lower().replace(' ', '')
                        s_p_out_normalized = s_player_out.lower().replace(' ', '')
                        if p_out_normalized == s_p_out_normalized or p_out_normalized in s_p_out_normalized or s_p_out_normalized in p_out_normalized:
                            player_in = s.get('player_in', '')
                            used_indices[key] = True
                            found = True
                            break
                
                if not found:
                    for idx, s in enumerate(minute_subs):
                        key = f"{minute}_{idx}"
                        if key not in used_indices:
                            player_in = s.get('player_in', '')
                            used_indices[key] = True
                            break
        
        if is_port_team:
            player_in = translate_player_name(player_in, player_map)
        
        filled_substitutions.append({
            'minute': minute,
            'minute_extra': sub.get('minute_extra'),
            'player_out': player_out,
            'player_in': player_in
        })
    
    return filled_substitutions

def process_file(file_path: Path, player_map: dict):
    """处理单个JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        teams = data.get('teams', {})
        home_name = teams.get('home', {}).get('name', '')
        away_name = teams.get('away', {}).get('name', '')
        
        home_is_port = is_port_team(home_name)
        away_is_port = is_port_team(away_name)
        
        events = data.get('events', [])
        processed_events = []
        substitution_map = {}
        
        for event in events:
            team = event.get('team', '')
            event_is_port = (team == 'home' and home_is_port) or (team == 'away' and away_is_port)
            processed_event = process_data(event, event_is_port, player_map)
            processed_events.append(processed_event)
            
            if processed_event.get('type') == 'substitution':
                minute = processed_event.get('minute', 0)
                player_in = processed_event.get('player', '')
                player_out = processed_event.get('player_out', '')
                if minute not in substitution_map:
                    substitution_map[minute] = []
                substitution_map[minute].append({'player_in': player_in, 'player_out': player_out})
        
        data['events'] = processed_events
        
        if 'home' in teams:
            data['teams']['home'] = process_data(teams['home'], home_is_port, player_map)
            if home_is_port and 'substitutions' in data['teams']['home']:
                data['teams']['home']['substitutions'] = fill_substitutions_player_in(
                    data['teams']['home']['substitutions'], substitution_map, 'home', home_is_port, player_map
                )
        
        if 'away' in teams:
            data['teams']['away'] = process_data(teams['away'], away_is_port, player_map)
            if away_is_port and 'substitutions' in data['teams']['away']:
                data['teams']['away']['substitutions'] = fill_substitutions_player_in(
                    data['teams']['away']['substitutions'], substitution_map, 'away', away_is_port, player_map
                )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ {file_path.name}")
        return True
    except Exception as e:
        print(f"✗ {file_path.name}: {str(e)}")
        return False

def main():
    if len(sys.argv) != 2:
        print("用法: python scripts/localize_all_players.py <赛季年份>")
        print("示例: python scripts/localize_all_players.py 2022")
        sys.exit(1)
    
    season = sys.argv[1]
    print(f"处理 {season} 赛季球员姓名汉化...")
    
    csv_path = f"datafile/上海海港{season}一线队大名单.csv"
    player_map = load_player_map(csv_path)
    print(f"已加载 {len(player_map)} 名球员")
    
    json_dir = Path(f"public/data/history/{season}")
    json_files = sorted(json_dir.glob("*.json"))
    
    success_count = 0
    for json_file in json_files:
        if process_file(json_file, player_map):
            success_count += 1
    
    print(f"\n处理完成: {success_count}/{len(json_files)} 个文件")

if __name__ == "__main__":
    main()