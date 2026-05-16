---
name: "match-result-updater"
description: "Updates match results for Shanghai Port FC teams. Invoke when user says 'update match result' or '更新比赛结果' with team name, opponent, and score."
---

# Match Result Updater

This skill automates the process of updating match results for Shanghai Port FC teams (first team and B team), including match report localization and standardization.

## Features

1. **Update Schedule Files**
   - Updates `schedule.json` for first team matches
   - Updates `schedule_b.json` for B team matches
   - Sets result and status fields

2. **Match Report Validation**
   - Checks corresponding JSON data file exists
   - Validates player names against official player lists
   - Verifies Chinese localization completeness

3. **Player Name Standardization**
   - Uses `players.json` for first team player names
   - Uses `players_b.json` for B team player names
   - Handles alias mapping (e.g., 莱奥 → 莱昂纳多, 布朗宁 → 蒋光太)
   - Processes starting players, substitutes, substitutions, and match events

4. **Match Report Localization**
   - Venue name localization
   - Competition name standardization
   - Timeline description standardization
   - Player name standardization in all sections

5. **Update Schedule Details**
   - Extracts referee from match report (`officials.referee`)
   - Extracts home and away coaches (`lineups.home.manager`, `lineups.away.manager`)
   - Extracts attendance numbers (`match.attendance`)
   - Extracts scorers from `highlights` or `matchTimeline`
   - Adds special markers for penalty goals (PK) and own goals (OG)

6. **Update Statistics**
   - Runs incremental update by default (based on file date prefix)
   - Supports full update when needed
   - Handles penalty goal marking in statistics

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

1. **Identify Team** - Determines whether to update first team or B team
2. **Locate Match** - Searches schedule file for matching teams
3. **Update Schedule** - Sets result and status fields
4. **Validate Match Report** - Checks JSON file exists
5. **Match Report Localization & Standardization** - Runs `normalize_match_report.py`
   - Player name standardization
   - Venue name localization
   - Competition name standardization
   - Timeline player name updates
6. **Extract Schedule Details** - Extracts referee, coaches, attendance, and scorers
7. **Add Special Markers** - Adds (PK) for penalty goals and (OG) for own goals based on `goal_type` field
8. **Verify Scorers Count** - Ensures number of scorers matches the score
9. **Update Statistics** - Runs incremental update by default

## Files Modified

| File | Description |
|------|-------------|
| `public/data/schedule.json` | First team schedule |
| `public/data/schedule_b.json` | B team schedule |
| `public/data/current_stats.json` | Season statistics |
| `public/data/YYYY-MM-DD-赛事类型-第X轮.json` | Match report data |

## Supporting Scripts

| Script | Description |
|--------|-------------|
| `scripts/normalize_match_report.py` | Match report localization and player name standardization |
| `scripts/update_schedule_details_v2.py` | Extracts match details from match reports |
| `scripts/update_stats.py` | Updates season statistics (supports incremental and full update) |

## Player Name Standardization

### Supported Alias Mappings

| Alias | Official Name |
|-------|--------------|
| 莱奥 | 莱昂纳多 |
| 莱昂纳多·席尔瓦 | 莱昂纳多 |
| 布朗宁 | 蒋光太 |
| Tyias Browning | 蒋光太 |
| 马修·奥尔 | 让克劳德 |
| Matthew Orr | 让克劳德 |
| 乌米提江·玉素甫 | 吾米提江 |
| 乌米提江 | 吾米提江 |

### Processing Fields

- `lineups.home.players[].name`
- `lineups.home.substitutes[].name` / `lineups.home.bench[].name`
- `lineups.away.players[].name`
- `lineups.away.substitutes[].name` / `lineups.away.bench[].name`
- `matchTimeline[].player`
- `matchTimeline[].playerIn` / `matchTimeline[].playerOut`
- `matchTimeline[].player2`

## Validation Checks

1. Team Names must match existing names in schedule files
2. Score Format must be "X-Y"
3. Match must exist in schedule file
4. JSON File must exist for the match report
5. Player names must match official player lists

## Notes

- Reports player name discrepancies if found
- Uses incremental update for performance (processes files with date prefix later than last update)
- Automatically handles penalty goals and own goals with special markers
- Supports both camelCase (`playerIn`, `playerOut`) and snake_case (`player_in`, `player_out`) field formats
- Prompts for confirmation before changes

## Example Workflow

User: 更新一线队比赛结果，上海海港vs武汉三镇 4:0

Skill Actions:
1. Identify team: 一线队
2. Find match in schedule.json
3. Update result to "4-0", status to "已结束"
4. Check match report JSON file exists
5. Run match report normalization:
   - Standardize player names against players.json
   - Localize venue name
   - Update matchTimeline player names
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
| `penalty_goal` / `penalty` | (PK) | 温钧翔(PK) |
| `own_goal` | (OG) | 邓嘉俊(OG) |

Example with special markers:
```json
{
  "scorers": {
    "home": ["武磊", "武磊(PK)"],
    "away": ["克雷桑", "邓嘉俊(OG)"]
  }
}
```

## Key Data Sources

| Data Source | Path | Description |
|-------------|------|-------------|
| First Team Players | `public/data/players.json` | Official first team player list |
| B Team Players | `public/data/players_b.json` | Official B team player list |
| First Team Schedule | `public/data/schedule.json` | First team match schedule |
| B Team Schedule | `public/data/schedule_b.json` | B team match schedule |
| Match Reports | `public/data/YYYY-MM-DD-*.json` | Individual match reports |