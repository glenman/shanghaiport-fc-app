---
name: football-data-audit
description: 上海海港数据应用的多源数据交叉对账与校验。用户要求校验/审计/修复 player_history_stats、player_appearance_details、history_schedule、goal_details、年度出场记录或 Excel 汇总表之间的一致性（场次/分钟/进球/助攻/姓名归并）时使用。不用于比赛结果录入。
---

# 海港数据交叉审计与校验

对 `public/data/` 下五类数据源 + Excel 基线做交叉对账，定位差异、取证后修复并回归校验。

## 数据源与主从关系

| 文件 | 角色 |
|---|---|
| `public/data/player_history_stats.json` | 球员生涯/分赛事汇总（前端展示） |
| `public/data/player_appearance_details.json` | 逐场明细（出场/分钟真值来源） |
| `public/data/history/<year>/<year>-出场记录.json` | 年度归档（逐场 + 该年分赛事 stats，首发/替补拆分真值） |
| `public/data/history_schedule.json` | 赛程（M0001…，比分/胜负/进球者清单） |
| `public/data/goal_details.json` | 逐球记录（进球者/助攻者/日期码） |
| `datafile/上海海港球员历史出场汇总(2006-2026).xlsx` | stats 的 Excel 基线，`scripts/convert_player_history.py` 转换 |

真值优先级：年度归档逐场记录 ≈ details > goal_details > stats JSON ≈ Excel。stats 与 Excel 互为镜像，**修复时必须双改**。

## 修复铁律

1. **先取证再改数**：差异必须落到具体 matchId/日期/场次，用年度文件 appearances 条目（`date`/`opponent`/`status`/`minutes`）核对；存疑的历史事实必须联网核实（战报/央视/懂球帝等至少两源）。
2. **stats JSON 与 Excel 双改**，改完回读 Excel（`read_sheet`）逐字段比对 JSON。
3. **禁止擅自 `--full` 重建**（`update_player_history_stats.py`/`update_player_appearance_details.py`）：team-a 报告不全，full 会覆盖/丢失历史。只用就地增量修正。
4. 就地改值，不重建对象、不改 schema、不动无关字段（防止结构漂移）。
5. JSON 写回：`ensure_ascii=False, indent=2`、LF、保留末尾换行；改完与基线 `git diff` 确认无格式噪声。
6. 姓名归并时同步两个构建脚本的 ALIAS_MAP（`scripts/update_player_history_stats.py`、`scripts/update_player_appearance_details.py`）；stats 的 `short_name` 是刻意保留的简写，不要动。
7. 临时脚本放 `scripts/_*.py`，用完即删；Excel 修改前先备份，验证后删备份。

## Excel 约定

- 数据从第 3 行起，B 列姓名，C 出生 D 位置 E 国籍，F 出场 G 首发 H 替补 I 分钟，J 进球（`整数(点球数)` 或纯整数），K 助攻 L 黄 M 红。
- sheet→key：汇总/中乙联赛/中甲联赛/中超联赛/足协杯/亚冠联赛(含资格赛)/超级杯 → summary/c2l/c1l/csl/cfa/acle/supercup。
- 球员可能在某赛事 sheet 缺行（JSON 对应块为 null），需要时新增行而不是只改 JSON。

## 标准校验清单

运行 `scripts/validate_data.py`（本 skill 目录内），并人工确认 WARN 项：

**硬错误（exit 1）**
- 关键 JSON 或年度归档无法解析
- stats 任一球员 summary ≠ 6 个赛事块之和（9 个数值字段逐一比对）
- 数值字段出现负值；stats 球员重名

**WARN（需人工判断，含已知历史局限）**
- stats vs details 出场/分钟不一致（贾天子缺明细、8 条"出场但分钟=0"等）
- 2006/07 中乙老球员（王燊超/武磊/蔡慧康/吕文君/张琳芃/朱峥嵘）首发+替补≠出场属正常（当年无拆分）
- 赛程进球者清单 vs goal_details 进球条数不一致
- stats 有、details 无的 0 出场球员（万桂文/梁锦鸿等属正常）

## 推荐工作流

1. 跑校验脚本收集全部差异清单，一次只处理用户确认的档位
2. 逐条取证（年度归档→赛程 matchId→必要时联网），记录"旧值→新值"依据
3. 写临时脚本就地修正（赛程/details/stats/goal_details），Excel 单独脚本双改
4. 重跑校验脚本 + 针对性对账（分赛事合计、details 逐场、Excel 回读、`git diff` 净度）
5. 删除临时脚本与备份，汇报改动表与仍挂起的问题

## 典型陷阱

- 跨年赛季：2021/2022 中超实际赛期可能在次年 1 月，`season` 按赛季年标注，日期码是真实比赛日——排查"幽灵比赛"前先核对这个。
- 同名不同后缀：年度归档中同一人可能带 `(U23)/(U21)/(补报)/(撤销)` 后缀或纯简写，先全局搜名字再判定。
- 同分钟多起换人不能用 minute 单键匹配（复合键 (minute, player_out)）。
- schedule 的 scorers 是展示清单（含 `(PK)`/`(OG)` 后缀），做集合比对时要做归一化；`武磊2` 这类"名字+数字"合并写法代表 N 球，比对条数前先展开。
- goal_details 只记海港方进球（对手球不录），比对基数用"我方进球数"而非比分总球数；约 92 场早期比赛（2008-2020 零散）整场未收录，属数据集固有边界，报告为 WARN 即可。
- goal_details 的对手队名常用全称（山东鲁能泰山/北京理工贵人鸟/江苏舜天国信/天津泰达权健），schedule 用简称（山东鲁能/北京理工/江苏舜天/天津泰达），按日期+队名互含做宽松匹配。
- goal_details 历史上出现过日期码/赛事错挂（如 2019-04-10 亚冠悉尼FC 两球挂在 03-30 中超名下），发现"同日多场条目"要逐条核对 match_name 与比分。

## 校验基线（2026-10-05 全绿后）

硬错误 0。剩余 WARN 固定基线：W1 30 条（中乙时代缺明细 6 人 + 2026 年 5 月起口径切换 + 分钟±1 级差异）、W2 1 条（贾天子）、W3 92 条（goal_details 未收录场次）。修复引入的新差异若使 WARN 高于该基线，视为回归。
