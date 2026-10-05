#!/usr/bin/env python3
"""
从 public/data/team-a/*.json 比赛报告更新球员出场明细（默认增量模式，--full 为全量重建）。

输出：
1. public/data/player_appearance_details.json —— 当季赛季节点（matchId 关联 history_schedule.json）
2. public/data/history/<年份>/<年份>-出场记录.json —— 年度文件（与其他年份同构，附 matchId）

【增量模式（默认）】
- 基线：当前两份输出文件本身（基线留存见 datafile/baseline-<日期>/）
- 只处理「文件日期 > scripts/update_state.json 的 baselineDate 且已结束且未在 processed 清单」的新报告
- details 当季节点按 matchId 追加；年度文件 matches/球员记录按场追加
- 已处理文件记录于 update_state.json 的 processed 清单，防止重复累计

【全量重建 --full（仅数据修复用，会覆盖当季节点与年度文件）】
- 解析全部已结束报告重建当季数据

口径与 update_player_history_stats.py 保持一致：
- 首发 = lineups.{role}.players[]；替补登场 = substitutes[]/bench[] 中带 substitutedAt（或 minutes>0）
- 替补分钟按 90 - substitutedAt 估算；首发分钟取报告值
- 别名映射 ALIAS_MAP 同步（让克劳德->克劳德 / 维塔尔->马特乌斯·维塔尔 / 吾米提江->吾米提江.玉苏普）
"""
import json
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path(r"d:\Workspace\shanghaiport-fc-app")
DATA_DIR = BASE_DIR / "public" / "data"
TEAM_A_DIR = DATA_DIR / "team-a"
SCHED_PATH = DATA_DIR / "history_schedule.json"
DETAIL_PATH = DATA_DIR / "player_appearance_details.json"
HIST_DIR = DATA_DIR / "history"

SHANGHAI_PORT = "上海海港"
ALIAS_MAP = {
    "让克劳德": "克劳德",
    "维塔尔": "马特乌斯·维塔尔",
    "吾米提江": "吾米提江.玉苏普",
    # 历史名单错别字（2007 中乙名单"柏佳俊"，实名柏佳骏，生日相同）
    "柏佳俊": "柏佳骏",
    # 报告/名单简写 -> 全名
    "阿布拉汗": "阿布拉汗·哈力克",
}


def std_name(name):
    return ALIAS_MAP.get(name, name)


def is_first_team(name):
    return name == SHANGHAI_PORT or (name.startswith(SHANGHAI_PORT) and "富盛" not in name)


def to_int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0


