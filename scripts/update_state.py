#!/usr/bin/env python3
"""更新状态记录（共享工具）—— 增量更新模式的状态中枢。

scripts/update_state.json 结构：
{
  "baselineDate": "2026-10-05",          # 基线日：此日(含)之前的比赛已冻结在基线文件中
  "lastMatch": {...},                    # team-a 中最新已结束比赛（含 match_id）
  "scripts": {"<脚本名>": "<最后运行时间>"},
  "processed": {"<脚本名>": ["<已增量处理过的报告文件名>", ...]}
}

规则：
- 基线留存：datafile/baseline-<YYYYMMDD>/ 保存基线日当天的三份数据文件
- 增量更新：各脚本只处理「文件日期 > baselineDate 且已结束 且 未记录在 processed」的报告
- processed 清单防止同一脚本重复累计（增量累加不幂等，必须记账）
"""
import json
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
STATE_PATH = BASE / "scripts" / "update_state.json"
TEAM_A_DIR = BASE / "public" / "data" / "team-a"
SCHED_PATH = BASE / "public" / "data" / "history_schedule.json"


def _load():
    if STATE_PATH.exists():
        try:
            with open(STATE_PATH, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save(state):
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def get_baseline_date():
    """返回基线日字符串 YYYY-MM-DD；无则返回 None。"""
    return _load().get("baselineDate")


def init_baseline(date_str=None):
    """设置基线日（若尚未设置）。返回生效的基线日。"""
    state = _load()
    if not state.get("baselineDate"):
        state["baselineDate"] = date_str or datetime.now().strftime("%Y-%m-%d")
        _save(state)
    return state["baselineDate"]


def get_processed(script_name):
    """返回某脚本已增量处理过的报告文件名集合。"""
    return set(_load().get("processed", {}).get(script_name, []))


def record_processed(script_name, filenames):
    """把本次增量处理的报告文件名记入状态（防止重复累计）。"""
    state = _load()
    done = set(state.get("processed", {}).get(script_name, []))
    done.update(filenames)
    state.setdefault("processed", {})[script_name] = sorted(done)
    _save(state)


def latest_finished_report(after_date=None):
    """返回 team-a 中最新「已结束」报告摘要；after_date 给定时只统计该日之后的。"""
    sched_index = []
    try:
        with open(SCHED_PATH, encoding="utf-8") as f:
            for r in json.load(f):
                sched_index.append(r)
    except Exception:
        pass

    best = None
    for p in sorted(TEAM_A_DIR.glob("*.json")):
        if p.stem.endswith("-MO"):
            continue
        date = p.stem[:10]
        if len(date) == 10 and date[4] == "-" and after_date and date <= after_date:
            continue
        try:
            with open(p, encoding="utf-8") as f:
                rep = json.load(f)
        except Exception:
            continue
        m = rep.get("match") or {}
        if m.get("status") not in ("已结束", "Finished", "finished"):
            continue
        d = m.get("date") or date
        if best and d <= best["date"]:
            continue
        ht, at = m.get("homeTeam") or "", m.get("awayTeam") or ""
        mid = None
        for r in sched_index:
            if r.get("date") == d and {ht, at} == {r.get("home_team"), r.get("away_team")}:
                mid = r.get("match_id")
                break
        best = {"file": p.name, "date": d, "matchId": mid,
                "competition": m.get("competition"), "round": m.get("round"),
                "homeTeam": ht, "awayTeam": at, "result": m.get("result")}
    return best


def record_run(script_name, processed_files=None):
    """脚本成功运行后调用：记录运行时间/最新比赛/已处理清单。返回最新已结束比赛。"""
    state = _load()
    lm = latest_finished_report()
    if lm:
        state["lastMatch"] = lm
    state.setdefault("scripts", {})[script_name] = datetime.now().isoformat(timespec="seconds")
    if processed_files:
        done = set(state.get("processed", {}).get(script_name, []))
        done.update(processed_files)
        state.setdefault("processed", {})[script_name] = sorted(done)
    _save(state)
    return lm


if __name__ == "__main__":
    print("baselineDate:", get_baseline_date())
    lm = latest_finished_report()
    print(json.dumps(lm, ensure_ascii=False, indent=2) if lm else "无已结束比赛")
    print("状态文件:", STATE_PATH)
