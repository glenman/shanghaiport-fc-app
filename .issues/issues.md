# Issue 清单 — 全功能检查（2026-11-19 立项，2026-11-20 结案）

> 来源：静态代码审查（全部 src 组件）+ 数据文件核验 + 浏览器全页面实测（7 页控件全通过、console 0 error）+ 第二轮布局/排版/按钮专项巡检（2026-11-20，3 路并行覆盖全部 7 页）。
> 状态：**已全部结案**。共 13 个 issue（1-9 第一轮，10-13 第二轮巡检新增），13 个独立 commit；最终核对通过（tsc exit 0、build 成功、源码树无残留改动、全部修复 grep 在位）。

## 结案记录

| 编号 | 严重度 | 摘要 | Commit | 验证 |
|---|---|---|---|---|
| ISSUE-1 | HIGH | tsc 基线修复（tsconfig types:[] + downlevelIteration，PlayerStats 三处类型错误） | ee5054b9 | tsc exit 0 + build |
| ISSUE-2 | MEDIUM | 进球助攻榜补中甲/中乙分桶列（合计与分项一致，2011 武磊 12 球归中甲） | c99724d6 | tsc + build + 浏览器实测 |
| ISSUE-3 | HIGH | 教练进失球统计（点球大战常规比分解析 + NaN 累加器重置），穆斯卡特 44/21→275/171 | 7b297fe2 | tsc + build + 浏览器实测（275/171、60/30、72/42） |
| ISSUE-4 | HIGH | 4 个报告页移除外部 Google Fonts，消除受限网络下加载永久阻塞 | e2221fe7 | tsc + build + 4 页实测无 fonts.googleapis 请求、不再挂起 |
| ISSUE-5 | MEDIUM | 进球助攻榜默认赛季由硬编码 2025 → 最新赛季（seasons[0] 回退） | f9033b75 | tsc + build + 实测默认 2026/27、切换正常 |
| ISSUE-6 | MEDIUM | Seasons.tsx 删除全部调试 console.log（约 50 条/轮） | 66f2390f | tsc + build + 实测 0 log 0 error |
| ISSUE-7 | - | 删除无引用死代码 MatchReport.tsx/Stats.tsx（346 行） | 65f3389e | tsc + build |
| ISSUE-8 | LOW | 球员页搜索支持球衣号码匹配（搜 7 命中 4 人含武磊，B队 5 人） | 82cb0e6d | tsc + build + 实测 |
| ISSUE-9 | LOW | 报告链接统一新标签打开（target=_blank rel=noopener，4 处） | f2aa2f00 | tsc + build + 实测 106 链接属性全对、原页不动 |
| ISSUE-10 | MEDIUM | 赛季排名图表窄容器适配：宽度下限 600→320 + effect 依赖补 loading（修复首次加载不测量）+ Y 轴刻度 16→6 消除叠压 | 015d2375 | tsc + build + 复验 SVG 534px≤574px、20 赛季标签全可见、6 刻度无叠压 |
| ISSUE-11 | LOW | seasons.json 2018 备注删除粘贴残留"国家体育总局" | 1ab6990f | JSON 校验 + tsc + build + 实测文案 |
| ISSUE-12 | LOW | 历史交锋搜索框 39px→48px 对齐全站标准 | c7e3a697 | tsc + build + 实测 48px、建议列表正常 |
| ISSUE-13 | LOW | 清除查询按钮 46px→48px + justifyContent:center 修复 .team-tab 列向 flex 文字贴顶 | 5d50f196 | tsc + build + 实测 48px、居中偏移 1.2px |

## 已核查排除项（非缺陷，留档）

- Seasons.tsx 图表排名覆盖：联赛行排名（冠军/第 X/4 强/季军/亚军/南区第 7）全部被 getRankValue 覆盖；中文数字类排名（四强/十六强等）均属杯赛行，不进图表
- 巡检观察"当季数据统计页按钮组周期性重挂载"：代码无定时器/轮询，判定为巡检工具注入伪影，未复现，不立 issue
- Schedule.tsx 点球胜负判定（getResultStatus）：逻辑正确
- 第二轮巡检：赛程页（tab/筛选/表格/比分链接）、进球助攻榜（对齐/交互）、球员页（tab/筛选/搜索/照片）均 PASS 无问题

## 遗留事项（后续专项，非缺陷）

- **报告数据缺失类（用户指示专项后查）**：match-report.html（B队页）对 2025 中超场次取 `data/team-b/` 文件不存在（team-b 仅 2026 中乙）；match-overview-stats.html 的 `-MO.json`（team-a）仅覆盖 2026-03-07 起。页面在 Vite 下落 SPA 回退 HTML 后 JSON.parse 报错。需补数据或加路径/schema 回退与 content-type 校验
- 历史交锋搜索框拒绝程序化 fill 输入（键盘逐键正常，真机不受影响），低优先级不处理
