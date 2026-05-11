import json
import os

def load_official_players():
    """加载一线队官方球员名单"""
    with open('public/data/players.json', encoding='utf-8') as f:
        return {p['name'] for p in json.load(f)}

def load_b_team_players():
    """加载B队球员名单"""
    players = set()
    csv_path = 'datafile/上海海港B队大名单.csv'
    if os.path.exists(csv_path):
        import csv
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if '球员' in row:
                    players.add(row['球员'].strip())
                elif '姓名' in row:
                    players.add(row['姓名'].strip())
    return players

def check_match_report(filepath, official_players, b_team_players):
    """检查赛事报告中的海港球员"""
    print(f"\n=== 检查: {os.path.basename(filepath)} ===")
    with open(filepath, encoding='utf-8') as f:
        data = json.load(f)
    
    mismatches = []
    lineups = data.get('lineups', data.get('teams', {}))
    
    # 判断海港是主队还是客队
    home_name = lineups.get('home', {}).get('name', '')
    away_name = lineups.get('away', {}).get('name', '')
    
    home_is_port = '上海海港' in home_name or '海港富盛' in home_name
    away_is_port = '上海海港' in away_name or '海港' in away_name
    
    # 确定海港队数据位置
    if home_is_port:
        port_team = lineups.get('home', {})
        port_side = '主队'
        is_b_team = '富盛' in home_name
    elif away_is_port:
        port_team = lineups.get('away', {})
        port_side = '客队'
        is_b_team = False
    else:
        print("  未找到海港队数据")
        return True
    
    # 使用对应的球员名单
    target_players = b_team_players if is_b_team else official_players
    team_type = 'B队' if is_b_team else '一线队'
    
    print(f"  海港队位置: {port_side} ({team_type})")
    
    # 检查首发球员
    players = port_team.get('players', [])
    for player in players:
        name = player.get('name', '').strip()
        if name and name not in target_players:
            mismatches.append(f"首发: {name}")
    
    # 检查替补球员
    substitutes = port_team.get('substitutes', [])
    for player in substitutes:
        name = player.get('name', '').strip()
        if name and name not in target_players:
            mismatches.append(f"替补: {name}")
    
    # 检查换人信息
    substitutions = port_team.get('substitutions', [])
    for sub in substitutions:
        if 'player' in sub:
            name = sub['player'].strip()
            if name and name not in target_players:
                mismatches.append(f"换人入: {name}")
        if 'player_out' in sub:
            name = sub['player_out'].strip()
            if name and name not in target_players:
                mismatches.append(f"换人出: {name}")
    
    if mismatches:
        print("  发现不一致的球员姓名:")
        for m in mismatches:
            print(f"    - {m}")
        return False
    else:
        print("  所有海港球员姓名与官方名单一致")
        return True

def main():
    print("=== 海港球员姓名检查 ===")
    
    official_players = load_official_players()
    b_team_players = load_b_team_players()
    
    print(f"一线队球员名单数量: {len(official_players)}")
    print(f"B队球员名单数量: {len(b_team_players)}")
    
    # 检查赛事报告
    check_match_report('public/data/2026-05-10-中超-第11轮.json', official_players, b_team_players)
    check_match_report('public/data/2026-05-10-中乙-第8轮.json', official_players, b_team_players)

if __name__ == '__main__':
    main()