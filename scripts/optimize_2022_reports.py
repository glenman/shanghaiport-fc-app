#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2022赛季赛事报告优化脚本
功能：
1. 从CSV大名单加载球员映射（英文名称 -> 中文名称 + 位置）
2. 根据比赛中上海海港是主队还是客队进行判断
3. 只对上海海港的球员进行汉化（首发、替补、事件）
4. 更新场地、主教练、裁判信息
5. 更新球员位置信息
"""

import csv
import json
import re
from pathlib import Path
from typing import Dict, List

# 配置
ROSTER_CSV_PATH = r'datafile/上海海港2022一线队大名单.csv'

# 上海海港英文名称标识
SHANGHAI_PORT_ENGLISH_NAMES = ["Shanghai Port", "Shanghai Port FC", "SIPG"]

# 球队名称汉化字典
TEAM_NAME_TRANSLATIONS = {
    "Shanghai Port": "上海海港",
    "Shanghai Port FC": "上海海港",
    "Shanghai Shenhua": "上海绿地",
    "Beijing Guoan": "北京国安",
    "Shandong Taishan": "山东泰山",
    "Zhejiang Professional": "浙江队",
    "Chengdu Rongcheng": "成都蓉城",
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
    "Guangzhou Evergrande": "广州队",
    "Hebei China Fortune": "河北队",
    "Wuhan Zall": "武汉长江",
}

# 主教练映射
COACH_TRANSLATIONS = {
    "Ivan Leko": "伊万·莱科",
    "Ivan\u00A0Leko": "伊万·莱科",  # 处理NBSP特殊空格
    "Vítor Pereira": "维托尔·佩雷拉",
    "André Villas-Boas": "安德烈·维拉斯-博阿斯",
    "Wu Jingui": "吴金贵",
    "Wu\u00A0Jingui": "吴金贵",  # 处理NBSP特殊空格
}

# 场地名称汉化
VENUE_TRANSLATIONS = {
    "Jinzhou Stadium": "金州体育场",
    "Shanghai Stadium": "上海体育场",
    "Pudong Football Stadium": "浦东足球场",
    "SAIC Motor Pudong Arena": "上汽浦东足球场",
    "Tianjin Olympic Center Stadium": "天津奥林匹克中心体育场",
    "Beijing Workers Stadium": "北京工人体育场",
    "Shandong Sports Center": "山东省体育中心体育场",
    "Chengdu Longquanyi Football Stadium": "成都龙泉驿足球场",
    "Wuhan Five Rings Sports Center": "武汉五环体育中心",
    "Dalian Sports Center Stadium": "大连体育中心体育场",
    "Haikou City Stadium": "海口市五源河体育场",
    "Huangshi Stadium": "黄石市奥体中心",
    "Nanjing Olympic Sports Center": "南京奥体中心体育场",
    "Suzhou Sports Center": "苏州市体育中心体育场",
    "Kunming Football Center": "昆明市足球训练基地",
    "Zhengzhou Hanghai Stadium": "郑州航海体育场",
    "Jinan Olympic Sports Center": "济南奥体中心体育场",
    "Guangzhou Tianhe Stadium": "广州天河体育场",
    "Shenzhen Universiade Center": "深圳大运中心体育场",
    "Meizhou Sports Center": "梅州五华惠堂体育场",
    "Rizhao International Football Centre Stadium": "日照国际足球中心体育场",
    "Puwan Stadium": "普湾体育场",
}

# 位置缩写映射
POSITION_MAPPING = {
    "GK": "门将",
    "DF": "后卫",
    "MF": "中场",
    "FW": "前锋",
}

def load_roster_from_csv(csv_path: str) -> Dict[str, dict]:
    """从CSV文件加载球员信息（英文名称 -> 中文名称 + 位置）"""
    player_map = {}
    
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name_en = row.get('英文名称', '').strip()
            name_cn = row.get('中文名称', '').strip()
            position = row.get('位置', '').strip()
            
            if name_en and name_cn:
                player_map[name_en] = {
                    'name': name_cn,
                    'position': position
                }
                player_map[name_en.replace(' ', '')] = {
                    'name': name_cn,
                    'position': position
                }
                player_map[name_en.lower()] = {
                    'name': name_cn,
                    'position': position
                }
                # 同时添加中文名称到映射，方便查找位置
                player_map[name_cn] = {
                    'name': name_cn,
                    'position': position
                }
    
    print(f"已从CSV加载 {len(player_map)} 名球员")
    return player_map

def is_shanghai_port_team(team_name: str) -> bool:
    """判断是否是上海海港球队"""
    if not team_name:
        return False
    team_name_lower = team_name.lower().strip()
    
    # 检查英文名称
    for port_name in SHANGHAI_PORT_ENGLISH_NAMES:
        if port_name.lower() in team_name_lower:
            return True
    
    # 检查中文名称
    chinese_port_names = ["上海海港", "上海上港"]
    for port_name in chinese_port_names:
        if port_name in team_name:
            return True
    
    return False

def translate_team_name(name: str) -> str:
    """翻译球队名称"""
    if not name:
        return name
    if name in TEAM_NAME_TRANSLATIONS:
        return TEAM_NAME_TRANSLATIONS[name]
    for eng_name, cn_name in TEAM_NAME_TRANSLATIONS.items():
        if eng_name.lower() in name.lower():
            return cn_name
    return name

def translate_player_info(name: str, player_map: Dict[str, dict]) -> dict:
    """获取球员信息（中文名称和位置）"""
    if not name:
        return {'name': name, 'position': ''}
    
    # 先尝试精确匹配（支持中英文）
    if name in player_map:
        return player_map[name]
    
    # 如果已经是中文，尝试查找
    if re.search(r'[\u4e00-\u9fff]', name):
        # 尝试在player_map中查找中文名称
        for key, info in player_map.items():
            if info['name'] == name:
                return info
        return {'name': name, 'position': ''}
    
    # 去空格匹配
    name_no_space = name.replace(' ', '')
    if name_no_space in player_map:
        return player_map[name_no_space]
    
    # 小写匹配
    name_lower = name.lower()
    if name_lower in player_map:
        return player_map[name_lower]
    
    # 包含匹配
    for eng_name, info in player_map.items():
        if eng_name.lower() in name_lower or name_lower in eng_name.lower():
            return info
    
    return {'name': name, 'position': ''}

def translate_coach_name(coach_name: str) -> str:
    """翻译主教练名称"""
    if not coach_name:
        return coach_name
    
    # 先尝试直接匹配
    if coach_name in COACH_TRANSLATIONS:
        return COACH_TRANSLATIONS[coach_name]
    
    # 处理特殊空格字符（NBSP）
    coach_name_clean = coach_name.replace('\u00A0', ' ').replace('\u200b', '')
    if coach_name_clean in COACH_TRANSLATIONS:
        return COACH_TRANSLATIONS[coach_name_clean]
    
    # 尝试去除所有空格后匹配
    coach_name_no_space = coach_name.replace(' ', '').replace('\u00A0', '').replace('\u200b', '')
    for eng_name, cn_name in COACH_TRANSLATIONS.items():
        eng_name_no_space = eng_name.replace(' ', '').replace('\u00A0', '')
        if eng_name_no_space == coach_name_no_space:
            return cn_name
    
    return coach_name

def translate_venue_name(venue_name: str) -> str:
    """翻译场地名称"""
    if not venue_name:
        return venue_name
    if venue_name in VENUE_TRANSLATIONS:
        return VENUE_TRANSLATIONS[venue_name]
    for eng_name, cn_name in VENUE_TRANSLATIONS.items():
        if eng_name.lower() in venue_name.lower():
            return cn_name
    return venue_name

def translate_referee_name(referee_name: str) -> str:
    """翻译裁判姓名（去除特殊字符）"""
    if not referee_name:
        return referee_name
    # 去除特殊空格字符
    return referee_name.replace('\u200b', '').replace('\u00a0', ' ').strip()

def process_team(team: Dict, is_port_team: bool, player_map: Dict[str, dict], events: List[Dict] = None) -> Dict:
    """处理球队信息"""
    name = team.get("name", "")
    full_name = team.get("full_name", "")
    translated_name = translate_team_name(name)
    
    if is_port_team:
        full_name = "上海海港足球俱乐部" if not full_name or full_name == name else full_name
    else:
        full_name = translated_name if not full_name or full_name == name else full_name
    
    # 处理首发球员（更新姓名和位置）
    lineup = []
    for p in team.get("lineup", []):
        player_name = p.get("name", "")
        player_info = translate_player_info(player_name, player_map) if is_port_team else {'name': player_name, 'position': ''}
        
        # 使用大名单中的位置，如果没有则使用原位置
        position = player_info['position'] if player_info['position'] else p.get("position", "MF")
        
        lineup.append({
            "position": position,
            "number": int(p.get("number", 0)) if isinstance(p.get("number"), (int, str)) else 0,
            "name": player_info['name'],
            "country": "中国" if is_port_team else p.get("country", "Unknown")
        })
    
    # 处理替补球员（更新姓名和位置）
    substitutes = []
    for p in team.get("substitutes", []):
        player_name = p.get("name", "")
        player_info = translate_player_info(player_name, player_map) if is_port_team else {'name': player_name, 'position': ''}
        
        # 使用大名单中的位置，如果没有则使用原位置
        position = player_info['position'] if player_info['position'] else p.get("position", "MF")
        
        substitutes.append({
            "position": position,
            "number": int(p.get("number", 0)) if isinstance(p.get("number"), (int, str)) else 0,
            "name": player_info['name'],
            "country": "中国" if is_port_team else p.get("country", "Unknown")
        })
    
    # 从events中提取换人信息（支持同分钟多次换人）
    event_substitutions = {}
    if events:
        for event in events:
            if event.get("type") == "substitution":
                minute = event.get("minute", 0)
                player_in = event.get("player", "")
                player_out = event.get("player_out", "")
                if minute not in event_substitutions:
                    event_substitutions[minute] = []
                event_substitutions[minute].append({"player_in": player_in, "player_out": player_out})
    
    # 处理换人记录
    substitutions = []
    for idx, sub in enumerate(team.get("substitutions", [])):
        minute = sub.get("minute", 0)
        player_out = sub.get("player_out", "")
        player_in = sub.get("player_in", "")
        
        # 如果player_in为空，从events中获取
        if not player_in and minute in event_substitutions:
            # 获取该分钟的换人列表
            minute_subs = event_substitutions[minute]
            # 如果有多个换人，尝试根据player_out匹配
            if len(minute_subs) == 1:
                player_in = minute_subs[0].get("player_in", "")
            else:
                # 多个换人时，根据player_out匹配
                for s in minute_subs:
                    if player_out and s.get("player_out", "").lower() == player_out.lower():
                        player_in = s.get("player_in", "")
                        break
                # 如果没匹配到，使用第一个
                if not player_in and minute_subs:
                    player_in = minute_subs[0].get("player_in", "")
        
        if is_port_team:
            player_out_info = translate_player_info(player_out, player_map)
            player_in_info = translate_player_info(player_in, player_map)
            player_out = player_out_info['name']
            player_in = player_in_info['name']
        
        substitutions.append({
            "minute": minute,
            "minute_extra": sub.get("minute_extra"),
            "player_out": player_out,
            "player_in": player_in
        })
    
    # 翻译主教练和队长
    coach = team.get("coach", "")
    captain = team.get("captain", "")
    if is_port_team:
        coach = translate_coach_name(coach)
        captain_info = translate_player_info(captain, player_map)
        captain = captain_info['name']
    
    return {
        "name": translated_name,
        "full_name": full_name,
        "score": team.get("score", 0),
        "score_ht": team.get("score_ht", 0),
        "formation": team.get("formation", ""),
        "coach": coach,
        "captain": captain,
        "lineup": lineup,
        "substitutes": substitutes,
        "substitutions": substitutions
    }

def process_events(events: List[Dict], home_is_port: bool, away_is_port: bool, player_map: Dict[str, dict]) -> List[Dict]:
    """处理比赛事件 - 替换球员姓名"""
    processed_events = []
    for event in events:
        player = event.get("player", "")
        player2 = event.get("player2", "")
        player_out = event.get("player_out", "")
        team = event.get("team", "")
        
        # 判断是否是海港的事件
        is_port_event = (team == "home" and home_is_port) or (team == "away" and away_is_port)
        
        # 替换球员姓名
        if is_port_event:
            player_info = translate_player_info(player, player_map)
            player = player_info['name']
            
            player2_info = translate_player_info(player2, player_map)
            player2 = player2_info['name']
            
            player_out_info = translate_player_info(player_out, player_map)
            player_out = player_out_info['name']
        
        # 保留所有原始字段
        processed_event = {
            "minute": event.get("minute"),
            "minute_extra": event.get("minute_extra"),
            "type": event.get("type"),
            "team": event.get("team"),
            "player": player,
            "player2": player2,
            "description": event.get("description", "")
        }
        
        if "player_out" in event:
            processed_event["player_out"] = player_out
        
        processed_events.append(processed_event)
    
    return processed_events

def optimize_json_file(file_path: Path, player_map: Dict[str, dict]) -> bool:
    """优化单个JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 处理赛事信息
        match_info = data.get("match_info", {})
        competition = match_info.get("competition", {})
        venue = match_info.get("venue", {})
        referee = match_info.get("referee", {})
        
        # 翻译赛事名称
        if "Chinese" in competition.get("name", "") or "Super League" in competition.get("name", ""):
            competition["name"] = "中国足球协会超级联赛"
        
        # 翻译轮次
        if "Matchweek" in competition.get("round", ""):
            round_num = competition["round"].replace("Matchweek", "").strip()
            competition["round"] = f"第{round_num}轮"
        
        # 翻译场地名称
        venue_name = venue.get("name", "")
        if venue_name:
            venue["name"] = translate_venue_name(venue_name)
        
        # 翻译裁判姓名
        referee["main"] = translate_referee_name(referee.get("main", ""))
        referee["ar1"] = translate_referee_name(referee.get("ar1", ""))
        referee["ar2"] = translate_referee_name(referee.get("ar2", ""))
        referee["fourth"] = translate_referee_name(referee.get("fourth", ""))
        referee["var"] = translate_referee_name(referee.get("var", ""))
        
        # 判断海港是主队还是客队
        teams = data.get("teams", {})
        home_team = teams.get("home", {})
        away_team = teams.get("away", {})
        
        home_team_name = home_team.get("name", "")
        away_team_name = away_team.get("name", "")
        
        home_is_port = is_shanghai_port_team(home_team_name)
        away_is_port = is_shanghai_port_team(away_team_name)
        
        # 先处理事件（用于补充换人信息）
        events = data.get("events", [])
        processed_events = process_events(events, home_is_port, away_is_port, player_map)
        data["events"] = processed_events
        
        # 处理球队（传递原始events以正确匹配换人信息）
        teams["home"] = process_team(home_team, home_is_port, player_map, events)
        teams["away"] = process_team(away_team, away_is_port, player_map, events)
        
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
    print("2022赛季赛事报告优化脚本")
    print("基于CSV大名单进行球员姓名和位置更新")
    print("=" * 60)
    
    # 加载球员映射
    player_map = load_roster_from_csv(ROSTER_CSV_PATH)
    if not player_map:
        print("错误: 未能加载球员大名单")
        return
    
    # 查找JSON文件
    json_dir = Path("public/data/history/2022")
    json_files = sorted(json_dir.glob("*.json"))
    
    print(f"\n找到 {len(json_files)} 个2022赛季比赛文件")
    
    # 处理每个文件
    for json_file in json_files:
        optimize_json_file(json_file, player_map)
    
    print("\n优化完成")

if __name__ == "__main__":
    main()