import pandas as pd
import os

# 检查Excel文件是否存在
excel_path = 'data/上海海港队史进球记录(2006-2025).xlsx'
print(f"检查Excel文件: {excel_path}")
print(f"文件存在: {os.path.exists(excel_path)}")

# 读取Excel文件
try:
    print("\n读取Excel文件...")
    # 使用openpyxl引擎读取
    df = pd.read_excel(excel_path, engine='openpyxl')
    
    # 打印数据结构
    print(f"数据总行数: {len(df)}")
    print("列名:")
    print(df.columns.tolist())
    
    # 处理合并单元格，填充缺失值
    df = df.fillna(method='ffill')
    
    # 重命名列
    column_mapping = {
        '上海海港队史进球记录(2006-2025)': '序号',
        'Unnamed: 1': '赛事类别',
        'Unnamed: 2': '进球时间',
        'Unnamed: 3': '进球队员',
        'Unnamed: 4': '助攻队员',
        'Unnamed: 5': '造点(乌龙)队员',
        'Unnamed: 6': '比赛时间',
        'Unnamed: 7': '比赛类型',
        'Unnamed: 8': '主队',
        'Unnamed: 9': '比分',
        'Unnamed: 10': '中间列',
        'Unnamed: 11': '客队',
        'Unnamed: 12': '赛果',
        'Unnamed: 13': '备注'
    }
    
    # 重命名列
    for old_col, new_col in column_mapping.items():
        if old_col in df.columns:
            df.rename(columns={old_col: new_col}, inplace=True)
    
    # 跳过表头行
    header_row = 0
    for i, row in df.iterrows():
        if str(row.get('序号')) == '序号':
            header_row = i
            break
    
    # 从表头行之后开始读取数据
    df = df.iloc[header_row+1:].reset_index(drop=True)
    print(f"\n跳过表头后的数据行数: {len(df)}")
    
    # 打印前10行数据，查看实际格式
    print("\n前10行数据:")
    print(df.head(10))
    
    # 检查比赛时间列的格式
    print("\n比赛时间列的前20个值:")
    if '比赛时间' in df.columns:
        for i, value in enumerate(df['比赛时间'].head(20)):
            print(f"{i+1}: {value} (类型: {type(value).__name__})")
    
    # 检查比分列的格式
    print("\n比分列的前20个值:")
    if '比分' in df.columns:
        for i, value in enumerate(df['比分'].head(20)):
            print(f"{i+1}: {value} (类型: {type(value).__name__})")
    
    # 检查主队和客队列
    print("\n主队列的前10个值:")
    if '主队' in df.columns:
        print(df['主队'].head(10))
    
    print("\n客队列的前10个值:")
    if '客队' in df.columns:
        print(df['客队'].head(10))
    
    # 检查赛事类别列
    print("\n赛事类别列的前10个值:")
    if '赛事类别' in df.columns:
        print(df['赛事类别'].head(10))
    
    # 检查比赛类型列
    print("\n比赛类型列的前10个值:")
    if '比赛类型' in df.columns:
        print(df['比赛类型'].head(10))
    
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
