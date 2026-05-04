import csv
import json
import os
import re
from pathlib import Path

# 上海海港球员名称映射（英文 -> 中文）
PLAYER_NAME_MAP = {
    'Vítor Pereira': '佩雷拉',
    'Yan Junling': '颜骏凌',
    'Oscar': '奥斯卡',
    'Wang Shenchao': '王燊超',
    'Marko Arnautovic': '阿瑙托维奇',
    'Marko Arnautović': '阿瑙托维奇',
    'Fu Huan': '傅欢',
    'Ricardo Lopes Pereira': '洛佩斯',
    'Ricardo Lopes': '洛佩斯',
    'Shi Ke': '石柯',
    'Wei Zhen': '魏震',
    'Hulk': '胡尔克',
    'He Guan': '贺惯',
    'Mirahmetjan Muzepper': '买提江',
    'Mirahmetjan': '买提江',
    'Lü Wenjun': '吕文君',
    'Lv Wenjun': '吕文君',
    'Yang Shiyuan': '杨世元',
    'Odil Ahmedov': '艾哈迈多夫',
    'Chen Binbin': '陈彬彬',
    'Yu Hai': '于海',
    'Lin Chuangyi': '林创益',
    'Yu Rui': '于睿',
    'Cai Huikang': '蔡慧康',
    'Aaron Mooy': '穆伊',
    'Mooy': '穆伊',
    'Lei Wenjie': '雷文杰',
    'Zhang Wei': '张卫',
    'Li Shenglong': '李圣龙',
    'Chen Wei': '陈威',
    'Jia Boyan': '贾博琰',
    'Chen Chunxin': '陈纯新',
    'Zhang Yi': '张一',
    'Zheng Zhiyun': '郑致云',
    'Liu Cong': '刘龙',
    'Sun Jiang': '孙俊',
    'Wang Yepeng': '王燊超',
}

# 球队名称映射（英文 -> 中文）
TEAM_NAME_MAP = {
    'Shanghai SIPG': '上海海港',
    'Tianjin TEDA': '天津泰达',
    'Hebei China Fortune': '河北华夏幸福',
    'Qingdao Huanghai': '青岛黄海',
    'Wuhan Zall': '武汉卓尔',
    'Shijiazhuang Ever Bright': '石家庄永昌',
    'Beijing Guoan': '北京国安',
    'Chongqing Lifan': '重庆力帆',
    'Shanghai Shenhua': '上海绿地',
    'Jiangsu Suning': '江苏苏宁',
    'Dalian Pro': '大连人',
    'Shenzhen': '深圳佳兆业',
    'Dalian Professional': '大连人',
}

# 赛事名称映射
COMPETITION_NAME_MAP = {
    'Chinese Football Association Super League': '中国足球协会超级联赛',
    'Chinese Super League': '中国足球协会超级联赛',
}

# 场地名称映射
VENUE_NAME_MAP = {
    'Kunshan Sports Center Stadium': '昆山体育中心体育场',
    'Dalian Sports Center Stadium': '大连体育中心体育场',
    'Suzhou Olympic Sports Center Stadium': '苏州奥林匹克体育中心',
    'Jiangsu Sports Center': '江苏体育中心',
    'Henan Provincial Sports Center Stadium': '河南省体育中心',
    'Huizhou Olympic Sports Center Stadium': '惠州奥林匹克体育中心',
    'Guangzhou Evergrande Stadium': '广州恒大体育场',
    'Chengdu Sports Center Stadium': '成都体育中心',
    'Beijing Workers Stadium': '北京工人体育场',
    'Tianjin Olympic Center Stadium': '天津奥林匹克中心体育场',
    'Yanbian Stadium': '延边体育场',
    'Changchun Sports Center Stadium': '长春体育中心体育场',
    'Shenzhen Universiade Sports Center Stadium': '深圳大运会体育中心',
    'Hefei Sports Center Stadium': '合肥体育中心体育场',
    'Nanjing Olympic Sports Center Stadium': '南京奥林匹克体育中心',
    'Shandong Sports Center Stadium': '山东省体育中心',
    'Wuhan Five Rings Sports Center Stadium': '武汉五环体育中心',
    'KASHEN Sports Center Stadium': '廊坊市体育中心',
    'Qingdao Youth Football Stadium': '青岛国信体育场',
    'Shanghai Stadium': '上海体育场',
    'Hongkou Football Stadium': '虹口足球场',
    'Shanghai Football Stadium': '上海体育场',
    ' Pudong Football Stadium': '浦东足球场',
    'Pudong Football Stadium': '浦东足球场',
}

# 教练名称映射（对手球队）
COACH_NAME_MAP = {
    'Uli Stielike': '斯蒂利克',
    '谢峰': '谢峰',
    '黄海': '黄海',
    '庞利': '庞利',
    '张外龙': '张外龙',
    '热内西奥': '热内西奥',
    '吴金贵': '吴金贵',
    '奥拉罗尤': '奥拉罗尤',
    '郝伟': '郝伟',
    '李霄鹏': '李霄鹏',
    '佩雷拉': '佩雷拉',
}

