import React, { useState, useEffect, useMemo, useRef } from 'react';

interface StatBlock {
  appearances: number | null;
  starts: number | null;
  substitute: number | null;
  minutes: number | null;
  goals: number | null;
  penalties: number | null;
  assists: number | null;
  yellowCards: number | null;
  redCards: number | null;
  goalsConceded: number | null;
  cleanSheets: number | null;
  penaltySaves: number | null;
}

interface PlayerHistory {
  name: string;
  birthDate: string;
  position: string;
  nationality: string;
  summary: StatBlock;
  [key: string]: StatBlock | string | undefined;
}

interface PlayerHistoryData {
  players: PlayerHistory[];
}

interface CoachMatch {
  season: string;
  date: string;
  competition: string;
  round: string;
  homeAway: string;
  opponent: string;
  score: string;
  result: string;
  /** 该场为代理教练临场指挥（正牌主帅停赛），记录代理教练名 */
  standin?: string;
}

interface CoachSummary {
  total: number;
  wins: number;
  draws: number;
  losses: number;
  goalsFor: number;
  goalsAgainst: number;
  winRate: number;
}

interface CoachHistory {
  name: string;
  shortName: string;
  seasons: string[];
  seasonRange: string;
  summary: CoachSummary;
  matches: CoachMatch[];
}

// 历史赛程记录（history_schedule.json）
interface ScheduleMatch {
  match_id?: string;
  season: string;
  match_type: string;
  match_name: string;
  round: string;
  date: string;
  home_team: string;
  away_team: string;
  result: string;
  win_loss: string;
  home_coach?: string;
  away_coach?: string;
  /** 代理教练名：存在时表示该场为正牌主帅停赛、由其代理临场指挥（coach 字段为正牌主帅） */
  standin_coach?: string;
}

// 进球明细（goal_details.json，仅提取所需字段）
interface GoalDetail {
  season: string;
  match_type: string;
  goal_time: string;
  goal_player: string;
  assist_player: string;
  match_date_code: number;
  match_name: string;
  home_team: string;
  home_score: number;
  away_score: number;
  away_team: string;
  match_result: string;
}

// 出场明细（player_appearance_details.json，仅提取所需字段）
interface AppAppearance {
  matchId?: string;
  date?: string;
  competition?: string;
  opponent?: string;
  score?: string;
  status?: string;
  goals?: number;
  assists?: number;
  yellowCards?: number;
  redCards?: number;
}

interface AppPlayer {
  name: string;
  seasons: { appearances: AppAppearance[] }[];
  otherCareer?: {
    nationalTeam?: { appearances: AppAppearance[] };
    espanyol?: { appearances: AppAppearance[] };
  };
}

// 统计单元格明细视图（进球/助攻/黄牌/红牌）
interface StatDetail {
  kind: 'goals' | 'assists' | 'yellowCards' | 'redCards';
  scope: string; // summary | career | 赛事key
  label: string; // 行标签（总计/中超联赛/国家队...）
}

// 我方球队历史名称（含 2012 年冠名"上海特莱士"）
const OUR_TEAM_NAMES = ['上海东亚', '上海特莱士', '上海上港', '上海海港'];

// 主教练简称映射表：从 data/short_names.json 加载（外籍教练用简称展示，未配置时回退全名）

// 教练姓名归一化：去掉"(国籍)"后缀，合并同一人的不同写法
const normalizeCoachName = (name: string): string => {
  const n = name.replace(/\(.*?\)/g, '').trim();
  if (/穆斯卡特|马斯卡特/.test(n)) {
    return '凯文·文森特·穆斯卡特';
  }
  return n;
};

const RESULT_COLORS: Record<string, string> = {
  胜: '#4caf50',
  平: '#ffaa00',
  负: '#ff4444',
};

// 统计字段定义（顺序即展示顺序）
const FIELD_DEFS: { key: keyof StatBlock; label: string }[] = [
  { key: 'appearances', label: '出场' },
  { key: 'starts', label: '首发' },
  { key: 'substitute', label: '替补' },
  { key: 'minutes', label: '分钟' },
  { key: 'goals', label: '进球' },
  { key: 'penalties', label: '点球' },
  { key: 'assists', label: '助攻' },
  { key: 'yellowCards', label: '黄牌' },
  { key: 'redCards', label: '红牌' },
  { key: 'goalsConceded', label: '失球' },
  { key: 'cleanSheets', label: '零封' },
  { key: 'penaltySaves', label: '扑点' },
];

// 门将专属字段（对非门将为 null）
const GK_KEYS: (keyof StatBlock)[] = ['goalsConceded', 'cleanSheets', 'penaltySaves'];

