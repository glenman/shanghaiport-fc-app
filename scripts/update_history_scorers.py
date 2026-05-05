import json
import pandas as pd
from pathlib import Path

# 文件路径
EXCEL_PATH = r'd:\Workspace\shanghaiport-fc-app\datafile\主教练.xlsx'
HISTORY_SCHEDULE_PATH = r'd:\Workspace\shanghaiport-fc-app\public\data\history_schedule.json'

# 上海海港历史名称
SHANGHAI_PORT_NAMES = [
    '上海海港', '上海上港', '上海东亚', '上海特莱士',
    'Shanghai SIPG', 'Shanghai Port', 'Shanghai East Asia'
]

def load_excel_data():
    """加载Excel中所有主教练sheet的比赛数据"""
    matches = []
    
    xls = pd.ExcelFile(EXCEL_PATH)
    
    # 排除汇总类sheet
    summary_sheets = ['汇总', '主客场汇总', '主场', '客场', '中立场']
    
    for sheet_name in xls.sheet_names:
        if sheet_name in summary_sheets:
            continue
            
        try:
            df = pd.read_excel(EXCEL_PATH, sheet_name=sheet_name, header=1)
            
            for idx, row in df.iterrows():
                date = row.get('比赛日期', '')
                if pd.isna(date):
                    continue
                
                # 解析日期
                try:
                    date_str = str(date).strip()
                    if '.' in date_str:
                        parts = date_str.split('.')
                        if len(parts) == 3:
                            date_str = f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
                except:
                    continue
                
                match_data = {
                    'date': date_str,
                    'home_team': str(row.get('主队', '')).strip(),
                    'away_team': str(row.get('客队', '')).strip(),
                    'home_away': str(row.get('主客场', '')).strip(),
                    'score': str(row.get('比分', '')).strip(),
                    'our_scorers': str(row.get('本队进球队员', '')).strip(),
                    'opponent_scorers': str(row.get('对手进球队员', '')).strip()
                }
                
                if match_data['date'] and match_data['home_team'] and match_data['away_team']:
                    matches.append(match_data)
                    
        except Exception as e:
            print(f"读取Sheet {sheet_name}失败: {e}")
    
    return matches

def parse_scorers(scorers_str):
    """解析进球球员字符串"""
    if not scorers_str or scorers_str in ['—', '-', 'None', 'none', 'nan']:
        return []
    
    # 尝试多种分隔符
    separators = ['，', ',', '、', '；', ';', ' ', '和', '及']
    
    for sep in separators:
        if sep in scorers_str:
            return [s.strip() for s in scorers_str.split(sep) if s.strip()]
    
    # 如果没有分隔符，可能是单个球员
    return [scorers_str.strip()]

def is_shanghai_port(team_name):
    """判断是否为上海海港"""
    team = str(team_name).strip()
    for name in SHANGHAI_PORT_NAMES:
        if name in team or team in name:
            return True
    return False

def update_history_schedule():
    """更新history_schedule.json中的进球者信息"""
    print("加载Excel数据...")
    excel_matches = load_excel_data()
    print(f"加载了 {len(excel_matches)} 场比赛数据")
    
    print("\n加载history_schedule.json...")
    with open(HISTORY_SCHEDULE_PATH, 'r', encoding='utf-8') as f:
        schedule = json.load(f)
    
    updated_count = 0
    not_found_count = 0
    
    print("\n开始匹配并更新...")
    for match in schedule:
        match_date = match.get('date', '')
        home_team = match.get('home_team', '')
        away_team = match.get('away_team', '')
        
        if not match_date or not home_team or not away_team:
            continue
        
        # 查找匹配的Excel数据
        found = False
        for excel_match in excel_matches:
            if excel_match['date'] == match_date:
                # 检查主队或客队是否匹配
                excel_home = excel_match['home_team']
                excel_away = excel_match['away_team']
                
                # 尝试多种匹配方式
                if (home_team in excel_home or excel_home in home_team or 
                    home_team in excel_away or excel_away in home_team):
                    found = True
                    break
        
        if found:
            # 判断上海海港是主队还是客队
            is_home = is_shanghai_port(home_team)
            
            # 解析进球者
            our_scorers = parse_scorers(excel_match['our_scorers'])
            opponent_scorers = parse_scorers(excel_match['opponent_scorers'])
            
            # 根据主客场分配进球者
            if is_home:
                home_scorers = our_scorers
                away_scorers = opponent_scorers
            else:
                home_scorers = opponent_scorers
                away_scorers = our_scorers
            
            # 更新scorers字段
            match['scorers'] = {
                'home': home_scorers,
                'away': away_scorers
            }
            
            updated_count += 1
            
            if updated_count % 50 == 0:
                print(f"已更新 {updated_count} 场比赛...")
        else:
            not_found_count += 1
    
    # 保存更新
    print(f"\n保存更新...")
    with open(HISTORY_SCHEDULE_PATH, 'w', encoding='utf-8') as f:
        json.dump(schedule, f, ensure_ascii=False, indent=2)
    
    print(f"\n更新完成！")
    print(f"成功更新: {updated_count} 场比赛")
    print(f"未找到匹配: {not_found_count} 场比赛")

if __name__ == '__main__':
    update_history_schedule()