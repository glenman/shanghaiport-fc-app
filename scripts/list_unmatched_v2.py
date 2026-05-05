import pandas as pd
import json
import re

EXCEL_PATH = r'd:\Workspace\shanghaiport-fc-app\datafile\主教练.xlsx'
JSON_PATH = r'd:\Workspace\shanghaiport-fc-app\public\data\history_schedule.json'

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

                all_matches.append({
                    'date': date,
                    'home_team': home_team,
                    'away_team': away_team,
                })
        except Exception as e:
            continue

    return all_matches

def main():
    excel_matches = load_coach_data()
    print(f"Loaded {len(excel_matches)} match records from Excel\n")

    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        history_data = json.load(f)
    print(f"Loaded {len(history_data)} match records from JSON\n")

    unmatched = []

    for match in history_data:
        json_date = match.get('date')
        json_home = normalize_team_name(match.get('home_team'))
        json_away = normalize_team_name(match.get('away_team'))

        if not json_date or not json_home or not json_away:
            continue

        found = False
        for excel_match in excel_matches:
            if (excel_match['date'] == json_date and
                excel_match['home_team'] == json_home and
                excel_match['away_team'] == json_away):
                found = True
                break

        if not found:
            unmatched.append({
                'season': match.get('season'),
                'date': json_date,
                'home_team': match.get('home_team'),
                'away_team': match.get('away_team'),
                'result': match.get('result'),
                'round': match.get('round')
            })

    print(f"=== 未匹配的比赛列表 (共{len(unmatched)}场) ===\n")

    by_season = {}
    for m in unmatched:
        season = m['season']
        if season not in by_season:
            by_season[season] = []
        by_season[season].append(m)

    for season in sorted(by_season.keys()):
        matches = by_season[season]
        print(f"\n--- {season}赛季 ({len(matches)}场) ---")
        for m in matches:
            print(f"  {m['date']} | {m['home_team']} vs {m['away_team']} | {m['result']} | {m.get('round', '')}")

if __name__ == '__main__':
    main()