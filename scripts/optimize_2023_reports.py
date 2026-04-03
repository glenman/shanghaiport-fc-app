#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2023赛季赛事报告优化脚本
功能：
1. 基于号码和拼音对照球员姓名
2. 汉化球队名称
3. 优化JSON文件中的英文内容
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional

# 上海海港2023一线队大名单（基于号码和拼音）
SHANGHAI_PORT_2023_ROSTER = {
    # 门将
    1: {"name": "颜骏凌", "pinyin": "Yan Junling"},
    
    # 后卫
    2: {"name": "李昂", "pinyin": "Li Ang"},
    3: {"name": "蒋光太", "pinyin": "Jiang Guangtai"},
    4: {"name": "王燊超", "pinyin": "Wang Shenchao"},
    513: {"name": "张琳芃", "pinyin": "Zhang Linpeng"},
    13: {"name": "魏震", "pinyin": "Wei Zhen"},
    15: {"name": "明天", "pinyin": "Mingtian"},
    16: {"name": "徐新", "pinyin": "Xu Xin"},
    19: {"name": "王振澳", "pinyin": "Wang Zhen'ao"},
    20: {"name": "杨世元", "pinyin": "Yang Shiyuan"},
    21: {"name": "于海", "pinyin": "Yu Hai"},
    22: {"name": "杜佳", "pinyin": "Du Jia"},
    23: {"name": "傅欢", "pinyin": "Fu Huan"},
    24: {"name": "巴尔加斯", "pinyin": "Bargas"},
    25: {"name": "买提江", "pinyin": "Maitijiang"},
    26: {"name": "张华晨", "pinyin": "Zhang Huachen"},
    27: {"name": "冯劲", "pinyin": "Feng Jin"},
    28: {"name": "贺惯", "pinyin": "He Guan"},
    29: {"name": "张华晨", "pinyin": "Zhang Huachen"},
    31: {"name": "奚安杰", "pinyin": "Xi Anjie"},
    32: {"name": "李帅", "pinyin": "Li Shuai"},
    33: {"name": "刘祝润", "pinyin": "Liu Zhurun"},
    36: {"name": "阿布拉汗·哈力克", "pinyin": "Abdulahim Halilike"},
    37: {"name": "陈威", "pinyin": "Chen Wei"},
    38: {"name": "陈彬彬", "pinyin": "Chen Binbin"},
    39: {"name": "刘小龙", "pinyin": "Liu Xiaolong"},
    40: {"name": "吾米提江", "pinyin": "Wumitijiang"},
    41: {"name": "梁锟", "pinyin": "Liang Kun"},
    42: {"name": "向荣峻", "pinyin": "Xiang Rongjun"},
    43: {"name": "王逸伟", "pinyin": "Wang Yiwei"},
    44: {"name": "吕坤", "pinyin": "Lü Kun"},
    
    # 中场
    6: {"name": "蔡慧康", "pinyin": "Cai Huikang"},
    7: {"name": "武磊", "pinyin": "Wu Lei"},
    8: {"name": "奥斯卡", "pinyin": "Oscar"},
    9: {"name": "保利尼奥", "pinyin": "Paulinho"},
    10: {"name": "马库斯·平科", "pinyin": "Markus Pekovic"},
    11: {"name": "吕文君", "pinyin": "Lü Wenjun"},
    12: {"name": "陈威", "pinyin": "Chen Wei"},
    14: {"name": "李圣龙", "pinyin": "Li Shenglong"},
    17: {"name": "陈彬彬", "pinyin": "Chen Binbin"},
    18: {"name": "刘若钒", "pinyin": "Liu Ruofan"},
    30: {"name": "伊萨·卡隆", "pinyin": "Isa Carlon"},
    
    # 前锋
    34: {"name": "伊萨·卡隆", "pinyin": "Isa Carlon"},
    35: {"name": "阿布拉汗·哈力克", "pinyin": "Abdulahim Halilike"},
}

