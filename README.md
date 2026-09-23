# 上海海港足球俱乐部数据查询应用

上海海港足球俱乐部数据查询平台，基于 Vite + React 实现的单页应用，提供球队当前赛季赛程、球员信息、参赛统计、历史赛季成绩以及进球助攻汇总等数据查询功能。支持移动端响应式展示。

## 功能特性

应用侧边栏提供 **8 大功能模块**：

### 👥 当前球员信息
- 一线队（中超）与 B 队（中乙）球员名单
- 按姓名搜索、按位置筛选
- 展示球衣号码、年龄、国籍、身高、体重等资料

### ⚽ 当前球队赛程
- 一线队赛程（中超 / 足协杯 / 亚冠 / 超级杯）与 B 队赛程（中乙）
- 赛程筛选（全部 / 未赛 / 已赛 / 胜 / 平 / 负）与搜索
- 点球大战比分单独换行展示，避免撑宽列

### 📈 当季数据统计
- 一线队与 B 队战绩总览（场次、胜平负、进失球、积分）
- 进球榜 / 助攻榜 / 黄牌榜 / 红牌榜（可点击查看单场明细）
- 按比赛类型分类展示（中超 / 杯赛 / 中乙）

### 📋 参赛统计查询
> 前身「球员数据统计」，现为「参赛统计查询」，支持 **球员查询** 与 **主教练查询** 两种模式。
- **球员查询**：输入球员姓名，查看其历史参赛统计（出场、首发、替补、分钟、进球、点球、助攻、红黄牌、失球、零封、扑点），并按赛事类型（中乙/中甲/中超/足协杯/亚冠/超级杯）分类展示；门将专属字段按需显示
- **主教练查询**：输入主教练姓名，基于 `history_schedule.json` 前端聚合执教记录，展示执教赛季（首尾年份）、场次、胜平负、进失球、胜率及逐场执教明细
- 外籍教练使用简称展示（如「穆斯卡特」），悬停显示全名，简称映射配置于 `short_names.json`

### 🏆 历史赛季排名
- 联赛各赛季成绩总览（排名、场次、胜平负、进失球、积分、备注）
- **赛季成绩走向折线图**（SVG）：标注冠季军、亚冠区（前 4）、保级线
- **杯赛成绩汇总**：足协杯、亚冠、超级杯各赛季最终成绩汇总（基于 `seasons.json`）
- 支持按赛季、赛事类型、排名 / 最终成绩、备注搜索筛选联赛表与杯赛表

### 📊 进球助攻汇总
- 按赛季切换、按进球 / 助攻切换
- 球员进球 / 助攻榜，按赛事类型细分（中超 / 足协杯 / 超级杯 / 亚冠）及合计

### 📅 历史比赛统计
- 历史所有比赛记录（2015 至今）按赛季折叠浏览
- **历史交锋查询**：选择对手球队，展示对阵胜平负、进失球、净胜、主客场战绩及逐场交锋记录
- 每场比赛可跳转查看赛事报告（`history-match-report.html`）

### 📝 赛事报告
- 详细的比赛分析
- 球员评分
- 比赛亮点和关键时刻
- 乌龙球(OG)标识显示
- 详细数据分析：控球率、预期进球(xG/xGOT)、射门、进攻、传球、对抗、防守、门将、定位球

## 技术栈

- **前端框架**: React 17 + TypeScript
- **构建工具**: Vite
- **样式**: 自定义 CSS（`App.css` / `index.css`，含移动端 ≤768px 响应式）
- **数据格式**: JSON（前端 `fetch` 加载）
- **图表**: SVG（自绘赛季成绩走势图）
- **路由/SPA**: React 组件切换（侧边栏菜单）

