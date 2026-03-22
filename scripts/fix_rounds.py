import os
import json
import shutil

HISTORY_SCHEDULE_PATH = '../public/data/history_schedule.json'
HISTORY_2025_DIR = '../public/data/history/2025'

def load_history_schedule():
    with open(HISTORY_SCHEDULE_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_2025_csl_matches(schedule):
    csl_matches = {}
    for match in schedule:
        if match['season'] == '2025' and match['match_type'] == '中超联赛':
            date = match['date']
            csl_matches[date] = {
                'round': match['round'],
                'home_team': match['home_team'],
                'away_team': match['away_team'],
                'result': match['result']
            }
    return csl_matches

def parse_filename(filename):
    parts = filename.replace('.json', '').split('-')
    if len(parts) >= 4:
        date = f"{parts[0]}-{parts[1]}-{parts[2]}"
        match_type = parts[3]
        round_str = '-'.join(parts[4:])
        return date, match_type, round_str
    return None, None, None

def normalize_round(round_str):
    round_str = round_str.replace('第', '').replace('轮', '').replace('（补赛）', '').replace('(补赛)', '').strip()
    try:
        return int(round_str)
    except:
        return None

def main():
    schedule = load_history_schedule()
    csl_matches = get_2025_csl_matches(schedule)
    
    print("=== 2025赛季中超比赛对照表 ===")
    print(f"{'日期':<12} {'schedule轮次':<15} {'文件轮次':<15} {'状态':<8}")
    print("-" * 60)
    
    files = sorted([f for f in os.listdir(HISTORY_2025_DIR) if f.endswith('.json') and '中超' in f])
    
    mismatches = []
    
    for filename in files:
        date, match_type, file_round = parse_filename(filename)
        if date and date in csl_matches:
            schedule_round = csl_matches[date]['round']
            
            schedule_round_num = normalize_round(schedule_round)
            file_round_num = normalize_round(file_round)
            
            if schedule_round_num and file_round_num:
                if schedule_round_num != file_round_num:
                    status = "❌ 不匹配"
                    mismatches.append({
                        'filename': filename,
                        'date': date,
                        'old_round': file_round,
                        'new_round': schedule_round,
                        'old_round_num': file_round_num,
                        'new_round_num': schedule_round_num
                    })
                else:
                    status = "✓"
            else:
                status = "?"
            
            print(f"{date:<12} {schedule_round:<15} {file_round:<15} {status}")
    
    print("\n=== 需要修复的文件 ===")
    for m in mismatches:
        print(f"  {m['filename']}: {m['old_round']} -> {m['new_round']}")
    
    if mismatches:
        confirm = input("\n是否执行修复? (y/n): ")
        if confirm.lower() == 'y':
            for m in mismatches:
                old_path = os.path.join(HISTORY_2025_DIR, m['filename'])
                
                new_filename = m['filename'].replace(
                    f"第{m['old_round_num']}轮",
                    f"第{m['new_round_num']}轮"
                )
                new_path = os.path.join(HISTORY_2025_DIR, new_filename)
                
                with open(old_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if 'match' in data and 'round' in data['match']:
                    data['match']['round'] = m['new_round']
                
                if old_path != new_path:
                    os.rename(old_path, new_path)
                    print(f"  重命名: {m['filename']} -> {new_filename}")
                
                with open(new_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                print(f"  更新内容: {new_filename}")
            
            print("\n修复完成!")
    else:
        print("\n没有需要修复的文件")

if __name__ == '__main__':
    main()
