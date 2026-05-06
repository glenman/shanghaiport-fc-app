import json
import csv
import sys
from pathlib import Path

def load_roster(season):
    """加载指定赛季的球员大名单"""
    roster_file = f'datafile/上海海港{season}一线队大名单.csv'
    roster = {}
    
    try:
        with open(roster_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name_en = row.get('英文名称', '').strip()
                name_cn = row.get('中文名称', '').strip()
                if name_en and name_cn:
                    roster[name_en] = name_cn
                    if ' ' in name_en:
                        roster[name_en.replace(' ', '')] = name_cn
                        last_name = name_en.split()[-1]
                        roster[last_name] = name_cn
        print(f'已加载 {len(roster)} 名球员')
        return roster
    except Exception as e:
        print(f'加载球员名单失败: {e}')
        return {}

def update_player_names(data, roster):
    """递归更新所有球员姓名"""
    updated = False
    
    if isinstance(data, dict):
        for key, value in list(data.items()):
            # 处理所有可能包含球员姓名的字段
            player_fields = ['name', 'player', 'player_out', 'player2', 'captain', 'scorer']
            if key in player_fields and isinstance(value, str) and value:
                if value in roster:
                    data[key] = roster[value]
                    updated = True
                elif value.replace(' ', '') in roster:
                    data[key] = roster[value.replace(' ', '')]
                    updated = True
                elif value.strip() and value.split()[-1] in roster:
                    data[key] = roster[value.split()[-1]]
                    updated = True
            
            if isinstance(value, (dict, list)):
                if update_player_names(value, roster):
                    updated = True
    
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, (dict, list)):
                if update_player_names(item, roster):
                    updated = True
    
    return updated

def main():
    if len(sys.argv) < 2:
        print('用法: python scripts/localize_players.py <赛季>')
        print('例如: python scripts/localize_players.py 2015')
        sys.exit(1)
    
    season = sys.argv[1]
    print(f'开始对{season}赛季赛事报告进行球员姓名汉化...')
    
    roster = load_roster(season)
    if not roster:
        print('无法加载球员名单，退出')
        sys.exit(1)
    
    history_dir = Path(f'public/data/history/{season}')
    if not history_dir.exists():
        print(f'目录不存在: {history_dir}')
        sys.exit(1)
    
    json_files = list(history_dir.glob('*.json'))
    updated_count = 0
    
    for json_file in json_files:
        with open(json_file, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        updated = update_player_names(report, roster)
        
        if updated:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            updated_count += 1
            print(f'更新: {json_file.name}')
    
    print(f'\n球员姓名汉化完成！')
    print(f'处理文件: {len(json_files)}')
    print(f'更新文件: {updated_count}')

if __name__ == '__main__':
    main()