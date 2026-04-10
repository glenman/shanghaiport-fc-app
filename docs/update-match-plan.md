# 更新本赛季比赛记录操作指南

## 概述
本指南用于更新本赛季（2026赛季）的比赛记录，包括更新赛果比分和添加赛事报告链接。

## 前与其他操作的区别

### 不需要做的操作
- ❌ **不要更新历史比赛** (`history_schedule.json`)
- ❌ **不要更新进球助攻榜** (`goal_history.json`)
- ❌ **不要更新其他赛季的数据**

### 需要做的操作
- ✅ **更新当前赛季的赛果比分** (`schedule.json`)
- ✅ **添加赛事报告链接** (`match_report.json`)
- ✅ **更新海港B队的赛果比分** (`schedule_b.json`)
- ✅ **为海港B队添加赛事报告链接**

## 操作步骤

### 步骤1：更新赛果比分

**目标文件**：`data/schedule.json`

**操作说明**：
1. 找到对应轮次的比赛记录
2. 更新 `result` 字段为实际比分（如 "4-1"）
3. 更新 `status` 字段为 "已结束"

**示例**：
```json
{
  "id": 2,
  "round": "第2轮",
  "date": "2026-03-15",
  "time": "19:00",
  "homeTeam": "上海海港",
  "awayTeam": "青岛西海岸",
  "venue": "上海体育场",
  "city": "上海",
  "result": "4-1",        // 更新为实际比分
  "status": "已结束"      // 更新为已结束
}
```

### 步骤2：添加赛事报告链接

**目标文件**：`data/match_report.json`

**操作说明**：
1. 打开 `data/match_report.json`
2. 添加新的赛事报告条目，指向match-report.html
3. 该条目包含基本信息（id, matchId, round, date, homeTeam, awayTeam, result, reportType, reportTitle）
4. 不需要添加具体的 `reportUrl`，因为match-report.html是通用模板

**示例**：
```json
{
  "id": 2.1,                    // 比赛ID + 小数（如2.1表示第2轮第1个报告）
  "matchId": 2,                  // 对应的比赛ID
  "round": "第2轮",             // 轮次
  "date": "2026-03-15",         // 比赛日期
  "homeTeam": "上海海港",         // 主队
  "awayTeam": "青岛西海岸",       // 客队
  "result": "4-1",              // 比分
  "reportType": "中超",          // 赛事类型
  "reportTitle": "上海海港4-1青岛西海岸 赛后报告"  // 报告标题
  "summary": "比赛总结",        // 比赛总结
  "keyPoints": [                // 关键点
    "关键点1",
    "关键点2"
  ]
}
```

**注意事项**：
- `id` 字段使用小数来区分同一轮次的多个报告（如2.1, 2.2等）
- 不需要添加 `reportUrl` 字段，因为match-report.html是通用模板
- match-report.html通过URL参数动态读取对应的比赛数据文件
- URL参数格式：`?date=2026-03-15&type=中超&round=2`
- 对应的比赛数据文件必须已存在：`data/{日期}-{赛事类型}-{轮次}.json`

## 完整操作流程

### 场景：更新第2轮比赛记录

1. **准备比赛数据文件**
   - 确保 `data/2026-03-15-中超-第2轮.json` 文件已生成并包含完整的比赛信息

2. **更新赛果比分**
   - 打开 `data/schedule.json`
   - 找到第2轮的比赛记录（id: 2）
   - 更新 `result` 为 "4-1"
   - 更新 `status` 为 "已结束"

3. **添加赛事报告链接**
   - 打开 `data/match_report.json`
   - 添加新的赛事报告条目，指向match-report.html
   - 该条目包含基本信息（id, matchId, round, date, homeTeam, awayTeam, result, reportType, reportTitle）
   - 不需要添加具体的 `reportUrl`，因为match-report.html是通用模板

## 文件结构

```
data/
├── schedule.json                    # 赛程文件（需要更新）
├── 2026-03-15-中超-第2轮.json     # 比赛详细数据（已生成）
└── match_report.json               # 赛事报告索引（需要添加）
```

## 验证清单

完成操作后，请验证以下内容：

- [ ] `schedule.json` 中第2轮的 `result` 已更新为 "4-1"
- [ ] `schedule.json` 中第2轮的 `status` 已更新为 "已结束"
- [ ] `match_report.json` 中已添加新的赛事报告条目
- [ ] 网站上可以正常显示更新后的赛果

## 常见问题

### Q1: 如何确定比赛ID？
A: 比赛ID对应 `schedule.json` 中的 `id` 字段，从1开始递增。

### Q2: match-report.html如何读取数据？
A: match-report.html是通用模板，通过URL参数动态读取对应的比赛数据文件：
   - URL参数格式：`?date=2026-03-15&type=中超&round=2`
   - 会自动加载 `data/2026-03-15-中超-第2轮.json` 文件

### Q3: 需要更新其他文件吗？
A: 不需要。只更新 `schedule.json` 和 `match_report.json`，不要修改历史比赛和进球助攻榜。

### Q4: 如何处理同一轮次的多个报告？
A: 使用小数来区分，如第2轮的第一个报告ID为 `2.1`，第二个为 `2.2`，以此类推。

## 总结

本指南的核心原则是：
1. **只更新当前赛季** - 不影响历史数据
2. **最小化修改** - 只修改必要的赛果和报告链接
3. **保持数据一致性** - 确保所有相关文件的数据保持同步
