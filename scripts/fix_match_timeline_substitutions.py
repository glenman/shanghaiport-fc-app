import json
from pathlib import Path

def fix_match_timeline_substitutions(file_path: Path) -> bool:
    """将lineups中的substitutes换人信息补充到matchTimeline中"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        lineups = data.get("lineups", {})
        match_timeline = data.get("matchTimeline", [])

        # 收集已存在的substitution记录
        existing_subs = set()
        for event in match_timeline:
            if event.get("type") == "substitution":
                team = event.get("team", "")
                minute = event.get("minute", 0)
                player_in = event.get("playerIn", "")
                player_out = event.get("playerOut", "")
                existing_subs.add((team, minute, player_in, player_out))

        print(f"已存在的换人记录: {len(existing_subs)} 条")
        for sub in existing_subs:
            print(f"  - {sub}")

        # 从lineups中提取substitutes信息
        new_subs_to_add = []

        for team_key in ["home", "away"]:
            team_data = lineups.get(team_key, {})
            substitutes = team_data.get("substitutes", [])

            for sub in substitutes:
                if "substitutedAt" in sub and "substitutedFor" in sub:
                    minute = sub["substitutedAt"]
                    player_out = sub["substitutedFor"]
                    player_in = sub["name"]

                    # 检查是否已存在
                    if (team_key, minute, player_in, player_out) not in existing_subs:
                        new_sub = {
                            "minute": minute,
                            "minute_extra": 0,
                            "type": "substitution",
                            "team": team_key,
                            "playerIn": player_in,
                            "playerOut": player_out,
                            "description": f"{'青岛海牛' if team_key == 'home' else '上海海港'}{player_in}替换{player_out}上场"
                        }
                        new_subs_to_add.append(new_sub)
                        print(f"将添加新换人: {team_key}, {minute}', {player_in} -> {player_out}")

        # 将新的substitution记录按时间顺序插入matchTimeline
        if new_subs_to_add:
            # 找到最后一个非substitution事件的位置
            insert_index = len(match_timeline)
            for i, event in enumerate(match_timeline):
                if event.get("type") == "substitution":
                    insert_index = i
                    break

            # 在第一个substitution之前插入新的substitution
            for new_sub in sorted(new_subs_to_add, key=lambda x: (x["minute"], x["team"])):
                match_timeline.insert(insert_index, new_sub)
                print(f"已添加: {new_sub['minute']}' {new_sub['playerIn']} <- {new_sub['playerOut']}")

        # 保存更新后的文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 更新完成！共添加 {len(new_subs_to_add)} 条换人记录")
        return True

    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return False

def main():
    file_path = Path("public/data/2026-05-02-中超-第9轮.json")
    print("=" * 60)
    print("补充matchTimeline中的换人信息")
    print("=" * 60)
    fix_match_timeline_substitutions(file_path)

if __name__ == "__main__":
    main()
