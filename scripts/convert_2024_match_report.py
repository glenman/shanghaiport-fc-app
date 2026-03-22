# -*- coding: utf-8 -*-
import os
import json
import re

TEAM_TRANSLATIONS = {
    "Shanghai Port": "上海海港",
    "Wuhan Three Towns": "武汉三镇",
    "Chengdu Rongcheng": "成都蓉城",
    "Beijing Guoan": "北京国安",
    "Shanghai Shenhua": "上海申花",
    "Shandong Taishan": "山东泰山",
    "Henan FC": "河南俱乐部酒祖杜康",
    "Tianjin Jinmen Tiger": "天津津门虎",
    "Zhejiang Professional": "浙江队",
    "Changchun Yatai": "长春亚泰",
    "Qingdao Hainiu": "青岛海牛",
    "Dalian Pro": "大连英博海发",
    "Shenzhen Pengcheng": "深圳新鹏城",
    "Meizhou Hakka": "梅州客家",
    "Cangzhou Lions": "沧州雄狮",
    "Nantong Zhiyun": "南通支云",
    "Qingdao West Coast": "青岛西海岸",
    "Sichuan Jiuniu": "四川九牛",
}

def parse_snapshot(snapshot_text):
    lines = snapshot_text.split('\n')
    data = {
        'home_team': None,
        'away_team': None,
        'score': None,
        'halftime_score': None,
        'venue': None,
        'date': None,
        'time': None,
        'attendance': None,
        'referee': None,
        'players': {'home': [], 'away': []},
        'substitutions': [],
        'goals': [],
        'cards': [],
        'stats': {}
    }
    
    current_team = None
    current_section = None
    
    for line in lines:
        line = line.strip()
        
        if 'Shanghai Port' in line or 'Wuhan Three Towns' in line:
            if 'Shanghai Port' in line:
                data['home_team'] = 'Shanghai Port'
                current_team = 'home'
            elif 'Wuhan Three Towns' in line:
                data['away_team'] = 'Wuhan Three Towns'
                current_team = 'away'
        
        if 'Score' in line or 'score' in line:
            score_match = re.search(r'(\d+)\s*-\s*(\d+)', line)
            if score_match:
                data['score'] = f"{score_match.group(1)}-{score_match.group(2)}"
        
        if 'Halftime' in line:
            score_match = re.search(r'(\d+)\s*-\s*(\d+)', line)
            if score_match:
                data['halftime_score'] = f"{score_match.group(1)}-{score_match.group(2)}"
        
        if 'Stadium' in line or 'Venue' in line:
            venue_match = re.search(r'Stadium\s*\[:\]\s*(.+)', line)
            if venue_match:
                data['venue'] = venue_match.group(1).strip()
        
        if 'Attendance' in line:
            att_match = re.search(r'(\d+,?\d*)', line)
            if att_match:
                data['attendance'] = att_match.group(1)
        
        if 'Referee' in line:
            ref_match = re.search(r'Referee\s*\[:\]\s*(.+)', line)
            if ref_match:
                data['referee'] = ref_match.group(1).strip()
    
    return data

