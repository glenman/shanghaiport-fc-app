import csv
import json
import os
import re
from pathlib import Path

def load_schedule_from_csv(csv_path):
    """从CSV文件读取赛程数据"""
    schedule = {}
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()

        # 跳过标题行，从第2行开始
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            # 移除首尾引号
            if line.startswith('"') and line.endswith('"'):
                line = line[1:-1]

            parts = line.split(',')
            if len(parts) >= 6:
                round_str = parts[0].strip()
                date = parts[1].strip()
                home_team = parts[4].strip()
                away_team = parts[5].strip()

                match = round_str.replace('Matchweek', '').strip()
                if match.isdigit():
                    round_num = int(match)
                    schedule[round_num] = {
                        'date': date,
                        'home': home_team,
                        'away': away_team
                    }

        return schedule
    except Exception as e:
        print(f"读取赛程失败: {str(e)}")
        return {}

def normalize_team_name(name):
    """标准化球队名称"""
    name = name.strip()
    replacements = {
        '上海绿地': '上海绿地',
        '上海绿地绿地': '上海绿地',
        '上海绿地绿地绿地': '上海绿地',
        '江苏苏宁': '江苏苏宁',
        '河北华夏幸福': '河北华夏幸福',
        '重庆力帆': '重庆力帆',
        '重庆当代': '重庆力帆',
        '武汉卓尔': '武汉卓尔',
        '天津天海': '天津天海',
        '天津泰达': '天津泰达',
        '广州恒大': '广州恒大',
        '广州恒大淘宝': '广州恒大',
        '山东鲁斯': '山东泰山',
        '山东泰山': '山东泰山',
        '河南建业': '河南建业',
        '北京国安': '北京国安',
        '北京中赫国安': '北京国安',
        '大连一方': '大连人',
        '大连人': '大连人',
        '广州富力': '广州富力',
        '深圳佳兆业': '深圳佳兆业',
        '北京人和': '北京人和',
        '上海上港': '上海海港',
        '上海海港': '上海海港',
    }
    for old, new in replacements.items():
        if old in name:
            return new
    return name

def extract_round_from_filename(filename):
    """从文件名提取轮次"""
    # 文件名格式: 2019-03-01-中超-第1轮.json
    match = re.search(r'第(\d+)轮', filename)
    if match:
        return int(match.group(1))
    return None

def fix_match_report(json_path, schedule):
    """修复单个比赛报告的球队名称"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        teams = data.get('teams', {})

        # 从文件名提取轮次
        filename = os.path.basename(json_path)
        round_num = extract_round_from_filename(filename)

        if round_num is None:
            print(f"  警告: 无法从文件名 {filename} 提取轮次")
            return False

        if round_num not in schedule:
            print(f"  警告: 无法找到轮次 {round_num} 的赛程数据")
            return False

        sched = schedule[round_num]
        csv_home = normalize_team_name(sched['home'])
        csv_away = normalize_team_name(sched['away'])

        # 判断上海上港在CSV中是home还是away
        sipg_is_home = '上海海港' in csv_home or '上海上港' in csv_home
        sipg_is_away = '上海海港' in csv_away or '上海上港' in csv_away

        # 根据CSV赛程更新球队名称
        if sipg_is_home:
            # 上海上港在CSV中是主队，更新home
            teams['home']['name'] = csv_home
            teams['home']['full_name'] = csv_home
            teams['away']['name'] = csv_away
            teams['away']['full_name'] = csv_away
        elif sipg_is_away:
            # 上海上港在CSV中是客队，更新away
            teams['home']['name'] = csv_home
            teams['home']['full_name'] = csv_home
            teams['away']['name'] = csv_away
            teams['away']['full_name'] = csv_away
        else:
            print(f"  警告: 轮次 {round_num} 未找到上海上港")
            return False

        data['teams'] = teams

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"  修复: {filename} - home={teams['home']['name']}, away={teams['away']['name']}")
        return True

    except Exception as e:
        print(f"  错误: 处理 {json_path} 时出错: {str(e)}")
        return False

def main():
    csv_path = r'd:\Workspace\shanghaiport-fc-app\datafile\上海海港2019一线队中超赛程.csv'
    json_dir = r'd:\Workspace\shanghaiport-fc-app\public\data\history\2019'

    print("加载赛程数据...")
    schedule = load_schedule_from_csv(csv_path)
    print(f"已加载 {len(schedule)} 轮赛程")

    # 打印前3轮验证
    for i in range(1, 4):
        if i in schedule:
            print(f"  第{i}轮: {schedule[i]}")

    print("\n开始修复球队名称...")
    json_files = sorted(Path(json_dir).glob('*.json'))

    success_count = 0
    for json_path in json_files:
        if fix_match_report(json_path, schedule):
            success_count += 1

    print(f"\n完成: 成功修复 {success_count}/{len(json_files)} 个文件")

if __name__ == '__main__':
    main()