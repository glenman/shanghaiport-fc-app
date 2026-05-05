import pandas as pd

excel_path = r'd:\Workspace\shanghaiport-fc-app\datafile\主教练.xlsx'
xls = pd.ExcelFile(excel_path)

print("All sheet names:")
for i, name in enumerate(xls.sheet_names):
    print(f"{i}: {name}")

# Now check coach sheets - ones that look like actual coach names
coach_keywords = ['高洪波', '奚志康', '埃里克森', '博阿斯', '佩雷拉', '莱科', '哈维尔', '穆斯卡特', '克劳德', '苏泽', '范志毅']
actual_coach_sheets = [s for s in xls.sheet_names if any(kw in s for kw in coach_keywords)]

print("\n\nActual coach sheets:")
for name in actual_coach_sheets[:3]:
    df = pd.read_excel(excel_path, sheet_name=name, header=None)
    print(f"\n=== Sheet: {name} ===")
    print("First 3 rows:")
    for i in range(3):
        row_data = list(df.iloc[i])
        # Only print first 15 columns to see structure
        print(f"Row {i}: {row_data[:15]}")
    print(f"\nTotal columns: {len(df.columns)}")