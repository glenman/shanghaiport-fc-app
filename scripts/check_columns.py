import pandas as pd

excel_path = r'd:\Workspace\shanghaiport-fc-app\datafile\主教练.xlsx'

# Read the coach sheet with proper header
df = pd.read_excel(excel_path, sheet_name='斯文·戈兰·埃里克森', header=1)
print("Columns:")
for i, col in enumerate(df.columns):
    print(f"{i}: {col}")

print("\nFirst 3 rows:")
print(df.head(3).to_string())

print("\n\nAll column names with index:")
for i, col in enumerate(df.columns):
    print(f"{i}: '{col}'")