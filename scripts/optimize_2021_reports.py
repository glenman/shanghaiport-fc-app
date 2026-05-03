#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2021赛季赛事报告优化脚本
功能：
1. 只对上海海港的球员和主教练进行汉化（区分主客队）
2. 其他球队的球员保持原样
3. 优化JSON文件中的英文内容
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional

# 上海海港2021一线队大名单（基于号码）
SHANGHAI_PORT_2021_ROSTER = {
    # 门将
    1: {"name": "颜骏凌", "pinyin": "Yan Junling"},
    12: {"name": "陈威", "pinyin": "Chen Wei"},
    22: {"name": "杜佳", "pinyin": "Du Jia"},
    31: {"name": "郭通", "pinyin": "Guo Tong"},

    # 后卫
    2: {"name": "李昂", "pinyin": "Li Ang"},
    3: {"name": "于睿", "pinyin": "Yu Rui"},
    4: {"name": "王燊超", "pinyin": "Wang Shenchao"},
    5: {"name": "魏震", "pinyin": "Wei Zhen"},
    13: {"name": "李申圆", "pinyin": "Li Shenyuan"},
    18: {"name": "于海", "pinyin": "Yu Hai"},
    19: {"name": "张卫", "pinyin": "Zhang Wei"},
    20: {"name": "杨世元", "pinyin": "Yang Shiyuan"},
    23: {"name": "傅欢", "pinyin": "Fu Huan"},
    28: {"name": "贺惯", "pinyin": "He Guan"},
    29: {"name": "聂孟", "pinyin": "Nie Meng"},

    # 中场
    6: {"name": "蔡慧康", "pinyin": "Cai Huikang"},
    8: {"name": "奥斯卡", "pinyin": "Oscar"},
    9: {"name": "保利尼奥", "pinyin": "Paulinho"},
    10: {"name": "马尔科·阿瑙托维奇", "pinyin": "Marko Arnautović"},
    11: {"name": "吕文君", "pinyin": "Lü Wenjun"},
    14: {"name": "李圣龙", "pinyin": "Li Shenglong"},
    15: {"name": "张华晨", "pinyin": "Zhang Huachen"},
    16: {"name": "买提江", "pinyin": "Mirahmetjan Muzepper"},
    17: {"name": "阿布拉汗·哈力克", "pinyin": "Ablahan Haliq"},
    21: {"name": "阿隆·穆伊", "pinyin": "Aaron Mooy"},
    24: {"name": "陈纯新", "pinyin": "Chen Chunxin"},
    25: {"name": "陈彬彬", "pinyin": "Chen Binbin"},
    26: {"name": "胡靖航", "pinyin": "Hu Jinghang"},
    27: {"name": "张一", "pinyin": "Zhang Yi"},
    32: {"name": "贾博琰", "pinyin": "Jia Boyan"},
    33: {"name": "刘祝润", "pinyin": "Liu Zhurun"},

    # 前锋
    7: {"name": "里卡多·洛佩斯", "pinyin": "Ricardo Lopes Pereira"},
}

# 上海海港主教练名单
SHANGHAI_PORT_COACHES = {
    "Ivan Leko": "伊万·莱科",
    "Kim Jinho": "金度亨",
    "Javier Aguirre": "哈维尔·阿吉雷",
    "Milan Ivanovic": "米兰·伊万诺维奇",
    "Xu Genbao": "徐根宝",
    "Shi Jin": "石玏",
    "Wu Jingui": "吴金贵",
}

def is_shanghai_port_team(team_name: str) -> bool:
    """判断是否是上海海港球队"""
    if not team_name:
        return False
    shanghai_port_names = [
        "Shanghai Port", "Shanghai Port FC",
        "上海海港", "上海海港足球俱乐部",
        "Port", "SIPG"
    ]
    return team_name in shanghai_port_names

def normalize_pinyin(pinyin: str) -> str:
    """标准化拼音，用于匹配"""
    if not pinyin:
        return ""
    pinyin = pinyin.strip().lower()
    pinyin = re.sub(r'[-\s·\'"]+', '', pinyin)
    return pinyin

def find_player_by_number(number: int) -> Optional[Dict]:
    """根据号码查找球员"""
    return SHANGHAI_PORT_2021_ROSTER.get(number)

def find_player_by_pinyin(name: str) -> Optional[Dict]:
    """根据拼音查找球员"""
    normalized_name = normalize_pinyin(name)

    for number, player_info in SHANGHAI_PORT_2021_ROSTER.items():
        player_pinyin = normalize_pinyin(player_info.get("pinyin", ""))
        if player_pinyin and (normalized_name in player_pinyin or player_pinyin in normalized_name):
            return player_info

    return None

def translate_coach_name(coach_name: str) -> str:
    """翻译主教练名称（只对上海海港有效）"""
    if not coach_name:
        return coach_name

    if coach_name in SHANGHAI_PORT_COACHES:
        return SHANGHAI_PORT_COACHES[coach_name]

    for eng_name, cn_name in SHANGHAI_PORT_COACHES.items():
        if normalize_pinyin(eng_name) in normalize_pinyin(coach_name):
            return cn_name

    return coach_name

def translate_player_name(name: str, number: Optional[int] = None, is_port_team: bool = False) -> str:
    """翻译球员名称（只对上海海港有效）"""
    if not name:
        return name

    if re.search(r'[\u4e00-\u9fff]', name):
        return name

    if not is_port_team:
        return name

    if number:
        player_info = find_player_by_number(number)
        if player_info:
            return player_info["name"]

    player_info = find_player_by_pinyin(name)
    if player_info:
        return player_info["name"]

    return name