## 快速开始

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run dev
```

访问 http://localhost:5173/shanghaiport-fc-app/

### 生产构建

```bash
npm run build
```

### 预览构建结果

```bash
npm run preview
```

## 项目结构

```
shanghaiport-fc-app/
├── public/
│   ├── data/
│   │   ├── team-a/                     # 一线队当前赛季比赛数据
│   │   │   ├── YYYY-MM-DD-赛事-第X轮.json      # 比赛报告
│   │   │   └── YYYY-MM-DD-赛事-第X轮-MO.json   # 赛事统计详情（MO=Match Overview）
│   │   ├── team-b/                     # B队当前赛季比赛数据
│   │   ├── history/                    # 历史逐场比赛报告（2015-2025，按年分目录）
│   │   ├── schedule.json               # 一线队当前赛季赛程
│   │   ├── schedule_b.json             # B队当前赛季赛程
│   │   ├── players.json                # 一线队球员名单
│   │   ├── players_b.json              # B队球员名单
│   │   ├── current_stats.json          # 当季数据统计（进球/助攻/红黄牌）
│   │   ├── seasons.json                # 历史赛季记录（联赛 + 杯赛成绩汇总）
│   │   ├── history_schedule.json       # 历史逐场比赛记录（2015 至今，含主客场教练）
│   │   ├── player_history_stats.json   # 球员历史参赛统计
│   │   ├── goal_details.json           # 逐场进球/助攻明细
│   │   ├── short_names.json            # 外籍教练/球员简称映射表
│   │   └── competitions.json           # 比赛类型映射
│   ├── match-overview-stats.html       # 赛事统计详情页面
│   ├── match-report.html               # B队赛事报告模板
│   ├── match-report-v2.html            # 一线队赛事报告模板
│   ├── history-match-report.html       # 历史赛事报告页面
│   └── index.html                      # 主页面
├── src/
│   ├── components/                     # React组件
│   │   ├── Players.tsx                 # 当前球员信息组件
│   │   ├── Schedule.tsx                # 当前球队赛程组件
│   │   ├── CurrentStats.tsx            # 当季数据统计组件
│   │   ├── PlayerStats.tsx             # 参赛统计查询组件（球员 + 主教练）
│   │   ├── Seasons.tsx                 # 历史赛季排名组件（联赛 + 杯赛汇总）
│   │   ├── Statistics.tsx              # 进球助攻汇总组件
│   │   └── History.tsx                 # 历史比赛统计组件（含历史交锋）
│   ├── App.tsx                         # 主应用组件（侧边栏菜单）
│   └── main.tsx                        # 入口文件
├── datafile/                           # 源数据（CSV / XLSX，如历史比分、球员汇总、主教练表）
├── docs/                               # 项目文档
└── package.json
```

## 数据更新

### 更新比赛结果

使用 match-result-updater 技能或手动更新：

```bash
# 更新赛程文件
# - 一线队: public/data/schedule.json
# - B队: public/data/schedule_b.json

# 更新数据统计（增量更新）
python scripts/update_stats.py --incremental

