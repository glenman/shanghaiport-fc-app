import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';

interface StatDetail {
  match: string;
  date: string;
  time: string;
  opponent: string;
  reason?: string;
  type?: string;
}

interface PlayerStat {
  rank: number;
  name: string;
  number: number;
  position: string;
  goals: number;
  assists: number;
  yellowCards: number;
  redCards: number;
  matches: number;
  minutes: number;
  details?: StatDetail[];
}

interface CompetitionStats {
  matchesPlayed: number;
  record: string;
  goalsFor: number;
  goalsAgainst: number;
  points: number;
  topScorers: PlayerStat[];
  topAssists: PlayerStat[];
  yellowCards: PlayerStat[];
  redCards: PlayerStat[];
}

interface TeamStats {
  teamName: string;
  matchesPlayed: number;
  record: string;
  goalsFor: number;
  goalsAgainst: number;
  points: number;
  topScorers: PlayerStat[];
  topAssists: PlayerStat[];
  yellowCards: PlayerStat[];
  redCards: PlayerStat[];
  competitions?: Record<string, CompetitionStats>;
}

interface CurrentStatsData {
  lastUpdated: string;
  season: string;
  firstTeam: TeamStats;
  bTeam: TeamStats;
}

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  playerName: string;
  playerNumber: number;
  statType: 'goals' | 'assists' | 'yellowCards' | 'redCards';
  details: StatDetail[];
  clickY: number;
}

