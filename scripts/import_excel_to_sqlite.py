import sqlite3
import pandas as pd
import os

# 检查Excel文件是否存在
excel_path = 'data/上海海港队史进球记录(2006-2025).xlsx'
print(f"检查Excel文件: {excel_path}")
print(f"文件存在: {os.path.exists(excel_path)}")

# 连接SQLite数据库
conn = sqlite3.connect('football.db')
cursor = conn.cursor()

# 清空表数据
cursor.execute('DELETE FROM goal_details')
print("\n清空表数据成功")

# 创建表（如果不存在）
cursor.execute('''
CREATE TABLE IF NOT EXISTS goal_details ( 
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    season VARCHAR(20) NOT NULL, 
    match_type VARCHAR(30) NOT NULL, 
    goal_time VARCHAR(10), 
    goal_player VARCHAR(20) NOT NULL, 
    assist_player VARCHAR(20), 
    create_player VARCHAR(20), 
    match_date_code INTEGER, 
    match_name VARCHAR(50) NOT NULL, 
    home_team VARCHAR(20) NOT NULL, 
    home_score INTEGER NOT NULL, 
    away_score INTEGER NOT NULL, 
    away_team VARCHAR(20) NOT NULL, 
    match_result VARCHAR(10) NOT NULL, 
    remark TEXT
)
''')

# 创建索引
cursor.execute('CREATE INDEX IF NOT EXISTS idx_season ON goal_details(season)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_goal_player ON goal_details(goal_player)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_match_type ON goal_details(match_type)')

# 读取Excel文件
try:
    # 读取Excel文件，不跳过行，保留原始格式
    print("\n读取Excel文件...")
    # 使用openpyxl引擎读取，保留合并单元格信息
    df = pd.read_excel(excel_path, engine='openpyxl')
    
    # 打印数据结构
    print(f"\n数据总行数: {len(df)}")
    print("列名:")
    print(df.columns.tolist())
    
    # 处理合并单元格，填充缺失值
    # 前向填充合并的单元格
    df = df.fillna(method='ffill')
    
    # 重命名列，使用实际的中文列名
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
            print(f"重命名列: {old_col} -> {new_col}")
    
    # 跳过表头行
    # 找到实际数据开始的行
    header_row = 0
    for i, row in df.iterrows():
        if str(row.get('序号')) == '序号':
            header_row = i
            break
    
    # 从表头行之后开始读取数据
    df = df.iloc[header_row+1:].reset_index(drop=True)
    print(f"\n跳过表头后的数据行数: {len(df)}")
    
    # 处理比赛时间
    if '比赛时间' in df.columns:
        try:
            # 先将比赛时间列转换为数值类型
            df['比赛时间'] = pd.to_numeric(df['比赛时间'], errors='coerce')
            # 处理Excel日期序列号
            df['match_date_code'] = pd.to_datetime(df['比赛时间'], origin='1900-01-01', unit='D', errors='coerce')
            # 转换为YYYYMMDD格式
            df['match_date_code'] = df['match_date_code'].dt.strftime('%Y%m%d')
            # 处理NaN值
            df['match_date_code'] = df['match_date_code'].fillna(0)
            # 转换为整数
            df['match_date_code'] = df['match_date_code'].astype(int)
            print("\n比赛时间转换成功")
        except Exception as e:
            print(f"\n日期转换失败: {e}")
            df['match_date_code'] = 0
    else:
        df['match_date_code'] = 0
        print("\n没有找到比赛时间列")
    
    # 处理比分
    if '比分' in df.columns and '中间列' in df.columns:
        df['home_score'] = df['比分'].fillna(0).astype(int)
        df['away_score'] = df['中间列'].fillna(0).astype(int)
        print("\n比分提取成功")
    else:
        df['home_score'] = 0
        df['away_score'] = 0
        print("\n没有找到比分相关列")
    
    # 提取赛季信息
    # 从比赛时间中提取年份
    df['season'] = '2025'  # 默认值
    if 'match_date_code' in df.columns:
        try:
            df['season'] = df['match_date_code'].astype(str).str[:4]
            # 处理0值
            df['season'] = df['season'].replace('0', '2025')
            print("\n从比赛时间提取赛季成功")
        except Exception as e:
            print(f"\n无法从比赛时间提取赛季，使用默认值: {e}")
    
    # 插入数据
    inserted_count = 0
    print("\n开始插入数据...")
    
    # 打印可用的列
    print("可用的列:", df.columns.tolist())
    
    for idx, row in df.iterrows():
        # 检查必要字段
        if '进球队员' in df.columns and pd.notna(row.get('进球队员')):
            # 构建插入数据，确保所有NOT NULL字段都有值
            season = row.get('season', '2025') or '2025'
            match_type = row.get('赛事类别', '') or ''
            goal_time = row.get('进球时间', '') or ''
            goal_player = row.get('进球队员', '') or ''
            assist_player = row.get('助攻队员', '') or ''
            create_player = row.get('造点(乌龙)队员', '') or ''
            match_date_code = row.get('match_date_code', 0) or 0
            match_name = row.get('比赛类型', '') or '未知比赛'
            home_team = row.get('主队', '') or '未知球队'
            home_score = row.get('home_score', 0) or 0
            away_score = row.get('away_score', 0) or 0
            away_team = row.get('客队', '') or '未知球队'
            match_result = row.get('赛果', '') or '未知'
            remark = row.get('备注', '') or ''
            
            # 打印插入的数据
            if idx < 5:  # 打印前5行
                print(f"插入数据 {idx+1}: {season}, {match_type}, {goal_player}, {match_date_code}, {home_team} {home_score}-{away_score} {away_team}")
            
            try:
                cursor.execute('''
                INSERT INTO goal_details (season, match_type, goal_time, goal_player, assist_player, 
                                       create_player, match_date_code, match_name, home_team, 
                                       home_score, away_score, away_team, match_result, remark)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    season,
                    match_type,
                    goal_time,
                    goal_player,
                    assist_player,
                    create_player,
                    match_date_code,
                    match_name,
                    home_team,
                    home_score,
                    away_score,
                    away_team,
                    match_result,
                    remark
                ))
                inserted_count += 1
            except Exception as e:
                print(f"插入数据失败: {e}")
                continue
    
    print(f"\n成功插入 {inserted_count} 条数据到表中")
    
except Exception as e:
    print(f"\n错误: {e}")
    import traceback
    traceback.print_exc()

# 提交事务并关闭连接
conn.commit()
conn.close()

print("\n数据导入完成！")
