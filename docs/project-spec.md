# 上海海港足球俱乐部数据查询系统 - 项目规格文档

## 1. 项目概述

本项目是一个基于 React + Vite 架构的上海海港足球俱乐部数据查询系统，旨在为用户提供球队信息、赛程、历史赛季排名、进球助攻榜和历史比赛等数据的查询功能。系统采用现代化的前端技术栈，提供清晰、美观的用户界面，同时确保数据的准确性和实时性。

### 1.1 项目目标

- 提供统一的 React + Vite 架构，替代传统的独立 HTML 页面
- 将静态默认数据保存为 JSON 文件，实现统一的数据读取和调用处理
- 保持与原 index.html 相同的展示效果
- 提供良好的用户体验，包括响应式设计、加载状态和错误处理
- 确保系统的可维护性和可扩展性

## 2. 技术栈

- **前端框架**: React 18
- **构建工具**: Vite 5
- **编程语言**: TypeScript
- **样式方案**: CSS
- **数据存储**: JSON 文件
- **开发服务器**: Vite 开发服务器

## 3. 项目结构

```
shanghaiport-fc-app/
├── data/                  # 主数据目录，存储所有 JSON 数据文件
│   ├── history/           # 历史比赛数据目录
│   │   └── 2025/          # 2025赛季历史比赛数据
│   ├── 2026-03-07-中超-第1轮.json  # 2026赛季第一场比赛数据
│   ├── goal_details.json  # 进球和助攻详情数据
│   ├── history_schedule.json  # 历史赛程数据
│   ├── match_report.json  # 赛事报告数据
│   ├── players.json       # 球员信息数据
│   ├── schedule.json      # 2026赛季赛程数据
│   └── seasons.json       # 历史赛季排名数据
├── datafile/              # 数据文件目录，存储原始数据文件
├── dist/                  # 构建输出目录
├── images/                # 图片资源目录
├── public/                # 静态资源目录
│   ├── data/              # 静态数据目录，供 match-report.html 使用
│   ├── images/            # 静态图片目录
│   └── match-report.html  # 赛事报告页面
├── scripts/               # 脚本目录，包含数据处理脚本
├── src/                   # 源代码目录
│   ├── components/        # 组件目录
│   │   ├── History.tsx    # 历史比赛组件
│   │   ├── Players.tsx    # 球队信息组件
│   │   ├── Schedule.tsx   # 球队赛程组件
│   │   ├── Seasons.tsx    # 历史赛季排名组件
│   │   └── Statistics.tsx # 进球助攻榜组件
│   ├── App.css            # 应用样式
│   ├── App.tsx            # 主应用组件
│   ├── index.css          # 全局样式
│   ├── main.tsx           # 应用入口
│   └── react-app-env.d.ts # TypeScript 类型声明
├── test/                  # 测试目录
├── docs/                  # 文档目录
├── .gitignore             # Git 忽略文件
├── README.md              # 项目说明
├── package.json           # 项目配置和依赖
├── tsconfig.json          # TypeScript 配置
├── tsconfig.node.json     # TypeScript 节点配置
└── vite.config.ts         # Vite 配置
```

## 4. 核心组件

### 4.1 App 组件

- **位置**: `src/App.tsx`
- **功能**: 主应用组件，负责整体布局和导航
- **状态管理**:
  - `activeTab`: 当前激活的标签页
  - `isSidebarCollapsed`: 侧边栏折叠状态
- **导航菜单**: 包含球队信息、球队赛程、历史赛季排名、进球助攻榜和历史比赛五个菜单项
- **布局结构**:
  - 左侧侧边栏导航
  - 右侧主内容区，包含头部、内容区和底部

### 4.2 Schedule 组件

- **位置**: `src/components/Schedule.tsx`
- **功能**: 显示2026赛季球队赛程
- **数据来源**: `data/schedule.json`
- **功能特性**:
  - 搜索功能（轮次、日期、对手或城市）
  - 比赛类型过滤（全部比赛、主场比赛、客场比赛）
  - 比赛状态过滤（全部、已结束、未开始）
  - 自动计算星期几并只显示最后一个字
  - 已结束比赛的赛果可点击查看赛事报告
  - 加载状态和错误处理