// 分类赛事定义（顺序即展示顺序）；国家队/西班牙人为武磊等球员的非俱乐部生涯分项（仅有个别球员有值，无值显示 -）
const COMPETITION_DEFS: { key: string; label: string }[] = [
  { key: 'c2l', label: '中乙联赛' },
  { key: 'c1l', label: '中甲联赛' },
  { key: 'csl', label: '中超联赛' },
  { key: 'cfa', label: '足协杯' },
  { key: 'acle', label: '亚冠联赛' },
  { key: 'supercup', label: '超级杯' },
  { key: 'nationalTeam', label: '国家队' },
  { key: 'espanyol', label: '西班牙人' },
];

const formatStat = (value: number | null | undefined): string => {
  if (value === null || value === undefined) {
    return '-';
  }
  return String(value);
};

// 数值字段相加合并两个统计块（null 字段保持 null，如门将专属字段）
const addStatBlocks = (a: StatBlock, b: StatBlock): StatBlock => {
  const out = { ...a };
  (Object.keys(out) as (keyof StatBlock)[]).forEach((k) => {
    const va = a[k];
    const vb = b[k];
    if (typeof va === 'number' && typeof vb === 'number') {
      out[k] = va + vb;
    }
  });
  return out;
};

// 统计范围 -> match_type 关键词（includes 匹配）；summary=俱乐部总计, career=职业生涯总计
const CLUB_SCOPE_TYPES = ['中超', '中甲', '中乙', '足协杯', '亚冠', '超级杯'];
const SCOPE_MATCH_KEYWORDS: Record<string, string[]> = {
  summary: CLUB_SCOPE_TYPES,
  career: ['中超', '中甲', '中乙', '足协杯', '亚冠', '超级杯', '国家队', '西甲', '国王杯', '欧联', '西乙'],
  c2l: ['中乙'],
  c1l: ['中甲'],
  csl: ['中超'],
  cfa: ['足协杯'],
  acle: ['亚冠'],
  supercup: ['超级杯'],
  nationalTeam: ['国家队'],
  espanyol: ['西甲', '国王杯', '欧联', '西乙'],
};

const STAT_KIND_LABELS: Record<StatDetail['kind'], string> = {
  goals: '进球',
  assists: '助攻',
  yellowCards: '黄牌',
  redCards: '红牌',
};

interface StatDetailRow {
  date: string;
  type: string;
  round: string;
  home: string;
  away: string;
  score: string;
  result: string;
  time: string;
  /** 进球球员（助攻明细用） */
  scorer?: string;
}

// 明细条数与汇总统计期望值比对（不一致时显示口径说明）；未知期望返回 -1
const statDetailCountHint = (d: StatDetail, p: PlayerHistory): number => {
  let block: StatBlock | undefined;
  if (d.scope === 'career') {
    const extras = [p.nationalTeam, p.espanyol].filter(Boolean) as StatBlock[];
    block = extras.length ? extras.reduce((acc, b) => addStatBlocks(acc, b), p.summary) : p.summary;
  } else if (d.scope === 'summary') {
    block = p.summary;
  } else {
    block = p[d.scope] as StatBlock | undefined;
  }
  const v = block ? block[d.kind] : null;
  return typeof v === 'number' ? v : -1;
};

// ===== 明细显示转换器（仅渲染层，数据文件保留原始信息）=====

// 比赛类型 -> 简称（中甲联赛->中甲、亚冠联赛->亚冠、西班牙国王杯->国王杯 等）
const shortMatchType = (t: string): string =>
  (t || '')
    .replace('亚冠精英联赛', '亚冠精英')
    .replace('亚冠联赛', '亚冠')
    .replace('西甲联赛', '西甲')
    .replace('西乙联赛', '西乙')
    .replace('西班牙国王杯', '国王杯')
    .replace('中超联赛', '中超')
    .replace('中甲联赛', '中甲')
    .replace('中乙联赛', '中乙');

// 中文数字 -> 阿拉伯数字（一~九十九）
const cn2num = (cn: string): number => {
  if (/^\d+$/.test(cn)) return Number(cn);
  const d: Record<string, number> = { 一: 1, 二: 2, 三: 3, 四: 4, 五: 5, 六: 6, 七: 7, 八: 8, 九: 9 };
  const m = cn.match(/^([一二三四五六七八九])?十([一二三四五六七八九])?$/);
  if (m) return (m[1] ? d[m[1]] : 1) * 10 + (m[2] ? d[m[2]] : 0);
  return cn in d ? d[cn] : NaN;
};

