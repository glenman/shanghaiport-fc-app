import pandas as pd
import json
import re
from datetime import datetime

# File paths
EXCEL_PATH = r'd:\Workspace\shanghaiport-fc-app\datafile\主教练.xlsx'
JSON_PATH = r'd:\Workspace\shanghaiport-fc-app\public\data\history_schedule.json'

# Coach name mapping (to match Excel sheet names)
COACH_NAMES = [
    '斯文·戈兰·埃里克森', '维托尔·佩雷拉', '安德烈·维拉斯·博阿斯',
    '高洪波', '伊万·莱科', '奚志康', '范志毅', '克劳德·鲁伊兹',
    '丹尼尔·苏泽', '菲利佩·阿尔梅达', '谢晖', '金子隆之',
    '陈旭峰', '孙祥', '弗朗西斯科·哈维尔·佩雷拉·梅吉亚',
    '何塞·奥古斯丁·伊兹奎尔多·泰纳', '凯文·文森特·穆斯卡特', '罗斯·阿洛伊西', '蒋炳尧'
]

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
}

def normalize_date(date_str):
    """Convert date format from YYYY.MM.DD or YYYY-MM-DD to YYYY-MM-DD"""
    if pd.isna(date_str):
        return None
    date_str = str(date_str).strip()
    # Already in YYYY-MM-DD format
    if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
        return date_str
    # Convert YYYY.MM.DD to YYYY-MM-DD
    match = re.match(r'(\d{4})\.(\d{2})\.(\d{2})', date_str)
    if match:
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    return None

def normalize_team_name(name):
    """Normalize team name"""
    if pd.isna(name):
        return None
    name = str(name).strip()
    return TEAM_NAME_MAP.get(name, name)

def load_coach_data():
    """Load all coach data from Excel"""
    all_matches = []
    xls = pd.ExcelFile(EXCEL_PATH)

    for sheet_name in xls.sheet_names:
        if sheet_name in ['汇总', '主客场汇总', '主场', '客场', '中立场']:
            continue

        try:
            df = pd.read_excel(EXCEL_PATH, sheet_name=sheet_name, header=1)
            if df.empty:
                continue

            # Extract coach name from sheet
            coach_name = sheet_name

            for idx, row in df.iterrows():
                date = normalize_date(row.get('比赛日期'))
                if not date:
                    continue

                home_team = normalize_team_name(row.get('主队'))
                away_team = normalize_team_name(row.get('客队'))
                venue = row.get('比赛场地')
                referee = row.get('主裁判')

                if pd.isna(venue):
                    venue = None
                if pd.isna(referee):
                    referee = None

                all_matches.append({
                    'date': date,
                    'home_team': home_team,
                    'away_team': away_team,
                    'venue': venue,
                    'coach': coach_name,
                    'referee': referee
                })
        except Exception as e:
            print(f"Error reading sheet {sheet_name}: {e}")
            continue

    return all_matches

def match_json_to_excel(json_match, excel_matches):
    """Match a JSON match record to Excel data based on date and teams"""
    json_date = json_match.get('date')
    json_home = normalize_team_name(json_match.get('home_team'))
    json_away = normalize_team_name(json_match.get('away_team'))

    if not json_date or not json_home or not json_away:
        return None

    # Try to find exact match
    for excel_match in excel_matches:
        if excel_match['date'] == json_date:
            # Check if home/away teams match (considering swapped roles)
            if (excel_match['home_team'] == json_home and excel_match['away_team'] == json_away):
                return excel_match

    # Try matching with team name variations
    for excel_match in excel_matches:
        if excel_match['date'] == json_date:
            # Allow for team name variations
            excel_home = excel_match['home_team'] or ''
            excel_away = excel_match['away_team'] or ''

            # Check direct match
            if (excel_home == json_home and excel_away == json_away):
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

    # Track statistics
    matched_count = 0
    unmatched_count = 0
    venue_added = 0
    coach_added = 0
    referee_added = 0

    # Process each match
    for match in history_data:
        result = match_json_to_excel(match, excel_matches)

        if result:
            matched_count += 1

            # Add venue
            if result['venue'] and 'venue' not in match:
                match['venue'] = result['venue']
                venue_added += 1

            # Add coach
            if result['coach'] and 'coach' not in match:
                match['coach'] = result['coach']
                coach_added += 1

            # Add referee
            if result['referee'] and 'referee' not in match:
                match['referee'] = result['referee']
                referee_added += 1
        else:
            unmatched_count += 1
            # Print first few unmatched for debugging
            if unmatched_count <= 5:
                print(f"Unmatched: date={match.get('date')}, home={match.get('home_team')}, away={match.get('away_team')}")

    print(f"\n=== Summary ===")
    print(f"Total matches: {len(history_data)}")
    print(f"Matched: {matched_count}")
    print(f"Unmatched: {unmatched_count}")
    print(f"Venue added: {venue_added}")
    print(f"Coach added: {coach_added}")
    print(f"Referee added: {referee_added}")

    # Save updated JSON
    print(f"\nSaving updated JSON to {JSON_PATH}...")
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(history_data, f, ensure_ascii=False, indent=2)
    print("Done!")

if __name__ == '__main__':
    main()