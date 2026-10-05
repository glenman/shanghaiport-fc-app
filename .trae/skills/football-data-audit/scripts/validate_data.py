#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""海港数据多源一致性校验。

硬错误（exit 1）：
  E1 关键 JSON / 年度归档解析失败
  E2 stats 球员重名 / 数值为负
  E3 stats summary != 6 赛事块之和
警告（exit 0，需人工判定）：
  W1 stats vs details 出场/分钟不一致
  W2 stats 有出场但 details 无此人
  W3 赛程比分/进球者条数 vs goal_details 进球条数不一致
用法： python validate_data.py [--strict]   # --strict 时 WARN 也算失败
"""
import json
import re
import sys
import glob
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DATA = ROOT / "public" / "data"

COMPS = ["c2l", "c1l", "csl", "cfa", "acle", "supercup"]
FIELDS = ["appearances", "starts", "substitute", "minutes", "goals",
          "penalties", "assists", "yellowCards", "redCards"]

errors, warns = [], []


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


# ---------- E1 解析 ----------
key_files = ["player_history_stats.json", "player_appearance_details.json",
             "history_schedule.json", "goal_details.json", "players.json",
             "players_b.json"]
loaded = {}
for name in key_files:
    try:
        loaded[name] = load(DATA / name)
    except Exception as e:
        errors.append(f"E1 {name} 解析失败: {e}")

annual = sorted(glob.glob(str(DATA / "history" / "*" / "*出场记录.json")))
annual_bad = 0
for f in annual:
    try:
        load(f)
    except Exception as e:
        annual_bad += 1
        errors.append(f"E1 年度归档解析失败 {f}: {e}")

if errors:
    print("\n".join(errors))
    sys.exit(1)

stats = loaded["player_history_stats.json"]["players"]
details = loaded["player_appearance_details.json"]
schedule = loaded["history_schedule.json"]
goals = loaded["goal_details.json"]
goals = goals if isinstance(goals, list) else goals.get("goals") or goals.get("details")

# ---------- E2 重名 / 负值 ----------
names = [p["name"] for p in stats]
if len(names) != len(set(names)):
    dup = sorted({n for n in names if names.count(n) > 1})
    errors.append(f"E2 stats 重名: {dup}")

for p in stats:
    for blk in [p["summary"]] + [p.get(c) for c in COMPS]:
        if not blk:
            continue
        for f in FIELDS:
            v = blk.get(f)
            if isinstance(v, (int, float)) and v < 0:
                errors.append(f"E2 {p['name']} 负值 {f}={v}")

# ---------- E3 summary = 分赛事合计 ----------
for p in stats:
    for f in FIELDS:
        s = p["summary"].get(f) or 0
        t = sum((p.get(c) or {}).get(f) or 0 for c in COMPS)
        if s != t:
            errors.append(f"E3 {p['name']} {f}: summary={s} 分赛事合计={t}")

# ---------- W1/W2 stats vs details ----------
det_by_name = {}
for q in details["players"]:
    apps = sum(1 for s in q["seasons"] for a in s["appearances"] if a["status"] == "出场")
    mins = sum(a["minutes"] for s in q["seasons"] for a in s["appearances"] if a["status"] == "出场")
    det_by_name[q["name"]] = (apps, mins)

w1, w2 = [], []
for p in stats:
    sa, sm = p["summary"]["appearances"], p["summary"]["minutes"]
    if sa == 0:
        continue
    d = det_by_name.get(p["name"])
    if d is None:
        w2.append(f"W2 {p['name']}: stats {sa}场/{sm}分，details 无此人")
    elif d != (sa, sm):
        w1.append(f"W1 {p['name']}: stats {sa}场/{sm}分 vs details {d[0]}场/{d[1]}分")

# ---------- W3 赛程 vs goal_details ----------
def code_to_date(c):
    s = str(c)
    return f"{s[:4]}-{s[4:6]}-{s[6:8]}" if len(s) == 8 else None

gd_by_match = {}
for g in goals:
    dt = code_to_date(g.get("match_date_code"))
    if not dt:
        continue
    gd_by_match.setdefault((dt, g.get("home_team"), g.get("away_team")), 0)
    gd_by_match[(dt, g.get("home_team"), g.get("away_team"))] += 1

w3 = []
OUR_NAMES = {"上海东亚", "上海东亚特莱士", "上海特莱士", "上海上港", "上海海港"}

def expand_goals(scorer_list):
    """scorers 条目按进球数展开：'武磊2' 代表 2 球；'王燊超'/'武磊(PK)'/'伊班(OG)' 各 1 球"""
    n = 0
    for s in scorer_list:
        m = re.match(r"^(.+?)([2-9])$", s)
        n += int(m.group(2)) if m else 1
    return n

for m in schedule:
    if m["home_team"] in OUR_NAMES:
        exp = expand_goals(m["scorers"]["home"])
    elif m["away_team"] in OUR_NAMES:
        exp = expand_goals(m["scorers"]["away"])
    else:
        continue  # 无法识别我方队名（不应出现）
    if exp == 0:
        continue  # 我方未进球，goal_details 无条目属正常
    key = (m["date"], m["home_team"], m["away_team"])
    n = gd_by_match.get(key)
    if n is None:
        # 宽松匹配：日期相同且队名互为包含
        cand = [v for (dt, h, a), v in gd_by_match.items()
                if dt == m["date"] and (m["home_team"] in h or h in m["home_team"])
                and (m["away_team"] in a or a in m["away_team"])]
        n = cand[0] if cand else 0
    if n != exp:
        w3.append(f"W3 {m['match_id']} {m['date']} {m['home_team']}{m['result']}{m['away_team']}: "
                  f"我方{exp}球, goal_details {n}条")

# ---------- 输出 ----------
def section(title, items, limit=20):
    print(f"\n{title}：{len(items)} 条")
    for x in items[:limit]:
        print("  " + x)
    if len(items) > limit:
        print(f"  … 其余 {len(items) - limit} 条略")

print("=" * 60)
print(f"已校验：stats {len(stats)} 人 / details {details.get('totalPlayers', len(det_by_name))} 人"
      f" / 赛程 {len(schedule)} 场 / goal_details {len(goals)} 球 / 年度归档 {len(annual)} 个")
section("WARN W1 stats vs details 不一致", w1)
section("WARN W2 stats 有出场但 details 无", w2)
section("WARN W3 赛程比分 vs goal_details 条数", w3)

print("\n" + "=" * 60)
if errors:
    print("硬错误：")
    for e in errors:
        print("  " + e)
    sys.exit(1)
warn_n = len(w1) + len(w2) + len(w3)
print(f"硬错误 0，警告 {warn_n}（已知历史局限见 SKILL.md）")
if "--strict" in sys.argv and warn_n:
    sys.exit(1)
sys.exit(0)
