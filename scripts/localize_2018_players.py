import json
import csv
from pathlib import Path

ROSTER_CSV = r'd:\Workspace\shanghaiport-fc-app\datafile\上海海港2018一线队大名单.csv'
HISTORY_2018_PATH = r'd:\Workspace\shanghaiport-fc-app\public\data\history\2018'

def load_roster():
    """加载2018年球员大名单"""
    roster = {}
    with open(ROSTER_CSV, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name_en = row.get('英文名称', '').strip()
            name_cn = row.get('中文名称', '').strip()
            if name_en and name_cn:
                roster[name_en] = name_cn
                # 处理带空格的名字
                if ' ' in name_en:
                    # 也添加不带空格的版本
                    roster[name_en.replace(' ', '')] = name_cn
                    # 只保留姓氏
                    last_name = name_en.split()[-1]
                    roster[last_name] = name_cn
    print(f'加载了 {len(roster)} 名球员')
    return roster

def update_player_names(data, roster, parent_key=''):
    """递归更新所有球员姓名"""
    updated = False
    
    if isinstance(data, dict):
        for key, value in data.items():
            new_key = f'{parent_key}.{key}' if parent_key else key
            
            # 检查是否是球员名称字段
            if key == 'name' and isinstance(value, str):
                # 检查是否需要汉化
                if value in roster:
                    data[key] = roster[value]
                    updated = True
                    # print(f'  汉化: {value} -> {data[key]}')
                elif value.replace(' ', '') in roster:
                    data[key] = roster[value.replace(' ', '')]
                    updated = True
                    # print(f'  汉化(去空格): {value} -> {data[key]}')
                elif value.split()[-1] in roster:
                    data[key] = roster[value.split()[-1]]
                    updated = True
                    # print(f'  汉化(姓氏): {value} -> {data[key]}')
            
            # 递归处理嵌套结构
            if isinstance(value, (dict, list)):
                if update_player_names(value, roster, new_key):
                    updated = True
    
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, (dict, list)):
                if update_player_names(item, roster, f'{parent_key}[{i}]'):
                    updated = True
    
    return updated

def main():
    roster = load_roster()
    
    history_dir = Path(HISTORY_2018_PATH)
    json_files = list(history_dir.glob('*.json'))
    
    updated_count = 0
    total_changes = 0
    
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
    print('开始对2018赛季赛事报告进行球员姓名汉化...')
    main()