import pandas as pd

excel_path = r'd:\Workspace\shanghaiport-fc-app\datafile\主教练.xlsx'
xls = pd.ExcelFile(excel_path)

# Get the actual header row (row 0 seems to have the header information based on output)
for sheet_name in xls.sheet_names[:3]:  # Check first 3 sheets
    df = pd.read_excel(excel_path, sheet_name=sheet_name, header=None)
    print(f"\n=== Sheet: {sheet_name} ===")
    print("First 2 rows (all columns):")
    for i in range(2):
        print(f"Row {i}: {list(df.iloc[i])}")