# 上海海港足球俱乐部数据查询应用

一个专为上海海港足球俱乐部球迷设计的数据查询应用，提供球队赛程、球员信息、历史赛季成绩和数据统计等功能。(全部由AI生成)

## 功能特性

### 1. 球队赛程
- 显示2026赛季完整的30轮中超联赛赛程
- 支持按轮次、日期、对手、城市搜索
- 支持筛选主场/客场比赛
- 支持按比赛状态（全部/已结束/未开始）过滤

### 2. 球员信息
- 展示2026赛季一线队35名球员详细信息
- 支持按球员姓名搜索
- 支持按位置过滤
- 包含球员号码、年龄、国籍、身高、体重等信息

### 3. 历史赛季
- 展示上海海港过往赛季的联赛成绩
- 包含排名、比赛场次、胜负平、进球失球和积分等数据

### 4. 数据统计
- 球员数据统计：出场次数、进球、助攻、黄牌、红牌
- 球队成绩统计：主场、客场和总计的比赛数据

## 技术栈

- **前端**：HTML5, CSS3, JavaScript (ES6+)
- **框架**：React 17 (通过CDN引入)
- **构建工具**：无（纯静态HTML应用）
- **部署**：支持GitHub Pages, Vercel, Netlify等静态网站托管平台

## 如何运行

### 方法一：直接打开
1. 下载项目文件
2. 直接在浏览器中打开 `index.html` 文件

### 方法二：本地服务器（推荐）
1. 下载项目文件
2. 在项目目录中运行：
   ```bash
   # 使用Python 3
   python -m http.server 8000
   
   # 或使用Python 2
   python -m SimpleHTTPServer 8000
   
   # 或使用Node.js
   npx http-server -p 8000
   ```
3. 在浏览器中访问：`http://localhost:8000`

## 如何部署

### GitHub Pages
1. 将项目上传到GitHub仓库
2. 在仓库设置中开启GitHub Pages
3. 选择主分支作为源
4. 部署完成后，通过 `https://your-username.github.io/repository-name` 访问

### Vercel
1. 注册Vercel账号
2. 连接GitHub仓库或直接上传项目
3. 配置部署设置（默认配置即可）
4. 部署完成后，通过Vercel提供的链接访问

### Netlify
1. 注册Netlify账号
2. 连接GitHub仓库或直接上传项目
3. 配置部署设置
4. 部署完成后，通过Netlify提供的链接访问

## 项目结构

```
shanghaiport-fc-app/
├── index.html          # 主应用文件
├── README.md           # 项目说明文件
└── .gitignore          # Git忽略文件配置
```

## 数据说明

### 赛程数据
- 包含2026赛季30轮中超联赛完整赛程
- 数据来源：2026中超联赛官方赛程

### 球员数据
- 包含2026赛季上海海港一线队35名球员信息
- 数据来源：上海海港足球俱乐部官方名单

### 统计数据
- 球员统计：基于2026赛季预期表现
- 球队统计：基于2026赛季预期表现

## 贡献指南

欢迎对项目进行改进和贡献！请按照以下步骤：

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件

## 联系方式

如果您有任何问题或建议，请通过 GitHub Issues 与我们联系。

---

**上海海港足球俱乐部数据查询应用** - 为球迷提供便捷的数据查询服务
