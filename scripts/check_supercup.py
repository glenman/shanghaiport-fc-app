import pandas as pd

excel_path = r'd:\Workspace\shanghaiport-fc-app\datafile\主教练.xlsx'

df = pd.read_excel(excel_path, sheet_name='凯文·文森特·穆斯卡特', header=1)

print("查找2026年超级杯比赛的完整数据：\n")

for idx, row in df.iterrows():
    date = row.get('比赛日期')
    if pd.isna(date):
        continue

    date_str = str(date).strip()
    if '2026.03.01' in date_str:
        print(f"完整数据:")
        print(f"  日期: {date_str}")
        print(f"  比赛类别: {row.get('比赛类别')}")
        print(f"  主队: {row.get('主队')}")
        print(f"  比分: {row.get('比分')}")
        print(f"  客队: {row.get('客队')}")
        print(f"  赛果: {row.get('赛果')}")
        print(f"  比赛场地: {row.get('比赛场地')}")
        print(f"  开球时间: {row.get('开球时间(北京时间)')}")
        print(f"  比赛城市: {row.get('比赛城市')}")
        print(f"  主裁判: {row.get('主裁判')}")
        print(f"  本队主教练: {row.get('本队主教练')}")
        print(f"  对手主教练: {row.get('对手主教练')}")
        print(f"  观众人数: {row.get('观众人数')}")
        print(f"  本队进球队员: {row.get('本队进球队员')}")
        print(f"  对手进球队员: {row.get('对手进球队员')}")