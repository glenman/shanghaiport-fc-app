import json
from pathlib import Path

# 英文队名到中文队名的映射
EN_TO_CN_TEAM_MAP = {
    "Shanghai Port": "上海海港",
    "Shanghai Shenhua": "上海海港",
    "Beijing Guoan": "北京国安",
    "Shandong Taishan": "山东泰山",
    "Tianjin Jinmen Tiger": "天津津门虎",
    "Changchun Yatai": "长春亚泰",
    "Dalian Pro": "大连人",
    "Wuhan": "武汉",
    "Wuhan Three Towns": "武汉三镇",
    "Hebei": "河北",
    "Hebei China Fortune": "河北",
    "Shenzhen": "深圳",
    "Shenzhen Pengcheng": "深圳",
    "Guangzhou City": "广州城",
    "Guangzhou": "广州",
    "Guangzhou Evergrande": "广州",
}

def convert_to_chinese_names(json_dir: Path):
    """将所有文件的主客队名称改为中文"""
    print("=" * 60)
    print("2021赛季球队名称中文化")
    print("=" * 60)
    print()

    json_files = sorted(json_dir.glob("*.json"))
    success_count = 0

    for file in json_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            modified = False

            # 处理home队
            if 'teams' in data and 'home' in data['teams']:
                home_name = data['teams']['home'].get('name', '')
                if home_name in EN_TO_CN_TEAM_MAP:
                    data['teams']['home']['name'] = EN_TO_CN_TEAM_MAP[home_name]
                    data['teams']['home']['full_name'] = EN_TO_CN_TEAM_MAP[home_name]
                    modified = True

            # 处理away队
            if 'teams' in data and 'away' in data['teams']:
                away_name = data['teams']['away'].get('name', '')
                if away_name in EN_TO_CN_TEAM_MAP:
                    data['teams']['away']['name'] = EN_TO_CN_TEAM_MAP[away_name]
                    data['teams']['away']['full_name'] = EN_TO_CN_TEAM_MAP[away_name]
                    modified = True

            if modified:
                with open(file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                success_count += 1
                print(f"✅ {file.name}")

        except Exception as e:
            print(f"❌ 错误处理 {file.name}: {str(e)}")

    print()
    print("=" * 60)
    print(f"完成：成功修改 {success_count} 个文件")
    print("=" * 60)

def verify_conversion(json_dir: Path):
    """验证转换结果"""
    print("\n验证转换结果（前5个文件）：")
    json_files = sorted(json_dir.glob("*.json"))[:5]

    for file in json_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        home_name = data.get('teams', {}).get('home', {}).get('name', 'N/A')
        away_name = data.get('teams', {}).get('away', {}).get('name', 'N/A')
        print(f"  {file.name}: home={home_name}, away={away_name}")

def main():
    json_dir = Path("public/data/history/2021")
    convert_to_chinese_names(json_dir)
    verify_conversion(json_dir)

if __name__ == "__main__":
    main()
