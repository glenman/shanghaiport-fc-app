import json
import os
import re
import csv
from pathlib import Path

# 球队名称翻译表
TEAM_NAME_TRANSLATIONS = {
    "Shanghai SIPG": "上海上港",
    "Shanghai Shenhua": "上海绿地",
    "Shanghai Greenland": "上海绿地",
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
    "Shenzhen": "深圳队",
    "Meizhou Hakka": "梅州客家",
    "Nantong Zhejiang": "南通支云",
    "Qingdao West Coast": "青岛西海岸",
    "Sichuan Jiuniu": "四川九牛",
    "Chongqing Liangjiang": "重庆两江",
}

# 场地名称翻译
VENUE_TRANSLATIONS = {
    "Shanghai Stadium": "上海体育场",
    "Hongkou Football Stadium": "虹口足球场",
    "Jinshan Sports Center": "金山体育中心",
    "Pudong Football Stadium": "浦东足球场",
    "SAIC Motor Pudong Arena": "上汽浦东足球场",
}

def load_roster_from_csv(csv_path):
    """从CSV文件读取球员名单"""
    roster = {}
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name_cn = row.get('中文名称', '').strip()
                name_en = row.get('英文名称', '').strip()
                if name_cn and name_en:
                    roster[name_en] = name_cn
        return roster
    except Exception as e:
        print(f"读取球员名单失败: {str(e)}")
        return {}

def translate_team_name(name):
    """翻译球队名称"""
    return TEAM_NAME_TRANSLATIONS.get(name, name)

def translate_venue_name(name):
    """翻译场地名称"""
    return VENUE_TRANSLATIONS.get(name, name)

def normalize_pinyin(pinyin):
    """标准化拼音"""
    if not pinyin:
        return ""
    pinyin = pinyin.lower().strip()
    pinyin = pinyin.replace("-", " ").replace("'", " ").replace("·", " ").replace("ü", "u")
    pinyin = re.sub(r'\s+', ' ', pinyin)
    return pinyin

def find_player_name(player_name, roster):
    """根据球员数据尝试找到对应的中文名"""
    if not player_name:
        return None

    normalized_name = normalize_pinyin(player_name)
    if normalized_name in roster:
        return roster[normalized_name]

    for name_en, name_cn in roster.items():
        normalized_en = normalize_pinyin(name_en)
        if normalized_name and normalized_en:
            if normalized_name in normalized_en or normalized_en in normalized_name:
                return name_cn
            name_parts = normalized_name.split()
            en_parts = normalized_en.split()
            if any(part in en_parts for part in name_parts if len(part) > 2):
                return name_cn

    return player_name

def is_shanghai_sipg_team(team_name, formation_name):
    """检查是否是上海上港的球队"""
    sipg_names = ["Shanghai SIPG", "Shanghai Port", "上海上港", "上海海港"]
    if team_name in sipg_names:
        return True
    if formation_name and any(name in formation_name for name in sipg_names):
        return True
    return False

def optimize_file(json_path, roster):
    """优化单个JSON文件"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        modified = False

        if "match_info" in data:
            match_info = data["match_info"]

            if "competition" in match_info:
                comp = match_info["competition"]
                if comp.get("name") == "Chinese Football Association Super League":
                    comp["name"] = "中国足球协会超级联赛"
                    modified = True

                if "round" in comp:
                    round_val = comp["round"]
                    match = re.match(r'Matchweek\s*(\d+)', round_val)
                    if match:
                        round_num = match.group(1)
                        comp["round"] = f"第{round_num}轮"
                        modified = True

            if "venue" in match_info:
                venue = match_info["venue"]
                if "name" in venue:
                    venue["name"] = translate_venue_name(venue["name"])
                    modified = True

        if "teams" in data:
            teams = data["teams"]

            for team_side in ["home", "away"]:
                if team_side not in teams:
                    continue

                team = teams[team_side]
                formation = team.get("formation", "")

                team_name = team.get("name", "")
                is_sipg = is_shanghai_sipg_team(team_name, formation)

                translated_name = translate_team_name(team_name)
                if translated_name != team_name:
                    team["name"] = translated_name
                    team["full_name"] = translated_name
                    modified = True

                if formation and "(" in formation:
                    new_formation = re.sub(r'^[^(]+', '', formation).strip()
                    if new_formation != formation:
                        team["formation"] = new_formation
                        modified = True

                if is_sipg:
                    if "lineup" in team:
                        for player in team["lineup"]:
                            original_name = player.get("name", "")
                            chinese_name = find_player_name(original_name, roster)
                            if chinese_name and chinese_name != original_name:
                                player["name"] = chinese_name
                                modified = True
                            if player.get("country") == "Unknown":
                                player["country"] = "中国"

                    if "substitutes" in team:
                        for player in team["substitutes"]:
                            original_name = player.get("name", "")
                            chinese_name = find_player_name(original_name, roster)
                            if chinese_name and chinese_name != original_name:
                                player["name"] = chinese_name
                                modified = True
                            if player.get("country") == "Unknown":
                                player["country"] = "中国"

        if "events" in data:
            for event in data["events"]:
                team = event.get("team", "")
                if team in ["home", "away"] and "teams" in data:
                    team_name = data["teams"].get(team, {}).get("name", "")
                    if is_shanghai_sipg_team(team_name, ""):
                        if "player" in event:
                            player_name = event["player"]
                            chinese_name = find_player_name(player_name, roster)
                            if chinese_name and chinese_name != player_name:
                                event["player"] = chinese_name
                                modified = True
                        if "player2" in event and event["player2"]:
                            player2_name = event["player2"]
                            chinese_name = find_player_name(player2_name, roster)
                            if chinese_name and chinese_name != player2_name:
                                event["player2"] = chinese_name
                                modified = True

        if modified:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        return modified

    except Exception as e:
        print(f"  错误: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("2019赛季赛事报告优化脚本")
    print("=" * 60)

    csv_path = Path("datafile/上海海港2019一线队大名单.csv")
    roster = load_roster_from_csv(csv_path)
    print(f"\n加载了 {len(roster)} 名2019赛季球员\n")

    dir_path = Path("public/data/history/2019")
    if not dir_path.exists():
        print(f"目录不存在: {dir_path}")
        return

    json_files = list(dir_path.glob("*.json"))
    print(f"找到 {len(json_files)} 个2019赛季比赛文件\n")

    success_count = 0
    modified_count = 0

    for json_file in sorted(json_files):
        print(f"处理: {json_file.name}")
        modified = optimize_file(json_file, roster)
        if modified:
            print(f"  ✓ 已优化")
            modified_count += 1
        else:
            print(f"  - 无需修改")
        success_count += 1

    print("\n" + "=" * 60)
    print(f"优化完成")
    print("=" * 60)
    print(f"成功: {success_count} 个文件")
    print(f"已修改: {modified_count} 个文件")

if __name__ == "__main__":
    main()
