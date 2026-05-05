import json
from pathlib import Path

SCHEDULE_PATH = r'd:\Workspace\shanghaiport-fc-app\public\data\schedule.json'
DATA_DIR = r'd:\Workspace\shanghaiport-fc-app\public\data'

def update_all_scorers():
    print("更新所有已结束比赛的进球者信息...\n")
    
    with open(SCHEDULE_PATH, 'r', encoding='utf-8') as f:
        schedule = json.load(f)
    
    for match in schedule:
        if match.get('status') == '已结束':
            date = match.get('date')
            home_team = match.get('homeTeam')
            away_team = match.get('awayTeam')
            result = match.get('result')
            
            if not date or not home_team or not away_team:
                continue
            
            date_parts = date.split('-')
            pattern = f"{date_parts[0]}-{date_parts[1]}-{date_parts[2]}-*.json"
            
            found = False
            for file_path in Path(DATA_DIR).glob(pattern):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        report = json.load(f)
                    
                    report_home = report.get('match', {}).get('homeTeam', '')
                    report_away = report.get('match', {}).get('awayTeam', '')
                    
                    if report_home == home_team and report_away == away_team:
                        home_scorers = []
                        away_scorers = []
                        
                        # 方法1: 从lineups中提取
                        home_players = report.get('lineups', {}).get('home', {}).get('players', [])
                        for p in home_players:
                            goals = p.get('goals', 0)
                            if goals > 0:
                                home_scorers.extend([p['name']] * goals)
                        
                        away_players = report.get('lineups', {}).get('away', {}).get('players', [])
                        for p in away_players:
                            goals = p.get('goals', 0)
                            if goals > 0:
                                away_scorers.extend([p['name']] * goals)
                        
                        # 方法2: 从matchDetails或其他数组中提取
                        if 'matchDetails' in report:
                            details = report['matchDetails']
                            if isinstance(details, list):
                                for event in details:
                                    if event.get('type') == 'goal':
                                        player = event.get('player', '')
                                        team = event.get('team', '')
                                        if team == 'home':
                                            home_scorers.append(player)
                                        elif team == 'away':
                                            away_scorers.append(player)
                        
                        # 方法3: 检查是否有其他统计数组
                        for key, value in report.items():
                            if isinstance(value, list):
                                for item in value:
                                    if isinstance(item, dict) and 'player' in item and 'goals' in item:
                                        player_name = item['player']
                                        goals = item.get('goals', 0)
                                        if goals > 0:
                                            # 判断是主队还是客队球员
                                            is_home = False
                                            for hp in home_players:
                                                if hp.get('name') == player_name:
                                                    is_home = True
                                                    break
                                            if is_home:
                                                home_scorers.extend([player_name] * goals)
                                            else:
                                                away_scorers.extend([player_name] * goals)
                        
                        match['scorers'] = {
                            'home': home_scorers,
                            'away': away_scorers
                        }
                        
                        print(f"✓ {date} {home_team} {result} {away_team}")
                        print(f"   进球者: 主队{home_scorers}, 客队{away_scorers}")
                        print()
                        found = True
                        break
                except Exception as e:
                    print(f"读取文件失败: {file_path} - {e}")
                    continue
            
            if not found:
                print(f"⚠️ {date} {home_team} vs {away_team} - 未找到赛事报告")
    
    with open(SCHEDULE_PATH, 'w', encoding='utf-8') as f:
        json.dump(schedule, f, ensure_ascii=False, indent=2)
    
    print("\n更新完成！")

if __name__ == '__main__':
    update_all_scorers()