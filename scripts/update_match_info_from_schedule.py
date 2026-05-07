#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 history_schedule.json 更新赛事报告信息
功能：根据比赛日期匹配，更新主教练、主裁判、场地、城市、观众人数等信息
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

def load_schedule_data(schedule_path: str) -> Dict[str, dict]:
    """加载赛程数据，建立日期到比赛信息的映射"""
    with open(schedule_path, 'r', encoding='utf-8') as f:
        schedule_list = json.load(f)
    
    # 建立日期到比赛信息的映射（一个日期可能有多场比赛）
    schedule_map = {}
    for match in schedule_list:
        date = match.get('date', '')
        if date:
            if date not in schedule_map:
                schedule_map[date] = []
            schedule_map[date].append(match)
    
    print(f"已加载 {len(schedule_list)} 条赛程记录")
    return schedule_map

def find_match_info(schedule_map: Dict[str, list], match_date: str, home_team: str, away_team: str) -> Optional[dict]:
    """根据日期和队名查找匹配的比赛信息"""
    if match_date not in schedule_map:
        # 尝试前后一天的日期
        import datetime
        try:
            date_obj = datetime.datetime.strptime(match_date, '%Y-%m-%d')
            for offset in [-1, 1]:
                alt_date = (date_obj + datetime.timedelta(days=offset)).strftime('%Y-%m-%d')
                if alt_date in schedule_map:
                    print(f"  日期 {match_date} 未找到，尝试 {alt_date}")
                    return find_match_info(schedule_map, alt_date, home_team, away_team)
        except:
            pass
        return None
    
    # 如果同一天有多场比赛，根据队名匹配
    matches = schedule_map[match_date]
    if len(matches) == 1:
        return matches[0]
    
    # 尝试根据队名匹配
    for match in matches:
        s_home = match.get('home_team', '').lower()
        s_away = match.get('away_team', '').lower()
        h_home = home_team.lower() if home_team else ''
        h_away = away_team.lower() if away_team else ''
        
        # 检查队名是否匹配（双向匹配）
        if (s_home in h_home or h_home in s_home) and (s_away in h_away or h_away in s_away):
            return match
        if (s_away in h_home or h_home in s_away) and (s_home in h_away or h_away in s_home):
            return match
    
    return matches[0]  # 默认返回第一个

def update_match_report(json_path: Path, schedule_map: Dict[str, list]) -> bool:
    """更新单个赛事报告"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 获取当前比赛信息
        match_info = data.get('match_info', {})
        teams = data.get('teams', {})
        home_team = teams.get('home', {}).get('name', '')
        away_team = teams.get('away', {}).get('name', '')
        match_date = match_info.get('date', '')
        
        if not match_date:
            print(f"✗ {json_path.name}: 缺少比赛日期")
            return False
        
        # 查找匹配的赛程信息
        schedule_match = find_match_info(schedule_map, match_date, home_team, away_team)
        
        if not schedule_match:
            print(f"✗ {json_path.name}: 未找到匹配的赛程信息 ({match_date})")
            return False
        
        # 更新场地信息
        venue = match_info.get('venue', {})
        schedule_venue = schedule_match.get('venue', '')
        schedule_city = schedule_match.get('city', '')
        
        if schedule_venue:
            venue['name'] = schedule_venue
            match_info['venue'] = venue
        
        if schedule_city:
            venue['city'] = schedule_city
            match_info['venue'] = venue
        
        # 更新裁判信息
        referee = match_info.get('referee', {})
        schedule_referee = schedule_match.get('referee', '')
        if schedule_referee:
            # 清理裁判姓名中的地区信息 (如 "莫伟聪(广州)")
            clean_referee = schedule_referee.split('(')[0].strip()
            referee['main'] = clean_referee
            match_info['referee'] = referee
        
        # 更新观众人数
        attendance = schedule_match.get('attendance', '')
        # 处理可能的类型问题
        try:
            attendance_int = int(attendance)
            if attendance_int > 0:
                venue['attendance'] = attendance_int
                match_info['venue'] = venue
        except (ValueError, TypeError):
            pass
        
        # 更新主教练信息
        home_coach = schedule_match.get('home_coach', '')
        away_coach = schedule_match.get('away_coach', '')
        
        if home_coach and 'home' in teams:
            teams['home']['coach'] = home_coach
        
        if away_coach and 'away' in teams:
            teams['away']['coach'] = away_coach
        
        # 写回文件
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ {json_path.name}: 已更新场地、裁判、主教练信息")
        return True
    
    except Exception as e:
        print(f"✗ {json_path.name}: {str(e)}")
        return False

def process_season(season: str, schedule_map: Dict[str, list]) -> int:
    """处理单个赛季"""
    json_dir = Path(f"public/data/history/{season}")
    if not json_dir.exists():
        print(f"跳过 {season} 赛季: 目录不存在")
        return 0
    
    json_files = sorted(json_dir.glob("*.json"))
    if not json_files:
        print(f"跳过 {season} 赛季: 没有JSON文件")
        return 0
    
    print(f"\n=== 处理 {season} 赛季 ===")
    print(f"找到 {len(json_files)} 个比赛文件")
    
    success_count = 0
    for json_file in json_files:
        if update_match_report(json_file, schedule_map):
            success_count += 1
    
    print(f"完成: {success_count}/{len(json_files)} 个文件已更新")
    return success_count

def main():
    """主函数"""
    print("=" * 60)
    print("从 history_schedule.json 更新赛事报告信息")
    print("功能：更新主教练、主裁判、场地、城市、观众人数")
    print("=" * 60)
    
    # 加载赛程数据
    schedule_path = "public/data/history_schedule.json"
    schedule_map = load_schedule_data(schedule_path)
    
    if not schedule_map:
        print("错误: 未能加载赛程数据")
        return
    
    # 处理所有赛季
    seasons = ["2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023"]
    
    total_updated = 0
    for season in seasons:
        total_updated += process_season(season, schedule_map)
    
    print(f"\n=== 总计 ===")
    print(f"已更新 {total_updated} 个赛事报告文件")

if __name__ == "__main__":
    main()