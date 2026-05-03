#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2022赛季赛事报告优化脚本
功能：
1. 只对上海海港的球员和主教练进行汉化
2. 其他球队的球员保持原样
3. 优化JSON文件中的英文内容
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional

# 上海海港2022一线队大名单（基于CSV文件）
SHANGHAI_PORT_2022_ROSTER = {
    # 门将
    "颜骏凌": {"number": 1, "pinyin": "Yan Junling", "country": "中国"},
    "吕文君": {"number": 3, "pinyin": "Lü Wenjun", "country": "中国"},
    "王燊超": {"number": 4, "pinyin": "Wang Shenchao", "country": "中国"},
    "保利尼奥": {"number": 5, "pinyin": "Paulinho", "country": "巴西"},
    "蔡慧康": {"number": 6, "pinyin": "Cai Huikang", "country": "中国"},
    "魏震": {"number": 7, "pinyin": "Wei Zhen", "country": "中国"},
    "恩迪亚耶": {"number": 8, "pinyin": "Cherif Ndiaye", "country": "塞内加尔"},
    "李昂": {"number": 9, "pinyin": "Li Ang", "country": "中国"},
    "马蒂亚斯·巴尔加斯": {"number": 10, "pinyin": "Matías Vargas", "country": "阿根廷"},
    "张琳芃": {"number": 11, "pinyin": "Zhang Linpeng", "country": "中国"},
    "蒋光太": {"number": 12, "pinyin": "Tyias Browning", "country": "中国"},
    "李申圆": {"number": 13, "pinyin": "Li Shenyuan", "country": "中国"},
    "冯劲": {"number": 14, "pinyin": "Feng Jing", "country": "中国"},
    "武磊": {"number": 15, "pinyin": "Wu Lei", "country": "中国"},
    "张华晨": {"number": 16, "pinyin": "Zhang Huachen", "country": "中国"},
    "买提江": {"number": 17, "pinyin": "Mirahmetjan Muzepper", "country": "中国"},
    "于海": {"number": 18, "pinyin": "Yu Hai", "country": "中国"},
    "徐新": {"number": 19, "pinyin": "Xu Xin", "country": "中国"},
    "陈纯新": {"number": 20, "pinyin": "Chen Chunxin", "country": "中国"},
    "刘祝润": {"number": 21, "pinyin": "Liu Zhurun", "country": "中国"},
    "卡隆": {"number": 22, "pinyin": "Issa Kallon", "country": "塞拉利昂"},
    "王逸伟": {"number": 23, "pinyin": "Wang Yiwei", "country": "中国"},
    "刘柏杨": {"number": 24, "pinyin": "Liu Baiyang", "country": "中国"},
    "杨世元": {"number": 25, "pinyin": "Yang Shiyuan", "country": "中国"},
    "贺惯": {"number": 26, "pinyin": "He Guan", "country": "中国"},
    "阿布拉汗·哈力克": {"number": 27, "pinyin": "Ablahan Haliq", "country": "中国"},
    "陈威": {"number": 28, "pinyin": "Chen Wei", "country": "中国"},
    "傅欢": {"number": 29, "pinyin": "Fu Huan", "country": "中国"},
    "李圣龙": {"number": 30, "pinyin": "Li Shenglong", "country": "中国"},
    "奥斯卡": {"number": 31, "pinyin": "Oscar", "country": "巴西"},
    "陈旭黄": {"number": 32, "pinyin": "Chen Xuhuang", "country": "中国"},
    "李帅": {"number": 33, "pinyin": "Li Shuai", "country": "中国"},
    "赵申澳": {"number": 34, "pinyin": "Zhao Shen'ao", "country": "中国"},
    "杨子涵": {"number": 35, "pinyin": "Yang Zihan", "country": "中国"},
    "杜佳": {"number": 36, "pinyin": "Du Jia", "country": "中国"},
    "向荣峻": {"number": 37, "pinyin": "Xiang Rongjun", "country": "中国"},
    "黎德明": {"number": 38, "pinyin": "Li Deming", "country": "中国"},
    "王淞": {"number": 39, "pinyin": "Wang Song", "country": "中国"},
    "陈彬彬": {"number": 40, "pinyin": "Chen Binbin", "country": "中国"},
    "奚安杰": {"number": 41, "pinyin": "Xi Anjie", "country": "中国"},
    "张慧宇": {"number": 42, "pinyin": "Zhang Huiyu", "country": "中国"},
    "梁锟": {"number": 43, "pinyin": "Liang Kun", "country": "中国"},
    "吕坤": {"number": 44, "pinyin": "Lyu Kun", "country": "中国"},
    "王玉龙": {"number": 45, "pinyin": "Wang Yulong", "country": "中国"},
    "汤宇璇": {"number": 46, "pinyin": "Tang Yuxuan", "country": "中国"},
}

