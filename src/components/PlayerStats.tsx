import React, { useState, useEffect } from 'react';

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
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selected, setSelected] = useState<PlayerHistory | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('data/player_history_stats.json');
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const jsonData = await response.json();
        setData(jsonData);
        setLoading(false);
      } catch (err) {
        console.error('Error loading player history stats:', err);
        setError('加载球员历史统计数据失败，请刷新页面重试');
        setLoading(false);
      }
    };

    fetchData();
  }, []);

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

  const selectPlayer = (player: PlayerHistory) => {
    setSelected(player);
    setSearchTerm('');
  };

  const resetSearch = () => {
    setSelected(null);
    setSearchTerm('');
  };

  if (loading) {
    return (
      <div className="card">
        <div className="card-header">
          <h2>球员数据统计</h2>
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
          <h2>球员数据统计</h2>
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

  return (
    <div className="card">
      <div className="card-header">
        <h2>球员数据统计</h2>
        <div className="player-filters" style={{ marginTop: '1rem' }}>
          <input
            type="text"
            placeholder="输入球员姓名查询..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          {selected && (
            <button className="team-tab" onClick={resetSearch} style={{ flex: 'none', padding: '0.6rem 1.2rem' }}>
              清除查询
            </button>
          )}
        </div>
      </div>

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
    </div>
  );
};

export default PlayerStats;
