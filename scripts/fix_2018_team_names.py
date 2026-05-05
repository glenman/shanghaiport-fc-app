import json
import re
from pathlib import Path

HISTORY_2018_PATH = r'd:\Workspace\shanghaiport-fc-app\public\data\history\2018'

def extract_team_name_from_formation(formation):
    """从formation字段提取队名（括号前面的部分）"""
    if not formation or '(' not in formation:
        return None
    
    match = re.match(r'^(.+?)\s*\(', formation)
    if match:
        team_name = match.group(1).strip()
        return team_name
    return None

def clean_formation(formation):
    """清理formation，只保留阵型部分（括号及内容）"""
    if not formation:
        return formation
    
    match = re.search(r'\([\d-]+\)', formation)
    if match:
        return match.group(0)
    return formation

def fix_team_names():
    """修复2018赛季所有赛事报告中的队名问题"""
    history_dir = Path(HISTORY_2018_PATH)
    json_files = list(history_dir.glob('*.json'))
    
    updated_count = 0
    fixed_count = 0
    
    for json_file in json_files:
        with open(json_file, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        updated = False
        
        if 'teams' in report:
            for team_key in ['home', 'away']:
                if team_key in report['teams']:
                    team = report['teams'][team_key]
                    
                    if team.get('name') == 'Opponent':
                        formation = team.get('formation', '')
                        team_name = extract_team_name_from_formation(formation)
                        
                        if team_name:
                            team['name'] = team_name
                            team['formation'] = clean_formation(formation)
                            fixed_count += 1
                            updated = True
                            print(f'  修复 {json_file.name}: {team_key}队 "{team_name}"')
                        else:
                            print(f'  无法修复 {json_file.name}: {team_key}队 formation="{formation}"')
        
        if updated:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            updated_count += 1
    
    print(f'\n修复完成！')
    print(f'处理文件: {len(json_files)}')
    print(f'更新文件: {updated_count}')
    print(f'修复队名: {fixed_count}')

if __name__ == '__main__':
    print('开始修复2018赛季赛事报告中的队名问题...')
    fix_team_names()