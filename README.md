﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿# 上海海港足球俱乐部官网

上海海港足球俱乐部官方网站，提供球队最新动态、比赛结果、球员信息等内容。

## 功能特性

### 🏆 比赛结果
- 一线队中超联赛赛程和结果
- B队中乙联赛赛程和结果
- 赛事报告详细分析

### 📊 数据统计
- 当季数据统计（进球榜、助攻榜、红黄牌榜）
- 一线队与B队数据对比
- 按赛事类型分类展示
- **新增**: 赛事统计详情页面（控球率、预期进球、射门、进攻、传球、对抗、防守、门将、定位球）

### 👥 球员信息
- 一线队球员名单
- B队球员名单
- 球员详细资料

### 📝 赛事报告
- 详细的比赛分析
- 球员评分
- 比赛亮点和关键时刻
- **新增**: 详细数据分析页面（match-overview-stats.html）

## 技术栈

- **前端框架**: React 18 + TypeScript
- **构建工具**: Vite
- **样式**: TailwindCSS 3
- **图标**: Lucide React
- **数据格式**: JSON

## 快速开始

### 安装依赖

`ash
npm install
`

### 开发模式

`ash
npm run dev
`

访问 http://localhost:5173/shanghaiport-fc-app/

### 生产构建

`ash
npm run build
`

### 预览构建结果

`ash
npm run preview
`

## 项目结构

```
shanghaiport-fc-app/
├── public/
│   ├── data/
│   │   ├── team-a/     # 一线队比赛数据
│   │   │   ├── YYYY-MM-DD-赛事-第X轮.json     # 比赛报告
│   │   │   └── YYYY-MM-DD-赛事-第X轮-MO.json  # 赛事统计详情
│   │   ├── team-b/     # B队比赛数据
│   │   │   └── YYYY-MM-DD-赛事-第X轮.json
│   │   ├── schedule.json      # 一线队赛程
│   │   ├── schedule_b.json    # B队赛程
│   │   ├── players.json       # 球员名单
│   │   └── current_stats.json # 当季数据统计
│   ├── match-overview-stats.html  # 赛事统计详情页面
│   ├── match-report.html      # B队赛事报告模板
│   ├── match-report-v2.html   # 一线队赛事报告模板
│   └── index.html
├── src/
│   ├── components/     # React组件
│   ├── App.tsx         # 主应用组件
│   ├── main.tsx        # 入口文件
│   └── App.css         # 全局样式
├── scripts/
│   ├── update_stats.py        # 数据统计更新脚本
│   └── normalize_match_report.py # 球员姓名标准化脚本
├── docs/               # 文档
├── .trae/
│   └── skills/         # Trae技能定义
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## 数据更新

### 更新比赛结果

使用 match-result-updater 技能或手动更新：

`ash
# 更新赛程文件
# - 一线队: public/data/schedule.json
# - B队: public/data/schedule_b.json

# 更新数据统计（增量更新）
python scripts/update_stats.py --incremental

# 更新数据统计（全量更新）
python scripts/update_stats.py --full
`

### 技能触发

输入以下指令自动触发比赛结果更新：
- "更新一线队比赛结果，上海海港vs对手 比分"
- "更新B队比赛结果，主队vs上海海港富盛经开 比分"

## 文件说明

| 文件 | 说明 |
|------|------|
| public/data/schedule.json | 一线队赛程 |
| public/data/schedule_b.json | B队赛程 |
| public/data/players.json | 球员名单 |
| public/data/current_stats.json | 当季数据统计 |
| public/data/team-a/YYYY-MM-DD-赛事-第X轮.json | 一线队单场比赛报告 |
| public/data/team-a/YYYY-MM-DD-赛事-第X轮-MO.json | 一线队赛事统计详情 |
| public/data/team-b/YYYY-MM-DD-赛事-第X轮.json | B队单场比赛报告 |
| public/match-overview-stats.html | 赛事统计详情页面 |

### 统计数据字段说明

**match_overview 统计维度:**
- `possession`: 控球率
- `expected_goals`: 预期进球(xG)
- `shots`: 射门统计（总射门、射正、射偏、被封堵）
- `attack`: 进攻统计（进攻三区进入次数、危险进攻、界外球）
- `passing`: 传球统计（传球总数、成功率）
- `duels`: 对抗统计（总对抗、成功率）
- `defense`: 防守统计（拦截、解围、铲抢）
- `goalkeeper`: 门将统计（扑救、出击、高空球）
- `set_pieces`: 定位球统计（角球、任意球、红黄牌）

## 文档

- docs/更新比赛结果操作指南.md - 比赛结果更新流程
- docs/当季数据统计更新操作指南.md - 数据统计更新说明
- docs/汉化指南.md - 汉化处理指南
- docs/match-result-updater-skill.md - 技能使用说明

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License