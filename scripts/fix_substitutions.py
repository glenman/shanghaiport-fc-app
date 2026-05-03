import json
from pathlib import Path

def fix_substitution_events(file_path: Path) -> bool:
    """修复换人事件，将下场球员信息放到player2字段"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 删除之前错误添加的player_out字段
        events = data.get("events", [])
        for event in events:
            if event.get("type") == "substitution" and "player_out" in event:
                del event["player_out"]

        # 获取home和away的换人信息
        teams = data.get("teams", {})
        home_substitutions = teams.get("home", {}).get("substitutions", [])
        away_substitutions = teams.get("away", {}).get("substitutions", [])

        # 创建换人信息字典，按时间和球队分组，使用列表存储多个换人
        substitution_map = {
            "home": {},
            "away": {}
        }

        for sub in home_substitutions:
            minute = sub.get("minute", 0)
            minute_extra = sub.get("minute_extra", 0)
            key = (minute, minute_extra)
            if key not in substitution_map["home"]:
                substitution_map["home"][key] = []
            substitution_map["home"][key].append(sub.get("player_out", ""))

        for sub in away_substitutions:
            minute = sub.get("minute", 0)
            minute_extra = sub.get("minute_extra", 0)
            key = (minute, minute_extra)
            if key not in substitution_map["away"]:
                substitution_map["away"][key] = []
            substitution_map["away"][key].append(sub.get("player_out", ""))

        # 更新events中的substitution事件，将下场球员放到player2字段
        modified_count = 0

        used_indices = {
            "home": {},
            "away": {}
        }

        for event in events:
            if event.get("type") == "substitution":
                team = event.get("team", "")
                minute = event.get("minute", 0)
                minute_extra = event.get("minute_extra", 0)

                if team in substitution_map:
                    key = (minute, minute_extra)
                    if key in substitution_map[team]:
                        player_outs = substitution_map[team][key]
                        
                        if key not in used_indices[team]:
                            used_indices[team][key] = 0
                        
                        if used_indices[team][key] < len(player_outs):
                            player_out = player_outs[used_indices[team][key]]
                            used_indices[team][key] += 1
                            
                            if player_out and not event.get("player2"):
                                event["player2"] = player_out
                                modified_count += 1
                                print(f"  补充换人: team={team}, minute={minute}, player(上场)={event.get('player')}, player2(下场)={player_out}")

        # 保存修改后的文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"\n✅ {file_path.name}: 成功补充 {modified_count} 条换人信息")
        return True

    except Exception as e:
        print(f"❌ 错误处理 {file_path.name}: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("2021赛季第1轮换人信息补充（使用player2字段）")
    print("=" * 60)

    file_path = Path("public/data/history/2021/2021-04-22-中超-第1轮.json")
    fix_substitution_events(file_path)

if __name__ == "__main__":
    main()