// 轮次 -> 简洁显示（数据原始值为 match_name/round，如"中甲联赛15轮"、"第十六届亚洲杯预选赛"）
const shortRound = (r: string): string => {
  if (!r || r === '-') return r || '-';
  let s = r;
  // 届数中文化数字并去掉"第"：第十六届 -> 16届
  s = s.replace(/第([一二三四五六七八九十]+)届/g, (_, cn) => `${cn2num(cn)}届`);
  // 预选赛简称：亚洲杯预选赛->亚预赛、世界杯预选赛->世预赛
  s = s.replace('亚洲杯预选赛', '亚预赛').replace('世界杯预选赛', '世预赛');
  // 杯赛阶段简称
  s = s.replace('十六分之一决赛', '1/16决赛')
    .replace('八分之一决赛', '1/8决赛')
    .replace('四分之一决赛', '1/4决赛')
    .replace('二分之一决赛', '半决赛');
  // 去掉赛事名前缀（match_name 形如"中超联赛第30轮"）
  s = s.replace(/^(中超联赛|中甲联赛|中乙联赛|亚冠精英联赛|亚冠联赛|足协杯|超级杯|西班牙国王杯|西甲联赛|西乙联赛|欧联杯)/, '');
  // 轮次规整为"第X轮"：15轮 / 第十五轮 -> 第15轮
  s = s.replace(/第?([一二三四五六七八九十]+|\d+)轮/g, (full, n) => `第${cn2num(n)}轮`);
  // 去掉 sync 生成的"次回合轮/首回合轮"尾部多余"轮"
  s = s.replace(/(首回合|次回合)轮/g, '$1');
  return s || '-';
};

// 进球时间 -> 统一分号格式：45+2 -> 45+2'
const fmtGoalTime = (t: string): string => {
  if (!t || t === '-') return t;
  const s = t.replace('’', "'");
  return s.endsWith("'") ? s : s + "'";
};

