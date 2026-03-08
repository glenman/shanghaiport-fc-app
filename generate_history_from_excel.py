#!/usr/bin/env python3
import json
import pandas as pd
import re

# 汉字数字到阿拉伯数字的转换函数
def chinese_to_arabic(chinese_num):
    # 基本数字映射
    num_map = {
        '零': 0, '一': 1, '二': 2, '三': 3, '四': 4,
        '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
        '十': 10, '百': 100
    }
    
    # 处理纯阿拉伯数字
    if chinese_num.isdigit():
        return int(chinese_num)
    
    # 处理汉字数字
    result = 0
    temp = 0
    for char in chinese_num:
        if char in num_map:
            value = num_map[char]
            if value >= 10:
                if temp == 0:
                    temp = 1
                result += temp * value
                temp = 0
            else:
                temp = value
    if temp > 0:
        result += temp
    return result

# 从比赛名称中提取轮次信息
def extract_round(match_name):
    # 处理特殊字符，将各种破折号转换为"一"
    match_name = match_name.replace('—', '一')
    match_name = match_name.replace('-', '一')
    
    # 匹配中文数字和阿拉伯数字的轮次
    round_match = re.search(r'第([\d一二三四五六七八九十百]+)轮', match_name)
    if round_match:
        round_num = round_match.group(1)
        # 转换为阿拉伯数字
        arabic_num = chinese_to_arabic(round_num)
        return f"第{arabic_num}轮"
    else:
        # 尝试匹配其他格式的轮次信息
        round_match = re.search(r'([\d一二三四五六七八九十百]+)轮', match_name)
        if round_match:
            round_num = round_match.group(1)
            # 转换为阿拉伯数字
            arabic_num = chinese_to_arabic(round_num)
            return f"第{arabic_num}轮"
        else:
            # 尝试匹配杯赛格式，如八分之一决赛、半决赛等
            cup_match = re.search(r'(八分之一|四分之一|半决赛|决赛|半准决赛|准决赛)', match_name)
            if cup_match:
                return cup_match.group(1)
            else:
                # 尝试匹配其他可能的轮次格式
                other_match = re.search(r'(第[\d一二三四五六七八九十百]+[阶段|组])', match_name)
                if other_match:
                    return other_match.group(1)
                else:
                    return ''

# 计算胜平负结果
def calculate_result(home_team, away_team, result_str):
    if not result_str or result_str == '-':
        return ''
    
    try:
        # 解析赛果
        scores = result_str.split('-')
        if len(scores) != 2:
            return ''
        
        home_score = int(scores[0])
        away_score = int(scores[1])
        
        # 确定上海海港是主队还是客队
        if home_team == '上海海港' or home_team == '上海上港':
            if home_score > away_score:
                return '胜'
            elif home_score < away_score:
                return '负'
            else:
                return '平'
        elif away_team == '上海海港' or away_team == '上海上港':
            if away_score > home_score:
                return '胜'
            elif away_score < home_score:
                return '负'
            else:
                return '平'
        else:
            return ''
    except:
        return ''

# 读取Excel文件
excel_file = 'data/上海海港历史比分记录.xlsx'
try:
    df = pd.read_excel(excel_file, sheet_name='比赛汇总')
    print(f"成功读取Excel文件，共 {len(df)} 条记录")
except Exception as e:
    print(f"读取Excel文件失败: {e}")
    exit(1)

# 处理数据
history_data = []

for index, row in df.iterrows():
    # 提取数据
    match_type = str(row.get('比赛类别', ''))
    round_info = str(row.get('轮次', ''))
    match_time = str(row.get('比赛时间', ''))
    home_team = str(row.get('主队', ''))
    home_score = row.get('比分', '')
    away_score = row.get('Unnamed: 5', '')
    away_team = str(row.get('客队', ''))
    win_loss = str(row.get('赛果', ''))
    
    # 转换日期格式：2006.05.06 -> 2006-05-06
    date = match_time.replace('.', '-')
    
    # 构建比赛名称
    if round_info and not round_info.endswith('轮') and not round_info.endswith('赛'):
        match_name = f"{match_type}{round_info}轮"
    else:
        match_name = f"{match_type}{round_info}"
    
    # 构建赛果字符串
    if pd.notna(home_score) and pd.notna(away_score):
        try:
            result = f"{int(home_score)}-{int(away_score)}"
        except:
            result = f"{home_score}-{away_score}"
    else:
        result = ""
    
    # 提取赛季（从比赛时间中提取年份）
    if date:
        season = date.split('-')[0]
    else:
        season = ""
    
    # 创建记录
    match_record = {
        "season": season,
        "match_type": match_type,
        "match_name": match_name,
        "round": round_info,
        "date": date,
        "home_team": home_team,
        "away_team": away_team,
        "result": result,
        "win_loss": win_loss
    }
    
    history_data.append(match_record)

# 保存到JSON文件
output_file = 'data/history_schedule.json'
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(history_data, f, ensure_ascii=False, indent=2)
    print(f"成功写入JSON文件，共 {len(history_data)} 条记录")
except Exception as e:
    print(f"写入JSON文件失败: {e}")
    exit(1)

print("任务完成！")
