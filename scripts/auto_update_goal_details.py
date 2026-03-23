
import json
import os
import glob
from datetime import datetime

def load_goal_details(file_path="public/data/goal_details.json"):
    """加载现有的进球记录"""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def get_latest_id(goal_details):
    """获取最新的ID"""
    return max(item['id'] for item in goal_details) if goal_details else 0

def scan_match_reports(base_dir="public/data"):
    """扫描比赛报告文件"""
    match_files = []
    
    # 扫描中超比赛报告
    super_league_files = glob.glob(os.path.join(base_dir, "202*-*-中超-*.json"))
    
    # 扫描中乙比赛报告
    second_league_files = glob.glob(os.path.join(base_dir, "202*-*-中乙-*.json"))
    
    match_files.extend(super_league_files)
    match_files.extend(second_league_files)
    
    return match_files

def extract_goals_from_report(file_path):
    """从比赛报告中提取进球信息"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            match_data = json.load(f)
        
        match_info = match_data['match']
        match_timeline = match_data.get('matchTimeline', [])
        
        # 只处理上海海港一线队的比赛，不处理B队
        is_home = match_info['homeTeam'] == '上海海港'
        is_away = match_info['awayTeam'] == '上海海港'
        
        if not is_home and not is_away:
            return None
        
        shanghaiport_team = match_info['homeTeam'] if is_home else match_info['awayTeam']
        opponent_team = match_info['awayTeam'] if is_home else match_info['homeTeam']
        
        # 提取上海海港的进球
        goals = []
        for event in match_timeline:
            if event['type'] == 'goal':
                # 检查是否是上海海港的进球
                if (is_home and event.get('team') == 'home') or (is_away and event.get('team') == 'away'):
                    player = event.get('player') or event.get('scorer')
                    assist = event.get('assist', '')
                    
                    if player:
                        goals.append({
                            'player': player,
                            'assist': assist,
                            'minute': event['minute']
                        })
        
        return {
            'match_info': match_info,
            'goals': goals,
            'is_home': is_home,
            'shanghaiport_team': shanghaiport_team,
            'opponent_team': opponent_team
        }
        
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {e}")
        return None

def generate_goal_record(match_data, goal, latest_id):
    """生成进球记录"""
    match_info = match_data['match_info']
    is_home = match_data['is_home']
    shanghaiport_team = match_data['shanghaiport_team']
    opponent_team = match_data['opponent_team']
    
    # 解析比分
    home_score, away_score = map(int, match_info['result'].split('-'))
    
    # 确定比赛结果
    if is_home:
        if home_score > away_score:
            result = '胜'
        elif home_score < away_score:
            result = '负'
        else:
            result = '平'
    else:
        if away_score > home_score:
            result = '胜'
        elif away_score < home_score:
            result = '负'
        else:
            result = '平'
    
    # 解析日期代码
    date_code = int(match_info['date'].replace('-', ''))
    
    # 确定比赛类型
    if '中超' in match_info['round']:
        match_type = '中超联赛'
    elif '中乙' in match_info['round']:
        match_type = '中乙联赛'
    else:
        match_type = '其他赛事'
    
    return {
        "id": latest_id,
        "season": match_info['season'],
        "match_type": match_type,
        "goal_time": f"{goal['minute']}'",
        "goal_player": goal['player'],
        "assist_player": goal['assist'] if goal['assist'] else '—',
        "create_player": "—",
        "match_date_code": date_code,
        "match_name": match_info['round'],
        "home_team": match_info['homeTeam'],
        "home_score": home_score,
        "away_score": away_score,
        "away_team": match_info['awayTeam'],
        "match_result": result,
        "remark": "—"
    }

def check_if_already_processed(goal_details, match_date_code, goal_player, goal_time):
    """检查进球是否已经处理过"""
    for goal in goal_details:
        if (goal['match_date_code'] == match_date_code and
            goal['goal_player'] == goal_player and
            goal['goal_time'] == goal_time):
            return True
    return False

def main():
    """主函数"""
    print("开始自动更新进球记录...")
    
    # 加载现有的进球记录
    goal_details = load_goal_details()
    latest_id = get_latest_id(goal_details)
    next_id = latest_id + 1
    
    # 扫描比赛报告文件
    match_files = scan_match_reports()
    print(f"找到 {len(match_files)} 个比赛报告文件")
    
    # 处理每个比赛报告
    new_goals_added = 0
    
    for file_path in match_files:
        print(f"\n处理文件: {os.path.basename(file_path)}")
        
        match_data = extract_goals_from_report(file_path)
        
        if match_data and match_data['goals']:
            print(f"  发现 {len(match_data['goals'])} 个上海海港进球")
            
            for goal in match_data['goals']:
                match_info = match_data['match_info']
                date_code = int(match_info['date'].replace('-', ''))
                goal_time = f"{goal['minute']}'"
                
                # 检查是否已经处理过
                if not check_if_already_processed(goal_details, date_code, goal['player'], goal_time):
                    # 生成新的进球记录
                    goal_record = generate_goal_record(match_data, goal, next_id)
                    goal_details.append(goal_record)
                    print(f"  添加进球: {goal['player']} {goal_time}, 助攻: {goal['assist']}")
                    new_goals_added += 1
                    next_id += 1
                else:
                    print(f"  进球已存在: {goal['player']} {goal_time}")
    
    # 如果有新进球，保存更新后的文件
    if new_goals_added > 0:
        with open("public/data/goal_details.json", 'w', encoding='utf-8') as f:
            json.dump(goal_details, f, ensure_ascii=False, indent=2)
        
        print(f"\n成功添加了 {new_goals_added} 个新进球记录")
        print(f"最新的ID是: {next_id - 1}")
    else:
        print("\n没有发现新的进球记录需要添加")

if __name__ == "__main__":
    main()