def normalize_name(name):
    """标准化球员/教练名称"""
    if not name:
        return name
    name = name.strip()
    # 尝试精确匹配
    if name in PLAYER_NAME_MAP:
        return PLAYER_NAME_MAP[name]
    # 尝试部分匹配
    for eng, chn in PLAYER_NAME_MAP.items():
        if eng.lower() in name.lower() or name.lower() in eng.lower():
            return chn
    return name

def normalize_team_name(name):
    """标准化球队名称"""
    if not name:
        return name
    name = name.strip()

    # 先检查是否在英文映射表中
    if name in TEAM_NAME_MAP:
        return TEAM_NAME_MAP[name]

    # 处理中文队名
    chinese_replacements = {
        '上海上港': '上海海港',
        '上海绿地': '上海绿地',
        '上海绿地绿地': '上海绿地',
        '江苏苏宁': '江苏苏宁',
        '河北华夏幸福': '河北华夏幸福',
        '河北华夏': '河北华夏幸福',
        '青岛黄海': '青岛黄海',
        '青岛黄海青港': '青岛黄海',
        '武汉卓尔': '武汉卓尔',
        '武汉': '武汉卓尔',
        '石家庄永昌': '石家庄永昌',
        '北京国安': '北京国安',
        '北京中赫国安': '北京国安',
        '重庆力帆': '重庆力帆',
        '重庆当代': '重庆力帆',
        '天津泰达': '天津泰达',
        '天津天海': '天津天海',
        '广州恒大': '广州恒大',
        '广州恒大淘宝': '广州恒大',
        '广州富力': '广州富力',
        '山东泰山': '山东泰山',
        '山东鲁斯': '山东泰山',
        '河南建业': '河南建业',
        '河南': '河南建业',
        '江苏': '江苏苏宁',
        '大连人': '大连人',
        '大连一方': '大连人',
        '深圳佳兆业': '深圳佳兆业',
        '深圳': '深圳佳兆业',
        '北京人和': '北京人和',
        '长春亚泰': '长春亚泰',
        '上海海港': '上海海港',
    }

    for old, new in chinese_replacements.items():
        if old in name:
            return new

    # 去掉阵型部分
    if '(' in name:
        name = name.split('(')[0].strip()
        if name in TEAM_NAME_MAP:
            return TEAM_NAME_MAP[name]
        for old, new in chinese_replacements.items():
            if old in name:
                return new

    return name

def normalize_competition_name(name):
    """标准化赛事名称"""
    if not name:
        return name
    name = name.strip()
    if name in COMPETITION_NAME_MAP:
        return COMPETITION_NAME_MAP[name]
    return name

def normalize_venue_name(name):
    """标准化场地名称"""
    if not name:
        return name
    name = name.strip()
    if name in VENUE_NAME_MAP:
        return VENUE_NAME_MAP[name]
    return name

def load_schedule_from_csv(csv_path):
    """从CSV加载赛程数据"""
    schedule = {}
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        if line.startswith('"') and line.endswith('"'):
            line = line[1:-1]
        parts = line.split(',')
        if len(parts) >= 6:
            round_type = parts[0].strip()
            date = parts[1].strip()
            home = parts[4].strip()
            away = parts[5].strip()
            schedule[date] = {'home': home, 'away': away, 'round_type': round_type}
    return schedule

