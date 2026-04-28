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

3. Update Statistics
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
5. Update Statistics - Runs incremental update by default

## Files Modified

| File | Description |
|------|-------------|
| public/data/schedule.json | First team schedule |
| public/data/schedule_b.json | B team schedule |
| public/data/current_stats.json | Season statistics |

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
6. Run incremental stats update