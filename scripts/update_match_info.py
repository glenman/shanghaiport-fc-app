import json
import re
import sys
from pathlib import Path
from datetime import datetime, timedelta

HISTORY_SCHEDULE_PATH = r'd:\Workspace\shanghaiport-fc-app\public\data\history_schedule.json'

CROSS_YEAR_SEASONS = {
    '2021': ['2022-01', '2022-02'],
    '2020': ['2021-01', '2021-02', '2021-03'],
    '2019': ['2020-01', '2020-02', '2020-03'],
}

COMPETITION_MAP = {
    'Chinese Super League': '中国足球协会超级联赛',
    'Chinese Football Association Super League': '中国足球协会超级联赛',
    'Chinese FA Cup': '中国足球协会杯',
    'AFC Champions League': '亚洲足球俱乐部冠军联赛',
    'AFC Champions League Elite': '亚洲足球俱乐部冠军联赛',
}

def load_season_schedule(season):
    """加载history_schedule.json中指定赛季的比赛数据，包括跨年赛季"""
    with open(HISTORY_SCHEDULE_PATH, 'r', encoding='utf-8') as f:
        schedule = json.load(f)

    matches = {}
    for match in schedule:
        if match.get('season') == season or match.get('date', '').startswith(season):
            date = match.get('date', '')
            matches[date] = match
    
    cross_year_prefixes = CROSS_YEAR_SEASONS.get(season, [])
    for prefix in cross_year_prefixes:
        for match in schedule:
            if match.get('date', '').startswith(prefix):
                date = match.get('date', '')
                if date not in matches:
                    matches[date] = match

    return matches

def find_matching_match(filename_date, matches):
    """尝试多种方式匹配日期"""
    if filename_date in matches:
        return filename_date, matches[filename_date]

    try:
        base_date = datetime.strptime(filename_date, '%Y-%m-%d')
        for delta in [-1, 1]:
            check_date = (base_date + timedelta(days=delta)).strftime('%Y-%m-%d')
            if check_date in matches:
                return check_date, matches[check_date]
    except:
        pass

    return None, None

def update_competition_info(data):
    """更新联赛信息（名称和轮次）"""
    updated = False
    
    if 'match_info' in data and 'competition' in data['match_info']:
        comp = data['match_info']['competition']
        
        if 'name' in comp:
            original_name = comp['name'].strip()
            # 精确匹配
            if original_name in COMPETITION_MAP:
                comp['name'] = COMPETITION_MAP[original_name]
                updated = True
            else:
                # 模糊匹配：检查是否包含关键字
                for key, value in COMPETITION_MAP.items():
                    if key.lower() in original_name.lower():
                        comp['name'] = value
                        updated = True
                        break
        
        if 'round' in comp:
            round_val = comp['round']
            if round_val.startswith('Matchweek '):
                comp['round'] = '第' + round_val.replace('Matchweek ', '') + '轮'
                updated = True
            elif round_val == 'Regular season':
                pass
        
    return updated

def update_match_report(report_path, match_data):
    """更新单个赛事报告"""
    with open(report_path, 'r', encoding='utf-8') as f:
        report = json.load(f)

    updated = False

    if 'teams' in report and 'home' in report['teams']:
        home_team = report['teams']['home']
        away_team = report['teams']['away']

        if match_data.get('home_team'):
            if home_team.get('name') != match_data['home_team']:
                home_team['name'] = match_data['home_team']
                home_team['full_name'] = match_data['home_team'] + '足球俱乐部'
                updated = True

        if match_data.get('away_team'):
            if away_team.get('name') != match_data['away_team']:
                away_team['name'] = match_data['away_team']
                away_team['full_name'] = match_data['away_team'] + '足球俱乐部'
                updated = True

        if match_data.get('home_coach'):
            if home_team.get('coach') != match_data['home_coach']:
                home_team['coach'] = match_data['home_coach']
                updated = True

        if match_data.get('away_coach'):
            if away_team.get('coach') != match_data['away_coach']:
                away_team['coach'] = match_data['away_coach']
                updated = True

    if 'match_info' in report:
        if match_data.get('venue'):
            venue_name = match_data['venue']
            if report['match_info'].get('venue', {}).get('name') != venue_name:
                report['match_info']['venue'] = {
                    'name': venue_name,
                    'city': match_data.get('city', ''),
                    'attendance': match_data.get('attendance', 0)
                }
                updated = True

        if match_data.get('attendance'):
            attendance = match_data['attendance']
            current_attendance = report['match_info'].get('venue', {}).get('attendance', 0)
            if current_attendance != attendance:
                if 'venue' not in report['match_info']:
                    report['match_info']['venue'] = {}
                report['match_info']['venue']['attendance'] = attendance
                updated = True

        if match_data.get('referee'):
            referee_name = match_data['referee']
            if report['match_info'].get('referee', {}).get('main') != referee_name:
                report['match_info']['referee'] = {
                    'main': referee_name,
                    'country': 'China'
                }
                updated = True

        if match_data.get('city'):
            city = match_data['city']
            if 'venue' not in report['match_info']:
                report['match_info']['venue'] = {'name': '', 'city': city}
            elif 'city' not in report['match_info']['venue']:
                report['match_info']['venue']['city'] = city
                updated = True

    comp_updated = update_competition_info(report)
    updated = updated or comp_updated

    return updated, report

def main():
    if len(sys.argv) != 2:
        print("用法: python scripts/update_match_info.py <赛季年份>")
        print("示例: python scripts/update_match_info.py 2022")
        sys.exit(1)

    season = sys.argv[1]
    print(f'加载{season}赛季比赛数据...')
    matches = load_season_schedule(season)
    print(f'加载了 {len(matches)} 场{season}赛季比赛')

    history_dir = Path(f'public/data/history/{season}')
    json_files = list(history_dir.glob('*.json'))
    print(f'找到 {len(json_files)} 个赛事报告文件')

    updated_count = 0
    matched_count = 0
    unmatched_files = []

    for json_file in json_files:
        filename = json_file.stem
        date_match = re.match(r'(\d{4}-\d{2}-\d{2})', filename)
        if not date_match:
            print(f'无法从文件名提取日期: {filename}')
            continue

        filename_date = date_match.group(1)
        matched_date, match_data = find_matching_match(filename_date, matches)

        if not matched_date:
            unmatched_files.append((filename, filename_date))
            print(f'未找到匹配: {filename} (尝试日期: {filename_date})')
            continue

        print(f'匹配成功: {filename} -> {matched_date}')

        updated, report = update_match_report(json_file, match_data)

        if updated:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            updated_count += 1
            print(f'  已更新: {filename}')

        matched_count += 1

    print(f'\n更新完成！')
    print(f'匹配比赛: {matched_count}')
    print(f'更新文件: {updated_count}')
    print(f'未匹配文件: {len(unmatched_files)}')

    if unmatched_files:
        print('\n未匹配的文件列表:')
        for filename, date in unmatched_files:
            print(f'  {filename} (日期: {date})')

if __name__ == '__main__':
    main()