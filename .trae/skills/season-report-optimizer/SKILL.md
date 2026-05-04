# Season Report Optimizer

这个Skill用于自动处理历史赛季赛事报告的优化工作，包括队名修复、球员汉化、文件名修正等。

## Features

- ✅ 问题诊断：自动检查Opponent、未汉化球员等问题
- ✅ 队名修复：根据赛程CSV自动更新主客队名称
- ✅ 内容汉化：球员姓名、主教练、场地名称汉化
- ✅ 文件名修复：根据比赛日期修正轮次
- ✅ 验证确认：自动验证优化结果

## Usage

```
# 优化2019赛季
优化2019赛季赛事报告

# 优化2020赛季
处理2020赛季数据

# 仅诊断问题
检查2021赛季有哪些问题

# 指定特定步骤
修复2022赛季的队名
```

## How it works

1. 检查datafile目录下是否有对应赛季的CSV文件
2. 自动诊断JSON文件的问题
3. 执行相应的Python脚本进行优化
4. 验证优化结果

## Requirements

- 对应赛季的球员大名单：`datafile/上海海港XXXX一线队大名单.csv`
- 对应赛季的赛程：`datafile/上海海港XXXX一线队中超赛程.csv`
- JSON文件：`public/data/history/XXXX/`

---
Created: 2026-05-04
Version: 2.0