const PlayerStats: React.FC = () => {
  const [data, setData] = useState<PlayerHistoryData | null>(null);
  const [scheduleData, setScheduleData] = useState<ScheduleMatch[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selected, setSelected] = useState<PlayerHistory | null>(null);
  const [queryMode, setQueryMode] = useState<'player' | 'coach'>('player');
  const [coachSearchTerm, setCoachSearchTerm] = useState('');
  const [selectedCoach, setSelectedCoach] = useState<CoachHistory | null>(null);
  const [coachShortNames, setCoachShortNames] = useState<Record<string, string>>({});
  // 明细数据（懒加载）：goal_details（进球/助攻明细）、player_appearance_details（黄红牌明细）
  const [goalDetails, setGoalDetails] = useState<GoalDetail[] | null>(null);
  const [appearanceData, setAppearanceData] = useState<{ players: AppPlayer[] } | null>(null);
  const [statDetail, setStatDetail] = useState<StatDetail | null>(null);
  const statDetailRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [playerRes, scheduleRes] = await Promise.all([
          fetch('data/player_history_stats.json'),
          fetch('data/history_schedule.json'),
        ]);
        if (!playerRes.ok || !scheduleRes.ok) {
          throw new Error('Network response was not ok');
        }
        const playerJson = await playerRes.json();
        const scheduleJson: any = await scheduleRes.json();
        setData(playerJson);
        setScheduleData(Array.isArray(scheduleJson) ? scheduleJson : scheduleJson.matches);
        setLoading(false);
      } catch (err) {
        console.error('Error loading stats data:', err);
        setError('加载统计数据失败，请刷新页面重试');
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // 加载简称映射表（辅助数据，加载失败时回退全名，不影响页面）
  useEffect(() => {
    fetch('data/short_names.json')
      .then((r) => (r.ok ? r.json() : {}))
      .then((j: any) => setCoachShortNames(j.coaches || {}))
      .catch(() => setCoachShortNames({}));
  }, []);

  // 点击统计单元格打开明细视图（进球/助攻走 goal_details，黄红牌走出场明细），数据按需懒加载
  const openStatDetail = (kind: StatDetail['kind'], scope: string, label: string) => {
    setStatDetail({ kind, scope, label });
    if ((kind === 'goals' || kind === 'assists') && goalDetails === null) {
      fetch('data/goal_details.json')
        .then((r) => (r.ok ? r.json() : Promise.reject(new Error('fail'))))
        .then((j: GoalDetail[]) => setGoalDetails(j))
        .catch(() => setGoalDetails([]));
    }
    if ((kind === 'yellowCards' || kind === 'redCards') && appearanceData === null) {
      fetch('data/player_appearance_details.json')
        .then((r) => (r.ok ? r.json() : Promise.reject(new Error('fail'))))
        .then((j: any) => setAppearanceData({ players: j.players || [] }))
        .catch(() => setAppearanceData({ players: [] }));
    }
  };

  // 从历史赛程聚合主教练执教信息
  const coaches = useMemo<CoachHistory[]>(() => {
    const map = new Map<string, CoachMatch[]>();
    (scheduleData || []).forEach((m) => {
      const isHome = OUR_TEAM_NAMES.includes(m.home_team);
      const isAway = OUR_TEAM_NAMES.includes(m.away_team);
      if (!isHome && !isAway) return;

      const rawCoach = ((isHome ? m.home_coach : m.away_coach) || '').trim();
      if (!rawCoach || rawCoach === 'Unknown') return;

      // coach 字段始终为正牌主帅（停赛场次已归位），standin_coach 记录代理教练供展示
      const coach = normalizeCoachName(rawCoach);
      const standin = m.standin_coach;
      // 先取常规时间比分（去掉括号内点球大战等附加信息），否则含点球的比分 split('-') 长度>2 会被判为无比分
      const regScore = (m.result || '').split('(')[0].trim();
      const parts = regScore.split('-');
      const ourGoals = Number(isHome ? parts[0] : parts[1]);
      const theirGoals = Number(isHome ? parts[1] : parts[0]);
      const hasScore = parts.length === 2 && !Number.isNaN(ourGoals) && !Number.isNaN(theirGoals);

      if (!map.has(coach)) map.set(coach, []);
      map.get(coach)!.push({
        season: m.season || m.date.slice(0, 4),
        date: m.date,
        competition: m.match_type || '其他',
        round: m.round || '',
        homeAway: isHome ? '主' : '客',
        opponent: isHome ? m.away_team : m.home_team,
        score: hasScore ? `${ourGoals}-${theirGoals}` : '-',
        result: m.win_loss || (hasScore ? (ourGoals > theirGoals ? '胜' : ourGoals === theirGoals ? '平' : '负') : '-'),
        standin,
      });
    });

    return Array.from(map.entries())
      .map(([name, matches]) => {
        matches.sort((a, b) => a.date.localeCompare(b.date));
        const valid = matches.filter((x) => x.result === '胜' || x.result === '平' || x.result === '负');
        const wins = valid.filter((x) => x.result === '胜').length;
        const draws = valid.filter((x) => x.result === '平').length;
        const losses = valid.filter((x) => x.result === '负').length;
        // Number(...)||0 逐场兜底（score='-' 时记 0），避免 NaN 污染整个累加器
        const goalsFor = matches.reduce((s, x) => s + (Number(x.score.split('-')[0]) || 0), 0);
        const goalsAgainst = matches.reduce((s, x) => s + (Number(x.score.split('-')[1]) || 0), 0);
        const seasons = Array.from(new Set(matches.map((x) => x.season))).sort();
        // 执教赛季用首尾年份表示，如 2024、2024/25、2026/27 -> "2024-2026"；单赛季 -> "2024"
        const yr = (v: string) => v.slice(0, 4);
        const seasonRange =
          seasons.length > 1 ? `${yr(seasons[0])}-${yr(seasons[seasons.length - 1])}` : yr(seasons[0] || '');
        return {
          name,
          shortName: coachShortNames[name] || name,
          seasons,
          seasonRange,
          summary: {
            total: matches.length,
            wins,
            draws,
            losses,
            goalsFor,
            goalsAgainst,
            winRate: valid.length ? Math.round((wins / valid.length) * 100) : 0,
          },
          matches,
        };
      })
      .sort((a, b) => b.summary.total - a.summary.total);
  }, [scheduleData, coachShortNames]);

  // matchId -> 赛程记录索引（黄红牌明细关联比赛信息）
  const scheduleById = useMemo(() => {
    const m = new Map<string, ScheduleMatch>();
    (scheduleData || []).forEach((s) => {
      if (s.match_id) m.set(s.match_id, s);
    });
    return m;
  }, [scheduleData]);

  // 统计单元格明细行（进球/助攻来自 goal_details；黄红牌来自出场明细，海港场经 matchId 关联赛程）
  const statDetailRows = useMemo<StatDetailRow[] | null>(() => {
    if (!statDetail || !selected) return null;
    const name = selected.name;
    const keywords = SCOPE_MATCH_KEYWORDS[statDetail.scope] || [];
    const inScope = (t: string) => keywords.some((k) => t.includes(k));

    if (statDetail.kind === 'goals' || statDetail.kind === 'assists') {
      if (!goalDetails) return null; // 数据加载中
      return goalDetails
        .filter((g) => {
          if (!inScope(g.match_type)) return false;
          if (statDetail!.kind === 'goals') {
            return (g.goal_player || '').split('(')[0] === name;
          }
          return g.assist_player === name;
        })
        .sort((a, b) => a.match_date_code - b.match_date_code)
        .map((g) => ({
          date: `${String(g.match_date_code).slice(0, 4)}-${String(g.match_date_code).slice(4, 6)}-${String(g.match_date_code).slice(6, 8)}`,
          type: g.match_type,
          round: g.match_name || '',
          home: g.home_team,
          away: g.away_team,
          score: `${g.home_score}-${g.away_score}`,
          result: g.match_result,
          time: g.goal_time,
          scorer: g.goal_player,
        }));
    }

    // 黄红牌
    if (!appearanceData) return null;
    const mine = appearanceData.players.find((p) => p.name === name);
    if (!mine) return [];
    const rows: StatDetailRow[] = [];
    const kind = statDetail.kind;
    // 海港俱乐部场次（summary/career/六大赛事 scope）
    (mine.seasons || []).forEach((s) =>
      (s.appearances || []).forEach((a) => {
        const n = (a[kind] as number) || 0;
        if (n <= 0 || !a.matchId) return;
        const m = scheduleById.get(a.matchId);
        if (!m || !inScope(m.match_type)) return;
        rows.push({
          date: m.date,
          type: m.match_type,
          round: m.round || m.match_name || '',
          home: m.home_team,
          away: m.away_team,
          score: (m.result || '').split('(')[0],
          result: m.win_loss,
          time: '-',
        });
      })
    );
    // 国家队/西班牙人场次
    const oc = mine.otherCareer || {};
    const extBlocks =
      statDetail.scope === 'career'
        ? [oc.nationalTeam, oc.espanyol]
        : statDetail.scope === 'nationalTeam'
          ? [oc.nationalTeam]
          : statDetail.scope === 'espanyol'
            ? [oc.espanyol]
            : [];
    extBlocks.filter(Boolean).forEach((b) =>
      (b!.appearances || []).forEach((a) => {
        const n = (a[kind] as number) || 0;
        if (n <= 0) return;
        rows.push({
          date: a.date || '',
          type: a.competition || '',
          round: '-',
          home: b === oc.nationalTeam ? '中国' : '西班牙人',
          away: a.opponent || '',
          score: a.score || '-',
          result: '-',
          time: '-',
        });
      })
    );
    return rows.sort((x, y) => x.date.localeCompare(y.date));
  }, [statDetail, selected, goalDetails, appearanceData, scheduleById]);

  // 点击统计单元格后滚动定位到明细面板（数据懒加载完成后补滚一次，保证首开也落位）
  useEffect(() => {
    if (statDetail && statDetailRef.current) {
      statDetailRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, [statDetail, statDetailRows]);

  const switchQueryMode = (mode: 'player' | 'coach') => {
    setQueryMode(mode);
    setSelectedCoach(null);
    setCoachSearchTerm('');
    setSelected(null);
    setSearchTerm('');
  };

  // 是否展示门将专属字段（该球员存在非空的门将数据时才展示）
  const hasGoalkeeperData = (player: PlayerHistory): boolean => {
    if (GK_KEYS.some((k) => player.summary[k] !== null && player.summary[k] !== undefined)) {
      return true;
    }
    return COMPETITION_DEFS.some((comp) => {
      const block = player[comp.key] as StatBlock | undefined;
      return block && GK_KEYS.some((k) => block[k] !== null && block[k] !== undefined);
    });
  };

  const players = data?.players || [];

  const matches = searchTerm.trim()
    ? players.filter((p) => p.name && p.name.includes(searchTerm.trim()))
    : [];

  const coachMatches = coachSearchTerm.trim()
    ? coaches.filter(
        (c) =>
          (c.name && c.name.includes(coachSearchTerm.trim())) ||
          (c.shortName && c.shortName.includes(coachSearchTerm.trim()))
      )
    : [];

  const selectPlayer = (player: PlayerHistory) => {
    setSelected(player);
    setSearchTerm('');
    setStatDetail(null);
  };

  const selectCoach = (coach: CoachHistory) => {
    setSelectedCoach(coach);
    setCoachSearchTerm('');
  };

  const resetSearch = () => {
    setSelected(null);
    setSearchTerm('');
    setSelectedCoach(null);
    setCoachSearchTerm('');
    setStatDetail(null);
  };

  if (loading) {
    return (
      <div className="card">
        <div className="card-header">
          <h2>参赛统计查询</h2>
        </div>
        <div className="card-content">
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '300px' }}>
            <div style={{ fontSize: '1.2rem', color: '#c00010' }}>加载数据中...</div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="card">
        <div className="card-header">
          <h2>参赛统计查询</h2>
        </div>
        <div className="card-content">
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '300px' }}>
            <div style={{ fontSize: '1.2rem', color: '#ff4444' }}>{error || '暂无数据'}</div>
          </div>
        </div>
      </div>
    );
  }

  const renderStatTable = (rows: { label: string; block: StatBlock | undefined; scope?: string }[]) => {
    const showGK = selected ? hasGoalkeeperData(selected) : false;
    const fields = FIELD_DEFS.filter((f) => !GK_KEYS.includes(f.key) || showGK);

    return (
      <div className="table-container">
        <table className="stats-table" style={{ minWidth: fields.length * 90 }}>
          <thead>
            <tr>
              <th>赛事</th>
              {fields.map((f) => (
                <th key={f.key}>{f.label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.label}>
                <td style={{ fontWeight: 'bold', color: '#c00010' }}>{row.label}</td>
                {fields.map((f) => {
                  const val = row.block ? row.block[f.key] : null;
                  // 进球/助攻/黄红牌数值可点击查看明细（>0 且该行有统计范围）；
                  // 国家队/西班牙人的助攻除外——goal_details 仅收录武磊本人进球，其助攻队友的球无逐球记录
                  const clickable =
                    row.scope !== undefined &&
                    (f.key === 'goals' || f.key === 'assists' || f.key === 'yellowCards' || f.key === 'redCards') &&
                    typeof val === 'number' &&
                    val > 0 &&
                    !(f.key === 'assists' && (row.scope === 'nationalTeam' || row.scope === 'espanyol'));
                  return (
                    <td key={f.key}>
                      {clickable ? (
                        <a
                          onClick={() => openStatDetail(f.key as StatDetail['kind'], row.scope!, row.label)}
                          style={{ color: '#c00010', fontWeight: 'bold', cursor: 'pointer', textDecoration: 'underline' }}
                          title={`查看${STAT_KIND_LABELS[f.key as StatDetail['kind']]}明细`}
                        >
                          {val}
                        </a>
                      ) : (
                        formatStat(val)
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const renderCoachDetail = (coach: CoachHistory) => {
    const s = coach.summary;
    return (
      <div>
        <div className="team-overview">
          <div className="overview-item">
            <span className="overview-label">主教练</span>
            <span className="overview-value" title={coach.name}>
              {coach.shortName}
            </span>
          </div>
          <div className="overview-item">
            <span className="overview-label">执教赛季</span>
            <span className="overview-value" style={{ whiteSpace: 'nowrap' }} title={coach.seasons.join('、')}>{coach.seasonRange}</span>
          </div>
          <div className="overview-item">
            <span className="overview-label">场次</span>
            <span className="overview-value">{s.total}</span>
          </div>
          <div className="overview-item">
            <span className="overview-label">胜/平/负</span>
            <span className="overview-value">{s.wins}/{s.draws}/{s.losses}</span>
          </div>
          <div className="overview-item">
            <span className="overview-label">进/失球</span>
            <span className="overview-value">{s.goalsFor}/{s.goalsAgainst}</span>
          </div>
          <div className="overview-item">
            <span className="overview-label">胜率</span>
            <span className="overview-value">{s.winRate}%</span>
          </div>
        </div>

        <div className="stats-section">
          <h3>执教比赛（{s.total} 场）</h3>
          <div className="table-container">
            <table className="stats-table" style={{ minWidth: 700 }}>
              <thead>
                <tr>
                  <th>日期</th>
                  <th>赛季</th>
                  <th>赛事</th>
                  <th>轮次</th>
                  <th>主/客</th>
                  <th>对手</th>
                  <th>比分</th>
                  <th>结果</th>
                </tr>
              </thead>
              <tbody>
                {[...coach.matches].reverse().map((m, idx) => (
                  <tr key={`${m.date}-${idx}`}>
                    <td>{m.date}</td>
                    <td>{m.season}</td>
                    <td style={{ fontWeight: 'bold', color: '#c00010' }}>{m.competition}</td>
                    <td>
                      {m.round || '-'}
                      {m.standin && (
                        <div style={{ fontSize: '0.75rem', color: '#888', fontWeight: 'normal' }} title="正牌主帅停赛，代理临场指挥">
                          {m.standin} 代理
                        </div>
                      )}
                    </td>
                    <td>{m.homeAway}</td>
                    <td style={{ fontWeight: 'bold', color: '#fff' }}>{m.opponent}</td>
                    <td>{m.score}</td>
                    <td style={{ fontWeight: 'bold', color: RESULT_COLORS[m.result] || '#fff' }}>{m.result}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2>参赛统计查询</h2>
        <div className="team-tabs" style={{ marginTop: '1rem' }}>
          <button
            className={`team-tab ${queryMode === 'player' ? 'active' : ''}`}
            onClick={() => switchQueryMode('player')}
          >
            <span className="tab-icon">👟</span>
            <span className="tab-text">球员查询</span>
          </button>
          <button
            className={`team-tab ${queryMode === 'coach' ? 'active' : ''}`}
            onClick={() => switchQueryMode('coach')}
          >
            <span className="tab-icon">🎯</span>
            <span className="tab-text">主教练查询</span>
          </button>
        </div>
        <div className="player-filters">
          {queryMode === 'player' ? (
            <input
              type="text"
              placeholder="输入球员姓名查询..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
          ) : (
            <input
              type="text"
              placeholder="输入主教练姓名查询..."
              value={coachSearchTerm}
              onChange={(e) => setCoachSearchTerm(e.target.value)}
              className="search-input"
            />
          )}
          {(selected || selectedCoach) && (
            <button className="team-tab" onClick={resetSearch} style={{ flex: 'none', padding: '0 1.2rem', height: '48px', boxSizing: 'border-box', justifyContent: 'center' }}>
              清除查询
            </button>
          )}
        </div>
      </div>

      {queryMode === 'coach' ? (
        <div className="card-content">
          {!selectedCoach && (
            <div>
              {coachSearchTerm.trim() === '' ? (
                <div style={{ textAlign: 'center', color: '#888', padding: '2rem 0' }}>
                  请输入主教练姓名进行查询
                </div>
              ) : coachMatches.length > 0 ? (
                <div className="stats-section">
                  <h3>查询结果（{coachMatches.length} 人）</h3>
                  <div className="table-container">
                    <table style={{ minWidth: 600 }}>
                      <thead>
                        <tr>
                          <th>姓名</th>
                          <th>执教赛季</th>
                          <th>场次</th>
                          <th>胜/平/负</th>
                          <th>胜率</th>
                        </tr>
                      </thead>
                      <tbody>
                        {coachMatches.map((coach) => (
                          <tr
                            key={coach.name}
                            onClick={() => selectCoach(coach)}
                            style={{ cursor: 'pointer' }}
                            title="点击查看执教比赛"
                          >
                            <td style={{ fontWeight: 'bold', color: '#fff' }} title={coach.name}>{coach.shortName}</td>
                            <td title={coach.seasons.join('、')}>{coach.seasonRange}</td>
                            <td>{coach.summary.total}</td>
                            <td>{coach.summary.wins}/{coach.summary.draws}/{coach.summary.losses}</td>
                            <td>{coach.summary.winRate}%</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ) : (
                <div style={{ textAlign: 'center', color: '#888', padding: '2rem 0' }}>
                  未找到匹配的主教练，请检查姓名
                </div>
              )}
            </div>
          )}

          {selectedCoach && renderCoachDetail(selectedCoach)}
        </div>
      ) : (
        <div className="card-content">
        {!selected && (
          <div>
            {searchTerm.trim() === '' ? (
              <div style={{ textAlign: 'center', color: '#888', padding: '2rem 0' }}>
                请输入球员姓名进行查询
              </div>
            ) : matches.length > 0 ? (
              <div className="stats-section">
                <h3>查询结果（{matches.length} 人）</h3>
                <div className="table-container">
                  <table style={{ minWidth: 500 }}>
                    <thead>
                      <tr>
                        <th>姓名</th>
                        <th>位置</th>
                        <th>国籍</th>
                        <th>出生日期</th>
                      </tr>
                    </thead>
                    <tbody>
                      {matches.map((player) => (
                        <tr
                          key={player.name}
                          onClick={() => selectPlayer(player)}
                          style={{ cursor: 'pointer' }}
                          title="点击查看详情"
                        >
                          <td style={{ fontWeight: 'bold', color: '#fff' }}>{player.name}</td>
                          <td>{player.position || '-'}</td>
                          <td>{player.nationality || '-'}</td>
                          <td>{player.birthDate || '-'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : (
              <div style={{ textAlign: 'center', color: '#888', padding: '2rem 0' }}>
                未找到匹配的球员，请检查姓名
              </div>
            )}
          </div>
        )}

        {selected && (
          <div>
            <div className="team-overview">
              <div className="overview-item">
                <span className="overview-label">姓名</span>
                <span className="overview-value">{selected.name}</span>
              </div>
              <div className="overview-item">
                <span className="overview-label">位置</span>
                <span className="overview-value">{selected.position || '-'}</span>
              </div>
              <div className="overview-item">
                <span className="overview-label">国籍</span>
                <span className="overview-value">{selected.nationality || '-'}</span>
              </div>
              <div className="overview-item">
                <span className="overview-label">出生日期</span>
                <span className="overview-value">{selected.birthDate || '-'}</span>
              </div>
            </div>

            <div className="stats-section" style={{ marginBottom: '1.5rem' }}>
              <h3>汇总统计</h3>
              {(() => {
                // 含国家队/留洋数据的球员（目前仅武磊）分列俱乐部总计与职业生涯总计
                const extraBlocks = [selected.nationalTeam, selected.espanyol].filter(Boolean) as StatBlock[];
                if (extraBlocks.length === 0) {
                  return renderStatTable([{ label: '总计', block: selected.summary, scope: 'summary' }]);
                }
                const careerTotal = extraBlocks.reduce((acc, b) => addStatBlocks(acc, b), selected.summary);
                return renderStatTable([
                  { label: '俱乐部总计', block: selected.summary, scope: 'summary' },
                  { label: '职业生涯总计', block: careerTotal, scope: 'career' },
                ]);
              })()}
            </div>

            <div className="stats-section">
              <h3>分类统计</h3>
              {renderStatTable(
                COMPETITION_DEFS.map((comp) => ({
                  label: comp.label,
                  block: selected[comp.key] as StatBlock | undefined,
                  scope: comp.key,
                }))
              )}
            </div>

            {statDetail && (
              <div className="stats-section" ref={statDetailRef}>
                <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  {selected.name} · {statDetail.label} · {STAT_KIND_LABELS[statDetail.kind]}明细
                  {statDetailRows ? `（${statDetailRows.length} 条）` : ''}
                  <span
                    onClick={() => setStatDetail(null)}
                    style={{ cursor: 'pointer', color: '#888', fontWeight: 'normal', fontSize: '0.9rem', padding: '0 0.4rem' }}
                    title="关闭明细"
                  >
                    ×
                  </span>
                </h3>
                {statDetailRows === null ? (
                  <div style={{ textAlign: 'center', color: '#888', padding: '1.5rem 0' }}>明细数据加载中...</div>
                ) : statDetailRows.length === 0 ? (
                  <div style={{ textAlign: 'center', color: '#888', padding: '1.5rem 0' }}>无明细记录</div>
                ) : (
                  <div>
                    {(() => {
                      const hint = statDetailCountHint(statDetail, selected);
                      return hint >= 0 && statDetailRows.length !== hint;
                    })() && (
                      <div style={{ fontSize: '0.8rem', color: '#888', marginBottom: '0.5rem' }}>
                        注：明细来自逐球/逐场收录，早期历史个别记录未收录明细，条数可能与汇总统计略有差异
                      </div>
                    )}
                    <div className="table-container stat-detail-scroll">
                    <table className="stats-table" style={{ minWidth: 800 }}>
                      <thead>
                        <tr>
                          <th>序号</th>
                          <th>比赛日期</th>
                          <th>比赛类型</th>
                          <th>轮次</th>
                          <th>主队</th>
                          <th>比分</th>
                          <th>客队</th>
                          <th>赛果</th>
                          {statDetail.kind === 'assists' && <th>进球球员</th>}
                          {(statDetail.kind === 'goals' || statDetail.kind === 'assists') && <th>进球时间</th>}
                        </tr>
                      </thead>
                      <tbody>
                        {statDetailRows.map((r, idx) => (
                          <tr key={`${r.date}-${idx}`}>
                            <td>{idx + 1}</td>
                            <td>{r.date}</td>
                            <td style={{ fontWeight: 'bold', color: '#c00010' }}>{shortMatchType(r.type)}</td>
                            <td>{shortRound(r.round)}</td>
                            <td>{r.home}</td>
                            <td>{r.score}</td>
                            <td>{r.away}</td>
                            <td style={{ fontWeight: 'bold', color: r.result === '胜' ? '#c00010' : r.result === '负' ? '#4caf50' : '#fff' }}>{r.result}</td>
                            {statDetail.kind === 'assists' && <td style={{ fontWeight: 'bold', color: '#fff' }}>{r.scorer || '-'}</td>}
                            {(statDetail.kind === 'goals' || statDetail.kind === 'assists') && <td>{fmtGoalTime(r.time)}</td>}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
        </div>
      )}
    </div>
  );
};

export default PlayerStats;
