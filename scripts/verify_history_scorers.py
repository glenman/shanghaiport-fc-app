import json

with open('public/data/history_schedule.json', 'r', encoding='utf-8') as f:
    schedule = json.load(f)

print('=== 最终验证 ===')
print(f'总比赛数: {len(schedule)}')

has_scorers = [m for m in schedule if 'scorers' in m]
print(f'有scorers字段的比赛: {len(has_scorers)}')

no_scorers = [m for m in schedule if 'scorers' not in m]
print(f'无scorers字段的比赛: {len(no_scorers)}')

if no_scorers:
    print('\n未更新的比赛:')
    for match in no_scorers:
        print(f"{match.get('date')} {match.get('home_team')} vs {match.get('away_team')}")
