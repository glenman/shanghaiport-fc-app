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
                        
                        # 优先从highlights提取
                        if 'highlights' in report:
                            for event in report['highlights']:
                                if event.get('type') == 'goal':
                                    player = event.get('player', '').strip()
                                    team = event.get('team', '')
                                    if player:
                                        if team == 'home':
                                            home_scorers.append(player)
                                        elif team == 'away':
                                            away_scorers.append(player)
                        
                        # 如果highlights不够，从matchTimeline补充
                        if 'matchTimeline' in report and (len(home_scorers) == 0 or len(away_scorers) == 0):
                            for event in report['matchTimeline']:
                                if event.get('type') == 'goal':
                                    player = event.get('player', '').strip()
                                    team = event.get('team', '')
                                    if player and team:
                                        if team == 'home' and player not in home_scorers:
                                            home_scorers.append(player)
                                        elif team == 'away' and player not in away_scorers:
                                            away_scorers.append(player)
                        
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