def process_player(player: Dict, is_port_team: bool = False) -> Dict:
    """处理单个球员信息"""
    try:
        number = int(player.get("number", 0))
    except (ValueError, TypeError):
        number = 0

    name = player.get("name", "")

    translated_name = translate_player_name(name, number, is_port_team)

    country = player.get("country", "Unknown")
    if is_port_team and country == "Unknown":
        country = "中国"

    return {
        "position": player.get("position", "MF"),
        "number": number,
        "name": translated_name,
        "country": country
    }

def process_team(team: Dict, is_port_team: bool = False) -> Dict:
    """处理球队信息"""
    name = team.get("name", "")
    full_name = team.get("full_name", "")

    if is_port_team:
        if not full_name or full_name == name:
            full_name = "上海海港足球俱乐部"
    else:
        if not full_name or full_name == name:
            full_name = name

    lineup = [process_player(p, is_port_team) for p in team.get("lineup", [])]
    substitutes = [process_player(p, is_port_team) for p in team.get("substitutes", [])]

    substitutions = []
    for sub in team.get("substitutions", []):
        player_out = translate_player_name(sub.get("player_out", ""), is_port_team=is_port_team)
        player_in = translate_player_name(sub.get("player_in", ""), is_port_team=is_port_team)
        substitutions.append({
            "minute": sub.get("minute"),
            "minute_extra": sub.get("minute_extra"),
            "player_out": player_out,
            "player_in": player_in
        })

    coach = team.get("coach", "")
    if is_port_team and coach:
        coach = translate_coach_name(coach)

    captain = translate_player_name(team.get("captain", ""), is_port_team=is_port_team)

    return {
        "name": name,
        "full_name": full_name,
        "score": team.get("score", 0),
        "score_ht": team.get("score_ht", 0),
        "formation": team.get("formation", ""),
        "coach": coach if is_port_team else team.get("coach", ""),
        "captain": captain,
        "lineup": lineup,
        "substitutes": substitutes,
        "substitutions": substitutions
    }

def process_events(events: List[Dict], home_is_port: bool, away_is_port: bool) -> List[Dict]:
    """处理比赛事件"""
    processed_events = []
    for event in events:
        player = event.get("player", "")
        player2 = event.get("player2", "")
        team = event.get("team", "")

        is_port_team = home_is_port if team == "home" else away_is_port

        translated_player = translate_player_name(player, is_port_team=is_port_team)
        translated_player2 = translate_player_name(player2, is_port_team=is_port_team)

        processed_events.append({
            "minute": event.get("minute"),
            "minute_extra": event.get("minute_extra"),
            "type": event.get("type"),
            "team": team,
            "player": translated_player,
            "player2": translated_player2,
            "description": event.get("description", "")
        })

    return processed_events

def process_player_stats(stats: List[Dict], is_port_team: bool = False) -> List[Dict]:
    """处理球员统计"""
    processed_stats = []
    for stat in stats:
        player = stat.get("player", "")
        translated_player = translate_player_name(player, is_port_team=is_port_team)

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
            "red_cards": stat.get("red_cards", 0),
            "rating": stat.get("rating", "7.0")
        })

    return processed_stats

def optimize_json_file(file_path: Path) -> bool:
    """优化单个JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        match_info = data.get("match_info", {})
        competition = match_info.get("competition", {})
        venue = match_info.get("venue", {})

        competition_name = competition.get("name", "")
        if "Chinese" in competition_name or "Super League" in competition_name:
            competition["name"] = "中国足球协会超级联赛"

        round_name = competition.get("round", "")
        if "Matchweek" in round_name:
            round_num = round_name.replace("Matchweek", "").strip()
            competition["round"] = f"第{round_num}轮"

        venue_name = venue.get("name", "")
        if venue_name and not re.search(r'[\u4e00-\u9fff]', venue_name):
            venue["name"] = "待补充"

        teams = data.get("teams", {})
        home_team = teams.get("home", {})
        away_team = teams.get("away", {})

        home_name = home_team.get("name", "")
        away_name = away_team.get("name", "")

        home_is_port = is_shanghai_port_team(home_name)
        away_is_port = is_shanghai_port_team(away_name)

        teams["home"] = process_team(home_team, home_is_port)
        teams["away"] = process_team(away_team, away_is_port)

        events = data.get("events", [])
        data["events"] = process_events(events, home_is_port, away_is_port)

        if "player_stats" in data:
            player_stats = data.get("player_stats", {})
            if "home" in player_stats:
                player_stats["home"] = process_player_stats(player_stats.get("home", []), home_is_port)
            if "away" in player_stats:
                player_stats["away"] = process_player_stats(player_stats.get("away", []), away_is_port)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        status = "✓" if (home_is_port or away_is_port) else "⚠️"
        print(f"{status} {file_path.name} (home_is_port={home_is_port}, away_is_port={away_is_port})")
        return True

    except Exception as e:
        print(f"✗ 错误处理 {file_path.name}: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("2021赛季赛事报告优化脚本（只汉化上海海港球员和教练）")
    print("=" * 60)
    print()

    json_dir = Path("public/data/history/2021")
    if not json_dir.exists():
        print(f"错误: 目录不存在 {json_dir}")
        return

    json_files = sorted(json_dir.glob("*.json"))

    if not json_files:
        print(f"未找到2021赛季的JSON文件")
        return

    print(f"找到 {len(json_files)} 个2021赛季比赛文件")
    print()

    success_count = 0
    fail_count = 0

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