# 球队名称汉化字典
TEAM_NAME_TRANSLATIONS = {
    # 中超球队
    "Shanghai Port": "上海海港",
    "Shanghai Shenhua": "上海申花",
    "Beijing Guoan": "北京国安",
    "Shandong Taishan": "山东泰山",
    "Zhejiang Professional": "浙江队",
    "Chengdu Rongcheng": "成都蓉城",
    "Shanghai Port FC": "上海海港",
    "Wuhan Three Towns": "武汉三镇",
    "Tianjin Jinmen Tiger": "天津津门虎",
    "Henan": "河南队",
    "Dalian Pro": "大连人",
    "Changchun Yatai": "长春亚泰",
    "Qingdao Hainiu": "青岛海牛",
    "Cangzhou Mighty Lions": "沧州雄狮",
    "Shenzhen Pengcheng": "深圳新鹏城",
    "Meizhou Hakka": "梅州客家",
    "Nantong Zhejiang": "南通支云",
    "Qingdao West Coast": "青岛西海岸",
    "Sichuan Jiuniu": "四川九牛",
    "Chongqing Liangjiang": "重庆两江",
    "Beijing Chengyuan": "北京国安",
    "Guangzhou Evergrande": "广州队",
    "Hebei China Fortune": "河北队",
    "Xinjiang Tianshan Leopard": "新疆雪豹",
    "Guizhou": "贵州队",
    "Tianjin Teda": "天津天海",
    "Changchun Yatai FC": "长春亚泰",
    "Dalian Yingbo": "大连英博",
    "Wuhan Three Towns FC": "武汉三镇",
    "Tianjin Jinmen Tiger FC": "天津津门虎",
    "Henan FC": "河南队",
    "Dalian Pro FC": "大连人",
    "Zhejiang Professional FC": "浙江队",
    "Chengdu Rongcheng FC": "成都蓉城",
    "Shandong Taishan FC": "山东泰山",
    "Cangzhou Mighty Lions FC": "沧州雄狮",
    "Shenzhen Pengcheng FC": "深圳新鹏城",
    "Meizhou Hakka FC": "梅州客家",
    "Nantong Zhejiang FC": "南通支云",
    "Qingdao West Coast FC": "青岛西海岸",
    "Sichuan Jiuniu FC": "四川九牛",
    "Chongqing Liangjiang FC": "重庆两江",
    "Guangzhou Evergrande FC": "广州队",
    "Hebei China Fortune FC": "河北队",
    "Xinjiang Tianshan Leopard FC": "新疆雪豹",
    "Guizhou FC": "贵州队",
    "Tianjin Teda FC": "天津天海",
    "Dalian Yingbo Haifa": "大连英博海发",
}

def normalize_pinyin(pinyin: str) -> str:
    """标准化拼音，用于匹配"""
    if not pinyin:
        return ""
    # 移除空格、特殊字符，统一大小写
    pinyin = pinyin.strip().lower()
    # 移除常见的拼音分隔符
    pinyin = re.sub(r'[-\s·\'"]+', '', pinyin)
    return pinyin

def find_player_by_number(number: int) -> Optional[Dict]:
    """根据号码查找球员"""
    return SHANGHAI_PORT_2023_ROSTER.get(number)

def find_player_by_pinyin(name: str) -> Optional[Dict]:
    """根据拼音查找球员"""
    normalized_name = normalize_pinyin(name)
    
    for number, player_info in SHANGHAI_PORT_2023_ROSTER.items():
        player_pinyin = normalize_pinyin(player_info.get("pinyin", ""))
        if player_pinyin and normalized_name in player_pinyin:
            return player_info
        
        # 也检查姓名是否包含拼音
        if normalized_name in player_pinyin or player_pinyin in normalized_name:
            return player_info
    
    return None

def translate_team_name(name: str) -> str:
    """翻译球队名称"""
    if not name:
        return name
    
    # 直接匹配
    if name in TEAM_NAME_TRANSLATIONS:
        return TEAM_NAME_TRANSLATIONS[name]
    
    # 模糊匹配（包含关系）
    for eng_name, cn_name in TEAM_NAME_TRANSLATIONS.items():
        if eng_name.lower() in name.lower() or name.lower() in eng_name.lower():
            return cn_name
    
    return name

def translate_player_name(name: str, number: Optional[int] = None) -> str:
    """翻译球员名称"""
    if not name:
        return name
    
    # 如果是中文，直接返回
    if re.search(r'[\u4e00-\u9fff]', name):
        return name
    
    # 先尝试根据号码查找
    if number:
        player_info = find_player_by_number(number)
        if player_info:
            return player_info["name"]
    
    # 尝试根据拼音查找
    player_info = find_player_by_pinyin(name)
    if player_info:
        return player_info["name"]
    
    return name

def process_player(player: Dict) -> Dict:
    """处理单个球员信息"""
    number = int(player.get("number", 0))
    name = player.get("name", "")
    
    # 翻译球员名称
    translated_name = translate_player_name(name, number)
    
    # 翻译国籍
    country = player.get("country", "Unknown")
    if country == "Unknown":
        country = "中国"
    
    return {
        "position": player.get("position", "MF"),
        "number": number,
        "name": translated_name,
        "country": country
    }

