#!/usr/bin/env python3
import pandas as pd

# 读取Excel文件
excel_file = 'data/上海海港历史比分记录.xlsx'
try:
    df = pd.read_excel(excel_file, sheet_name='比赛汇总')
    print(f"成功读取Excel文件，共 {len(df)} 条记录")
    print("\nExcel文件的列名：")
    for col in df.columns:
        print(f"- {col}")
    
    print("\n前5行数据：")
    print(df.head())
except Exception as e:
    print(f"读取Excel文件失败: {e}")
    exit(1)