### 4.3 History 组件

- **位置**: `src/components/History.tsx`
- **功能**: 显示历史比赛数据
- **数据来源**: `data/history_schedule.json`
- **功能特性**:
  - 按赛季分组显示
  - 赛季展开/折叠功能
  - 赛季降序排序
  - 赛事报告查看链接
  - 加载状态和错误处理

### 4.4 Statistics 组件

- **位置**: `src/components/Statistics.tsx`
- **功能**: 显示进球助攻榜
- **数据来源**: `data/goal_details.json`
- **功能特性**:
  - 赛季选择
  - 统计类型切换（进球统计、助攻统计）
  - 按总进球/助攻数排序
  - 按比赛类型分类统计（中超联赛、足协杯、超级杯、亚冠联赛）
  - 加载状态和错误处理

### 4.5 Players 组件

- **位置**: `src/components/Players.tsx`
- **功能**: 显示球队球员信息
- **数据来源**: `data/players.json`
- **功能特性**:
  - 搜索功能（球员姓名）
  - 位置过滤
  - 加载状态和错误处理

### 4.6 Seasons 组件

- **位置**: `src/components/Seasons.tsx`
- **功能**: 显示历史赛季排名
- **数据来源**: `data/seasons.json`
- **功能特性**:
  - 搜索功能（赛季、联赛）
  - 加载状态和错误处理

### 4.7 Match Report 页面

- **位置**: `public/match-report.html`
- **功能**: 显示详细的赛事报告
- **数据来源**: 根据URL参数动态加载对应的JSON文件
- **功能特性**:
  - 从URL参数获取比赛信息
  - 区分历史比赛和当前赛季比赛的数据路径
  - 显示比赛信息、摘要、亮点、阵容、统计和关键因素
  - 加载状态和错误处理
  - 返回按钮（使用浏览器历史回退）

## 5. 数据流向

### 5.1 数据加载流程

1. **组件初始化** → **useEffect 触发** → **fetch 请求** → **数据处理** → **状态更新** → **UI 渲染**

### 5.2 数据文件说明

| 文件名 | 路径 | 用途 | 格式 |
|-------|------|------|------|
| players.json | data/ | 球员信息 | 包含id、name、position、number、age、nationality等字段 |
| schedule.json | data/ | 2026赛季赛程 | 包含id、round、date、time、homeTeam、awayTeam、venue、city、result、status等字段 |
| seasons.json | data/ | 历史赛季排名 | 包含id、season、league、rank、matches、wins、draws、losses、goalsFor、goalsAgainst、points、notes等字段 |
| goal_details.json | data/ | 进球和助攻详情 | 包含id、season、match_date、match_type、match_round、home_team、away_team、goal_player、assist_player、minute、score等字段 |
| history_schedule.json | data/ | 历史赛程 | 包含season、match_type、match_name、round、date、home_team、away_team、result、win_loss等字段 |
| 比赛报告JSON | data/ 和 data/history/{year}/ | 详细的赛事报告 | 包含match、summary、highlights、lineups、statistics、keyFactors等字段 |

## 6. 关键功能

### 6.1 数据加载和错误处理

- 所有组件都实现了数据加载状态和错误处理
- 使用 `try-catch` 捕获网络请求错误
- 显示友好的错误信息和加载提示

### 6.2 赛事报告查看

- 从赛程和历史比赛页面点击赛果或查看链接
- 使用 `encodeURIComponent` 处理URL参数中的中文
- 区分历史比赛和当前赛季比赛的数据路径
- 使用浏览器历史回退实现返回功能

### 6.3 数据过滤和搜索

- 各组件都实现了搜索和过滤功能
- 支持多条件组合过滤
- 实时响应过滤条件变化

### 6.4 响应式设计

- 适配不同屏幕尺寸
- 侧边栏可折叠
- 表格内容自适应

## 7. 维护指南

### 7.1 数据更新

1. **球员数据更新**:
   - 修改 `data/players.json` 文件
   - 确保数据格式与现有格式一致

