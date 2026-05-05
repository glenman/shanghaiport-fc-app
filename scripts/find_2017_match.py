import pandas as pd
import re

excel_path = r'd:\Workspace\shanghaiport-fc-app\datafile\主教练.xlsx'

# Check all coach sheets for this match
xls = pd.ExcelFile(excel_path)

for sheet_name in xls.sheet_names:
    if sheet_name in ['汇总', '主客场汇总', '主场', '客场', '中立场']:
        continue

    df = pd.read_excel(excel_path, sheet_name=sheet_name, header=1)

    for idx, row in df.iterrows():
        date = row.get('比赛日期')
        if pd.isna(date):
            continue

        date_str = str(date).strip()
        home = str(row.get('主队', '')).strip()
        away = str(row.get('客队', '')).strip()

        # Look for 2017-08-10 match
        if '2017' in date_str and ('华夏' in home or '华夏' in away):
            print(f"Sheet: {sheet_name}")
            print(f"  日期: {date_str}")
            print(f"  主队: {home}")
            print(f"  客队: {away}")
            print()