def process_match_report(json_path, schedule):
    """处理单个比赛报告"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        modified = False

        # 更新赛事名称
        if 'competition' in data.get('match_info', {}):
            comp_name = data['match_info']['competition'].get('name', '')
            new_name = normalize_competition_name(comp_name)
            if new_name != comp_name:
                data['match_info']['competition']['name'] = new_name
                modified = True

        # 更新场地名称
        if 'venue' in data.get('match_info', {}):
            venue_name = data['match_info']['venue'].get('name', '')
            new_name = normalize_venue_name(venue_name)
            if new_name != venue_name:
                data['match_info']['venue']['name'] = new_name
                modified = True

        # 更新主客队信息
        if 'teams' in data:
            teams = data['teams']

            # 从赛程获取正确的主客队名称
            date = data.get('match_info', {}).get('date', '')
            if date in schedule:
                sched = schedule[date]
                sched_home = normalize_team_name(sched['home'])
                sched_away = normalize_team_name(sched['away'])

                # 更新home队
                if 'home' in teams:
                    old_home_name = teams['home'].get('name', '')
                    new_home_name = sched_home
                    if old_home_name != new_home_name:
                        teams['home']['name'] = new_home_name
                        teams['home']['full_name'] = new_home_name
                        modified = True

                    # 清理formation，只保留阵型
                    formation = teams['home'].get('formation', '')
                    if formation and '(' in formation:
                        match = re.search(r'\(([\d-]+)\)', formation)
                        if match:
                            new_formation = f"({match.group(1)})"
                            if new_formation != formation:
                                teams['home']['formation'] = new_formation
                                modified = True

                    # 更新教练
                    if 'coach' in teams['home']:
                        old_coach = teams['home']['coach']
                        new_coach = normalize_name(old_coach) if old_coach not in TEAM_NAME_MAP else old_coach
                        if new_coach != old_coach:
                            teams['home']['coach'] = new_coach
                            modified = True

                    # 更新队长
                    if 'captain' in teams['home']:
                        old_captain = teams['home']['captain']
                        new_captain = normalize_name(old_captain)
                        if new_captain != old_captain:
                            teams['home']['captain'] = new_captain
                            modified = True

                    # 更新阵容球员名称
                    for player in teams['home'].get('lineup', []):
                        if 'name' in player:
                            old_name = player['name']
                            new_name = normalize_name(old_name)
                            if new_name != old_name:
                                player['name'] = new_name
                                modified = True

                    for player in teams['home'].get('substitutes', []):
                        if 'name' in player:
                            old_name = player['name']
                            new_name = normalize_name(old_name)
                            if new_name != old_name:
                                player['name'] = new_name
                                modified = True

                # 更新away队
                if 'away' in teams:
                    old_away_name = teams['away'].get('name', '')
                    new_away_name = sched_away
                    if old_away_name != new_away_name:
                        teams['away']['name'] = new_away_name
                        teams['away']['full_name'] = new_away_name
                        modified = True

                    # 清理formation，只保留阵型
                    formation = teams['away'].get('formation', '')
                    if formation and '(' in formation:
                        match = re.search(r'\(([\d-]+)\)', formation)
                        if match:
                            new_formation = f"({match.group(1)})"
                            if new_formation != formation:
                                teams['away']['formation'] = new_formation
                                modified = True

                    # 更新教练
                    if 'coach' in teams['away']:
                        old_coach = teams['away']['coach']
                        new_coach = normalize_name(old_coach) if old_coach not in TEAM_NAME_MAP else old_coach
                        if new_coach != old_coach:
                            teams['away']['coach'] = new_coach
                            modified = True

                    # 更新队长
                    if 'captain' in teams['away']:
                        old_captain = teams['away']['captain']
                        new_captain = normalize_name(old_captain)
                        if new_captain != old_captain:
                            teams['away']['captain'] = new_captain
                            modified = True

                    # 更新阵容球员名称
                    for player in teams['away'].get('lineup', []):
                        if 'name' in player:
                            old_name = player['name']
                            new_name = normalize_name(old_name)
                            if new_name != old_name:
                                player['name'] = new_name
                                modified = True

                    for player in teams['away'].get('substitutes', []):
                        if 'name' in player:
                            old_name = player['name']
                            new_name = normalize_name(old_name)
                            if new_name != old_name:
                                player['name'] = new_name
                                modified = True

            # 更新换人事件中的球员名称
            for team_key in ['home', 'away']:
                if team_key in teams:
                    for sub in teams[team_key].get('substitutions', []):
                        if 'player' in sub:
                            old_name = sub['player']
                            new_name = normalize_name(old_name)
                            if new_name != old_name:
                                sub['player'] = new_name
                                modified = True
                        if 'player_out' in sub:
                            old_name = sub['player_out']
                            new_name = normalize_name(old_name)
                            if new_name != old_name:
                                sub['player_out'] = new_name
                                modified = True
                        if 'player2' in sub:
                            old_name = sub['player2']
                            if old_name:
                                new_name = normalize_name(old_name)
                                if new_name != old_name:
                                    sub['player2'] = new_name
                                    modified = True

        # 更新事件中的球员名称
        if 'events' in data:
            for event in data['events']:
                if 'player' in event:
                    old_name = event['player']
                    new_name = normalize_name(old_name)
                    if new_name != old_name:
                        event['player'] = new_name
                        modified = True
                if 'player2' in event:
                    old_name = event['player2']
                    if old_name:
                        new_name = normalize_name(old_name)
                        if new_name != old_name:
                            event['player2'] = new_name
                            modified = True
                if 'player_out' in event:
                    old_name = event['player_out']
                    new_name = normalize_name(old_name)
                    if new_name != old_name:
                        event['player_out'] = new_name
                        modified = True

        if modified:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        return False

    except Exception as e:
        print(f"  错误: 处理 {json_path} 时出错: {str(e)}")
        return False

def main():
    csv_path = r'd:\Workspace\shanghaiport-fc-app\datafile\上海海港2020一线队中超赛程.csv'
    json_dir = r'd:\Workspace\shanghaiport-fc-app\public\data\history\2020'

    print("加载赛程数据...")
    schedule = load_schedule_from_csv(csv_path)
    print(f"已加载 {len(schedule)} 条赛程记录")

    print("\n开始汉化处理...")
    json_files = sorted(Path(json_dir).glob('*.json'))

    modified_count = 0
    for json_path in json_files:
        if process_match_report(json_path, schedule):
            print(f"  已汉化: {json_path.name}")
            modified_count += 1
        else:
            print(f"  无需修改: {json_path.name}")

    print(f"\n完成: 已处理 {modified_count}/{len(json_files)} 个文件")

if __name__ == '__main__':
    main()