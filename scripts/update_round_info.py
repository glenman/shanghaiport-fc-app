#!/usr/bin/env python3
import json
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

# 读取JSON文件
with open('data/history_schedule.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 处理每个比赛记录
for match in data:
    match_name = match.get('match_name', '')
    # 从match_name中提取轮次信息
    
    # 处理特殊字符，将各种破折号转换为"一"
    match_name = match_name.replace('—', '一')  # 将全角破折号替换为"一"
    match_name = match_name.replace('-', '一')  # 将半角破折号替换为"一"
    
    # 匹配中文数字和阿拉伯数字的轮次
    round_match = re.search(r'第([\d一二三四五六七八九十百]+)轮', match_name)
    if round_match:
        round_num = round_match.group(1)
        # 转换为阿拉伯数字
        arabic_num = chinese_to_arabic(round_num)
        match['round'] = f"第{arabic_num}轮"
    else:
        # 尝试匹配其他格式的轮次信息
        round_match = re.search(r'([\d一二三四五六七八九十百]+)轮', match_name)
        if round_match:
            round_num = round_match.group(1)
            # 转换为阿拉伯数字
            arabic_num = chinese_to_arabic(round_num)
            match['round'] = f"第{arabic_num}轮"
        else:
            # 尝试匹配杯赛格式，如八分之一决赛、半决赛等
            cup_match = re.search(r'(八分之一|四分之一|半决赛|决赛|半准决赛|准决赛)', match_name)
            if cup_match:
                match['round'] = cup_match.group(1)
            else:
                # 尝试匹配其他可能的轮次格式
                other_match = re.search(r'(第[\d一二三四五六七八九十百]+[阶段|组])', match_name)
                if other_match:
                    match['round'] = other_match.group(1)
                else:
                    match['round'] = ''

# 保存更新后的JSON文件
with open('data/history_schedule.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"更新轮次信息成功，处理了 {len(data)} 条比赛记录")