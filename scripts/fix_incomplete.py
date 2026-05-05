import json
import pandas as pd

EXCEL_PATH = r'd:\Workspace\shanghaiport-fc-app\datafile\主教练.xlsx'
HISTORY_SCHEDULE_PATH = r'd:\Workspace\shanghaiport-fc-app\public\data\history_schedule.json'

SHANGHAI_PORT_NAMES = [
    '上海海港', '上海上港', '上海东亚', '上海特莱士',
    'Shanghai SIPG', 'Shanghai Port', 'Shanghai East Asia'
]

def parse_scorers(scorers_str):
    if not scorers_str or scorers_str in ['—', '-', 'None', 'none', 'nan']:
        return []
    
    separators = ['，', ',', '、', '；', ';', ' ', '和', '及']
    
    for sep in separators:
        if sep in scorers_str:
            return [s.strip() for s in scorers_str.split(sep) if s.strip()]
    
    return [scorers_str.strip()]

def update_specific_matches():
    print('加载Excel数据...')
    
    xls = pd.ExcelFile(EXCEL_PATH)
    excel_data = {}
    
    for sheet_name in xls.sheet_names:
        if sheet_name in ['汇总', '主客场汇总', '主场', '客场', '中立场']:
            continue
            
        try:
            df = pd.read_excel(EXCEL_PATH, sheet_name=sheet_name, header=1)
            
            for idx, row in df.iterrows():
                date = row.get('比赛日期', '')
                if pd.isna(date):
                    continue
                
                date_str = str(date).strip()
                if '.' in date_str:
                    parts = date_str.split('.')
                    if len(parts) == 3:
                        date_str = f'{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}'
                
                excel_data[date_str] = {
                    'home_team': str(row.get('主队', '')).strip(),
                    'away_team': str(row.get('客队', '')).strip(),
                    'home_away': str(row.get('主客场', '')).strip(),
                    'our_scorers': str(row.get('本队进球队员', '')).strip(),
                    'opponent_scorers': str(row.get('对手进球队员', '')).strip()
                }
        except:
            pass
    
    print(f'加载了 {len(excel_data)} 场比赛数据')
    print('\n加载history_schedule.json...')
    
    with open(HISTORY_SCHEDULE_PATH, 'r', encoding='utf-8') as f:
        schedule = json.load(f)
    
    print('\n更新有问题的比赛...')
    
    for match in schedule:
        date = match.get('date', '')
        
        if date not in excel_data:
            continue
        
        excel_match = excel_data[date]
        
        our_scorers = parse_scorers(excel_match['our_scorers'])
        opponent_scorers = parse_scorers(excel_match['opponent_scorers'])
        
        # 检查主客场
        is_home = any(name in match.get('home_team', '') for name in SHANGHAI_PORT_NAMES)
        
        # 特殊处理2023-08-08
        if date == '2023-08-08':
            match['scorers'] = {
                'home': [],
                'away': ['马兴煜(OG)', '武磊', '卡隆', '武磊', '卡隆']
            }
            continue
        
        # 根据主客场分配
        if is_home:
            home_scorers = our_scorers
            away_scorers = opponent_scorers
        else:
            home_scorers = opponent_scorers
            away_scorers = our_scorers
        
        # 只有在之前是空列表时才更新
        current_scorers = match.get('scorers', {})
        if len(current_scorers.get('home', [])) == 0 and len(current_scorers.get('away', [])) == 0:
            match['scorers'] = {
                'home': home_scorers,
                'away': away_scorers
            }
    
    # 保存
    print('保存更新...')
    with open(HISTORY_SCHEDULE_PATH, 'w', encoding='utf-8') as f:
        json.dump(schedule, f, ensure_ascii=False, indent=2)
    
    print('更新完成！')

if __name__ == '__main__':
    update_specific_matches()