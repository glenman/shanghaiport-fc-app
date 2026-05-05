import json
import re
from pathlib import Path
from datetime import datetime, timedelta

HISTORY_SCHEDULE_PATH = r'd:\Workspace\shanghaiport-fc-app\public\data\history_schedule.json'
HISTORY_2018_PATH = r'd:\Workspace\shanghaiport-fc-app\public\data\history\2018'

SHANGHAI_PORT_NAMES = ['上海海港', '上海上港', '上海东亚', '上海特莱士']

def load_2018_schedule():
    """加载history_schedule.json中2018赛季的比赛数据"""
    with open(HISTORY_SCHEDULE_PATH, 'r', encoding='utf-8') as f:
        schedule = json.load(f)

    matches_2018 = {}
    for match in schedule:
        if match.get('season') == '2018' or match.get('date', '').startswith('2018-'):
            date = match.get('date', '')
            matches_2018[date] = match

    return matches_2018

def find_matching_match(filename_date, matches_2018):
    """尝试多种方式匹配日期"""
    # 直接匹配
    if filename_date in matches_2018:
        return filename_date, matches_2018[filename_date]

    # 尝试±1天
    try:
        base_date = datetime.strptime(filename_date, '%Y-%m-%d')
        for delta in [-1, 1]:
            check_date = (base_date + timedelta(days=delta)).strftime('%Y-%m-%d')
            if check_date in matches_2018:
                return check_date, matches_2018[check_date]
    except:
        pass

    return None, None

def update_match_report(report_path, match_data):
    """更新单个赛事报告"""
    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()
        report = json.loads(content)

    updated = False

    # 更新主队信息
    if 'teams' in report and 'home' in report['teams']:
        home_team = report['teams']['home']
        away_team = report['teams']['away']

        # 更新主队名称
        if match_data.get('home_team'):
            if home_team.get('name') != match_data['home_team']:
                home_team['name'] = match_data['home_team']
                updated = True

        # 更新客队名称
        if match_data.get('away_team'):
            if away_team.get('name') != match_data['away_team']:
                away_team['name'] = match_data['away_team']
                updated = True

        # 更新主队主教练
        if match_data.get('home_coach'):
            if home_team.get('coach') != match_data['home_coach']:
                home_team['coach'] = match_data['home_coach']
                updated = True

        # 更新客队主教练
        if match_data.get('away_coach'):
            if away_team.get('coach') != match_data['away_coach']:
                away_team['coach'] = match_data['away_coach']
                updated = True

    # 更新match_info中的场地信息
    if 'match_info' in report:
        match_info = report['match_info']

        # 更新场地名称
        if match_data.get('venue'):
            venue_name = match_data['venue']
            if report['match_info'].get('venue', {}).get('name') != venue_name:
                report['match_info']['venue'] = {
                    'name': venue_name,
                    'city': match_data.get('city', ''),
                    'attendance': match_data.get('attendance', 0)
                }
                updated = True

        # 更新观众人数
        if match_data.get('attendance'):
            attendance = match_data['attendance']
            current_attendance = report['match_info'].get('venue', {}).get('attendance', 0)
            if current_attendance != attendance:
                if 'venue' not in report['match_info']:
                    report['match_info']['venue'] = {}
                report['match_info']['venue']['attendance'] = attendance
                updated = True

        # 更新主裁判
        if match_data.get('referee'):
            referee_name = match_data['referee']
            if report['match_info'].get('referee', {}).get('main') != referee_name:
                report['match_info']['referee'] = {
                    'main': referee_name,
                    'country': 'China'
                }
                updated = True

        # 新建比赛城市字段
        if match_data.get('city'):
            city = match_data['city']
            if 'venue' not in report['match_info']:
                report['match_info']['venue'] = {'name': '', 'city': city}
            elif 'city' not in report['match_info']['venue']:
                report['match_info']['venue']['city'] = city
                updated = True

    return updated, report

def main():
    print('加载2018赛季比赛数据...')
    matches_2018 = load_2018_schedule()
    print(f'加载了 {len(matches_2018)} 场2018赛季比赛')

    history_dir = Path(HISTORY_2018_PATH)
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

        # 查找匹配的日期
        matched_date, match_data = find_matching_match(filename_date, matches_2018)

        if not matched_date:
            unmatched_files.append((filename, filename_date))
            print(f'未找到匹配: {filename} (尝试日期: {filename_date})')
            continue

        print(f'匹配成功: {filename} -> {matched_date}')

        # 更新赛事报告
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