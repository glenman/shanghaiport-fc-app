import json
import os
import re
from pathlib import Path

# 球队名称翻译字典
TEAM_NAME_TRANSLATIONS = {
    "Shanghai Port": "上海海港",
    "Shanghai Shen": "上海申花",
    "Beijing Guoan": "北京国安",
    "Shandong Taishan": "山东泰山",
    "Zhejiang Professional": "浙江队",
    "Chengdu Rongcheng": "成都蓉城",
    "Shanghai Port FC": "上海海港",
    "Wuhan Three Towns": "武汉三镇",
    "Tianjin Jinmen Tiger": "天津津门虎",
    "Henan": "河南队",
    "Dalian Pro": "大连人",
    "Changchun Yatai": "长春亚泰",
    "Qingdao Hainiu": "青岛海牛",
    "Cangzhou Mighty Lions": "沧州雄狮",
    "Shenzhen Pengcheng": "深圳新鹏城",
    "Meizhou Hakka": "梅州客家",
    "Nantong Zhejiang": "南通支云",
    "Qingdao West Coast": "青岛西海岸",
    "Sichuan Jiuniu": "四川九牛",
    "Chongqing Liangjiang": "重庆两江",
    "Guangzhou Evergrande": "广州队",
    "Hebei China Fortune": "河北队",
    "Chongqing Lifan": "重庆当代",
    "Beijing Renhe": "北京人和",
    "Dalian Yifang": "大连一方",
    "Tianjin Tianhai": "天津天海",
    "Shenzhen": "深圳队",
}

def extract_team_name_from_formation(formation: str) -> str:
    """从formation中提取球队名称"""
    if not formation:
        return ""
    # 匹配 "Team Name (3-4-3)" 格式，提取 "Team Name"
    match = re.match(r'^(.+?)\s*\(\d', formation)
    if match:
        team_name = match.group(1).strip()
        return team_name
    return ""

def clean_formation(formation: str) -> str:
    """清理formation，去掉球队名称，只保留阵型"""
    if not formation:
        return ""
    # 匹配 "(3-4-3)" 格式的阵型
    match = re.search(r'(\(\d.*?\))', formation)
    if match:
        return match.group(1)
    return formation

def translate_team_name(team_name: str) -> str:
    """翻译球队名称"""
    if not team_name:
        return team_name
    # 直接匹配
    if team_name in TEAM_NAME_TRANSLATIONS:
        return TEAM_NAME_TRANSLATIONS[team_name]
    # 模糊匹配
    for eng_name, cn_name in TEAM_NAME_TRANSLATIONS.items():
        if eng_name.lower() in team_name.lower() or team_name.lower() in eng_name.lower():
            return cn_name
    return team_name

def fix_json_file(file_path: Path) -> bool:
    """修复单个JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        modified = False
        teams = data.get("teams", {})
        
        # 处理home队
        home_team = teams.get("home", {})
        home_name = home_team.get("name", "")
        home_formation = home_team.get("formation", "")
        
        # 如果formation有内容，清理并可能提取球队名
        if home_formation:
            cleaned_formation = clean_formation(home_formation)
            if cleaned_formation != home_formation:
                home_team["formation"] = cleaned_formation
                modified = True
        
        # 处理away队
        away_team = teams.get("away", {})
        away_name = away_team.get("name", "")
        away_formation = away_team.get("formation", "")
        
        # 如果away队名是"Opponent"，从formation中提取
        if away_name == "Opponent" and away_formation:
            extracted_name = extract_team_name_from_formation(away_formation)
            if extracted_name:
                away_team["name"] = extracted_name
                modified = True
                print(f"{file_path.name}: 修复 away.name: Opponent -> {extracted_name}")
        
        # 清理away队的formation
        if away_formation:
            cleaned_formation = clean_formation(away_formation)
            if cleaned_formation != away_formation:
                away_team["formation"] = cleaned_formation
                modified = True
        
        # 如果有修改，保存文件
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        
        return False
        
    except Exception as e:
        print(f"错误处理 {file_path.name}: {str(e)}")
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
    
    json_files = sorted(json_dir.glob("*.json"))
    if not json_files:
        print("未找到2021赛季的JSON文件")
        return
    
    print(f"找到 {len(json_files)} 个2021赛季比赛文件")
    print()
    
    success_count = 0
    fail_count = 0
    
    for json_file in json_files:
        if fix_json_file(json_file):
            success_count += 1
    
    print()
    print("=" * 60)
    print("修复完成")
    print("=" * 60)
    print(f"成功修复: {success_count} 个文件")
    print(f"总计: {len(json_files)} 个文件")

if __name__ == "__main__":
    main()
