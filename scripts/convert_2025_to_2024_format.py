# -*- coding: utf-8 -*-
import json
import os
import glob

def convert_2025_to_2024_format(data):
    """
    将 2025 年格式的 JSON 数据转换为 2024 年格式
    """
    old_match = data.get("match", {})
    old_lineups = data.get("lineups", {})
    old_home = old_lineups.get("home", {})
    old_away = old_lineups.get("away", {})
    
    result_str = old_match.get("result", "0-0")
    scores = result_str.split("-")
    home_score = int(scores[0].strip()) if len(scores) > 0 else 0
    away_score = int(scores[1].strip()) if len(scores) > 1 else 0
    
    def convert_players(players):
        lineup = []
        substitutes = []
        for i, p in enumerate(players):
            player = {
                "position": p.get("position", ""),
                "number": int(p.get("number", 0)),
                "name": p.get("name", ""),
                "country": p.get("nationality", "中国")
            }
            if i < 11:
                lineup.append(player)
            else:
                substitutes.append(player)
        return lineup, substitutes
    
    home_lineup, home_subs = convert_players(old_home.get("players", []))
    away_lineup, away_subs = convert_players(old_away.get("players", []))
    
    new_data = {
        "match_info": {
            "match_id": str(old_match.get("id", "")),
            "date": old_match.get("date", ""),
            "time": old_match.get("time", ""),
            "competition": {
                "name": "中国足球协会超级联赛",
                "season": "2025",
                "round": old_match.get("round", "")
            },
            "venue": {
                "name": old_match.get("venue", "未知"),
                "city": old_match.get("city", "上海"),
                "attendance": 0 if old_match.get("attendance", "未知") == "未知" else int(old_match.get("attendance", 0))
            },
            "referee": {
                "name": old_match.get("referee", "待补充"),
                "country": "China"
            }
        },
        "teams": {
            "home": {
                "name": old_home.get("name", ""),
                "full_name": old_home.get("name", "") + "足球俱乐部" if not old_home.get("name", "").endswith("俱乐部") else old_home.get("name", ""),
                "score": home_score,
                "score_ht": 0,
                "formation": old_home.get("formation", ""),
                "coach": old_home.get("manager", "待补充"),
                "captain": old_home.get("captain", "待补充"),
                "lineup": home_lineup,
                "substitutes": home_subs,
                "substitutions": []
            },
            "away": {
                "name": old_away.get("name", ""),
                "full_name": old_away.get("name", "") + "足球俱乐部" if not old_away.get("name", "").endswith("俱乐部") else old_away.get("name", ""),
                "score": away_score,
                "score_ht": 0,
                "formation": old_away.get("formation", ""),
                "coach": old_away.get("manager", "待补充"),
                "captain": old_away.get("captain", "待补充"),
                "lineup": away_lineup,
                "substitutes": away_subs,
                "substitutions": []
            }
        },
        "events": [],
        "statistics": {
            "possession": {"home": 50, "away": 50},
            "shots_on_target": {"home": 0, "away": 0},
            "saves": {"home": 0, "away": 0},
            "fouls": {"home": 0, "away": 0},
            "corners": {"home": 0, "away": 0},
            "crosses": {"home": 0, "away": 0},
            "interceptions": {"home": 0, "away": 0},
            "offsides": {"home": 0, "away": 0},
            "shots": {"home": 0, "away": 0},
            "yellow_cards": {"home": 0, "away": 0},
            "red_cards": {"home": 0, "away": 0}
        },
        "player_stats": {
            "home": [],
            "away": []
        },
        "metadata": {
            "source": "Converted from 2025 format",
            "url": "",
            "scraped_at": "",
            "version": "3.0"
        }
    }
    
    return new_data

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_dir = os.path.join(base_dir, "public", "data", "history", "2025")
    
    json_files = glob.glob(os.path.join(json_dir, "*.json"))
    
    print(f"找到 {len(json_files)} 个 JSON 文件")
    
    for json_file in json_files:
        print(f"处理: {os.path.basename(json_file)}")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        new_data = convert_2025_to_2024_format(data)
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, ensure_ascii=False, indent=2)
        
        print(f"  完成: {os.path.basename(json_file)}")
    
    print("\n所有文件转换完成!")

if __name__ == "__main__":
    main()
