import json
import sys
from pathlib import Path

COMPETITION_MAP = {
    'Chinese Super League': '中国足球协会超级联赛',
    'Chinese Football Association Super League': '中国足球协会超级联赛',
    'Chinese FA Cup': '中国足球协会杯',
    'AFC Champions League': '亚洲足球俱乐部冠军联赛',
    'Chinese Super League Playoffs': '中超联赛季后赛'
}

ROUND_MAP = {
    'Matchweek ': '第',
    'Round ': '第',
    'Week ': '第',
    'Regular season ': ''
}

def update_competition_info(data):
    """更新联赛信息"""
    updated = False
    
    if 'match_info' in data and 'competition' in data['match_info']:
        comp = data['match_info']['competition']
        
        # 更新联赛名称
        if 'name' in comp and comp['name'] in COMPETITION_MAP:
            old_name = comp['name']
            comp['name'] = COMPETITION_MAP[comp['name']]
            updated = True
            print(f'  联赛名称: {old_name} -> {comp["name"]}')
        
        # 更新轮次
        if 'round' in comp:
            round_str = comp['round']
            for old, new in ROUND_MAP.items():
                if old in round_str:
                    new_round = round_str.replace(old, new)
                    # 添加"轮"字
                    if new_round and not new_round.endswith('轮'):
                        new_round = new_round + '轮'
                    comp['round'] = new_round
                    updated = True
                    print(f'  轮次: {round_str} -> {comp["round"]}')
    
    return updated

def main():
    if len(sys.argv) < 2:
        print('用法: python scripts/localize_competition.py <赛季>')
        print('例如: python scripts/localize_competition.py 2016')
        sys.exit(1)
    
    season = sys.argv[1]
    print(f'开始对{season}赛季赛事报告进行联赛信息汉化...')
    
    history_dir = Path(f'public/data/history/{season}')
    if not history_dir.exists():
        print(f'目录不存在: {history_dir}')
        sys.exit(1)
    
    json_files = list(history_dir.glob('*.json'))
    updated_count = 0
    
    for json_file in json_files:
        print(f'\n处理: {json_file.name}')
        with open(json_file, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        updated = update_competition_info(report)
        
        if updated:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            updated_count += 1
    
    print(f'\n联赛信息汉化完成！')
    print(f'处理文件: {len(json_files)}')
    print(f'更新文件: {updated_count}')

if __name__ == '__main__':
    main()