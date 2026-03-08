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
input_file = 'data/history_schedule.json'
try:
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"成功读取JSON文件，共 {len(data)} 条记录")
except Exception as e:
    print(f"读取JSON文件失败: {e}")
    exit(1)

# 处理轮次格式
for match in data:
    round_info = match.get('round', '')
    
    if not round_info:
        continue
    
    # 处理轮次为"nan"的情况，设置为空字符串
    if round_info == "nan":
        match['round'] = ""
        continue
    
    # 检查是否已经是"第X轮"格式
    if re.match(r'^第\d+轮', round_info):
        # 如果是"第0轮"，设置为空字符串
        if round_info == "第0轮":
            match['round'] = ""
        continue
    
    # 检查是否包含"补赛"字样
    if "补赛" in round_info:
        # 提取数字部分
        num_match = re.search(r'(\d+)', round_info)
        if num_match:
            num = num_match.group(1)
            # 转换为"第X轮（补赛）"格式
            match['round'] = f"第{num}轮（补赛）"
        continue
    
    # 检查是否包含组别信息（如"H组第一轮"）
    group_match = re.search(r'[A-Za-z]+组第([\d一二三四五六七八九十百]+)轮', round_info)
    if group_match:
        round_num = group_match.group(1)
        # 转换为阿拉伯数字
        try:
            if round_num.isdigit():
                arabic_num = int(round_num)
            else:
                arabic_num = chinese_to_arabic(round_num)
            # 如果转换结果是0，设置为空字符串
            if arabic_num == 0:
                match['round'] = ""
            else:
                match['round'] = f"第{arabic_num}轮"
        except:
            # 如果转换失败，保持原格式
            pass
        continue
    
    # 检查是否是"第X轮"格式但使用汉字数字（如"第二轮"）
    chinese_round_match = re.search(r'第([一二三四五六七八九十百]+)轮', round_info)
    if chinese_round_match:
        round_num = chinese_round_match.group(1)
        # 转换为阿拉伯数字
        try:
            arabic_num = chinese_to_arabic(round_num)
            # 如果转换结果是0，设置为空字符串
            if arabic_num == 0:
                match['round'] = ""
            else:
                match['round'] = f"第{arabic_num}轮"
        except:
            # 如果转换失败，保持原格式
            pass
        continue
    
    # 检查是否是纯数字
    if round_info.isdigit():
        # 如果是0，设置为空字符串
        if round_info == "0":
            match['round'] = ""
        else:
            match['round'] = f"第{round_info}轮"
    else:
        # 检查是否是纯汉字数字（只包含汉字数字字符，不包含其他字符）
        if all(char in '一二三四五六七八九十百' for char in round_info) and round_info:
            try:
                arabic_num = chinese_to_arabic(round_info)
                # 如果转换结果是0，设置为空字符串
                if arabic_num == 0:
                    match['round'] = ""
                else:
                    match['round'] = f"第{arabic_num}轮"
            except:
                # 如果转换失败，保持原格式
                pass
        # 对于非数字和非纯汉字数字的轮次（如"八分之一决赛"、"半决赛"等），保持原格式不变

# 保存更新后的JSON文件
output_file = 'data/history_schedule.json'
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"成功写入JSON文件，共 {len(data)} 条记录")
except Exception as e:
    print(f"写入JSON文件失败: {e}")
    exit(1)

print("轮次格式转换完成！")