def process_team(team: Dict) -> Dict:
    """处理球队信息"""
    name = team.get("name", "")
    full_name = team.get("full_name", "")
    
    # 翻译球队名称
    translated_name = translate_team_name(name)
    
    # 如果full_name为空或与name相同，生成中文名
    if not full_name or full_name == name:
        full_name = f"{translated_name}足球俱乐部"
    
    # 处理阵容
    lineup = [process_player(p) for p in team.get("lineup", [])]
    
    # 处理替补
    substitutes = [process_player(p) for p in team.get("substitutes", [])]
    
    # 处理换人记录
    substitutions = []
    for sub in team.get("substitutions", []):
        player_out = translate_player_name(sub.get("player_out", ""))
        player_in = translate_player_name(sub.get("player_in", ""))
        substitutions.append({
            "minute": sub.get("minute"),
            "player_out": player_out,
            "player_in": player_in
        })
    
    return {
        "name": translated_name,
        "full_name": full_name,
        "score": team.get("score", 0),
        "score_ht": team.get("score_ht", 0),
        "formation": team.get("formation", ""),
        "coach": team.get("coach", "待补充"),
        "captain": team.get("captain", "待补充"),
        "lineup": lineup,
        "substitutes": substitutes,
        "substitutions": substitutions
    }

def process_events(events: List[Dict]) -> List[Dict]:
    """处理比赛事件"""
    processed_events = []
    for event in events:
        player = event.get("player", "")
        player2 = event.get("player2", "")
        
        # 翻译球员名称
        translated_player = translate_player_name(player)
        translated_player2 = translate_player_name(player2)
        
        processed_events.append({
            "minute": event.get("minute"),
            "minute_extra": event.get("minute_extra"),
            "type": event.get("type"),
            "team": event.get("team"),
            "player": translated_player,
            "player2": translated_player2,
            "description": event.get("description", "")
        })
    
    return processed_events

def process_player_stats(stats: List[Dict]) -> List[Dict]:
    """处理球员统计"""
    processed_stats = []
    for stat in stats:
        player = stat.get("player", "")
        translated_player = translate_player_name(player)
        
        processed_stats.append({
            "player": translated_player,
            "goals": stat.get("goals", 0),
            "assists": stat.get("assists", 0),
            "shots": stat.get("shots", 0),
            "shots_on_target": stat.get("shots_on_target", 0),
            "passes": stat.get("passes", 0),
            "pass_accuracy": stat.get("pass_accuracy", "0%"),
            "dribbles": stat.get("dribbles", 0),
            "dribble_success": stat.get("dribble_success", 0),
            "fouls_won": stat.get("fouls_won", 0),
            "fouls_committed": stat.get("fouls_committed", 0),
            "yellow_cards": stat.get("yellow_cards", 0),
            "rating": stat.get("rating", "7.0")
        })
    
    return processed_stats

def optimize_json_file(file_path: Path) -> bool:
    """优化单个JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 处理match_info
        match_info = data.get("match_info", {})
        competition = match_info.get("competition", {})
        venue = match_info.get("venue", {})
        
        # 翻译赛事名称
        competition_name = competition.get("name", "")
        if "Chinese" in competition_name or "Super League" in competition_name:
            competition["name"] = "中国足球协会超级联赛"
        
        # 翻译场地名称
        venue_name = venue.get("name", "")
        if venue_name and not re.search(r'[\u4e00-\u9fff]', venue_name):
            translated = translate_team_name(venue_name)
            if translated != venue_name:
                venue["name"] = translated
        
        # 处理球队信息
        teams = data.get("teams", {})
        home_team = teams.get("home", {})
        away_team = teams.get("away", {})
        
        teams["home"] = process_team(home_team)
        teams["away"] = process_team(away_team)
        
        # 处理事件
        events = data.get("events", [])
        data["events"] = process_events(events)
        
        # 处理球员统计
        player_stats = data.get("player_stats", {})
        player_stats["home"] = process_player_stats(player_stats.get("home", []))
        player_stats["away"] = process_player_stats(player_stats.get("away", []))
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 已优化: {file_path.name}")
        return True
        
    except Exception as e:
        print(f"✗ 错误处理 {file_path.name}: {str(e)}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("2023赛季赛事报告优化脚本")
    print("=" * 60)
    print()
    
    # 查找2023赛季的JSON文件
    json_dir = Path("public/data/history/2023")
    if not json_dir.exists():
        print(f"错误: 目录不存在 {json_dir}")
        return
    
    json_files = sorted(json_dir.glob("*.json"))
    
    if not json_files:
        print(f"未找到2023赛季的JSON文件")
        return
    
    print(f"找到 {len(json_files)} 个2023赛季比赛文件")
    print()
    
    # 统计信息
    success_count = 0
    fail_count = 0
    
    # 处理每个文件
    for json_file in json_files:
        if optimize_json_file(json_file):
            success_count += 1
        else:
            fail_count += 1
    
    print()
    print("=" * 60)
    print("优化完成")
    print("=" * 60)
    print(f"成功: {success_count} 个文件")
    print(f"失败: {fail_count} 个文件")
    print(f"总计: {len(json_files)} 个文件")

if __name__ == "__main__":
    main()
