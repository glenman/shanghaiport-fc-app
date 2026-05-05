---
name: "match-result-updater"
description: "Updates match results for Shanghai Port FC teams. Invoke when user says 'update match result' or '更新比赛结果' with team name, opponent, and score."
---

# Match Result Updater

This skill automates the process of updating match results for Shanghai Port FC teams (first team and B team).

## Features

1. Update Schedule Files
   - Updates schedule.json for first team matches
   - Updates schedule_b.json for B team matches
   - Sets result and status fields

2. Verify Match Report
   - Checks corresponding JSON data file exists
   - Validates player names against players.json
   - Verifies Chinese localization completeness

3. Update Schedule Details
   - Extracts referee from match report
   - Extracts home and away coaches
   - Extracts attendance numbers
   - Extracts scorers from highlights/matchTimeline
   - Adds special markers for penalty goals (PK) and own goals (OG)

4. Update Statistics
   - Runs incremental update by default
   - Supports full update when needed

## Usage

### Trigger Phrases

- "更新XX队比赛结果"
- "update match result for XX team"
- "更新上海海港比赛结果"

### Required Information

1. Team: "一线队" or "B队"
2. Home Team: Full team name
3. Away Team: Full team name  
4. Result: Score in "X-Y" format (home-away)

### Example Inputs

更新一线队比赛结果，上海海港vs武汉三镇 4:0

更新B队比赛结果，山西崇德荣海vs上海海港富盛经开 0:3

## Workflow

1. Identify Team - Determines whether to update first team or B team
2. Locate Match - Searches schedule file for matching teams
3. Update Schedule - Sets result and status fields
4. Validate Match Report - Checks JSON file and player names
5. Extract Schedule Details - Extracts referee, coaches, attendance, and scorers
6. Add Special Markers - Adds (PK) for penalty goals and (OG) for own goals based on goal_type field
7. Verify Scorers Count - Ensures number of scorers matches the score
8. Update Statistics - Runs incremental update by default

## Files Modified

| File | Description |
|------|-------------|
| public/data/schedule.json | First team schedule |
| public/data/schedule_b.json | B team schedule |
| public/data/current_stats.json | Season statistics |

## Supporting Scripts

| Script | Description |
|--------|-------------|
| scripts/update_schedule_details_v2.py | Extracts match details from match reports |
| scripts/update_scorers_v3.py | Updates scorers information |
| scripts/update_stats.py | Updates season statistics |

## Validation Checks

1. Team Names must match existing names
2. Score Format must be "X-Y"
3. Match must exist in schedule
4. JSON File must exist

## Notes

- Reports player name discrepancies if found
- Uses incremental update for performance
- Prompts for confirmation before changes

## Example Workflow

User: 更新一线队比赛结果，上海海港vs武汉三镇 4:0

Skill Actions:
1. Identify team: 一线队
2. Find match in schedule.json
3. Update result to "4-0", status to "已结束"
4. Check match report JSON
5. Validate player names against players.json
6. Extract details from match report:
   - Referee: 艾坤
   - Home Coach: 凯文·穆斯卡特
   - Away Coach: 待定
   - Attendance: 20033
   - Scorers: 魏震, 安佩姆, 蒋光太, 刘祝润
7. Verify scorers count matches score (4 goals = 4 scorers)
8. Update schedule.json with extracted details
9. Run incremental stats update

## Special Goal Markers

When extracting scorers, check the `goal_type` field in match report:

| goal_type | Marker | Example |
|-----------|--------|---------|
| penalty_goal / penalty | (PK) | 温钧翔(PK) |
| own_goal | (OG) | 邓嘉俊(OG) |

Example with special markers:
```json
{
  "scorers": {
    "home": ["武磊", "武磊(PK)"],
    "away": ["克雷桑", "邓嘉俊(OG)"]
  }
}
```