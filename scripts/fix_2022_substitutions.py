import json
from pathlib import Path

def fix_substitutions_for_file(file_path: Path) -> bool:
    """处理单个文件的换人信息：
    1. 从events的substitution事件中提取上场球员，更新teams中substitutions的player_in字段
    2. 从teams的substitutions中提取下场球员，更新events中substitution事件的player2字段
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        events = data.get("events", [])
        teams = data.get("teams", {})

        modified_count = 0

        # 1. 从events中提取上场球员信息
        player_in_map = {
            "home": {},
            "away": {}
        }

        for event in events:
            if event.get("type") == "substitution":
                team = event.get("team", "")
                minute = event.get("minute", 0)
                minute_extra = event.get("minute_extra", 0)
                player_in = event.get("player", "")

                if team in player_in_map and player_in:
                    key = (minute, minute_extra)
                    if key not in player_in_map[team]:
                        player_in_map[team][key] = []
                    player_in_map[team][key].append(player_in)

        # 2. 更新teams中home和away的substitutions的player_in字段
        for team_type in ["home", "away"]:
            team = teams.get(team_type, {})
            substitutions = team.get("substitutions", [])

            used_indices = {}
            for sub in substitutions:
                minute = sub.get("minute", 0)
                minute_extra = sub.get("minute_extra", 0)
                key = (minute, minute_extra)

                if key in player_in_map.get(team_type, {}):
                    player_ins = player_in_map[team_type][key]

                    if key not in used_indices:
                        used_indices[key] = 0

                    if used_indices[key] < len(player_ins):
                        player_in = player_ins[used_indices[key]]
                        used_indices[key] += 1

                        if player_in and not sub.get("player_in"):
                            sub["player_in"] = player_in
                            modified_count += 1

        # 3. 从teams的substitutions中提取下场球员信息
        player_out_map = {
            "home": {},
            "away": {}
        }

        for team_type in ["home", "away"]:
            team = teams.get(team_type, {})
            substitutions = team.get("substitutions", [])

            for sub in substitutions:
                minute = sub.get("minute", 0)
                minute_extra = sub.get("minute_extra", 0)
                player_out = sub.get("player_out", "")

                if player_out:
                    key = (minute, minute_extra)
                    if key not in player_out_map[team_type]:
                        player_out_map[team_type][key] = []
                    player_out_map[team_type][key].append(player_out)

        # 4. 更新events中substitution事件的player2字段
        for event in events:
            if event.get("type") == "substitution":
                team = event.get("team", "")
                minute = event.get("minute", 0)
                minute_extra = event.get("minute_extra", 0)
                key = (minute, minute_extra)

                if team in player_out_map and key in player_out_map[team]:
                    player_outs = player_out_map[team][key]

                    if player_outs:
                        player_out = player_outs.pop(0)
                        if player_out and not event.get("player2"):
                            event["player2"] = player_out
                            modified_count += 1

        # 保存修改后的文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✅ {file_path.name}: 更新 {modified_count} 处换人信息")
        return True

    except Exception as e:
        print(f"❌ 错误处理 {file_path.name}: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("2022赛季换人信息批量更新脚本")
    print("=" * 60)

    history_dir = Path("public/data/history/2022")
    json_files = sorted(history_dir.glob("*.json"))

    print(f"\n找到 {len(json_files)} 个文件")

    success_count = 0
    fail_count = 0

    for json_file in json_files:
        if fix_substitutions_for_file(json_file):
            success_count += 1
        else:
            fail_count += 1

    print("\n" + "=" * 60)
    print(f"处理完成")
    print(f"成功: {success_count} 个文件")
    print(f"失败: {fail_count} 个文件")
    print("=" * 60)

if __name__ == "__main__":
    main()