2. **赛程更新**:
   - 修改 `data/schedule.json` 文件
   - 确保日期格式为 `YYYY-MM-DD`
   - 确保字段名称正确（如 `homeTeam` 而不是 `homeTeamTeam`）

3. **历史数据更新**:
   - 修改 `data/history_schedule.json` 文件
   - 对于新赛季，创建对应的目录 `data/history/{year}/` 并添加比赛报告JSON文件

4. **赛事报告更新**:
   - 对于当前赛季，在 `data/` 目录下创建 `{date}-{type}-{round}.json` 文件
   - 对于历史赛季，在 `data/history/{year}/` 目录下创建对应的JSON文件
   - 确保JSON格式与现有格式一致

### 7.2 功能扩展

1. **添加新组件**:
   - 在 `src/components/` 目录下创建新的组件文件
   - 在 `App.tsx` 中添加导航菜单和组件渲染

2. **添加新数据**:
   - 在 `data/` 目录下创建新的JSON文件
   - 在组件中添加数据加载和处理逻辑

3. **修改现有功能**:
   - 直接修改对应的组件文件
   - 确保修改后功能正常且不影响其他部分

### 7.3 构建和部署

1. **开发环境**:
   - 运行 `npm run dev` 启动开发服务器
   - 访问 `http://localhost:5174` 查看应用

2. **生产构建**:
   - 运行 `npm run build` 构建生产版本
   - 构建产物将输出到 `dist/` 目录

3. **部署**:
   - 将 `dist/` 目录下的所有文件部署到服务器
   - 确保服务器正确配置静态文件服务

## 8. 常见问题和解决方案

### 8.1 数据加载失败

- **原因**:
  - JSON文件路径错误
  - JSON文件格式错误
  - 网络请求失败

- **解决方案**:
  - 检查JSON文件路径是否正确
  - 验证JSON文件格式是否合法
  - 检查网络连接

### 8.2 赛事报告无法加载

- **原因**:
  - URL参数格式错误
  - 对应的JSON文件不存在
  - 中文参数未编码

- **解决方案**:
  - 确保从赛程或历史比赛页面进入
  - 检查对应的JSON文件是否存在
  - 确保使用 `encodeURIComponent` 处理中文参数

### 8.3 表格内容对齐问题

- **原因**:
  - CSS样式未正确应用

- **解决方案**:
  - 确保表格样式包含 `text-align: center` 和 `vertical-align: middle`
  - 可以使用 `!important` 确保样式优先级

## 9. 项目依赖

| 依赖 | 版本 | 用途 |
|-----|------|------|
| react | ^18.2.0 | 前端框架 |
| react-dom | ^18.2.0 | React DOM操作 |
| typescript | ^5.2.2 | 类型检查 |
| vite | ^5.0.8 | 构建工具 |
| @types/react | ^18.2.43 | React类型定义 |
| @types/react-dom | ^18.2.17 | React DOM类型定义 |
| @vitejs/plugin-react | ^4.2.1 | Vite React插件 |

## 10. 开发规范

### 10.1 代码风格

- 使用 TypeScript 类型定义
- 遵循 React 组件命名规范（大驼峰）
- 使用函数组件和 Hooks
- 保持代码简洁明了

### 10.2 目录结构

- 组件文件放在 `src/components/` 目录
- 数据文件放在 `data/` 目录
- 静态资源放在 `public/` 目录
- 脚本文件放在 `scripts/` 目录
- 测试文件放在 `test/` 目录

### 10.3 数据格式

- 使用 JSON 格式存储数据
- 保持数据结构一致
- 使用语义化的字段名称

## 11. 总结

本项目采用 React + Vite 架构，实现了上海海港足球俱乐部数据查询系统，提供了球队信息、赛程、历史赛季排名、进球助攻榜和历史比赛等功能。系统采用组件化设计，数据驱动UI，提供了良好的用户体验和可维护性。

通过本项目规格文档，可以快速了解项目的架构、组件、数据流向和维护指南，为后续的开发和维护工作提供参考。