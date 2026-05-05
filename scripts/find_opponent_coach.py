import pandas as pd

excel_path = r'd:\Workspace\shanghaiport-fc-app\datafile\主教练.xlsx'

df = pd.read_excel(excel_path, sheet_name='蒋炳尧', header=1)

print("查找 2008-04-19 上海东亚 vs 北京宏登 这场比赛：")
print("(Excel中日期可能是2008.04.19)\n")

for idx, row in df.iterrows():
    date = row.get('比赛日期')
    if pd.isna(date):
        continue

    date_str = str(date).strip()
    home = row.get('主队')
    away = row.get('客队')

    if '2008' in date_str and '北京宏登' in str(away):
        print(f"找到匹配:")
        print(f"  日期: {date_str}")
        print(f"  主队: {home}")
        print(f"  客队: {away}")
        print(f"  对手主教练: {row.get('对手主教练')}")
        print(f"  本队主教练: {row.get('本队主教练')}")
        print(f"  比赛场地: {row.get('比赛场地')}")
        print(f"  主裁判: {row.get('主裁判')}")