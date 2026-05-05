import json
import re
import sys
from pathlib import Path

def extract_round_from_filename(filename):
    """从文件名提取轮次信息"""
    match = re.search(r'-第(\d+)轮\.json', filename)
    if match:
        return f"第{match.group(1)}轮"
    return None

def update_round_from_filename(json_path):
    """根据文件名更新轮次字段"""
    round_str = extract_round_from_filename(json_path.name)
    if not round_str:
        return False
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    updated = False
    if 'match_info' in data and 'competition' in data['match_info']:
        current_round = data['match_info']['competition'].get('round', '')
        if current_round != round_str:
            data['match_info']['competition']['round'] = round_str
            updated = True
            print(f'  轮次: {current_round} -> {round_str}')
    
    if updated:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    return updated

def main():
    if len(sys.argv) < 2:
        print('用法: python scripts/fix_round_from_filename.py <赛季>')
        print('例如: python scripts/fix_round_from_filename.py 2020')
        sys.exit(1)
    
    season = sys.argv[1]
    print(f'开始根据文件名更新{season}赛季赛事报告的轮次字段...')
    
    history_dir = Path(f'public/data/history/{season}')
    if not history_dir.exists():
        print(f'目录不存在: {history_dir}')
        sys.exit(1)
    
    json_files = list(history_dir.glob('*.json'))
    updated_count = 0
    
    for json_file in json_files:
        print(f'\n处理: {json_file.name}')
        if update_round_from_filename(json_file):
            updated_count += 1
    
    print(f'\n轮次更新完成！')
    print(f'处理文件: {len(json_files)}')
    print(f'更新文件: {updated_count}')

if __name__ == '__main__':
    main()