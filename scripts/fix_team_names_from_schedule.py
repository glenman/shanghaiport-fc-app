import csv
import json
import re
from datetime import datetime
from pathlib import Path

def parse_date(date_str):
    """解析日期字符串为标准格式"""
    if not date_str:
        return None
    # 处理 '2021/4/22' 或 '2021-4-22' 格式
    date_str = date_str.replace('/', '-')
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        return date.strftime('%Y-%m-%d')
    except ValueError:
        try:
            date = datetime.strptime(date_str, '%Y/%m/%d')
            return date.strftime('%Y-%m-%d')
        except:
            return None

def load_schedule_from_csv(csv_path):
    """从CSV文件加载赛程信息"""
    schedule_dict = {}
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 解析日期，尝试不同的列名
            date_str = row.get('比赛日期') or row.get('日期')
            if not date_str:
                continue
            date_key = parse_date(date_str)
            if not date_key:
                continue
            
            # 获取主队客队
            home_team = row.get('主队', '').strip()
            away_team = row.get('客队', '').strip()
            
            # 清理多余空格和特殊字符
            home_team = re.sub(r'\s+', '', home_team)
            home_team = re.sub(r'[\u200b-\u200d\ufeff]', '', home_team)
            away_team = re.sub(r'\s+', '', away_team)
            away_team = re.sub(r'[\u200b-\u200d\ufeff]', '', away_team)
            
            schedule_dict[date_key] = {
                'home_team': home_team,
                'away_team': away_team,
                'round': row.get('轮次', '')
            }
    return schedule_dict

def validate_and_fix_json(json_path, schedule_data):
    """验证并修复JSON文件中的球队名称"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        date_key = data.get('match_info', {}).get('date')
        if not date_key:
            print(f"⚠️ {json_path.name}: 缺少日期字段")
            return False
        
        # 查找对应的赛程信息
        if date_key not in schedule_data:
            print(f"⚠️ {json_path.name}: 在赛程文件中找不到日期 {date_key}")
            return False
        
        schedule = schedule_data[date_key]
        
        # 获取并清理当前球队名称
        current_home = data.get('teams', {}).get('home', {}).get('name', '')
        current_home = re.sub(r'[\u200b-\u200d\ufeff]', '', current_home)
        
        current_away = data.get('teams', {}).get('away', {}).get('name', '')
        current_away = re.sub(r'[\u200b-\u200d\ufeff]', '', current_away)
        
        needs_fix = False
        message = []
        
        # 检查主队名称
        if current_home != schedule['home_team']:
            needs_fix = True
            message.append(f"主队: {current_home} → {schedule['home_team']}")
        
        # 检查客队名称
        if current_away != schedule['away_team']:
            needs_fix = True
            message.append(f"客队: {current_away} → {schedule['away_team']}")
        
        if not needs_fix:
            return False
        
        # 开始修复
        print(f"🔧 {json_path.name}: {' | '.join(message)}")
        
        # 检查是否需要交换主客队
        home_is_port = current_home in ['上海海港', 'Shanghai Port']
        away_is_port = current_away in ['上海海港', 'Shanghai Port']
        schedule_home_is_port = schedule['home_team'] in ['上海海港']
        schedule_away_is_port = schedule['away_team'] in ['上海海港']
        
        if (home_is_port and schedule_away_is_port) or (away_is_port and schedule_home_is_port):
            # 需要交换主客队
            print(f"   交换主客队")
            home_data = data['teams'].pop('home')
            away_data = data['teams'].pop('away')
            data['teams']['home'] = away_data
            data['teams']['away'] = home_data
            
            # 同时交换比分
            home_score = data['teams']['home']['score']
            away_score = data['teams']['away']['score']
            data['teams']['home']['score'] = away_score
            data['teams']['away']['score'] = home_score
            
            # 交换半场比分
            if 'score_ht' in data['teams']['home'] and 'score_ht' in data['teams']['away']:
                home_score_ht = data['teams']['home']['score_ht']
                away_score_ht = data['teams']['away']['score_ht']
                data['teams']['home']['score_ht'] = away_score_ht
                data['teams']['away']['score_ht'] = home_score_ht
            
            # 更新events中的team字段
            if 'events' in data:
                for event in data['events']:
                    if event.get('team') == 'home':
                        event['team'] = 'away'
                    elif event.get('team') == 'away':
                        event['team'] = 'home'
        
        # 更新球队名称
        data['teams']['home']['name'] = schedule['home_team']
        data['teams']['home']['full_name'] = schedule['home_team']
        data['teams']['away']['name'] = schedule['away_team']
        data['teams']['away']['full_name'] = schedule['away_team']
        
        # 保存修改
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True
        
    except Exception as e:
        print(f"❌ {json_path.name}: 错误 - {str(e)}")
        return False

def process_season(season, csv_path):
    """处理整个赛季"""
    print(f"\n{'='*80}")
    print(f"处理 {season} 赛季...")
    print(f"{'='*80}")
    
    # 加载赛程
    schedule_data = load_schedule_from_csv(csv_path)
    if not schedule_data:
        print(f"❌ 无法加载 {season} 赛程")
        return
    
    # 查找JSON文件
    season_dir = Path(f"public/data/history/{season}")
    if not season_dir.exists():
        print(f"❌ {season_dir} 目录不存在")
        return
    
    json_files = list(season_dir.glob("*.json"))
    print(f"找到 {len(json_files)} 个JSON文件\n")
    
    fixed_count = 0
    for json_file in json_files:
        if validate_and_fix_json(json_file, schedule_data):
            fixed_count += 1
    
    print(f"\n✅ {season} 赛季完成: 修复了 {fixed_count} 个文件")

def main():
    # 处理2021赛季
    process_season("2021", Path("datafile/上海海港2021一线队中超赛程.csv"))
    
    # 处理2022赛季
    process_season("2022", Path("datafile/上海海港2022一线队中超赛程.csv"))
    
    # 处理2023赛季
    process_season("2023", Path("datafile/上海海港2023一线队中超赛程.csv"))

if __name__ == "__main__":
    main()
