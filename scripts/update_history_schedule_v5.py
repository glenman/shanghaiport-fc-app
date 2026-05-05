import pandas as pd
import json
import re

EXCEL_PATH = r'd:\Workspace\shanghaiport-fc-app\datafile\主教练.xlsx'
JSON_PATH = r'd:\Workspace\shanghaiport-fc-app\public\data\history_schedule.json'

# Team name normalization - for matching
TEAM_NAME_MAP = {
    '上海上港': '上海海港',
    '上海东亚': '上海海港',
    '上海绿地': '上海绿地',
    '上海绿地绿地': '上海绿地',
    '北京中赫国安': '北京国安',
    '山东鲁斯': '山东泰山',
    '天津泰达': '天津津门虎',
    '大连一方': '大连人',
    '上海特莱士': '上海海港',
    '河北华夏': '华夏幸福',  # Add this mapping
    '华夏幸福': '华夏幸福',
}

def normalize_date(date_str):
    if pd.isna(date_str):
        return None
    date_str = str(date_str).strip()
    if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
        return date_str
    match = re.match(r'(\d{4})\.(\d{2})\.(\d{2})', date_str)
    if match:
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    return None

def normalize_team_name(name):
    if pd.isna(name):
        return None
    name = str(name).strip()
    return TEAM_NAME_MAP.get(name, name)

def format_time(time_val):
    if pd.isna(time_val):
        return None
    if isinstance(time_val, str):
        return time_val
    try:
        hour = int(time_val.hour)
        minute = int(time_val.minute)
        second = int(time_val.second)
        return f"{hour:02d}:{minute:02d}:{second:02d}"
    except:
        return str(time_val)

def load_coach_data():
    all_matches = []
    xls = pd.ExcelFile(EXCEL_PATH)

    for sheet_name in xls.sheet_names:
        if sheet_name in ['汇总', '主客场汇总', '主场', '客场', '中立场']:
            continue

        try:
            df = pd.read_excel(EXCEL_PATH, sheet_name=sheet_name, header=1)
            if df.empty:
                continue

            sp_coach = sheet_name

            for idx, row in df.iterrows():
                date = normalize_date(row.get('比赛日期'))
                if not date:
                    continue

                home_team = normalize_team_name(row.get('主队'))
                away_team = normalize_team_name(row.get('客队'))
                venue = row.get('比赛场地')
                referee = row.get('主裁判')
                opponent_coach = row.get('对手主教练')
                kickoff_time = format_time(row.get('开球时间(北京时间)'))
                city = row.get('比赛城市')
                attendance = row.get('观众人数')

                if pd.isna(venue):
                    venue = None
                if pd.isna(referee):
                    referee = None
                if pd.isna(opponent_coach):
                    opponent_coach = None
                if pd.isna(city):
                    city = None
                if pd.isna(attendance) or attendance == 0:
                    attendance = None

                if home_team in ['上海海港', '上海上港', '上海东亚', '上海特莱士']:
                    home_coach = sp_coach
                    away_coach = opponent_coach
                elif away_team in ['上海海港', '上海上港', '上海东亚', '上海特莱士']:
                    home_coach = opponent_coach
                    away_coach = sp_coach
                else:
                    continue

                all_matches.append({
                    'date': date,
                    'home_team': home_team,
                    'away_team': away_team,
                    'venue': venue,
                    'home_coach': home_coach,
                    'away_coach': away_coach,
                    'referee': referee,
                    'kickoff_time': kickoff_time,
                    'city': city,
                    'attendance': attendance
                })
        except Exception as e:
            print(f"Error reading sheet {sheet_name}: {e}")
            continue

    return all_matches

def main():
    print("Loading coach data from Excel...")
    excel_matches = load_coach_data()
    print(f"Loaded {len(excel_matches)} match records from Excel")

    print("\nLoading history schedule JSON...")
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        history_data = json.load(f)
    print(f"Loaded {len(history_data)} match records from JSON")

    matched_count = 0
    kickoff_added = 0
    city_added = 0
    attendance_added = 0

    for match in history_data:
        result = None
        json_date = match.get('date')
        json_home = normalize_team_name(match.get('home_team'))
        json_away = normalize_team_name(match.get('away_team'))

        if json_date and json_home and json_away:
            for excel_match in excel_matches:
                if (excel_match['date'] == json_date and
                    excel_match['home_team'] == json_home and
                    excel_match['away_team'] == json_away):
                    result = excel_match
                    break

        if result:
            matched_count += 1

            if result['kickoff_time'] and 'kickoff_time' not in match:
                match['kickoff_time'] = result['kickoff_time']
                kickoff_added += 1

            if result['city'] and 'city' not in match:
                match['city'] = result['city']
                city_added += 1

            if result['attendance'] and 'attendance' not in match:
                match['attendance'] = result['attendance']
                attendance_added += 1

    print(f"\n=== Summary ===")
    print(f"Total matches: {len(history_data)}")
    print(f"Matched: {matched_count}")
    print(f"Kickoff time added: {kickoff_added}")
    print(f"City added: {city_added}")
    print(f"Attendance added: {attendance_added}")

    print(f"\nSaving updated JSON to {JSON_PATH}...")
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(history_data, f, ensure_ascii=False, indent=2)
    print("Done!")

if __name__ == '__main__':
    main()