def load_json(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def dump_json(obj, p):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def bench_of(team):
    b = team.get("substitutes")
    if b is None:
        b = team.get("bench", [])
    return b or []


def parse_team_a_reports(files=None):
    """返回 {season: [block, ...]}；files 给定时只解析指定文件（增量模式）。"""
    seasons = defaultdict(list)
    paths = sorted(TEAM_A_DIR.glob("*.json")) if files is None else sorted(files)
    for path in paths:
        if path.stem.endswith("-MO"):
            continue
        try:
            report = load_json(path)
        except Exception as e:
            print(f"  [跳过] {path.name}: {e}")
            continue
        m = report.get("match", {}) or {}
        if m.get("status") not in ("已结束", "Finished", "finished"):
            continue
        lu = report.get("lineups", {}) or {}
        h, a = lu.get("home", {}) or {}, lu.get("away", {}) or {}
        if is_first_team(h.get("name", "")):
            role, opp_side = "home", a
        elif is_first_team(a.get("name", "")):
            role, opp_side = "away", h
        else:
            continue
        team = lu.get(role, {}) or {}
        season = str(m.get("season") or path.stem[:4]).split("-")[0].split("/")[0]

        subs = []
        for ev in report.get("matchTimeline", []) or []:
            if ev.get("type") == "substitution" and ev.get("team") == role:
                minute = to_int(ev.get("minute")) + to_int(ev.get("minute_extra") or 0)
                subs.append({"minute": minute,
                             "playerOut": std_name(ev.get("playerOut") or ""),
                             "playerIn": std_name(ev.get("playerIn") or "")})
        off_at = {s["playerOut"]: s["minute"] for s in subs if s["playerOut"]}
        on_at = {s["playerIn"]: s["minute"] for s in subs if s["playerIn"]}

        lineup, bench, apps = [], [], []
        for p in team.get("players", []) or []:
            nm = std_name(p.get("name", ""))
            lineup.append({
                "number": to_int(p.get("number")), "name": nm,
                "offAt": off_at.get(nm),
                "yellowCards": to_int(p.get("yellowCards")),
                "redCards": to_int(p.get("redCards")),
            })
            apps.append({"name": nm, "status": "出场", "minutes": to_int(p.get("minutes")),
                         "position": p.get("position"), "nationality": p.get("nationality"),
                         "number": to_int(p.get("number"))})
        for p in bench_of(team):
            nm = std_name(p.get("name", ""))
            on_min = on_at.get(nm)
            if on_min is None and p.get("substitutedAt") is not None:
                on_min = to_int(p.get("substitutedAt"))
            played = on_min is not None or to_int(p.get("minutes")) > 0
            minutes = max(0, 90 - on_min) if on_min is not None else to_int(p.get("minutes"))
            bench.append({
                "number": to_int(p.get("number")), "name": nm, "onAt": on_min,
                "yellowCards": to_int(p.get("yellowCards")),
                "redCards": to_int(p.get("redCards")),
            })
            apps.append({"name": nm, "status": "出场" if played else "替补",
                         "minutes": minutes if played else 0,
                         "position": p.get("position"), "nationality": p.get("nationality"),
                         "number": to_int(p.get("number"))})

        seasons[season].append({
            "file": path.name, "date": m.get("date"), "round": m.get("round"),
            "competition_raw": m.get("competition"),
            "homeAway": "主场" if role == "home" else "客场",
            "opponent": opp_side.get("name", ""),
            "lineup": lineup, "substitutes": bench,
            "substitutions": sorted(subs, key=lambda s: s["minute"]),
            "appearances": apps,
        })
    return seasons


def candidate_match_types(block, schedule, season):
    """报告可能对应的 schedule match_type 候选（按可能性排序）"""
    raw = (block["competition_raw"] or "") + block["file"]
    types_in_season = {r["match_type"] for r in schedule if r["season"].split("/")[0] == season}
    cands = []
    if "超级杯" in raw:
        cands.append("超级杯")
    if "中超" in raw or "超级联赛" in raw:
        cands.append("中超联赛")
    if "足协杯" in raw or "协会杯" in raw:
        cands.append("足协杯")
    if "亚冠" in raw:
        cands += [t for t in ("亚冠精英联赛", "亚冠联赛") if t in types_in_season]
    if "中甲" in raw:
        cands.append("中甲联赛")
    if "中乙" in raw:
        cands.append("中乙联赛")
    cands += sorted(types_in_season)
    seen, out = set(), []
    for c in cands:
        if c and c not in seen:
            seen.add(c)
            out.append(c)
    return out


def opponent_close(opp, rec):
    for x in (rec.get("home_team"), rec.get("away_team")):
        if x and opp and (x in opp or opp in x):
            return True
    return False


def link_match_ids(seasons, schedule):
    idx_sd, idx_d = defaultdict(list), defaultdict(list)
    for r in schedule:
        idx_sd[(r["season"].split("/")[0], r["match_type"], r.get("date"))].append(r)
        idx_d[(r["match_type"], r.get("date"))].append(r)
    n_ok = n_miss = 0
    for season, blocks in seasons.items():
        for b in blocks:
            found = None
            for mt in candidate_match_types(b, schedule, season):
                pool = idx_sd.get((season, mt, b["date"])) or idx_d.get((mt, b["date"])) or []
                pool = [r for r in pool if opponent_close(b["opponent"], r)]
                if pool:
                    found = pool[0]
                    break
            b["matchId"] = found["match_id"] if found else None
            b["matchType"] = found["match_type"] if found else (b["competition_raw"] or "")
            if found:
                n_ok += 1
            else:
                n_miss += 1
                print(f"  [未关联] {b['file']} {b['date']} {b['opponent']}")
    return n_ok, n_miss


def match_entry_of(b):
    return {
        "competition": b["matchType"], "round": b["round"], "date": b["date"],
        "opponent": b["opponent"], "homeAway": b["homeAway"], "matchId": b["matchId"],
        "lineup": b["lineup"], "substitutes": b["substitutes"],
        "substitutions": b["substitutions"],
    }


def increment_year_file(yf, blocks, stats_meta):
    """把新比赛块追加到现有年度文件（按 matchId/日期+对手去重）。返回已处理的文件名。"""
    existing = {m.get("matchId") for m in yf["matches"]} | \
               {(m.get("date"), m.get("opponent")) for m in yf["matches"]}
    by_name = {p["name"]: p for p in yf["players"]}
    handled = []
    for b in blocks:
        if b["matchId"] in existing or (b["date"], b["opponent"]) in existing:
            continue
        existing.add(b["matchId"])
        existing.add((b["date"], b["opponent"]))
        yf["matches"].append(match_entry_of(b))
        if b["matchType"] not in yf.get("competitions", []):
            yf.setdefault("competitions", []).append(b["matchType"])
        for a in b["appearances"]:
            nm = a["name"]
            yp = by_name.get(nm)
            if yp is None:
                meta = stats_meta.get(nm) or {}
                yp = {"number": a.get("number"), "name": nm,
                      "birthDate": meta.get("birthDate") or "",
                      "position": a.get("position") or meta.get("position"),
                      "nationality": a.get("nationality") or meta.get("nationality"),
                      "stats": {}, "appearances": []}
                yf["players"].append(yp)
                by_name[nm] = yp
            yp["appearances"].append({
                "competition": b["matchType"], "round": b["round"], "date": b["date"],
                "opponent": b["opponent"], "homeAway": b["homeAway"],
                "status": a["status"], "minutes": a["minutes"],
            })
            in_lineup = any(l["name"] == nm for l in b["lineup"])
            came_on = any(s["name"] == nm and s.get("onAt") is not None for s in b["substitutes"])
            if not (in_lineup or came_on):
                continue
            c = yp["stats"].setdefault(
                b["matchType"], {"totalAppearances": 0, "starts": 0, "substitutes": 0,
                                 "minutes": 0, "goals": 0, "assists": 0,
                                 "yellowCards": 0, "redCards": 0})
            c["totalAppearances"] += 1
            c["starts" if in_lineup else "substitutes"] += 1
            c["minutes"] += a["minutes"]
        handled.append(b["file"])
    yf["matches"].sort(key=lambda m: (m.get("date") or "", m.get("matchId") or ""))
    yf["players"].sort(key=lambda p: (-sum(s["minutes"] for s in p.get("stats", {}).values()),
                                      p["name"]))
    return handled


def main(full=False):
    import update_state

    baseline = update_state.init_baseline()
    done = update_state.get_processed("update_player_appearance_details.py")
    schedule = load_json(SCHED_PATH)

    if full:
        seasons = parse_team_a_reports()
        print(f"全量重建模式: team-a 已结束比赛 {sum(len(v) for v in seasons.values())} 场")
    else:
        todo = []
        for p in sorted(TEAM_A_DIR.glob("*.json")):
            if "-MO" in p.stem or p.name in done:
                continue
            if p.stem[:10] <= baseline:
                continue
            todo.append(p)
        seasons = parse_team_a_reports(files=todo)
        total = sum(len(v) for v in seasons.values())
        if not total:
            print(f"增量模式：基线日 {baseline} 之后无新比赛，跳过（如需重建请加 --full）")
            update_state.record_run("update_player_appearance_details.py")
            return
        print(f"增量模式：基线日 {baseline}，待处理新报告 {total} 个")

    n_ok, n_miss = link_match_ids(seasons, schedule)
    print(f"match_id 关联: 成功 {n_ok}, 未关联 {n_miss}")

    detail = load_json(DETAIL_PATH)
    stats = load_json(DATA_DIR / "player_history_stats.json")
    stats_meta = {p["name"]: p for p in stats["players"]}
    handled_files = []

    for season in sorted(seasons):
        blocks = sorted(seasons[season], key=lambda b: (b["date"] or "", b["file"]))
        year_path = HIST_DIR / season / f"{season}-出场记录.json"

        # ---- 1) 年度文件 ----
        if not full and year_path.exists():
            year_file = load_json(year_path)
            handled_files += increment_year_file(year_file, blocks, stats_meta)
            dump_json(year_file, year_path)
            print(f"[{season}] 年度文件增量追加: {len(handled_files)} 场")
        else:
            agg = {}
            comp_set = []
            for b in blocks:
                if b["matchType"] not in comp_set:
                    comp_set.append(b["matchType"])
                for a in b["appearances"]:
                    ent = agg.setdefault(a["name"], {"apps": [], "numbers": defaultdict(int),
                                                     "positions": defaultdict(int),
                                                     "nationalities": defaultdict(int)})
                    ent["apps"].append({"block": b, "status": a["status"], "minutes": a["minutes"]})
                    if a.get("number"):
                        ent["numbers"][a["number"]] += 1
                    if a.get("position"):
                        ent["positions"][a["position"]] += 1
                    if a.get("nationality"):
                        ent["nationalities"][a["nationality"]] += 1

            year_players = []
            for nm, ent in agg.items():
                meta = stats_meta.get(nm) or {}
                year_players.append({
                    "number": max(ent["numbers"], key=ent["numbers"].get) if ent["numbers"] else None,
                    "name": nm,
                    "birthDate": meta.get("birthDate") or "",
                    "position": (max(ent["positions"], key=ent["positions"].get)
                                 if ent["positions"] else meta.get("position")),
                    "nationality": (max(ent["nationalities"], key=ent["nationalities"].get)
                                    if ent["nationalities"] else meta.get("nationality")),
                    "stats": {},
                    "appearances": [{
                        "competition": x["block"]["matchType"], "round": x["block"]["round"],
                        "date": x["block"]["date"], "opponent": x["block"]["opponent"],
                        "homeAway": x["block"]["homeAway"], "status": x["status"],
                        "minutes": x["minutes"],
                    } for x in ent["apps"]],
                })
                for b in blocks:
                    in_lineup = any(l["name"] == nm for l in b["lineup"])
                    came_on = any(s["name"] == nm and s.get("onAt") is not None
                                  for s in b["substitutes"])
                    if not (in_lineup or came_on):
                        continue
                    c = year_players[-1]["stats"].setdefault(
                        b["matchType"], {"totalAppearances": 0, "starts": 0, "substitutes": 0,
                                         "minutes": 0, "goals": 0, "assists": 0,
                                         "yellowCards": 0, "redCards": 0})
                    c["totalAppearances"] += 1
                    c["starts" if in_lineup else "substitutes"] += 1
                    c["minutes"] += next(x["minutes"] for x in ent["apps"] if x["block"] is b)
            year_players.sort(key=lambda p: (-sum(s["minutes"] for s in p["stats"].values()),
                                             p["name"]))
            year_file = {
                "season": season, "team": SHANGHAI_PORT, "competitions": comp_set,
                "dataNote": "由 public/data/team-a 比赛报告生成；替补登场分钟按 90-登场时间估算；"
                            "matchId 对应 history_schedule.json",
                "players": year_players,
                "matches": [match_entry_of(b) for b in blocks],
            }
            year_path.parent.mkdir(parents=True, exist_ok=True)
            dump_json(year_file, year_path)
            handled_files += [b["file"] for b in blocks]
            print(f"[{season}] 年度文件重建: {len(blocks)} 场 / {len(year_players)} 名球员")

        # ---- 2) player_appearance_details.json ----
        by_name = defaultdict(list)
        for p in detail["players"]:
            by_name[p["name"]].append(p)
        if full:
            for yp_name in {a["name"] for b in blocks for a in b["appearances"]}:
                apps = [{"matchId": b["matchId"], "status": a["status"], "minutes": a["minutes"]}
                        for b in blocks for a in b["appearances"] if a["name"] == yp_name]
                _upsert_player_season(detail, by_name, yp_name, season, apps, stats_meta)
        else:
            for b in blocks:
                if not b["matchId"]:
                    continue
                for a in b["appearances"]:
                    _append_detail_appearance(detail, by_name, a["name"], season,
                                              b["matchId"], a, stats_meta)

    # 重算汇总
    for p in detail["players"]:
        played = sum(1 for sn in p["seasons"] for a in sn["appearances"] if a["status"] == "出场")
        minutes = sum(a["minutes"] for sn in p["seasons"] for a in sn["appearances"])
        p["records"] = {"knownAppearances": played, "knownMinutes": minutes}
        p["seasons"].sort(key=lambda s: s["season"])
    detail["players"].sort(key=lambda x: (-x["records"]["knownMinutes"], x["name"]))
    detail["totalPlayers"] = len(detail["players"])
    detail["totalAppearanceEntries"] = sum(len(sn["appearances"]) for p in detail["players"]
                                           for sn in p["seasons"])
    all_seasons_seen = {sn["season"] for p in detail["players"] for sn in p["seasons"]}
    detail["seasonRange"] = min(all_seasons_seen) + "-" + max(all_seasons_seen)
    dump_json(detail, DETAIL_PATH)
    print(f"player_appearance_details.json 已更新: {detail['totalPlayers']} 球员 / "
          f"{detail['totalAppearanceEntries']} 条出场记录")

    lm = update_state.record_run("update_player_appearance_details.py",
                                 processed_files=handled_files)
    if lm:
        print(f"状态已记录 (scripts/update_state.json): 更新至 {lm['date']} {lm['competition']} "
              f"{lm['round']} ({lm.get('matchId')})")


def _ensure_detail_player(detail, by_name, name, stats_meta):
    cands = by_name.get(name, [])
    if cands:
        return cands[0] if len(cands) == 1 else cands[0]
    meta = stats_meta.get(name) or {}
    target = {"name": name, "birthDate": meta.get("birthDate") or "",
              "position": meta.get("position") or "", "nationality": meta.get("nationality") or "",
              "records": {"knownAppearances": 0, "knownMinutes": 0}, "seasons": []}
    detail["players"].append(target)
    by_name[name].append(target)
    return target


def _append_detail_appearance(detail, by_name, name, season, match_id, app, stats_meta):
    target = _ensure_detail_player(detail, by_name, name, stats_meta)
    sn = next((s for s in target["seasons"] if s["season"] == season), None)
    if sn is None:
        sn = {"season": season, "team": SHANGHAI_PORT, "appearances": []}
        target["seasons"].append(sn)
    if any(x["matchId"] == match_id for x in sn["appearances"]):
        return  # 该场已入账，防重复
    sn["appearances"].append({"matchId": match_id, "status": app["status"],
                              "minutes": app["minutes"]})


def _upsert_player_season(detail, by_name, name, season, apps, stats_meta):
    """全量模式：整季替换该球员的当季节点。"""
    target = _ensure_detail_player(detail, by_name, name, stats_meta)
    target["seasons"] = [s for s in target["seasons"] if s["season"] != season]
    target["seasons"].append({"season": season, "team": SHANGHAI_PORT, "appearances": apps})


if __name__ == "__main__":
    import sys
    main(full="--full" in sys.argv)
