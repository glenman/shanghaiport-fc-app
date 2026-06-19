# 上海海港足球俱乐部官网

上海海港足球俱乐部官方网站，提供球队最新动态、比赛结果、球员信息等内容。

## 功能特性

### 🏆 比赛结果
- 一线队中超联赛、足协杯、亚冠联赛赛程和结果
- B队中乙联赛赛程和结果
- 赛事报告详细分析

### 📊 数据统计
- 当季数据统计（进球榜、助攻榜、红黄牌榜）
- 一线队与B队数据对比
- 按赛事类型分类展示（中超/杯赛/中乙）
- **详细数据分析页面**：控球率、预期进球(xG/xGOT)、射门、进攻、传球、对抗、防守、门将、定位球

### 👥 球员信息
- 一线队球员名单
- B队球员名单
- 球员详细资料

### 📝 赛事报告
- 详细的比赛分析
- 球员评分
- 比赛亮点和关键时刻
- 乌龙球(OG)标识显示

## 技术栈

- **前端框架**: React 18 + TypeScript
- **构建工具**: Vite
- **样式**: TailwindCSS 3
- **图标**: Lucide React
- **数据格式**: JSON
- **后端脚本**: Python 3.x

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
│   │   ├── team-a/                  # 一线队比赛数据
│   │   │   ├── YYYY-MM-DD-赛事-第X轮.json      # 比赛报告
│   │   │   └── YYYY-MM-DD-赛事-第X轮-MO.json   # 赛事统计详情
│   │   ├── team-b/                  # B队比赛数据
│   │   │   └── YYYY-MM-DD-赛事-第X轮.json     # 比赛报告
│   │   ├── history/                  # 历史比赛数据(2023-2025)
│   │   ├── schedule.json             # 一线队赛程
│   │   ├── schedule_b.json           # B队赛程
│   │   ├── players.json              # 一线队球员名单
│   │   ├── players_b.json            # B队球员名单
│   │   ├── current_stats.json        # 当季数据统计
│   │   └── competitions.json         # 比赛类型映射
│   ├── match-overview-stats.html     # 赛事统计详情页面
│   ├── match-report.html             # B队赛事报告模板
│   ├── match-report-v2.html          # 一线队赛事报告模板
│   └── index.html                    # 主页面
├── src/
│   ├── components/                   # React组件
│   │   ├── CurrentStats.tsx          # 当季数据统计组件
│   │   ├── Schedule.tsx             # 赛程组件
│   │   ├── Players.tsx              # 球员信息组件
│   │   └── ...
│   ├── App.tsx                      # 主应用组件
│   └── main.tsx                     # 入口文件
├── scripts/
│   ├── update_stats.py               # 数据统计更新脚本
│   └── normalize_match_report.py    # 球员姓名标准化脚本
├── docs/                            # 项目文档
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
| public/data/schedule.json | 一线队赛程 |
| public/data/schedule_b.json | B队赛程 |
| public/data/players.json | 一线队球员名单 |
| public/data/players_b.json | B队球员名单 |
| public/data/current_stats.json | 当季数据统计（按比赛类型分组） |
| public/data/competitions.json | 比赛类型映射配置 |
| public/data/team-a/YYYY-MM-DD-赛事-第X轮.json | 一线队单场比赛报告 |
| public/data/team-a/YYYY-MM-DD-赛事-第X轮-MO.json | 一线队赛事统计详情 |
| public/data/team-b/YYYY-MM-DD-赛事-第X轮.json | B队单场比赛报告 |
| public/match-overview-stats.html | 赛事统计详情页面 |

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

## 文档

- [docs/综合项目报告.md](docs/综合项目报告.md) - 完整的项目分析报告
- [docs/更新比赛结果操作指南.md](docs/更新比赛结果操作指南.md) - 比赛结果更新流程
- [docs/当季数据统计更新操作指南.md](docs/当季数据统计更新操作指南.md) - 数据统计更新说明
- [docs/match-result-updater-skill.md](docs/match-result-updater-skill.md) - 技能使用说明

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License
