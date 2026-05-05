import json
from pathlib import Path

JSON_DIR = r"public\data\history\2019"
NEW_LEAGUE_NAME = "中国足球协会超级联赛"
NEW_HOME_VENUE = "上海体育场"
NEW_COACH = "维克多 佩雷拉"
NEW_CAPTAIN = "奥斯卡"

def update_json_files():
    """更新所有2019年的JSON文件"""
    json_dir = Path(JSON_DIR)
    json_files = sorted(list(json_dir.glob('*.json')))

    updated_count = 0
    for json_path in json_files:
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 1. 更新联赛名称
            if 'match_info' in data and 'competition' in data['match_info'] and 'name' in data['match_info']['competition']:
                data['match_info']['competition']['name'] = NEW_LEAGUE_NAME

            # 2. 更新上海上港主场地点
            if 'match_info' in data and 'venue' in data['match_info'] and 'name' in data['match_info']['venue']:
                # 检查是否是上海上港主场比赛
                is_home = False
                if 'teams' in data:
                    for team in ['home', 'away']:
                        if team in data['teams']:
                            team_name = data['teams'][team].get('name', '')
                            if '上海上港' in team_name and team == 'home':
                                is_home = True
                                break
                if is_home:
                    data['match_info']['venue']['name'] = NEW_HOME_VENUE

            # 3. 更新上海上港的主教练和队长
            if 'teams' in data:
                for team in ['home', 'away']:
                    if team in data['teams']:
                        team_name = data['teams'][team].get('name', '')
                        if '上海上港' in team_name:
                            # 更新主教练
                            if 'coach' in data['teams'][team]:
                                data['teams'][team]['coach'] = NEW_COACH
                            # 更新队长
                            if 'captain' in data['teams'][team]:
                                data['teams'][team]['captain'] = NEW_CAPTAIN

            # 保存文件
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            updated_count += 1
            print(f"✅ {json_path.name}")

        except Exception as e:
            print(f"❌ 处理失败 {json_path.name}: {e}")

    return updated_count

def main():
    print("=" * 60)
    print("2019赛季 信息更新")
    print("=" * 60)
    print(f"\n📋 更新内容:")
    print(f"  1. 联赛名称: {NEW_LEAGUE_NAME}")
    print(f"  2. 上海上港主场: {NEW_HOME_VENUE}")
    print(f"  3. 上海上港主教练: {NEW_COACH}")
    print(f"  4. 上海上港队长: {NEW_CAPTAIN}")
    print("\n📝 更新JSON文件...")

    updated = update_json_files()

    print("\n" + "=" * 60)
    print(f"✅ 更新完成! 共更新 {updated} 个文件")
    print("=" * 60)

if __name__ == "__main__":
    main()
