---
name: "issue-workflow"
description: "Issue 处理流程规范：发现(review-changes)→分析(next-issue)→修复→验证(resolve-this-issue)→commit→清单删除→全量核对。Invoke when user mentions 'issue 处理流程', '处理 issue', 'issue 清单', 'review-changes', 'next-issue', 'resolve-this-issue', or asks to batch-fix issues found in a review."
---

# Issue 处理流程规范

> 本规范定义本项目发现、分析、修复、验证、结案 issue 的标准流程。
> 流程文件位于 `.issues/` 目录；issue 清单默认记在 `.issues/issues.md`。

## 流程总览

```
review-changes ──→ 生成 issue 清单文件 ──→ 循环 { next-issue → 修复 → resolve-this-issue 验证 → commit → 从清单删除 } ──→ 全部解掉 ──→ 按清单全量核对 + 重写 issue 文件
```

## 步骤详解

### 1. 发现 issue（review-changes）

- 用 `review-changes` 对当前工作区变更/代码做全面审查，找出所有 issue。
- 将全部 issue 记录到 `.issues/` 目录下的清单文件（默认 `.issues/issues.md`），每个 issue 包含：
  - 编号（如 ISSUE-1）
  - 严重度（HIGH / MEDIUM / LOW）
  - 所在文件与位置（文件路径 + 行号）
  - 问题描述与证据
- 清单写好后先不逐个处理，保证全貌完整、无遗漏。

### 2. 分析 issue（next-issue）

- 用 `next-issue` 从清单中取出第一个待处理 issue，输出该 issue 的分析（根因、影响面、修复方案）。
- 一次只处理一个 issue，避免交叉改动。

### 3. 修复并验证（resolve-this-issue）

- 按分析实施修复。
- 用 `resolve-this-issue` 验证修复，验证手段至少包含：
  - `npx tsc --noEmit` 通过
  - `pnpm build`（或 `npm run build`）通过
  - 涉及 UI 行为的改动需浏览器实测（页面渲染、交互、console 干净）
- 验证通过后：
  1. `commit` 提交本次修复（一个 issue 一个 commit，提交信息注明 issue 编号）；
  2. 把该 issue 从清单文件中删除。
- 验证不通过则回到修复，不得提交。

### 4. 循环处理

- 反复执行步骤 2/3（next-issue → 修复 → resolve-this-issue → commit → 删除），直到清单中所有 issue 都解掉。

### 5. 全量核对与清单重写

- 所有 issue 解完后，按照清单文件里的 issue 记录对当前代码做一次全量核对：
  - 逐条确认每处修复的代码在位、逻辑正确；
  - 确认误报/非缺陷项的结论仍有依据；
  - 复跑 `tsc --noEmit` 与 build。
- 核对通过后重写 issue 清单文件：更新结案状态、验证记录、遗留事项，作为本轮审查的最终存档。

## 约定

- issue 清单是唯一进度来源：文件里没有的 issue 不处理，解掉的必须从文件删除（或按步骤 5 重写为结案存档）。
- 未经 `resolve-this-issue` 验证通过的修复不得 commit。
- 每个 issue 独立 commit，便于回溯与 review。
- 若某 issue 核实为误报或按设计接受，不 commit 代码，但需在清单中记录核实证据后再移除。