const StatDetailModal: React.FC<ModalProps> = ({ isOpen, onClose, title, playerName, playerNumber, statType, details, clickY }) => {
  if (!isOpen) return null;

  const statLabel = {
    'goals': '进球',
    'assists': '助攻',
    'yellowCards': '黄牌',
    'redCards': '红牌'
  }[statType];

  const statIcon = {
    'goals': '⚽',
    'assists': '🅰️',
    'yellowCards': '🟨',
    'redCards': '🟥'
  }[statType];

  const viewportHeight = window.innerHeight;
  let top = clickY + 10;
  if (top + 200 > viewportHeight) {
    top = clickY - 210;
  }
  if (top < 10) {
    top = 10;
  }

  // 计算main区域（.app-content）的中心位置
  const getMainCenterX = () => {
    const mainElement = document.querySelector('.app-content');
    if (mainElement) {
      const rect = mainElement.getBoundingClientRect();
      return rect.left + rect.width / 2;
    }
    return window.innerWidth / 2;
  };

  const mainCenterX = getMainCenterX();

  const modalContent = (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal-content modal-content-compact"
        onClick={(e) => e.stopPropagation()}
        style={{
          position: 'fixed',
          left: `${mainCenterX}px`,
          top: `${top}px`,
          transform: 'translateX(-50%)',
          zIndex: 1001
        }}
      >
        <div className="modal-header">
          <h3>{statIcon} {playerName} 的{statLabel}记录</h3>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        <div className="modal-body modal-body-compact">
          {details.length > 0 ? (
            <div className="detail-list-compact">
              {details.map((detail, index) => (
                <div key={index} className="detail-item-compact">
                  <span className="detail-round">{detail.match}</span>
                  <span className="detail-date">{detail.date}</span>
                  <span className="detail-opponent">vs {detail.opponent}</span>
                  <span className="detail-time">
                    {detail.time}
                    {detail.type === '点球' && <span style={{ color: '#4ecdc4', fontWeight: 'bold', marginLeft: '4px' }}>(P)</span>}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="modal-empty">暂无详细记录</div>
          )}
        </div>
      </div>
    </div>
  );

  return ReactDOM.createPortal(modalContent, document.body);
};

const CurrentStats: React.FC = () => {
  const [data, setData] = useState<CurrentStatsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTeam, setActiveTeam] = useState<'firstTeam' | 'bTeam'>('firstTeam');
  const [activeCompetition, setActiveCompetition] = useState<string>('中国足球协会超级联赛');
  const [competitionsMapping, setCompetitionsMapping] = useState<Record<string, { shortName: string; type: string }>>({});
  const [modalInfo, setModalInfo] = useState<{
    isOpen: boolean;
    title: string;
    playerName: string;
    playerNumber: number;
    statType: 'goals' | 'assists' | 'yellowCards' | 'redCards';
    details: StatDetail[];
    clickY: number;
  }>({
    isOpen: false,
    title: '',
    playerName: '',
    playerNumber: 0,
    statType: 'goals',
    details: [],
    clickY: 0
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        // 加载比赛类型映射
        const competitionsResponse = await fetch('data/competitions.json');
        if (competitionsResponse.ok) {
          const competitionsData = await competitionsResponse.json();
          setCompetitionsMapping(competitionsData.competitions || {});
        }

        // 加载统计数据
        const response = await fetch('data/current_stats.json');
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const statsData = await response.json();
        setData(statsData);
        setLoading(false);
      } catch (error) {
        console.error('Error loading current stats:', error);
        setError('加载数据失败，请刷新页面重试');
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const openModal = (playerName: string, playerNumber: number, statType: 'goals' | 'assists' | 'yellowCards' | 'redCards', details: StatDetail[], title: string, event: React.MouseEvent) => {
    setModalInfo({
      isOpen: true,
      title,
      playerName,
      playerNumber,
      statType,
      details,
      clickY: event.clientY
    });
  };

  const closeModal = () => {
    setModalInfo({
      ...modalInfo,
      isOpen: false
    });
  };

  if (loading) {
    return (
      <div className="card">
        <div className="card-header">
          <h2>当季数据统计</h2>
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
          <h2>当季数据统计</h2>
        </div>
        <div className="card-content">
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '300px' }}>
            <div style={{ fontSize: '1.2rem', color: '#ff4444' }}>{error || '暂无数据'}</div>
          </div>
        </div>
      </div>
    );
  }

  const currentTeam = activeTeam === 'firstTeam' ? data.firstTeam : data.bTeam;

  // 获取当前比赛类型的统计数据
  const getCurrentStats = () => {
    if (currentTeam.competitions && currentTeam.competitions[activeCompetition]) {
      return currentTeam.competitions[activeCompetition];
    }
    return {
      matchesPlayed: currentTeam.matchesPlayed,
      record: currentTeam.record,
      goalsFor: currentTeam.goalsFor,
      goalsAgainst: currentTeam.goalsAgainst,
      points: currentTeam.points,
      topScorers: currentTeam.topScorers,
      topAssists: currentTeam.topAssists,
      yellowCards: currentTeam.yellowCards,
      redCards: currentTeam.redCards
    };
  };

  const currentStats = getCurrentStats();

  // 获取可用比赛类型列表
  const getCompetitionList = () => {
    if (currentTeam.competitions) {
      return Object.keys(currentTeam.competitions);
    }
    // 如果没有competitions字段，根据球队类型返回默认值
    return activeTeam === 'firstTeam' ? ['中国足球协会超级联赛'] : ['中国足球协会乙级联赛'];
  };

  // 获取比赛类型简称
  const getCompetitionShortName = (comp: string) => {
    if (competitionsMapping[comp]) {
      return competitionsMapping[comp].shortName;
    }
    return comp; // 如果找不到映射，返回原名称
  };

  const renderStatTable = (
    title: string,
    stats: PlayerStat[],
    statKey: 'goals' | 'assists' | 'yellowCards' | 'redCards',
    icon: string
  ) => {
    const sortedStats = [...stats].sort((a, b) => {
      const aValue = a[statKey] as number;
      const bValue = b[statKey] as number;
      if (bValue !== aValue) {
        return bValue - aValue;
      }
      return a.name.localeCompare(b.name, 'zh-CN');
    });

    let currentRank = 0;
    let currentValue = -1;
    const statsWithRanks = sortedStats.map((stat, index) => {
      const statValue = stat[statKey] as number;
      if (statValue !== currentValue) {
        currentRank = index + 1;
        currentValue = statValue;
      }
      return { ...stat, calculatedRank: currentRank };
    });

    // 检查进球是否包含乌龙球
    const hasOwnGoal = (stat: PlayerStat) => {
      if (stat.details && Array.isArray(stat.details)) {
        return stat.details.some((d: any) => d.type === '乌龙球');
      }
      return false;
    };

    return (
      <div className="stats-section">
        <h3>{icon} {title}</h3>
        <table className="stats-table">
          <thead>
            <tr>
              <th>排名</th>
              <th>球员</th>
              <th>号码</th>
              <th>{title.replace('榜', '')}</th>
            </tr>
          </thead>
          <tbody>
            {statsWithRanks.length > 0 ? (
              statsWithRanks.map((stat) => (
                <tr key={`${stat.name}-${stat.calculatedRank}`}>
                  <td>{stat.calculatedRank}</td>
                  <td>
                    {stat.name}
                    {statKey === 'goals' && hasOwnGoal(stat) && (
                      <span style={{ color: '#ff6b6b', marginLeft: '4px' }}>(OG)</span>
                    )}
                  </td>
                  <td>{stat.number}</td>
                  <td
                    className="stat-clickable"
                    onClick={(e) => openModal(stat.name, stat.number, statKey, stat.details || [], title, e)}
                    title="点击查看详细"
                  >
                    {stat[statKey]}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={4} style={{ textAlign: 'center', color: '#888' }}>暂无数据</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2>当季数据统计</h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.5rem' }}>
          <span style={{ fontSize: '0.9rem', color: '#888' }}>更新时间: {data.lastUpdated}</span>
        </div>
      </div>

      <div className="card-content">
        <div className="team-tabs">
          <button
            className={`team-tab ${activeTeam === 'firstTeam' ? 'active' : ''}`}
            onClick={() => setActiveTeam('firstTeam')}
          >
            <span className="tab-icon">🦁</span>
            <span className="tab-text">一线队</span>
          </button>
          <button
            className={`team-tab ${activeTeam === 'bTeam' ? 'active' : ''}`}
            onClick={() => setActiveTeam('bTeam')}
          >
            <span className="tab-icon">🌊</span>
            <span className="tab-text">B队</span>
          </button>
        </div>

        <div className="competition-tabs">
          {getCompetitionList().map((comp) => (
            <button
              key={comp}
              className={`competition-tab ${activeCompetition === comp ? 'active' : ''}`}
              onClick={() => setActiveCompetition(comp)}
            >
              {getCompetitionShortName(comp)}
            </button>
          ))}
        </div>

        <div className="team-overview">
          <div className="overview-item">
            <span className="overview-label">球队</span>
            <span className="overview-value">{currentTeam.teamName}</span>
          </div>
          <div className="overview-item">
            <span className="overview-label">比赛</span>
            <span className="overview-value">{currentStats.matchesPlayed}</span>
          </div>
          <div className="overview-item">
            <span className="overview-label">战绩</span>
            <span className="overview-value">{currentStats.record}</span>
          </div>
          <div className="overview-item">
            <span className="overview-label">积分</span>
            <span className="overview-value">{currentStats.points}</span>
          </div>
          <div className="overview-item">
            <span className="overview-label">进球</span>
            <span className="overview-value">{currentStats.goalsFor}</span>
          </div>
          <div className="overview-item">
            <span className="overview-label">失球</span>
            <span className="overview-value">{currentStats.goalsAgainst}</span>
          </div>
        </div>

        <div className="stats-grid">
          {renderStatTable('进球榜', currentStats.topScorers, 'goals', '⚽')}
          {renderStatTable('助攻榜', currentStats.topAssists, 'assists', '🅰️')}
          {renderStatTable('黄牌榜', currentStats.yellowCards, 'yellowCards', '🟨')}
          {renderStatTable('红牌榜', currentStats.redCards, 'redCards', '🟥')}
        </div>

        <div style={{ fontSize: '0.85rem', color: '#888', marginTop: '1rem', textAlign: 'center' }}>
          💡 点击统计数据可查看详细记录
        </div>
      </div>

      <StatDetailModal
        isOpen={modalInfo.isOpen}
        onClose={closeModal}
        title={modalInfo.title}
        playerName={modalInfo.playerName}
        playerNumber={modalInfo.playerNumber}
        statType={modalInfo.statType}
        details={modalInfo.details}
        clickY={modalInfo.clickY}
      />
    </div>
  );
};

export default CurrentStats;