def convert_match_report(source_file, target_file):
    with open(source_file, 'r', encoding='utf-8') as f:
        source_data = json.load(f)
    
    match_info = source_data.get('match', {})
    parsed = parse_snapshot(source_data.get('snapshot', ''))
    
    round_num = re.search(r'第(\d+)轮', source_file)
    round_str = round_num.group(0) if round_num else '未知'
    
    home_team_cn = TEAM_TRANSLATIONS.get(match_info.get('homeTeam', ''), match_info.get('homeTeam', ''))
    away_team_cn = TEAM_TRANSLATIONS.get(match_info.get('awayTeam', ''), match_info.get('awayTeam', ''))
    
    result = {
        "match": {
            "id": match_info.get('id', 1),
            "round": round_str,
            "date": match_info.get('date', ''),
            "time": "19:35",
            "homeTeam": home_team_cn,
            "awayTeam": away_team_cn,
            "venue": parsed.get('venue', '未知'),
            "city": "上海" if 'Shanghai' in match_info.get('homeTeam', '') else "未知",
            "result": parsed.get('score', '0-0'),
            "status": "已结束",
            "attendance": parsed.get('attendance', '未知'),
            "referee": parsed.get('referee', '未知'),
            "weather": "未知",
            "competition": match_info.get('competition', '中国足球协会超级联赛'),
            "matchweek": int(round_str.replace('第', '').replace('轮', '')) if round_str != '未知' else 0,
            "season": match_info.get('season', '2024')
        },
        "matchDetails": {
            "stadiumCapacity": "未知",
            "pitchCondition": "良好",
            "temperature": "未知",
            "kickoffTime": "19:35",
            "halftimeScore": parsed.get('halftime_score', '0-0'),
            "fulltimeScore": parsed.get('score', '0-0')
        },
        "officials": {
            "referee": parsed.get('referee', '未知'),
            "assistantReferee1": "未知",
            "assistantReferee2": "未知",
            "fourthOfficial": "未知",
            "VAR": "未知"
        },
        "seasonRecords": {
            "home": {
                "currentPosition": "未知",
                "matchesPlayed": 0,
                "record": "未知",
                "points": 0,
                "goalsFor": 0,
                "goalsAgainst": 0,
                "form": ""
            },
            "away": {
                "currentPosition": "未知",
                "matchesPlayed": 0,
                "record": "未知",
                "points": 0,
                "goalsFor": 0,
                "goalsAgainst": 0,
                "form": ""
            }
        },
        "lineups": {
            "home": {
                "name": home_team_cn,
                "formation": "4-3-3",
                "manager": "未知",
                "captain": "未知",
                "players": [],
                "substitutes": []
            },
            "away": {
                "name": away_team_cn,
                "formation": "4-3-3",
                "manager": "未知",
                "captain": "未知",
                "players": [],
                "substitutes": []
            }
        },
        "detailedPlayerStats": {
            "home": [],
            "away": []
        },
        "matchTimeline": [],
        "tacticalAnalysis": {
            "homeFormation": "4-3-3",
            "awayFormation": "4-3-3",
            "possession": {
                "home": 50,
                "away": 50
            },
            "attackDirection": {
                "home": "未知",
                "away": "未知"
            },
            "defensiveLine": {
                "home": "未知",
                "away": "未知"
            },
            "playingStyle": {
                "home": "未知",
                "away": "未知"
            }
        },
        "statistics": [
            {"name": "控球率", "home": "50%", "away": "50%"},
            {"name": "射门", "home": "0", "away": "0"},
            {"name": "射正", "home": "0", "away": "0"},
            {"name": "射门准确率", "home": "0%", "away": "0%"},
            {"name": "扑救", "home": "0", "away": "0"},
            {"name": "扑救成功率", "home": "0%", "away": "0%"},
            {"name": "犯规", "home": "0", "away": "0"},
            {"name": "角球", "home": "0", "away": "0"},
            {"name": "传中", "home": "0", "away": "0"},
            {"name": "拦截", "home": "0", "away": "0"},
            {"name": "越位", "home": "0", "away": "0"},
            {"name": "黄牌", "home": "0", "away": "0"},
            {"name": "红牌", "home": "0", "away": "0"}
        ],
        "keyMetrics": {
            "expectedGoals": {"home": 0, "away": 0},
            "bigChances": {"home": 0, "away": 0},
            "passAccuracy": {"home": "0%", "away": "0%"},
            "aerialDuelsWon": {"home": "0%", "away": "0%"},
            "successfulDribbles": {"home": 0, "away": 0},
            "keyPasses": {"home": 0, "away": 0}
        },
        "playerRatings": {
            "manOfTheMatch": "未知",
            "homeBestPlayer": "未知",
            "awayBestPlayer": "未知",
            "topPerformers": []
        },
        "headToHead": {
            "totalMatches": 0,
            "homeWins": 0,
            "awayWins": 0,
            "draws": 0,
            "lastMeeting": "未知",
            "trend": "未知"
        },
        "socialMedia": {
            "hashtags": [],
            "fanSentiment": {
                "home": "未知",
                "away": "未知"
            },
            "matchTrending": False
        },
        "summary": f"{home_team_cn}与{away_team_cn}的比赛以{parsed.get('score', '0-0')}结束。数据来源于FBref网站快照，需要手动补充详细信息。",
        "highlights": [],
        "matchAnalysis": {
            "tacticalSummary": "数据来源于FBref网站快照，需要手动补充战术分析。",
            "keyMoments": [],
            "teamPerformance": {
                "home": {
                    "strengths": [],
                    "weaknesses": []
                },
                "away": {
                    "strengths": [],
                    "weaknesses": []
                }
            }
        },
        "postMatchComments": {
            "homeManager": "未知",
            "awayManager": "未知",
            "manOfTheMatchComment": "未知"
        },
        "nextMatches": {
            "home": {
                "opponent": "待定",
                "date": "未知",
                "venue": "未知"
            },
            "away": {
                "opponent": "待定",
                "date": "未知",
                "venue": "未知"
            }
        }
    }
    
    with open(target_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    return result

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    source_dir = os.path.join(base_dir, 'public', 'data', 'history', '2024')
    target_dir = os.path.join(base_dir, 'public', 'data')
    
    print(f"源目录: {source_dir}")
    print(f"目标目录: {target_dir}")
    
    converted_count = 0
    for filename in sorted(os.listdir(source_dir)):
        if filename.endswith('.json'):
            source_path = os.path.join(source_dir, filename)
            target_path = os.path.join(target_dir, filename)
            
            print(f"\n转换文件: {filename}")
            convert_match_report(source_path, target_path)
            converted_count += 1
    
    print(f"\n完成! 共转换了 {converted_count} 个文件")

if __name__ == '__main__':
    main()
