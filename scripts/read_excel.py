import pandas as pd
import json

# Read Excel file
excel_path = r'd:\Workspace\shanghaiport-fc-app\datafile\主教练.xlsx'
xls = pd.ExcelFile(excel_path)

print("Sheet names:", xls.sheet_names)

for sheet_name in xls.sheet_names:
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    print(f"\n=== Sheet: {sheet_name} ===")
    print(f"Columns: {list(df.columns)}")
    print(f"Shape: {df.shape}")
    print("\nFirst 5 rows:")
    print(df.head())
    print("\n" + "="*50)