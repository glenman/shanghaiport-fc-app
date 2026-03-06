import pandas as pd
import os

# 检查Excel文件
excel_path = 'data/上海海港队史进球记录(2006-2025).xlsx'
print(f"Excel文件路径: {excel_path}")
print(f"文件存在: {os.path.exists(excel_path)}")

if os.path.exists(excel_path):
    try:
        # 获取工作表
        xls = pd.ExcelFile(excel_path)
        sheets = xls.sheet_names
        print(f"\n工作表数量: {len(sheets)}")
        print("工作表名称:")
        for sheet in sheets:
            print(f"- {sheet}")
        
        # 检查第一个工作表
        if sheets:
            print(f"\n检查第一个工作表: {sheets[0]}")
            df = pd.read_excel(excel_path, sheet_name=0)
            print(f"行数: {len(df)}")
            print(f"列数: {len(df.columns)}")
            print("列名:")
            for col in df.columns:
                print(f"- {col}")
            
            # 打印前5行
            print("\n前5行数据:")
            print(df.head())
    except Exception as e:
        print(f"错误: {e}")
else:
    print("文件不存在！")
