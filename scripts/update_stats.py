#!/usr/bin/env python3
"""
统计上海海港足球俱乐部当季数据
自动从比赛数据文件中提取统计信息并更新current_stats.json
支持全部重新抓取和增量抓取
"""

import json
import os
import argparse
from datetime import datetime

# 数据文件路径
data_dir = 'public/data'
output_file = 'public/data/current_stats.json'

# 球队名称映射
TEAM_NAMES = {
    'first': '上海海港',
    'b_team': '上海海港富盛经开'
}

# 比赛类型映射
COMPETITIONS = {
    '中超': '中国足球协会超级联赛',
    '中乙': '中国足球协会乙级联赛'
}

def load_json_file(file_path):
    """加载JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载文件 {file_path} 失败: {e}")
        return None

def is_first_team_match(home_team, away_team):
    """判断是否为一线队比赛"""
    return TEAM_NAMES['first'] in [home_team, away_team]

def is_b_team_match(home_team, away_team):
    """判断是否为B队比赛"""
    b_team_names = [TEAM_NAMES['b_team'], '上海海港B队']
    for name in b_team_names:
        if name in [home_team, away_team]:
            return True
    return False

def get_team_role(team_name, home_team, away_team):
    """获取球队角色（home或away）"""
    # 处理B队的不同名称
    if team_name == TEAM_NAMES['b_team']:
        b_team_names = [TEAM_NAMES['b_team'], '上海海港B队']
        for name in b_team_names:
            if name == home_team:
                return 'home'
            elif name == away_team:
                return 'away'
    elif team_name == home_team:
        return 'home'
    elif team_name == away_team:
        return 'away'
    return None

def calculate_record(matches):
    """计算战绩"""
    wins = 0
    draws = 0
    losses = 0
    goals_for = 0
    goals_against = 0

    for match in matches:
        home_score, away_score = map(int, match['result'].split('-'))

        if match['team_role'] == 'home':
            if home_score > away_score:
                wins += 1
            elif home_score == away_score:
                draws += 1
            else:
                losses += 1
            goals_for += home_score
            goals_against += away_score
        else:  # away
            if away_score > home_score:
                wins += 1
            elif away_score == home_score:
                draws += 1
            else:
                losses += 1
            goals_for += away_score
            goals_against += home_score

    points = wins * 3 + draws
    record = f"{wins}胜{draws}平{losses}负"

    return record, points, goals_for, goals_against

def process_matches(full_update=False, last_update_date=None):
    """处理比赛文件
    
    Args:
        full_update: 是否全部重新抓取
        last_update_date: 上次更新时间，用于增量抓取
    """
    first_team_matches = []
    b_team_matches = []

    # 遍历所有JSON文件
    for filename in os.listdir(data_dir):
        if filename.endswith('.json') and not filename.startswith('current_stats') and not filename.startswith('players') and not filename.startswith('schedule'):
            file_path = os.path.join(data_dir, filename)
            
            # 检查文件修改时间
            if not full_update and last_update_date:
                file_mtime = os.path.getmtime(file_path)
                file_modify_date = datetime.fromtimestamp(file_mtime).date()
                if file_modify_date <= last_update_date:
                    continue
            
            data = load_json_file(file_path)

            if data and 'match' in data:
                match_info = data['match']
                home_team = match_info.get('homeTeam', '')
                away_team = match_info.get('awayTeam', '')
                result = match_info.get('result', '')
                status = match_info.get('status', '')

                # 只处理已结束的比赛
                if status == '已结束' and result and '-' in result:
                    # 检查是否为一线队比赛
                    if is_first_team_match(home_team, away_team):
                        team_role = get_team_role(TEAM_NAMES['first'], home_team, away_team)
                        if team_role:
                            first_team_matches.append({
                                'file': filename,
                                'home_team': home_team,
                                'away_team': away_team,
                                'result': result,
                                'team_role': team_role,
                                'data': data
                            })

                    # 检查是否为B队比赛
                    elif is_b_team_match(home_team, away_team):
                        team_role = get_team_role(TEAM_NAMES['b_team'], home_team, away_team)
                        if team_role:
                            b_team_matches.append({
                                'file': filename,
                                'home_team': home_team,
                                'away_team': away_team,
                                'result': result,
                                'team_role': team_role,
                                'data': data
                            })

    return first_team_matches, b_team_matches

def extract_statistics(matches, team_name):
    """提取统计数据"""
    # 统计球员数据
    player_stats = {}

    # 详细事件记录
    details = {
        'goals': {},
        'assists': {},
        'yellowCards': {},
        'redCards': {}
    }

    # 已统计的事件（用于去重）
    counted_events = {
        'yellowCards': set(),
        'redCards': set()
    }

    for match in matches:
        data = match['data']
        team_role = match['team_role']
        opponent = match['home_team'] if team_role == 'away' else match['away_team']
        match_info = data.get('match', {})
        match_round = match_info.get('round', '未知')
        match_date = match_info.get('date', '未知')
        match_time = match_info.get('time', '')

        # 处理比赛亮点（进球和助攻）
        if 'highlights' in data:
            for highlight in data['highlights']:
                if highlight.get('type') == 'goal' and highlight.get('team') == team_role:
                    scorer = highlight.get('player', '')
                    assist = highlight.get('player2', '')
                    minute = highlight.get('minute', 0)
                    minute_extra = highlight.get('minute_extra', 0)
                    goal_type = highlight.get('goal_type', 'regular')

                    # 处理名字简写
                    name_mapping = {
                        '克劳德': '让克劳德',
                        '让·克劳德': '让克劳德',
                        '维塔尔': '维塔尔'
                    }
                    if scorer in name_mapping:
                        scorer = name_mapping[scorer]
                    if assist in name_mapping:
                        assist = name_mapping[assist]

                    if scorer:
                        if scorer not in player_stats:
                            player_stats[scorer] = {
                                'name': scorer,
                                'number': 0,
                                'position': '',
                                'goals': 0,
                                'assists': 0,
                                'yellowCards': 0,
                                'redCards': 0,
                                'matches': 0,
                                'minutes': 0
                            }
                        player_stats[scorer]['goals'] += 1
                        if scorer not in details['goals']:
                            details['goals'][scorer] = []
                        details['goals'][scorer].append({
                            'match': match_round,
                            'date': match_date,
                            'time': f"{minute}'" + (f"+{minute_extra}'" if minute_extra else ''),
                            'opponent': opponent,
                            'type': '乌龙球' if goal_type == 'own_goal' else '进球'
                        })

                    if assist:
                        if assist not in player_stats:
                            player_stats[assist] = {
                                'name': assist,
                                'number': 0,
                                'position': '',
                                'goals': 0,
                                'assists': 0,
                                'yellowCards': 0,
                                'redCards': 0,
                                'matches': 0,
                                'minutes': 0
                            }
                        player_stats[assist]['assists'] += 1
                        if assist not in details['assists']:
                            details['assists'][assist] = []
                        details['assists'][assist].append({
                            'match': match_round,
                            'date': match_date,
                            'time': f"{minute}'",
                            'opponent': opponent
                        })

        # 从 matchTimeline 中提取黄牌和红牌事件
        if 'matchTimeline' in data:
            for event in data['matchTimeline']:
                event_type = event.get('type', '')
                event_team = event.get('team', '')

                # 判断是否是本方球队的事件
                # team_role 表示上海海港在这场比赛中的角色（home或away）
                # event_team 表示事件发生在哪一方（home或away）
                # 如果两者相同，说明是上海海港的事件
                if event_team != team_role:
                    continue

                if event_type == 'yellow_card':
                    player = event.get('player', '')
                    minute = event.get('minute', 0)
                    description = event.get('description', '')

                    name_mapping = {
                        '克劳德': '让克劳德',
                        '让·克劳德': '让克劳德',
                        '维塔尔': '维塔尔'
                    }
                    if player in name_mapping:
                        player = name_mapping[player]

                    # 去重检查 - 只根据球员和分钟去重
                    event_key = (player, minute)
                    if event_key in counted_events['yellowCards']:
                        continue
                    counted_events['yellowCards'].add(event_key)

                    if player:
                        if player not in player_stats:
                            player_stats[player] = {
                                'name': player,
                                'number': 0,
                                'position': '',
                                'goals': 0,
                                'assists': 0,
                                'yellowCards': 0,
                                'redCards': 0,
                                'matches': 0,
                                'minutes': 0
                            }
                        player_stats[player]['yellowCards'] += 1
                        if player not in details['yellowCards']:
                            details['yellowCards'][player] = []
                        details['yellowCards'][player].append({
                            'match': match_round,
                            'date': match_date,
                            'time': f"{minute}'",
                            'opponent': opponent,
                            'reason': description
                        })

                elif event_type == 'red_card':
                    player = event.get('player', '')
                    minute = event.get('minute', 0)
                    description = event.get('description', '')

                    name_mapping = {
                        '克劳德': '让克劳德',
                        '让·克劳德': '让克劳德',
                        '维塔尔': '维塔尔'
                    }
                    if player in name_mapping:
                        player = name_mapping[player]

                    # 去重检查 - 只根据球员和分钟去重
                    event_key = (player, minute)
                    if event_key in counted_events['redCards']:
                        continue
                    counted_events['redCards'].add(event_key)

                    if player:
                        if player not in player_stats:
                            player_stats[player] = {
                                'name': player,
                                'number': 0,
                                'position': '',
                                'goals': 0,
                                'assists': 0,
                                'yellowCards': 0,
                                'redCards': 0,
                                'matches': 0,
                                'minutes': 0
                            }
                        player_stats[player]['redCards'] += 1
                        if player not in details['redCards']:
                            details['redCards'][player] = []
                        details['redCards'][player].append({
                            'match': match_round,
                            'date': match_date,
                            'time': f"{minute}'",
                            'opponent': opponent,
                            'reason': description
                        })

        # 处理阵容数据（仅用于获取球员基本信息）
        if 'lineups' in data and 'home' in data['lineups'] and 'away' in data['lineups']:
            team_lineup = data['lineups'][team_role]

            name_mapping = {
                '克劳德': '让克劳德',
                '让·克劳德': '让克劳德',
                '维塔尔': '维塔尔'
            }

            # 处理首发球员
            if 'players' in team_lineup:
                for player in team_lineup['players']:
                    name = player.get('name', '')
                    if name and name in name_mapping:
                        name = name_mapping[name]

                    if name:
                        if name not in player_stats:
                            player_stats[name] = {
                                'name': name,
                                'number': player.get('number', 0),
                                'position': player.get('position', ''),
                                'goals': 0,
                                'assists': 0,
                                'yellowCards': 0,
                                'redCards': 0,
                                'matches': 0,
                                'minutes': 0
                            }
                        else:
                            # 更新已存在球员的号码和位置信息
                            player_stats[name]['number'] = player.get('number', 0) or player_stats[name]['number']
                            player_stats[name]['position'] = player.get('position', '') or player_stats[name]['position']
                        player_stats[name]['matches'] += 1
                        if 'minutes' in player:
                            player_stats[name]['minutes'] += player['minutes']

            # 处理替补球员
            if 'substitutes' in team_lineup:
                for player in team_lineup['substitutes']:
                    name = player.get('name', '')
                    if name and name in name_mapping:
                        name = name_mapping[name]

                    if name:
                        if name not in player_stats:
                            player_stats[name] = {
                                'name': name,
                                'number': player.get('number', 0),
                                'position': player.get('position', ''),
                                'goals': 0,
                                'assists': 0,
                                'yellowCards': 0,
                                'redCards': 0,
                                'matches': 0,
                                'minutes': 0
                            }
                        else:
                            # 更新已存在球员的号码和位置信息
                            player_stats[name]['number'] = player.get('number', 0) or player_stats[name]['number']
                            player_stats[name]['position'] = player.get('position', '') or player_stats[name]['position']
                        player_stats[name]['matches'] += 1

    # 生成各项榜单
    top_scorers = []
    top_assists = []
    yellow_cards = []
    red_cards = []

    for name, stats in player_stats.items():
        if stats['goals'] > 0:
            top_scorers.append({
                'rank': 0,
                'name': name,
                'number': stats['number'],
                'goals': stats['goals'],
                'details': details['goals'].get(name, [])
            })

        if stats['assists'] > 0:
            top_assists.append({
                'rank': 0,
                'name': name,
                'number': stats['number'],
                'assists': stats['assists'],
                'details': details['assists'].get(name, [])
            })

        if stats['yellowCards'] > 0:
            yellow_cards.append({
                'rank': 0,
                'name': name,
                'number': stats['number'],
                'yellowCards': stats['yellowCards'],
                'details': details['yellowCards'].get(name, [])
            })

        if stats['redCards'] > 0:
            red_cards.append({
                'rank': 0,
                'name': name,
                'number': stats['number'],
                'redCards': stats['redCards'],
                'details': details['redCards'].get(name, [])
            })

    # 排序并设置排名
    top_scorers.sort(key=lambda x: x['goals'], reverse=True)
    for i, scorer in enumerate(top_scorers, 1):
        scorer['rank'] = i

    top_assists.sort(key=lambda x: x['assists'], reverse=True)
    for i, assist in enumerate(top_assists, 1):
        assist['rank'] = i

    yellow_cards.sort(key=lambda x: x['yellowCards'], reverse=True)
    for i, card in enumerate(yellow_cards, 1):
        card['rank'] = i

    red_cards.sort(key=lambda x: x['redCards'], reverse=True)
    for i, card in enumerate(red_cards, 1):
        card['rank'] = i

    return top_scorers, top_assists, yellow_cards, red_cards

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='统计上海海港足球俱乐部当季数据')
    parser.add_argument('--full', action='store_true', help='全部重新抓取数据')
    parser.add_argument('--incremental', action='store_true', help='增量抓取数据')
    args = parser.parse_args()
    
    print("开始统计当季数据...")
    
    # 检查是否存在current_stats.json文件，获取上次更新时间
    last_update_date = None
    if not args.full and os.path.exists(output_file):
        existing_data = load_json_file(output_file)
        if existing_data and 'lastUpdated' in existing_data:
            last_update_date_str = existing_data['lastUpdated']
            try:
                last_update_date = datetime.strptime(last_update_date_str, '%Y-%m-%d').date()
                print(f"上次更新时间: {last_update_date_str}")
            except ValueError:
                print("无法解析上次更新时间，将进行全部重新抓取")
                last_update_date = None
    
    # 处理比赛文件
    first_team_matches, b_team_matches = process_matches(full_update=args.full or not args.incremental, last_update_date=last_update_date)

    print(f"找到一线队比赛: {len(first_team_matches)}场")
    print(f"找到B队比赛: {len(b_team_matches)}场")
    
    if not first_team_matches and not b_team_matches:
        if last_update_date:
            print("没有发现新的赛事报告，数据已是最新")
        else:
            print("没有找到符合条件的比赛数据")
        return

    # 统计一线队数据
    first_team_record, first_team_points, first_team_goals_for, first_team_goals_against = calculate_record(first_team_matches)
    first_team_scorers, first_team_assists, first_team_yellow, first_team_red = extract_statistics(first_team_matches, TEAM_NAMES['first'])

    # 统计B队数据
    b_team_record, b_team_points, b_team_goals_for, b_team_goals_against = calculate_record(b_team_matches)
    b_team_scorers, b_team_assists, b_team_yellow, b_team_red = extract_statistics(b_team_matches, TEAM_NAMES['b_team'])

    # 生成统计结果
    stats_data = {
        'lastUpdated': datetime.now().strftime('%Y-%m-%d'),
        'season': '2026',
        'firstTeam': {
            'teamName': TEAM_NAMES['first'],
            'competition': COMPETITIONS['中超'],
            'matchesPlayed': len(first_team_matches),
            'record': first_team_record,
            'goalsFor': first_team_goals_for,
            'goalsAgainst': first_team_goals_against,
            'points': first_team_points,
            'topScorers': first_team_scorers,
            'topAssists': first_team_assists,
            'yellowCards': first_team_yellow,
            'redCards': first_team_red
        },
        'bTeam': {
            'teamName': TEAM_NAMES['b_team'],
            'competition': COMPETITIONS['中乙'],
            'matchesPlayed': len(b_team_matches),
            'record': b_team_record,
            'goalsFor': b_team_goals_for,
            'goalsAgainst': b_team_goals_against,
            'points': b_team_points,
            'topScorers': b_team_scorers,
            'topAssists': b_team_assists,
            'yellowCards': b_team_yellow,
            'redCards': b_team_red
        }
    }

    # 保存结果
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(stats_data, f, ensure_ascii=False, indent=2)
        print(f"统计数据已保存到 {output_file}")
        print(f"一线队: {first_team_record}, 积分: {first_team_points}")
        print(f"B队: {b_team_record}, 积分: {b_team_points}")
    except Exception as e:
        print(f"保存文件失败: {e}")

if __name__ == '__main__':
    main()