---
name: "match-result-updater"
description: "Updates match results for Shanghai Port FC teams. Invoke when user says 'update match result' or '更新比赛结果' with team name, opponent, and score."
---

# Match Result Updater

This skill automates the process of updating match results for Shanghai Port FC teams (first team and B team), including match report localization and standardization.

## 四大汇总统计文件（比赛更新必达产物）

每次更新**一线队**比赛结果后，以下 4 个汇总统计文件必须全部同步更新（B队比赛不进这 4 个文件，仅更新 schedule_b/current_stats）：

| # | 文件 | 更新脚本 | 更新方式 |
|---|------|---------|---------|
| 1 | `public/data/history_schedule.json` | `sync_history_data.py` | 幂等追加新比赛，自动分配 Mxxxx 编号 |
| 2 | `public/data/goal_details.json` | `sync_history_data.py` | 幂等追加海港方进球（dedupe；乌龙不进；PK/OG 标记） |
| 3 | `public/data/player_history_stats.json` | `update_player_history_stats.py` | 增量累加（update_state.json 记录 processed 防重复） |
| 4 | `public/data/player_appearance_details.json` | `update_player_appearance_details.py` | 增量追加出场明细（matchId 关联；同步年度归档 `history/<年>/`） |

**顺序依赖**：`sync_history_data.py` 必须先跑（分配 matchId），两个增量脚本随后。

**更新后校验**：`python .trae/skills/football-data-audit/scripts/validate_data.py`（硬错误必须为 0；WARN 基线见 football-data-audit SKILL.md）。

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

7. **Sync History Data (留存)**
   - Syncs `team-a` match reports into `goal_details.json` (per-goal records) and `history_schedule.json` (per-match records)
   - Idempotent: dedupes by (date, home, away) for schedule and (date code, player, goal time) for goals
   - Handles penalty shootout results (e.g., `1-1 (点球 4-3)`) correctly

8. **Update Player History Stats (球员历史统计, 增量)**
   - Runs `update_player_history_stats.py`（默认增量模式；`--full` 为全量重算，仅数据修复用）
   - 增量：以当前 `player_history_stats.json` 为基线，只累加「基线日之后且未处理过」的新报告，绝不重算覆盖既有数据
   - 首发 = `lineups.{role}.players[]`；替补出场 = `lineups.{role}.substitutes[]` 中带 `substitutedAt`（或 `minutes>0`）的球员
   - 进球 = `matchTimeline` 中 `type=goal`（非乌龙）与 `type=penalty_goal` 两种事件；门将字段（失球/零封/扑点）记到当场门将

9. **Update Player Appearance Details (球员出场明细, 增量)**
   - Runs `update_player_appearance_details.py`（默认增量模式；`--full` 为全量重建）to append new matches to `player_appearance_details.json` and `history/<年份>/<年份>-出场记录.json`
   - 每条出场记录 `{matchId, status, minutes}`，matchId 关联 `history_schedule.json`（新赛程由 `sync_history_data.py` 自动分配 Mxxxx 编号）
   - 口径与 `update_player_history_stats.py` 一致（ALIAS_MAP：让克劳德->克劳德、维塔尔->马特乌斯·维塔尔、吾米提江->吾米提江.玉苏普；替补分钟按 90-登场时间估算）

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
10. **Sync History Data** - Runs `sync_history_data.py` to sync the match into `goal_details.json` and `history_schedule.json`
11. **Update Player History Stats** - Runs `update_player_history_stats.py` (incremental by default; only new matches after baseline are accumulated)
12. **Update Player Appearance Details** - Runs `update_player_appearance_details.py` (incremental; appends new matches to `player_appearance_details.json` + `history/<年份>/<年份>-出场记录.json`, matchId-linked)

## Files Modified

| File | Description |
|------|-------------|
| `public/data/schedule.json` | First team schedule |
| `public/data/schedule_b.json` | B team schedule |
| `public/data/current_stats.json` | Season statistics |
| `public/data/YYYY-MM-DD-赛事类型-第X轮.json` | Match report data |
| `public/data/goal_details.json` | Per-goal history records (synced) |
| `public/data/history_schedule.json` | Per-match history records (synced) |
| `public/data/player_history_stats.json` | Career stats (12 fields full-recalculated from Excel baseline + team-a) |
| `public/data/player_appearance_details.json` | Player appearance details (per-match matchId/status/minutes, current season rebuilt from team-a) |
| `public/data/history/<年份>/<年份>-出场记录.json` | Yearly appearance record file (lineup/substitutes/substitutions, with matchId) |

## Supporting Scripts

| Script | Description |
|--------|-------------|
| `scripts/normalize_match_report.py` | Match report localization and player name standardization |
| `scripts/update_schedule_details_v2.py` | Extracts match details from match reports |
| `scripts/update_stats.py` | Updates season statistics (supports incremental and full update) |
| `scripts/sync_history_data.py` | Syncs `team-a` reports into `goal_details.json` and `history_schedule.json` (idempotent) |
| `scripts/update_player_history_stats.py` | Full-recalculates `player_history_stats.json` (all 12 fields from Excel baseline + team-a, idempotent) |
| `scripts/update_player_appearance_details.py` | Rebuilds current-season nodes in `player_appearance_details.json` + yearly `history/<年份>/<年份>-出场记录.json` from team-a reports (idempotent, matchId-linked) |

## Player Name Standardization

### Supported Alias Mappings

| Alias | Official Name |
|-------|--------------|
| 莱奥 | 莱昂纳多 |
| 莱昂纳多·席尔瓦 | 莱昂纳多 |
| 布朗宁 | 蒋光太 |
| Tyias Browning | 蒋光太 |
| 马修·奥尔 | 安永佳 |
| Matthew Orr | 安永佳 |
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
- `update_player_history_stats.py` **默认增量模式**：以当前文件为基线只累加新比赛（基线留存于 `datafile/baseline-<日期>/`）；`--full` 全量重算仅数据修复用，且会自动恢复 BIRTH_FIX 生日修正与 short_name
- **更新状态记录 `scripts/update_state.json`**：记录 `baselineDate`（基线日，基线日及之前的比赛已冻结不再重算）、`lastMatch`（最新已结束比赛）、各脚本最后运行时间与 `processed` 已处理报告清单（防止增量重复累计）。日常更新前先查看该文件即可判断是否已有新比赛需要处理

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
10. Run `sync_history_data.py` to sync the match into `goal_details.json` and `history_schedule.json`
11. Run `update_player_history_stats.py` to full-recalculate `player_history_stats.json` (all 12 fields)
12. Run `update_player_appearance_details.py` to rebuild the current-season appearance details (`player_appearance_details.json` + yearly file, matchId-linked)

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