# 更新数据统计（全量更新）
python scripts/update_stats.py --full
```

### 比赛类型说明

比赛类型通过 `competitions.json` 统一管理：

| 比赛类型 | 全称 | 简称 | 类型标识 | 参赛球队 |
|---------|------|------|---------|---------|
| 中超 | 中国足球协会超级联赛 | 中超 | CSL | 一线队 |
| 杯赛 | 中国足球协会杯 | 杯赛 | CFA | 一线队 |
| 亚冠 | 亚足联冠军精英联赛 | 亚冠 | ACLE | 一线队 |
| 中乙 | 中国足球协会乙级联赛 | 中乙 | C2L | B队 |

### 统计数据说明

当季数据统计支持按比赛类型分组显示：
- 一线队：中超联赛战绩 + 杯赛战绩 + 亚冠战绩（分开统计）
- B队：中乙联赛战绩

统计数据包含：
- 进球榜（Top Scorers）
- 助攻榜（Top Assists）
- 黄牌榜（Yellow Cards）
- 红牌榜（Red Cards）

## 文件说明

| 文件 | 说明 |
|------|------|
| public/data/schedule.json | 一线队当前赛季赛程 |
| public/data/schedule_b.json | B队当前赛季赛程 |
| public/data/players.json | 一线队球员名单 |
| public/data/players_b.json | B队球员名单 |
| public/data/current_stats.json | 当季数据统计（按比赛类型分组） |
| public/data/seasons.json | 历史赛季记录（联赛成绩 + 足协杯/亚冠/超级杯杯赛成绩汇总） |
| public/data/history_schedule.json | 历史逐场比赛记录（含主客场教练，2015 至今） |
| public/data/player_history_stats.json | 球员历史参赛统计（供参赛统计查询使用） |
| public/data/goal_details.json | 逐场进球/助攻明细（供进球助攻汇总使用） |
| public/data/short_names.json | 外籍教练/球员简称映射表 |
| public/data/competitions.json | 比赛类型映射配置 |
| public/data/team-a/YYYY-MM-DD-赛事-第X轮.json | 一线队单场比赛报告 |
| public/data/team-a/YYYY-MM-DD-赛事-第X轮-MO.json | 一线队赛事统计详情（MO=Match Overview） |
| public/data/team-b/YYYY-MM-DD-赛事-第X轮.json | B队单场比赛报告 |
| public/data/history/YYYY/ | 历史逐场比赛报告（2015-2025，按年份分目录） |
| public/match-overview-stats.html | 赛事统计详情页面 |
| public/history-match-report.html | 历史赛事报告页面 |

### 数据来源说明

| 文件类型 | 数据来源 |
|---------|---------|
| 标准赛事报告（*.json） | FBref (https://fbref.com/) |
| 赛事统计详情（*-MO.json） | SofaScore (https://www.sofascore.com/) + Flashscore (https://www.flashscore.com/) |

### 统计数据字段说明

**current_stats.json 结构**:
```json
{
  "first-team": {
    "competitions": {
      "中国足球协会超级联赛": {
        "matchesPlayed": 15,
        "record": "4胜5平6负",
        "goalsFor": 25,
        "goalsAgainst": 22,
        "points": 17,
        "topScorers": [...],
        "topAssists": [...],
        "yellowCards": [...],
        "redCards": [...]
      }
    }
  },
  "team-b": {
    "competitions": {
      "中国足球协会乙级联赛": {...}
    }
  }
}
```

**match_overview 统计维度**:
- `possession`: 控球率
- `expected_goals`: 预期进球(xG)
- `xgot`: 射正预期进球(xGOT)
- `shots`: 射门统计（总射门、射正、射偏、被封堵）
- `attack`: 进攻统计（进攻三区进入次数、危险进攻、界外球）
- `passing`: 传球统计（传球总数、成功率）
- `duels`: 对抗统计（总对抗、成功率）
- `defense`: 防守统计（拦截、解围、铲抢）
- `goalkeeper`: 门将统计（扑救、出击、高空球）
- `set_pieces`: 定位球统计（角球、任意球、红黄牌）

### 历史赛季数据说明（seasons.json）

`seasons.json` 同时存放联赛成绩与杯赛成绩汇总记录，通过 `league` 字段区分：

- **联赛记录**：`league` 为「中超」等非杯赛名称，含 `rank`（排名）、`points`（积分）等字段
- **杯赛记录**：`league` 为「足协杯」「亚冠联赛」「亚冠精英联赛」「超级杯」之一，`rank` 表示最终成绩（冠军 / 亚军 / 四强 / 八强 / 十六强等），`points: null`，`notes` 存最终成绩备注

```json
{
  "id": 42,
  "season": "2024",
  "league": "足协杯",
  "rank": "冠军",
  "matches": 5,
  "wins": 5,
  "draws": 0,
  "losses": 0,
  "goalsFor": 13,
  "goalsAgainst": 4,
  "points": null,
  "notes": "决赛 3-1 胜山东泰山"
}
```

> 说明：杯赛成绩固化为 `seasons.json` 记录，而非存放在 `history_schedule.json`（该文件仅存逐场记录）；逐场杯赛战绩仍由 `history_schedule.json` 提供。

### 简称映射说明（short_names.json）

存储外籍教练/球员的全名 → 简称映射，便于在页面中以简称展示，并与赛事报告相互映射：

```json
{
  "description": "外籍教练/球员简称映射",
  "coaches": {
    "维托尔·佩雷拉": "佩雷拉",
    "凯文·文森特·穆斯卡特": "穆斯卡特"
  },
  "players": {}
}
```

## 文档

- [docs/综合项目报告.md](docs/综合项目报告.md) - 完整的项目分析报告
- [docs/更新比赛结果操作指南.md](docs/更新比赛结果操作指南.md) - 比赛结果更新流程
- [docs/当季数据统计更新操作指南.md](docs/当季数据统计更新操作指南.md) - 数据统计更新说明
- [docs/match-result-updater-skill.md](docs/match-result-updater-skill.md) - 技能使用说明

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License