# 上海海港主教练名单
SHANGHAI_PORT_COACHES = {
    "Ivan Leko": "伊万·莱科",
    "Vítor Pereira": "维托尔·佩雷拉",
    "André Villas-Boas": "安德烈·维拉斯-博阿斯",
    "Xu Genbao": "徐根宝",
    "Shi Jin": "石玏",
    "Wu Jingui": "吴金贵",
}

# 判断是否是上海海港球队的函数
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

# 球队名称汉化字典
TEAM_NAME_TRANSLATIONS = {
    "Shanghai Port": "上海海港",
    "Shanghai Shenhua": "上海海港",
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
    "Wuhan Zall": "武汉长江",
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
    "Changbinwang Stadium": "廊坊市体育场",
    "Guangzhou Tianhe Stadium": "广州天河体育场",
    "Shenzhen Universiade Center": "深圳大运中心体育场",
    "Wenzhou Longwan Stadium": "温州市奥体中心体育场",
    "Xinhua Street Stadium": "新华路体育场",
    "Yanbian Stadium": "延吉市人民体育场",
    "Meizhou Sports Center": "梅州五华惠堂体育场",
    "Putian Stadium": "莆田市体育中心体育场",
    "Liaoning Stadium": "辽宁省体育场",
}

def normalize_pinyin(pinyin: str) -> str:
    """标准化拼音，用于匹配"""
    if not pinyin:
        return ""
    pinyin = pinyin.strip().lower()
    pinyin = re.sub(r'[-\s·\'"]+', '', pinyin)
    return pinyin

def find_player_by_pinyin(name: str) -> Optional[Dict]:
    """根据拼音查找球员"""
    normalized_name = normalize_pinyin(name)

    for cn_name, player_info in SHANGHAI_PORT_2022_ROSTER.items():
        player_pinyin = normalize_pinyin(player_info.get("pinyin", ""))
        if player_pinyin and (normalized_name in player_pinyin or player_pinyin in normalized_name):
            return {"name": cn_name, **player_info}

    return None

def find_player_by_number_and_team(number: int, team_name: str) -> Optional[Dict]:
    """根据号码查找球员（只对上海海港有效）"""
    if not is_shanghai_port_team(team_name):
        return None

    for cn_name, player_info in SHANGHAI_PORT_2022_ROSTER.items():
        if player_info.get("number") == number:
            return {"name": cn_name, **player_info}

    return None

def translate_team_name(name: str) -> str:
    """翻译球队名称"""
    if not name:
        return name

    if name in TEAM_NAME_TRANSLATIONS:
        return TEAM_NAME_TRANSLATIONS[name]

    for eng_name, cn_name in TEAM_NAME_TRANSLATIONS.items():
        if eng_name.lower() in name.lower() or name.lower() in eng_name.lower():
            return cn_name

    return name

def translate_venue_name(name: str) -> str:
    """翻译场地名称"""
    if not name:
        return name

    if name in VENUE_TRANSLATIONS:
        return VENUE_TRANSLATIONS[name]

    for eng_name, cn_name in VENUE_TRANSLATIONS.items():
        if eng_name.lower() in name.lower() or name.lower() in eng_name.lower():
            return cn_name

    return name

def translate_coach_name(coach_name: str, team_name: str) -> str:
    """翻译主教练名称（只对上海海港有效）"""
    if not coach_name:
        return coach_name

    # 如果不是上海海港，保持原样
    if not is_shanghai_port_team(team_name):
        return coach_name

    # 检查是否是已知的主教练
    if coach_name in SHANGHAI_PORT_COACHES:
        return SHANGHAI_PORT_COACHES[coach_name]

    # 尝试根据拼音查找
    for eng_name, cn_name in SHANGHAI_PORT_COACHES.items():
        if normalize_pinyin(eng_name) in normalize_pinyin(coach_name):
            return cn_name

    return coach_name

def translate_player_name(name: str, number: Optional[int] = None, team_name: str = "") -> str:
    """翻译球员名称（只对上海海港有效）"""
    if not name:
        return name

    # 如果是中文，直接返回
    if re.search(r'[\u4e00-\u9fff]', name):
        return name

    # 如果不是上海海港，保持原样
    if not is_shanghai_port_team(team_name):
        return name

    # 先尝试根据号码查找
    if number:
        player_info = find_player_by_number_and_team(number, team_name)
        if player_info:
            return player_info["name"]

    # 尝试根据拼音查找
    player_info = find_player_by_pinyin(name)
    if player_info:
        return player_info["name"]

    return name

def process_player(player: Dict, team_name: str = "") -> Dict:
    """处理单个球员信息"""
    try:
        number = int(player.get("number", 0))
    except (ValueError, TypeError):
        number = 0

    name = player.get("name", "")

    # 只有上海海港的球员才翻译
    translated_name = translate_player_name(name, number, team_name)

    # 只有上海海港的球员才翻译国籍
    country = player.get("country", "Unknown")
    if is_shanghai_port_team(team_name) and country == "Unknown":
        country = "中国"

    return {
        "position": player.get("position", "MF"),
        "number": number,
        "name": translated_name,
        "country": country
    }

