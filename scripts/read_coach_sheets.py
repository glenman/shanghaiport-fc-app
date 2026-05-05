import pandas as pd

excel_path = r'd:\Workspace\shanghaiport-fc-app\datafile\主教练.xlsx'
xls = pd.ExcelFile(excel_path)

# Check actual coach sheets (skip summary sheets)
coach_sheets = [s for s in xls.sheet_names if s not in ['汇总', '主客场汇总', '主场']]

for sheet_name in coach_sheets[:2]:  # Check first 2 coach sheets
    df = pd.read_excel(excel_path, sheet_name=sheet_name, header=None)
    print(f"\n=== Sheet: {sheet_name} ===")
    print("First 3 rows:")
    for i in range(3):
        print(f"Row {i}: {list(df.iloc[i])}")
    print(f"\nShape: {df.shape}")