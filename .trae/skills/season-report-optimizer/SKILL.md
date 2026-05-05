# Season Report Optimizer

这个Skill用于自动处理历史赛季赛事报告的优化工作，包括队名修复、球员汉化、文件名修正等。

## Features

- ✅ 基础信息更新：从 `history_schedule.json` 获取并更新主客队名称、主教练、比赛城市、比赛场地、主裁判、观众人数
- ✅ 问题诊断：自动检查Opponent、未汉化球员等问题
- ✅ 队名修复：根据赛程CSV自动更新主客队名称
- ✅ 球员姓名汉化：基于大名单CSV文件进行球员姓名汉化（必要步骤）
- ✅ 其他内容汉化：主教练、场地名称汉化
- ✅ 文件名修复：根据比赛日期修正轮次
- ✅ 验证确认：自动验证优化结果

## Workflow

1. **更新基础信息** - 使用 `update_XXXX_reports.py` 从 `history_schedule.json` 获取：
   - 主队/客队名称 (home_team / away_team)
   - 主教练 (home_coach / away_coach)
   - 比赛场地 (venue)
   - 比赛城市 (city) - 新增字段
   - 主裁判 (referee)
   - 观众人数 (attendance)

2. **诊断问题** - 检查JSON文件存在的问题

3. **执行优化** - 根据问题执行相应脚本：
   - 文件名和轮次修复（如需要）
   - 队名修复
   - **球员姓名汉化**（基于大名单CSV，必要步骤）
   - 其他内容汉化（主教练、场地等）
   - 换人信息修复（如需要）

4. **验证结果** - 确认优化效果

## Usage

```
# 优化指定赛季（自动执行完整流程）
优化2017赛季赛事报告

# 优化指定赛季
优化2019赛季赛事报告

# 仅更新基础信息（从history_schedule.json）
更新2020赛季基础信息

# 仅诊断问题
检查2021赛季有哪些问题

# 指定特定步骤
修复2022赛季的队名
```

## Updated Fields

从 `history_schedule.json` 更新的字段：

| JSON Path | Source Field | Description |
|-----------|-------------|-------------|
| `teams.home.name` | home_team | 主队名称 |
| `teams.away.name` | away_team | 客队名称 |
| `teams.home.coach` | home_coach | 主队主教练 |
| `teams.away.coach` | away_coach | 客队主教练 |
| `match_info.venue.name` | venue | 比赛场地 |
| `match_info.venue.city` | city | 比赛城市（新增） |
| `match_info.venue.attendance` | attendance | 观众人数 |
| `match_info.referee.main` | referee | 主裁判 |

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/update_XXXX_reports.py` | 从history_schedule.json更新基础信息 |
| `scripts/fix_XXXX_filenames_and_rounds.py` | 修复文件名和轮次 |
| `scripts/fix_XXXX_team_names.py` | 修复队名 |
| `scripts/optimize_XXXX_reports.py` | 内容汉化 |
| `scripts/fix_XXXX_substitutions.py` | 换人信息修复 |

## Requirements

- 历史比赛数据：`public/data/history_schedule.json`
- 对应赛季的球员大名单：`datafile/上海海港XXXX一线队大名单.csv`
- 对应赛季的赛程：`datafile/上海海港XXXX一线队中超赛程.csv`
- JSON文件：`public/data/history/XXXX/`

## Date Matching

日期匹配逻辑：
- 优先直接匹配文件名日期与 `history_schedule.json` 中的日期
- 如未匹配，尝试 ±1 天偏移匹配（某些赛季存在1天误差）

---
Created: 2026-05-04
Version: 2.1