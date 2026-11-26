#!/usr/bin/env python3
"""一次性迁移：亚冠跨年赛季（2024/25、2025/26、2026/27）统一归并到起始年（2024、2025、2026）。

涉及：
1. team-a/*.json 报告源：match.season "2026/27" -> "2026"
2. history_schedule.json：matches[].season + 重建 summary
3. goal_details.json：goal[].season
4. player_appearance_details.json：players[].seasons[] 中跨年节点并入同年节点（按 matchId 去重）
5. seasons.json：跨年 season 条目改为起始年（按 league+year 与现有条目不冲突——亚冠是独立条目）

不改 history/YYYY-出场记录.json 年度文件（其顶层 season 本就是单年）。
"""
import json
from pathlib import Path

BASE = Path(r"d:\Workspace\shanghaiport-fc-app")
DATA = BASE / "public" / "data"
TEAM_A = DATA / "team-a"
TEAM_B = DATA / "public" / "data" / "team-b"  # 未用，占位


def norm(s):
    """跨年赛季标签 -> 起始年"""
    return s.split("/")[0] if s and "/" in s and len(s.split("/")[0]) == 4 else s


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def dump(obj, p):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def main():
    report_changes = 0
    # 1) team-a 报告源
    for path in sorted(TEAM_A.glob("*.json")):
        if path.stem.endswith("-MO"):
            continue
        rep = load(path)
        m = rep.get("match") or {}
        s = str(m.get("season") or "")
        if "/" in s:
            m["season"] = norm(s)
            dump(rep, path)
            report_changes += 1
            print(f"[报告] {path.name}: {s} -> {m['season']}")

    # 2) history_schedule.json
    sched_path = DATA / "history_schedule.json"
    sched = load(sched_path)
    sched_changes = 0
    for rec in sched["matches"]:
        s = str(rec.get("season") or "")
        if "/" in s:
            rec["season"] = norm(s)
            sched_changes += 1
    # summary.bySeason 按起始年聚合，条目结构 season 已是起始年，仅当存在跨年 key 时需重建
    by = {}
    for rec in sched["matches"]:
        y = str(rec.get("season") or "").split("/")[0]
        by.setdefault(y, {})
        by[y][rec.get("match_type", "")] = by[y].get(rec.get("match_type", ""), 0) + 1
    SUMMARY_TYPES = ['中乙联赛', '中甲联赛', '中超联赛', '亚冠联赛', '亚冠精英联赛', '足协杯', '超级杯']
    by_season = []
    for y in sorted((k for k in by if k.isdigit()), key=int):
        row = {'season': y}
        for t in SUMMARY_TYPES:
            row[t] = by[y].get(t, 0)
        row['total'] = sum(by[y].values())
        by_season.append(row)
    sched["summary"]["bySeason"] = by_season
    dump(sched, sched_path)
    print(f"[赛程] history_schedule: {sched_changes} 条 season 已归一，bySeason 已重建")

    # 3) goal_details.json
    goal_path = DATA / "goal_details.json"
    goals = load(goal_path)
    goal_changes = 0
    for g in goals:
        s = str(g.get("season") or "")
        if "/" in s:
            g["season"] = norm(s)
            goal_changes += 1
    dump(goals, goal_path)
    print(f"[进球] goal_details: {goal_changes} 条 season 已归一")

    # 4) player_appearance_details.json：合并跨年节点到同年节点
    detail_path = DATA / "player_appearance_details.json"
    detail = load(detail_path)
    merged_nodes = renamed_nodes = 0
    for p in detail["players"]:
        seasons = p.get("seasons") or []
        by_label = {}
        for s in seasons:
            by_label.setdefault(s["season"], s)
        cross_labels = [x for x in by_label if "/" in x]
        if not cross_labels:
            continue
        new_list = []
        for s in seasons:
            label = s["season"]
            if "/" not in label:
                new_list.append(s)
                continue
            y = label.split("/")[0]
            target = next((x for x in new_list if x["season"] == y), None)
            if target is None:
                s["season"] = y
                new_list.append(s)
                renamed_nodes += 1
            else:
                # 合并 appearances（按 matchId 去重）
                seen = {a.get("matchId") for a in target["appearances"]}
                for a in s["appearances"]:
                    if a.get("matchId") not in seen:
                        target["appearances"].append(a)
                        seen.add(a.get("matchId"))
                merged_nodes += 1
        # 排序：按赛季年份升序
        new_list.sort(key=lambda x: x["season"][:4])
        p["seasons"] = new_list
    dump(detail, detail_path)
    print(f"[出场] player_appearance_details: 合并 {merged_nodes} 节点，改名 {renamed_nodes} 节点")

    # 5) seasons.json
    seasons_path = DATA / "seasons.json"
    seasons_data = load(seasons_path)
    season_changes = 0
    for row in seasons_data:
        s = str(row.get("season") or "")
        if "/" in s:
            row["season"] = norm(s)
            season_changes += 1
    dump(seasons_data, seasons_path)
    print(f"[赛季] seasons.json: {season_changes} 条 season 已归一")

    # 6) 交叉校验
    d = load(detail_path)
    leftover = [s["season"] for p in d["players"] for s in p["seasons"] if "/" in s["season"]]
    assert not leftover, f"残留跨年节点: {leftover[:5]}"
    sd = load(sched_path)
    leftover_s = [r["season"] for r in sd["matches"] if "/" in str(r.get("season", ""))]
    assert not leftover_s, f"赛程残留: {leftover_s[:5]}"
    print("[校验] 全部数据已归一为起始年，无残留跨年标签")


if __name__ == "__main__":
    main()
