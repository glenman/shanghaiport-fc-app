import pandas as pd
import re

excel_path = r'd:\Workspace\shanghaiport-fc-app\datafile\主教练.xlsx'

df = pd.read_excel(excel_path, sheet_name='蒋炳尧', header=1)

print("Looking for 2008-04-18 and 2012 matches:\n")

for idx, row in df.iterrows():
    date = row.get('比赛日期')
    if pd.isna(date):
        continue

    date_str = str(date).strip()
    match = re.match(r'(\d{4})\.(\d{2})\.(\d{2})', date_str)
    if match:
        normalized_date = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"

        if '2008' in normalized_date or '2012' in normalized_date:
            print(f"Row {idx}: date={normalized_date}, home={row.get('主队')}, away={row.get('客队')}")

print("\n\nAll 2008 dates in Excel:")
for idx, row in df.iterrows():
    date = row.get('比赛日期')
    if pd.isna(date):
        continue
    date_str = str(date).strip()
    if '2008' in date_str:
        print(f"  {date_str}")