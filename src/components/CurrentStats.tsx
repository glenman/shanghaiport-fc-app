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

interface TeamStats {
  teamName: string;
  competition: string;
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
                  <span className="detail-time">{detail.time}</span>
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
  const [activeCompetition, setActiveCompetition] = useState<string>('中超');
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

  const renderStatTable = (
    title: string,
    stats: PlayerStat[],
    statKey: 'goals' | 'assists' | 'yellowCards' | 'redCards',
    icon: string
  ) => (
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
          {stats.length > 0 ? (
            stats.map((stat) => (
              <tr key={`${stat.name}-${stat.rank}`}>
                <td>{stat.rank}</td>
                <td>{stat.name}</td>
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

        <div className="team-overview">
          <div className="overview-item">
            <span className="overview-label">球队</span>
            <span className="overview-value">{currentTeam.teamName}</span>
          </div>
          <div className="overview-item">
            <span className="overview-label">比赛</span>
            <span className="overview-value">{currentTeam.matchesPlayed}</span>
          </div>
          <div className="overview-item">
            <span className="overview-label">战绩</span>
            <span className="overview-value">{currentTeam.record}</span>
          </div>
          <div className="overview-item">
            <span className="overview-label">积分</span>
            <span className="overview-value">{currentTeam.points}</span>
          </div>
          <div className="overview-item">
            <span className="overview-label">进球</span>
            <span className="overview-value">{currentTeam.goalsFor}</span>
          </div>
          <div className="overview-item">
            <span className="overview-label">失球</span>
            <span className="overview-value">{currentTeam.goalsAgainst}</span>
          </div>
        </div>

        <div className="competition-tabs">
          {activeTeam === 'firstTeam' && (
            <button
              className={`competition-tab ${activeCompetition === '中超' ? 'active' : ''}`}
              onClick={() => setActiveCompetition('中超')}
            >
              中超
            </button>
          )}
          {activeTeam === 'bTeam' && (
            <button
              className={`competition-tab ${activeCompetition === '中乙' ? 'active' : ''}`}
              onClick={() => setActiveCompetition('中乙')}
            >
              中乙
            </button>
          )}
        </div>

        <div className="stats-grid">
          {renderStatTable('进球榜', currentTeam.topScorers, 'goals', '⚽')}
          {renderStatTable('助攻榜', currentTeam.topAssists, 'assists', '🅰️')}
          {renderStatTable('黄牌榜', currentTeam.yellowCards, 'yellowCards', '🟨')}
          {renderStatTable('红牌榜', currentTeam.redCards, 'redCards', '🟥')}
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
