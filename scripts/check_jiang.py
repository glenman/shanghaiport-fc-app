import pandas as pd

excel_path = r'd:\Workspace\shanghaiport-fc-app\datafile\主教练.xlsx'

# Read the 蒋炳尧 sheet
df = pd.read_excel(excel_path, sheet_name='蒋炳尧', header=None)
print(f"Shape: {df.shape}")
print("\nFirst 5 rows:")
for i in range(5):
    row_data = list(df.iloc[i])
    print(f"Row {i}: {row_data[:15]}")