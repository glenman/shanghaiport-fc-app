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
            
            # 构建文件名模式
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
                        # 提取进球者
                        home_scorers = []
                        away_scorers = []
                        
                        home_players = report.get('lineups', {}).get('home', {}).get('players', [])
                        for p in home_players:
                            if p.get('goals', 0) > 0:
                                home_scorers.extend([p['name']] * p['goals'])
                        
                        away_players = report.get('lineups', {}).get('away', {}).get('players', [])
                        for p in away_players:
                            if p.get('goals', 0) > 0:
                                away_scorers.extend([p['name']] * p['goals'])
                        
                        # 更新schedule
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
                    continue
            
            if not found:
                print(f"⚠️ {date} {home_team} vs {away_team} - 未找到赛事报告")
    
    # 保存更新
    with open(SCHEDULE_PATH, 'w', encoding='utf-8') as f:
        json.dump(schedule, f, ensure_ascii=False, indent=2)
    
    print("\n更新完成！")

if __name__ == '__main__':
    update_all_scorers()