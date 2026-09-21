import React, { useState, useEffect, useMemo } from 'react';

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

// 分类赛事定义
const COMPETITION_DEFS: { key: string; label: string }[] = [
  { key: 'c2l', label: '中乙联赛' },
  { key: 'c1l', label: '中甲联赛' },
  { key: 'csl', label: '中超联赛' },
  { key: 'cfa', label: '足协杯' },
  { key: 'acle', label: '亚冠联赛' },
  { key: 'supercup', label: '超级杯' },
];

const formatStat = (value: number | null | undefined): string => {
  if (value === null || value === undefined) {
    return '-';
  }
  return String(value);
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
        const scheduleJson: ScheduleMatch[] = await scheduleRes.json();
        setData(playerJson);
        setScheduleData(scheduleJson);
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
      .then((j) => setCoachShortNames(j.coaches || {}))
      .catch(() => setCoachShortNames({}));
  }, []);

  // 从历史赛程聚合主教练执教信息
  const coaches = useMemo<CoachHistory[]>(() => {
    const map = new Map<string, CoachMatch[]>();
    (scheduleData || []).forEach((m) => {
      const isHome = OUR_TEAM_NAMES.includes(m.home_team);
      const isAway = OUR_TEAM_NAMES.includes(m.away_team);
      if (!isHome && !isAway) return;

      const rawCoach = ((isHome ? m.home_coach : m.away_coach) || '').trim();
      if (!rawCoach || rawCoach === 'Unknown') return;

      const coach = normalizeCoachName(rawCoach);
      const parts = (m.result || '').split('-');
      const ourGoals = Number(isHome ? parts[0] : parts[1]);
      const theirGoals = Number(isHome ? parts[1] : parts[0]);
      const hasScore = parts.length === 2 && !Number.isNaN(ourGoals) && !Number.isNaN(theirGoals);

      if (!map.has(coach)) map.set(coach, []);
      map.get(coach).push({
        season: m.season || m.date.slice(0, 4),
        date: m.date,
        competition: m.match_type || '其他',
        round: m.round || '',
        homeAway: isHome ? '主' : '客',
        opponent: isHome ? m.away_team : m.home_team,
        score: hasScore ? `${ourGoals}-${theirGoals}` : '-',
        result: m.win_loss || (hasScore ? (ourGoals > theirGoals ? '胜' : ourGoals === theirGoals ? '平' : '负') : '-'),
      });
    });

    return Array.from(map.entries())
      .map(([name, matches]) => {
        matches.sort((a, b) => a.date.localeCompare(b.date));
        const valid = matches.filter((x) => x.result === '胜' || x.result === '平' || x.result === '负');
        const wins = valid.filter((x) => x.result === '胜').length;
        const draws = valid.filter((x) => x.result === '平').length;
        const losses = valid.filter((x) => x.result === '负').length;
        const goalsFor = matches.reduce((s, x) => s + Number(x.score.split('-')[0]) || 0, 0);
        const goalsAgainst = matches.reduce((s, x) => s + Number(x.score.split('-')[1]) || 0, 0);
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

  const renderStatTable = (rows: { label: string; block: StatBlock | undefined }[]) => {
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
                {fields.map((f) => (
                  <td key={f.key}>{formatStat(row.block ? row.block[f.key] : null)}</td>
                ))}
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
                    <td>{m.round || '-'}</td>
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
            <button className="team-tab" onClick={resetSearch} style={{ flex: 'none', padding: '0.6rem 1.2rem' }}>
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
              {renderStatTable([{ label: '总计', block: selected.summary }])}
            </div>

            <div className="stats-section">
              <h3>分类统计</h3>
              {renderStatTable(
                COMPETITION_DEFS.map((comp) => ({
                  label: comp.label,
                  block: selected[comp.key] as StatBlock | undefined,
                }))
              )}
            </div>
          </div>
        )}
        </div>
      )}
    </div>
  );
};

export default PlayerStats;
