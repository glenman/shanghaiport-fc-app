import csv
import re

def load_schedule_csv(path):
    """加载赛程CSV"""
    schedule = {}
    with open(path, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        if line.startswith('"') and line.endswith('"'):
            line = line[1:-1]
        parts = line.split(',')
        if len(parts) >= 6:
            round_str = parts[0].strip().replace('Matchweek', '').strip()
            if round_str.isdigit():
                round_num = int(round_str)
                date = parts[1].strip()
                home = parts[4].strip()
                away = parts[5].strip()
                schedule[round_num] = {'date': date, 'home': home, 'away': away}
    return schedule

def load_result_csv(path):
    """加载比赛结果CSV - 格式: 比赛类别,轮次,比赛时间,主队,比分(主),比分(客),客队,赛果,进球队员"""
    results = {}
    with open(path, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        parts = line.split(',')
        if len(parts) >= 7:
            round_str = parts[1].strip()
            date = parts[2].strip()
            home = parts[3].strip()
            away = parts[6].strip()
            num_match = re.match(r'(\d+)', round_str)
            if num_match:
                round_num = int(num_match.group(1))
                results[round_num] = {'date': date, 'home': home, 'away': away}
    return results

def normalize_team(name):
    """标准化球队名称"""
    name = name.strip()
    if '绿地' in name or '绿地绿地' in name:
        return '上海绿地'
    if '上海上港' in name or '海港' in name:
        return '上海海港'
    if '江苏苏宁' in name:
        return '江苏苏宁'
    if '河北华夏' in name:
        return '河北华夏'
    if '重庆' in name:
        return '重庆力帆'
    if '武汉卓尔' in name:
        return '武汉卓尔'
    if '天津天海' in name:
        return '天津天海'
    if '天津泰达' in name:
        return '天津泰达'
    if '广州恒大' in name:
        return '广州恒大'
    if '广州富力' in name:
        return '广州富力'
    if '山东' in name:
        return '山东泰山'
    if '河南' in name:
        return '河南建业'
    if '北京国安' in name:
        return '北京国安'
    if '大连' in name:
        return '大连人'
    if '深圳' in name:
        return '深圳佳兆业'
    if '北京人和' in name:
        return '北京人和'
    return name

schedule_path = r'd:\Workspace\shanghaiport-fc-app\datafile\上海海港2019一线队中超赛程.csv'
result_path = r'd:\Workspace\shanghaiport-fc-app\datafile\上海海港2019中超联赛比赛结果.csv'

schedule = load_schedule_csv(schedule_path)
results = load_result_csv(result_path)

print("=" * 90)
print("核对赛程CSV vs 比赛结果CSV")
print("=" * 90)

all_match = True
for round_num in sorted(schedule.keys()):
    if round_num not in results:
        print(f"轮次 {round_num}: 赛程有，结果文件没有")
        all_match = False
        continue

    sched = schedule[round_num]
    res = results[round_num]

    sched_home = normalize_team(sched['home'])
    sched_away = normalize_team(sched['away'])
    res_home = normalize_team(res['home'])
    res_away = normalize_team(res['away'])

    sched_date = sched['date'].replace('-', '.')
    res_date = res['date']

    home_ok = sched_home == res_home
    away_ok = sched_away == res_away
    date_ok = sched_date == res_date

    status = "✅" if (home_ok and away_ok and date_ok) else "❌"
    print(f"第{round_num}轮 {status}")
    print(f"  赛程: {sched['date']} | 主队={sched_home} | 客队={sched_away}")
    print(f"  结果: {res['date']} | 主队={res_home} | 客队={res_away}")

    if not home_ok:
        print(f"  ⚠️ 主队不一致: 赛程'{sched_home}' vs 结果'{res_home}'")
        all_match = False
    if not away_ok:
        print(f"  ⚠️ 客队不一致: 赛程'{sched_away}' vs 结果'{res_away}'")
        all_match = False
    if not date_ok:
        print(f"  ⚠️ 日期不一致: 赛程'{sched['date']}' vs 结果'{res['date']}'")
        all_match = False

print("=" * 90)
if all_match:
    print("核对完成：所有30轮数据完全一致 ✅")
else:
    print("核对完成：存在不一致的数据 ❌")