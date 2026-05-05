import json
import re
from pathlib import Path

# File paths
SCHEDULE_PATH = r'd:\Workspace\shanghaiport-fc-app\public\data\schedule.json'
SCHEDULE_B_PATH = r'd:\Workspace\shanghaiport-fc-app\public\data\schedule_b.json'
DATA_DIR = r'd:\Workspace\shanghaiport-fc-app\public\data'

def find_match_report(date, home_team, away_team):
    """根据日期和球队查找对应的赛事报告"""
    date_str = date.replace('-', '')
    # 构建可能的文件名模式
    patterns = [
        f"{date[:4]}-{date[5:7]}-{date[8:10]}-*.json",
    ]
    
    for pattern in patterns:
        for file_path in Path(DATA_DIR).glob(pattern):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 检查是否匹配
                report_date = data.get('match_info', {}).get('date', '')
                report_home = data.get('teams', {}).get('home', {}).get('name', '')
                report_away = data.get('teams', {}).get('away', {}).get('name', '')
                
                if report_date == date or (home_team in report_home or away_team in report_home):
                    return data
            except Exception as e:
                continue
    
    # 尝试在history目录中查找
    history_dir = Path(DATA_DIR) / 'history'
    if history_dir.exists():
        for year_dir in history_dir.iterdir():
            if year_dir.is_dir():
                for pattern in patterns:
                    for file_path in year_dir.glob(pattern):
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                            
                            report_date = data.get('match_info', {}).get('date', '')
                            report_home = data.get('teams', {}).get('home', {}).get('name', '')
                            report_away = data.get('teams', {}).get('away', {}).get('name', '')
                            
                            if report_date == date or (home_team in report_home or away_team in report_home):
                                return data
                        except Exception as e:
                            continue
    
    return None

def extract_match_info(report_data, home_team, away_team):
    """从赛事报告中提取所需信息"""
    info = {}
    
    # 获取裁判信息
    if 'referee' in report_data:
        info['referee'] = report_data['referee']
    else:
        info['referee'] = None
    
    # 获取主教练信息
    if 'home_coach' in report_data:
        info['home_coach'] = report_data['home_coach']
    if 'away_coach' in report_data:
        info['away_coach'] = report_data['away_coach']
    
    # 获取观众人数
    if 'attendance' in report_data:
        info['attendance'] = report_data['attendance']
    
    # 获取进球者
    info['scorers'] = {'home': [], 'away': []}
    
    # 从matchTimeline或highlights中提取进球者
    if 'matchTimeline' in report_data:
        for event in report_data['matchTimeline']:
            if event.get('type') == 'goal':
                player = event.get('player', '')
                team = event.get('team', '')
                if team == 'home' or (home_team in str(event.get('description', ''))):
                    info['scorers']['home'].append(player)
                else:
                    info['scorers']['away'].append(player)
    elif 'highlights' in report_data:
        for event in report_data['highlights']:
            if event.get('type') == 'goal':
                player = event.get('player', '')
                team = event.get('team', '')
                if team == 'home' or home_team in str(event.get('description', '')):
                    info['scorers']['home'].append(player)
                else:
                    info['scorers']['away'].append(player)
    
    # 清理空列表
    if not info['scorers']['home']:
        info['scorers']['home'] = []
    if not info['scorers']['away']:
        info['scorers']['away'] = []
    
    return info

def update_schedule(schedule_path, team_name):
    """更新赛程文件"""
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
                    info = extract_match_info(report, home_team, away_team)
                    
                    # 更新字段
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
    
    # 保存更新
    with open(schedule_path, 'w', encoding='utf-8') as f:
        json.dump(schedule, f, ensure_ascii=False, indent=2)
    
    print(f"\n  共更新 {updated_count} 场比赛")

def main():
    print("开始更新赛程文件...")
    
    # 更新一线队赛程
    update_schedule(SCHEDULE_PATH, '上海海港')
    
    # 更新B队赛程
    update_schedule(SCHEDULE_B_PATH, '上海海港富盛经开')
    
    print("\n更新完成！")

if __name__ == '__main__':
    main()