def process_team(team: Dict, is_home: bool = True) -> Dict:
    """处理球队信息"""
    name = team.get("name", "")
    full_name = team.get("full_name", "")

    # 判断是否是上海海港
    is_port = is_shanghai_port_team(name)

    # 翻译球队名称
    translated_name = translate_team_name(name)

    # 生成full_name
    if is_port:
        if not full_name or full_name == name:
            full_name = "上海海港足球俱乐部"
    else:
        if not full_name or full_name == name:
            full_name = f"{translated_name}"

    # 处理阵容（传入球队名称以判断是否是上海海港）
    lineup = [process_player(p, name) for p in team.get("lineup", [])]

    # 处理替补
    substitutes = [process_player(p, name) for p in team.get("substitutes", [])]

    # 处理换人记录
    substitutions = []
    for sub in team.get("substitutions", []):
        player_out = translate_player_name(sub.get("player_out", ""), team_name=name)
        player_in = translate_player_name(sub.get("player_in", ""), team_name=name)
        substitutions.append({
            "minute": sub.get("minute"),
            "minute_extra": sub.get("minute_extra"),
            "player_out": player_out,
            "player_in": player_in
        })

    # 翻译主教练（只对上海海港）
    coach = translate_coach_name(team.get("coach", ""), name)

    # 翻译队长（只对上海海港）
    captain = translate_player_name(team.get("captain", ""), team_name=name)

    return {
        "name": translated_name,
        "full_name": full_name,
        "score": team.get("score", 0),
        "score_ht": team.get("score_ht", 0),
        "formation": team.get("formation", ""),
        "coach": coach if is_port else team.get("coach", ""),
        "captain": captain,
        "lineup": lineup,
        "substitutes": substitutes,
        "substitutions": substitutions
    }

def process_events(events: List[Dict], home_team_name: str = "", away_team_name: str = "") -> List[Dict]:
    """处理比赛事件"""
    processed_events = []
    for event in events:
        player = event.get("player", "")
        player2 = event.get("player2", "")
        team = event.get("team", "")

        # 根据事件发生的球队来判断是否翻译
        team_name = home_team_name if team == "home" else away_team_name

        # 翻译球员名称
        translated_player = translate_player_name(player, team_name=team_name)
        translated_player2 = translate_player_name(player2, team_name=team_name)

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

def process_player_stats(stats: List[Dict], team_name: str = "") -> List[Dict]:
    """处理球员统计"""
    processed_stats = []
    for stat in stats:
        player = stat.get("player", "")
        translated_player = translate_player_name(player, team_name=team_name)

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

        # 处理match_info
        match_info = data.get("match_info", {})
        competition = match_info.get("competition", {})
        venue = match_info.get("venue", {})

        # 翻译赛事名称
        competition_name = competition.get("name", "")
        if "Chinese" in competition_name or "Super League" in competition_name:
            competition["name"] = "中国足球协会超级联赛"

        # 翻译轮次
        round_name = competition.get("round", "")
        if "Matchweek" in round_name:
            round_num = round_name.replace("Matchweek", "").strip()
            competition["round"] = f"第{round_num}轮"

        # 翻译场地名称
        venue_name = venue.get("name", "")
        if venue_name and not re.search(r'[\u4e00-\u9fff]', venue_name):
            translated = translate_venue_name(venue_name)
            if translated != venue_name:
                venue["name"] = translated

        # 处理球队信息
        teams = data.get("teams", {})
        home_team = teams.get("home", {})
        away_team = teams.get("away", {})

        # 保存原始球队名称用于事件处理
        home_team_name = home_team.get("name", "")
        away_team_name = away_team.get("name", "")

        teams["home"] = process_team(home_team, is_home=True)
        teams["away"] = process_team(away_team, is_home=False)

        # 处理事件（传入主客队名称以判断是否是上海海港）
        events = data.get("events", [])
        data["events"] = process_events(events, home_team_name, away_team_name)

        # 处理球员统计
        if "player_stats" in data:
            player_stats = data.get("player_stats", {})
            if "home" in player_stats:
                player_stats["home"] = process_player_stats(player_stats.get("home", []), home_team_name)
            if "away" in player_stats:
                player_stats["away"] = process_player_stats(player_stats.get("away", []), away_team_name)

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
    print("2022赛季赛事报告优化脚本（只汉化上海海港球员和教练）")
    print("=" * 60)
    print()

    # 查找2022赛季的JSON文件
    json_dir = Path("public/data/history/2022")
    if not json_dir.exists():
        print(f"错误: 目录不存在 {json_dir}")
        return

    json_files = sorted(json_dir.glob("*.json"))

    if not json_files:
        print(f"未找到2022赛季的JSON文件")
        return

    print(f"找到 {len(json_files)} 个2022赛季比赛文件")
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
