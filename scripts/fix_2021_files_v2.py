import json
import os
import re
from pathlib import Path

# 2021赛季比赛数据
MATCH_DATA = [
    {"round": 1, "date": "2021-04-22", "home": "天津津门虎", "away": "上海海港", "home_score": 1, "away_score": 6},
    {"round": 2, "date": "2021-04-28", "home": "上海海港", "away": "北京国安", "home_score": 3, "away_score": 1},
    {"round": 3, "date": "2021-05-05", "home": "上海申花", "away": "上海海港", "home_score": 1, "away_score": 1},
    {"round": 4, "date": "2021-05-11", "home": "上海海港", "away": "长春亚泰", "home_score": 0, "away_score": 0},
    {"round": 5, "date": "2021-05-16", "home": "上海海港", "away": "大连人", "home_score": 3, "away_score": 0},
    {"round": 6, "date": "2021-07-19", "home": "武汉", "away": "上海海港", "home_score": 0, "away_score": 0},
    {"round": 7, "date": "2021-07-23", "home": "上海海港", "away": "河北", "home_score": 1, "away_score": 0},
    {"round": 9, "date": "2021-07-28", "home": "北京国安", "away": "上海海港", "home_score": 1, "away_score": 1},
    {"round": 10, "date": "2021-07-31", "home": "上海海港", "away": "上海申花", "home_score": 1, "away_score": 0},
    {"round": 11, "date": "2021-08-03", "home": "长春亚泰", "away": "上海海港", "home_score": 2, "away_score": 1},
    {"round": 12, "date": "2021-08-06", "home": "大连人", "away": "上海海港", "home_score": 0, "away_score": 5},
    {"round": 13, "date": "2021-08-09", "home": "上海海港", "away": "武汉", "home_score": 3, "away_score": 0},
    {"round": 14, "date": "2021-08-12", "home": "河北", "away": "上海海港", "home_score": 1, "away_score": 0},
    {"round": 8, "date": "2021-08-15", "home": "上海海港", "away": "天津津门虎", "home_score": 5, "away_score": 0},
    {"round": 15, "date": "2021-12-13", "home": "深圳", "away": "上海海港", "home_score": 1, "away_score": 3},
    {"round": 16, "date": "2021-12-16", "home": "上海海港", "away": "广州城", "home_score": 1, "away_score": 0},
    {"round": 17, "date": "2021-12-19", "home": "上海海港", "away": "山东泰山", "home_score": 0, "away_score": 2},
    {"round": 18, "date": "2021-12-22", "home": "广州", "away": "上海海港", "home_score": 0, "away_score": 0},
    {"round": 19, "date": "2021-12-26", "home": "上海海港", "away": "深圳", "home_score": 3, "away_score": 1},
    {"round": 20, "date": "2021-12-29", "home": "广州城", "away": "上海海港", "home_score": 1, "away_score": 2},
    {"round": 21, "date": "2022-01-01", "home": "山东泰山", "away": "上海海港", "home_score": 2, "away_score": 2},
    {"round": 22, "date": "2022-01-04", "home": "上海海港", "away": "广州", "home_score": 1, "away_score": 0},
]

# 中文队名到英文队名的映射（用于JSON中的name字段）
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
    """修复单个JSON文件"""
    date = match_info["date"]
    round_num = match_info["round"]
    home_cn = match_info["home"]
    away_cn = match_info["away"]
    home_score = match_info["home_score"]
    away_score = match_info["away_score"]
    
    # 查找当前目录中匹配该日期的文件
    pattern = f"{date}-*.json"
    files = list(json_dir.glob(pattern))
    
    if not files:
        print(f"⚠️ 未找到日期为 {date} 的文件")
        return False
    
    old_path = files[0]
    old_name = old_path.name
    
    # 构建新文件名
    new_name = f"{date}-中超-第{round_num}轮.json"
    new_path = json_dir / new_name
    
    try:
        # 读取文件
        with open(old_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 更新轮次
        if 'match_info' in data and 'competition' in data['match_info']:
            data['match_info']['competition']['round'] = f"Matchweek {round_num}"
        
        # 更新球队信息
        if 'teams' in data:
            if 'home' in data['teams']:
                data['teams']['home']['name'] = CN_TO_EN_TEAM_MAP.get(home_cn, home_cn)
                data['teams']['home']['score'] = home_score
            
            if 'away' in data['teams']:
                data['teams']['away']['name'] = CN_TO_EN_TEAM_MAP.get(away_cn, away_cn)
                data['teams']['away']['score'] = away_score
        
        # 写回文件
        with open(old_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 重命名文件（如果需要）
        if old_name != new_name:
            os.rename(old_path, new_path)
            print(f"✅ {old_name} -> {new_name}")
        else:
            print(f"✅ {old_name} 内容已更新")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误处理 {old_name}: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("2021赛季文件修复脚本")
    print("=" * 60)
    print()
    
    json_dir = Path("public/data/history/2021")
    if not json_dir.exists():
        print(f"错误: 目录不存在 {json_dir}")
        return
    
    success_count = 0
    
    for match_info in MATCH_DATA:
        if fix_json_file(json_dir, match_info):
            success_count += 1
    
    print()
    print("=" * 60)
    print("修复完成")
    print("=" * 60)
    print(f"成功修复: {success_count} 个文件")
    print(f"总计: {len(MATCH_DATA)} 个比赛")

if __name__ == "__main__":
    main()
