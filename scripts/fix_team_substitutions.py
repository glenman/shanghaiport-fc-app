import json
from pathlib import Path

def fix_team_substitutions(file_path: Path) -> bool:
    """更新球队名单中substitutions的player_in字段"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 从events中提取换人信息（上场球员）
        events = data.get("events", [])
        
        # 创建上场球员字典，按时间和球队分组，使用列表存储
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

        # 更新teams中home和away的substitutions的player_in字段
        teams = data.get("teams", {})
        modified_count = 0

        for team_type in ["home", "away"]:
            team = teams.get(team_type, {})
            substitutions = team.get("substitutions", [])
            
            # 维护一个索引来按顺序分配上场球员
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
                            print(f"  更新换人: team={team_type}, minute={minute}, player_out={sub.get('player_out')}, player_in={player_in}")

        # 保存修改后的文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"\n✅ {file_path.name}: 成功更新 {modified_count} 条换人信息")
        return True

    except Exception as e:
        print(f"❌ 错误处理 {file_path.name}: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("2021赛季第1轮换人信息更新（补充player_in字段）")
    print("=" * 60)

    file_path = Path("public/data/history/2021/2021-04-22-中超-第1轮.json")
    fix_team_substitutions(file_path)

if __name__ == "__main__":
    main()
