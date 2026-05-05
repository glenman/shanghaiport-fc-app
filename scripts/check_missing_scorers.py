import pandas as pd

excel_path = r'datafile\主教练.xlsx'

check_dates = ['2022-12-19', '2022-12-27', '2023-08-08']

xls = pd.ExcelFile(excel_path)

print('搜索这几个日期的比赛：')
print('-' * 60)

for sheet_name in xls.sheet_names:
    if sheet_name in ['汇总', '主客场汇总', '主场', '客场', '中立场']:
        continue
        
    try:
        df = pd.read_excel(excel_path, sheet_name=sheet_name, header=1)
        
        for idx, row in df.iterrows():
            date = row.get('比赛日期', '')
            if pd.isna(date):
                continue
            
            date_str = str(date).strip()
            if '.' in date_str:
                parts = date_str.split('.')
                if len(parts) == 3:
                    date_str = f'{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}'
            
            if date_str in check_dates:
                home = str(row.get('主队', '')).strip()
                away = str(row.get('客队', '')).strip()
                score = str(row.get('比分', '')).strip()
                our_scorers = str(row.get('本队进球队员', '')).strip()
                opp_scorers = str(row.get('对手进球队员', '')).strip()
                
                print(f'Sheet: {sheet_name}')
                print(f'日期: {date_str}')
                print(f'{home} {score} {away}')
                print(f'本队进球: {our_scorers}')
                print(f'对手进球: {opp_scorers}')
                print()
                
    except Exception as e:
        pass