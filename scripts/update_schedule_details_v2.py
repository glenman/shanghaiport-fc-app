import json
import re
from pathlib import Path

SCHEDULE_PATH = r'd:\Workspace\shanghaiport-fc-app\public\data\schedule.json'
SCHEDULE_B_PATH = r'd:\Workspace\shanghaiport-fc-app\public\data\schedule_b.json'
DATA_DIR = r'd:\Workspace\shanghaiport-fc-app\public\data'

def find_match_report(date, home_team, away_team):
    date_parts = date.split('-')
    pattern = f"{date_parts[0]}-{date_parts[1]}-{date_parts[2]}-*.json"
    
    for file_path in Path(DATA_DIR).glob(pattern):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            match_date = data.get('match', {}).get('date', '')
            match_home = data.get('match', {}).get('homeTeam', '')
            match_away = data.get('match', {}).get('awayTeam', '')
            
            if match_date == date or (home_team in match_home and away_team in match_away):
                return data
        except Exception as e:
            continue
    
    return None

def extract_match_info(report_data):
    info = {}
    
    # 裁判
    ref = report_data.get('officials', {}).get('referee', '')
    if not ref:
        ref = report_data.get('match', {}).get('referee', '')
    if ref:
        info['referee'] = ref
    
    # 主教练
    home_manager = report_data.get('lineups', {}).get('home', {}).get('manager', '')
    away_manager = report_data.get('lineups', {}).get('away', {}).get('manager', '')
    if home_manager:
        info['home_coach'] = home_manager
    if away_manager:
        info['away_coach'] = away_manager
    
    # 观众人数
    attendance = report_data.get('match', {}).get('attendance', '')
    if attendance:
        try:
            info['attendance'] = int(attendance)
        except:
            pass
    
    # 进球者
    info['scorers'] = {'home': [], 'away': []}
    
    home_players = report_data.get('lineups', {}).get('home', {}).get('players', [])
    for player in home_players:
        if player.get('goals', 0) > 0:
            info['scorers']['home'].append(player.get('name', ''))
    
    away_players = report_data.get('lineups', {}).get('away', {}).get('players', [])
    for player in away_players:
        if player.get('goals', 0) > 0:
            info['scorers']['away'].append(player.get('name', ''))
    
    return info

def update_schedule(schedule_path, team_name):
    print(f"\n=== 更新 {schedule_path} ===")
    
    with open(schedule_path, 'r', encoding='utf-8') as f:
        schedule = json.load(f)
    
    updated_count = 0
    
    for match in schedule:
        if match.get('status') == '已结束':
            date = match.get('date')
            home_team = match.get('homeTeam')
            away_team = match.get('awayTeam')
            
            if date and home_team and away_team:
                report = find_match_report(date, home_team, away_team)
                
                if report:
                    info = extract_match_info(report)
                    
                    updated = False
                    
                    if info.get('referee') and 'referee' not in match:
                        match['referee'] = info['referee']
                        updated = True
                    
                    if info.get('home_coach') and 'home_coach' not in match:
                        match['home_coach'] = info['home_coach']
                        updated = True
                    
                    if info.get('away_coach') and 'away_coach' not in match:
                        match['away_coach'] = info['away_coach']
                        updated = True
                    
                    if info.get('attendance') and 'attendance' not in match:
                        match['attendance'] = info['attendance']
                        updated = True
                    
                    if info['scorers'] and 'scorers' not in match:
                        match['scorers'] = info['scorers']
                        updated = True
                    
                    if updated:
                        updated_count += 1
                        print(f"  更新: {date} {home_team} vs {away_team}")
    
    with open(schedule_path, 'w', encoding='utf-8') as f:
        json.dump(schedule, f, ensure_ascii=False, indent=2)
    
    print(f"\n  共更新 {updated_count} 场比赛")

def main():
    print("开始更新赛程文件...")
    
    update_schedule(SCHEDULE_PATH, '上海海港')
    update_schedule(SCHEDULE_B_PATH, '上海海港富盛经开')
    
    print("\n更新完成！")

if __name__ == '__main__':
    main()