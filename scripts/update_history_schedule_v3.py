import pandas as pd
import json
import re

# File paths
EXCEL_PATH = r'd:\Workspace\shanghaiport-fc-app\datafile\主教练.xlsx'
JSON_PATH = r'd:\Workspace\shanghaiport-fc-app\public\data\history_schedule.json'

# Team name normalization mapping
TEAM_NAME_MAP = {
    '上海上港': '上海海港',
    '上海东亚': '上海海港',
    '上海绿地': '上海绿地',
    '上海绿地绿地': '上海绿地',
    '北京中赫国安': '北京国安',
    '山东鲁斯': '山东泰山',
    '天津泰达': '天津津门虎',
    '大连一方': '大连人',
    '上海特莱士': '上海海港',  # Add this mapping
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

                if pd.isna(venue):
                    venue = None
                if pd.isna(referee):
                    referee = None
                if pd.isna(opponent_coach):
                    opponent_coach = None

                # Determine home_coach and away_coach based on which team is Shanghai Port
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
                    'referee': referee
                })
        except Exception as e:
            print(f"Error reading sheet {sheet_name}: {e}")
            continue

    return all_matches

def match_json_to_excel(json_match, excel_matches):
    json_date = json_match.get('date')
    json_home = normalize_team_name(json_match.get('home_team'))
    json_away = normalize_team_name(json_match.get('away_team'))

    if not json_date or not json_home or not json_away:
        return None

    for excel_match in excel_matches:
        if excel_match['date'] == json_date:
            if (excel_match['home_team'] == json_home and excel_match['away_team'] == json_away):
                return excel_match

    return None

def main():
    print("Loading coach data from Excel...")
    excel_matches = load_coach_data()
    print(f"Loaded {len(excel_matches)} match records from Excel")

    print("\nLoading history schedule JSON...")
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        history_data = json.load(f)
    print(f"Loaded {len(history_data)} match records from JSON")

    matched_count = 0
    unmatched_count = 0
    venue_added = 0
    home_coach_added = 0
    away_coach_added = 0
    referee_added = 0
    old_coach_removed = 0

    for match in history_data:
        if 'coach' in match:
            del match['coach']
            old_coach_removed += 1

        result = match_json_to_excel(match, excel_matches)

        if result:
            matched_count += 1

            if result['venue'] and 'venue' not in match:
                match['venue'] = result['venue']
                venue_added += 1

            if result['home_coach'] and 'home_coach' not in match:
                match['home_coach'] = result['home_coach']
                home_coach_added += 1

            if result['away_coach'] and 'away_coach' not in match:
                match['away_coach'] = result['away_coach']
                away_coach_added += 1

            if result['referee'] and 'referee' not in match:
                match['referee'] = result['referee']
                referee_added += 1
        else:
            unmatched_count += 1
            if unmatched_count <= 10:
                print(f"Unmatched: date={match.get('date')}, home={match.get('home_team')}, away={match.get('away_team')}")

    print(f"\n=== Summary ===")
    print(f"Total matches: {len(history_data)}")
    print(f"Matched: {matched_count}")
    print(f"Unmatched: {unmatched_count}")
    print(f"Venue added: {venue_added}")
    print(f"Home coach added: {home_coach_added}")
    print(f"Away coach added: {away_coach_added}")
    print(f"Referee added: {referee_added}")
    print(f"Old coach field removed: {old_coach_removed}")

    print(f"\nSaving updated JSON to {JSON_PATH}...")
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(history_data, f, ensure_ascii=False, indent=2)
    print("Done!")

if __name__ == '__main__':
    main()