import React, { useState, useEffect } from 'react';

interface Player {
  id: number;
  name: string;
  position: string;
  number: number;
  age: number;
  nationality: string;
  height?: string;
  weight?: string;
}

type TeamTab = 'first' | 'b';

const Players: React.FC = () => {
  const [firstTeamData, setFirstTeamData] = useState<Player[]>([]);
  const [bTeamData, setBTeamData] = useState<Player[]>([]);
  const [activeTab, setActiveTab] = useState<TeamTab>('first');
  const [searchTerm, setSearchTerm] = useState('');
  const [positionFilter, setPositionFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPlayersData = async () => {
      try {
        const [firstTeamResponse, bTeamResponse] = await Promise.all([
          fetch('data/players.json'),
          fetch('data/players_b.json')
        ]);
        
        if (!firstTeamResponse.ok || !bTeamResponse.ok) {
          throw new Error('Network response was not ok');
        }
        
        const firstTeamData = await firstTeamResponse.json();
        const bTeamData = await bTeamResponse.json();
        
        setFirstTeamData(firstTeamData);
        setBTeamData(bTeamData);
        setLoading(false);
      } catch (error) {
        console.error('Error loading players data:', error);
        setError('加载球员数据失败，请刷新页面重试');
        setLoading(false);
      }
    };

    fetchPlayersData();
  }, []);

  const currentPlayers = activeTab === 'first' ? firstTeamData : bTeamData;

  const filteredPlayers = currentPlayers.filter(player => {
    const matchesSearch = player.name && player.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesPosition = positionFilter === 'all' || player.position === positionFilter;
    return matchesSearch && matchesPosition;
  });

  const positions = ['all', ...new Set(currentPlayers.map(player => player.position).filter(Boolean))];

  const handleTabChange = (tab: TeamTab) => {
    setActiveTab(tab);
    setSearchTerm('');
    setPositionFilter('all');
  };

  const renderPlayerTable = (players: Player[], showExtraInfo: boolean) => (
    <div className="table-container">
      <table>
        <thead>
          <tr>
            <th>号码</th>
            <th>姓名</th>
            <th>位置</th>
            <th>年龄</th>
            <th>国籍</th>
            {showExtraInfo && <th>身高</th>}
            {showExtraInfo && <th>体重</th>}
          </tr>
        </thead>
        <tbody>
          {players.map((player, index) => (
            <tr key={player.id || index}>
              <td>{player.number || '-'}</td>
              <td>{player.name || '-'}</td>
              <td>{player.position || '-'}</td>
              <td>{player.age || '-'}</td>
              <td>{player.nationality || '-'}</td>
              {showExtraInfo && <td>{player.height || '-'}</td>}
              {showExtraInfo && <td>{player.weight || '-'}</td>}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  return (
    <div className="card players-card">
      <div className="card-header">
        <h2>球员信息</h2>
        <div className="team-tabs">
          <button
            className={`team-tab ${activeTab === 'first' ? 'active' : ''}`}
            onClick={() => handleTabChange('first')}
          >
            一线队 ({firstTeamData.length}人)
          </button>
          <button
            className={`team-tab ${activeTab === 'b' ? 'active' : ''}`}
            onClick={() => handleTabChange('b')}
          >
            B队 ({bTeamData.length}人)
          </button>
        </div>
        <div className="player-filters">
          <input
            type="text"
            placeholder="搜索球员..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          <select
            value={positionFilter}
            onChange={(e) => setPositionFilter(e.target.value)}
            className="position-filter"
          >
            {positions.map(position => (
              <option key={position} value={position}>
                {position === 'all' ? '全部位置' : position}
              </option>
            ))}
          </select>
        </div>
      </div>
      <div className="card-content">
        {loading ? (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '300px' }}>
            <div style={{ fontSize: '1.2rem', color: '#c00010' }}>加载数据中...</div>
          </div>
        ) : error ? (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '300px' }}>
            <div style={{ fontSize: '1.2rem', color: '#ff4444' }}>{error}</div>
          </div>
        ) : (
          <>
            {activeTab === 'first' && (
              <div className="team-section">
                <h3 className="team-title">上海海港一线队</h3>
                {renderPlayerTable(filteredPlayers, true)}
              </div>
            )}
            {activeTab === 'b' && (
              <div className="team-section">
                <h3 className="team-title">上海海港B队</h3>
                {renderPlayerTable(filteredPlayers, false)}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default Players;
