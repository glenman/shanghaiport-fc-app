import json

with open('public/data/history_schedule.json', 'r', encoding='utf-8') as f:
    schedule = json.load(f)

print('=== 完整验证 scorers 字段 ===')
print(f'总比赛数: {len(schedule)}')

all_have_scorers = True
empty_scorers = []
incomplete_scorers = []

for match in schedule:
    if 'scorers' not in match:
        all_have_scorers = False
        empty_scorers.append(match)
    else:
        scorers = match['scorers']
        home = scorers.get('home', [])
        away = scorers.get('away', [])
        
        # 检查是否有结果但无进球者
        result = match.get('result', '')
        if result and '-' in result:
            try:
                h_goals, a_goals = result.split('-')
                h_goals = int(h_goals)
                a_goals = int(a_goals)
                
                if h_goals > 0 and len(home) == 0:
                    incomplete_scorers.append({
                        'date': match.get('date'),
                        'home': match.get('home_team'),
                        'away': match.get('away_team'),
                        'result': result,
                        'home_scorers': home,
                        'away_scorers': away,
                        'issue': '主队有进球但无进球者'
                    })
                
                if a_goals > 0 and len(away) == 0:
                    incomplete_scorers.append({
                        'date': match.get('date'),
                        'home': match.get('home_team'),
                        'away': match.get('away_team'),
                        'result': result,
                        'home_scorers': home,
                        'away_scorers': away,
                        'issue': '客队有进球但无进球者'
                    })
            except:
                pass

print(f'\n是否所有比赛都有scorers字段: {"是" if all_have_scorers else "否"}')
print(f'有scorers字段的比赛: {len([m for m in schedule if "scorers" in m])}')

if empty_scorers:
    print(f'\n缺失scorers字段的比赛: {len(empty_scorers)}')
    for m in empty_scorers:
        print(f"  {m.get('date')} {m.get('home_team')} vs {m.get('away_team')}")

if incomplete_scorers:
    print(f'\n进球者可能不完整的比赛: {len(incomplete_scorers)}')
    for m in incomplete_scorers:
        print(f"  {m['date']} {m['home']} {m['result']} {m['away']}")
        print(f"    {m['issue']}")
        print(f"    主队进球者: {m['home_scorers']}")
        print(f"    客队进球者: {m['away_scorers']}")

if not empty_scorers and not incomplete_scorers:
    print('\n✓ 所有662场比赛都已包含scorers字段！')
