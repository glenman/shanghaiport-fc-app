import json
import os
from pathlib import Path

# 需要特别处理的第7轮
MATCH_DATA = [
    {"date": "2021-07-22", "round": 7, "home": "上海海港", "away": "河北", "home_score": 1, "away_score": 0},
]

CN_TO_EN_TEAM_MAP = {
    "上海海港": "Shanghai Port",
    "上海申花": "Shanghai Shenhua",
    "北京国安": "Beijing Guoan",
    "山东泰山": "Shandong Taishan",
    "天津津门虎": "Tianjin Jinmen Tiger",
    "长春亚泰": "Changchun Yatai",
    "大连人": "Dalian Pro",
    "武汉": "Wuhan",
    "河北": "Hebei",
    "深圳": "Shenzhen",
    "广州城": "Guangzhou City",
    "广州": "Guangzhou",
}

def fix_json_file(json_dir: Path, match_info: dict):
    date = match_info["date"]
    round_num = match_info["round"]
    home_cn = match_info["home"]
    away_cn = match_info["away"]
    
    pattern = f"{date}-*.json"
    files = list(json_dir.glob(pattern))
    
    if not files:
        print(f"⚠️ 未找到日期为 {date} 的文件")
        return False
    
    old_path = files[0]
    old_name = old_path.name
    
    try:
        with open(old_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'match_info' in data and 'competition' in data['match_info']:
            data['match_info']['competition']['round'] = f"Matchweek {round_num}"
        
        if 'teams' in data:
            if 'home' in data['teams']:
                data['teams']['home']['name'] = CN_TO_EN_TEAM_MAP.get(home_cn, home_cn)
            
            if 'away' in data['teams']:
                data['teams']['away']['name'] = CN_TO_EN_TEAM_MAP.get(away_cn, away_cn)
        
        with open(old_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ {old_name} 已修复")
        return True
        
    except Exception as e:
        print(f"❌ 错误处理 {old_name}: {str(e)}")
        return False

def verify_all_files(json_dir: Path):
    print("\n验证所有文件:")
    json_files = sorted(json_dir.glob("*.json"))
    
    for file in json_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        round_info = data.get('match_info', {}).get('competition', {}).get('round', 'N/A')
        home_name = data.get('teams', {}).get('home', {}).get('name', 'N/A')
        away_name = data.get('teams', {}).get('away', {}).get('name', 'N/A')
        
        status = "✓" if away_name != "Opponent" else "⚠️"
        print(f"{status} {file.name}: round={round_info}, home={home_name}, away={away_name}")

def main():
    print("=" * 60)
    print("2021赛季第7轮修复")
    print("=" * 60)
    
    json_dir = Path("public/data/history/2021")
    
    for match_info in MATCH_DATA:
        fix_json_file(json_dir, match_info)
    
    verify_all_files(json_dir)

if __name__ == "__main__":
    main()
