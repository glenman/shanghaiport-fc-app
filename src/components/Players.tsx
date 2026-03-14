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

const Players: React.FC = () => {
  const [playersData, setPlayersData] = useState<Player[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [positionFilter, setPositionFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPlayersData = async () => {
      try {
        const response = await fetch('data/players.json');
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        setPlayersData(data);
        setLoading(false);
      } catch (error) {
        console.error('Error loading players data:', error);
        setError('加载球员数据失败，请刷新页面重试');
        setLoading(false);
      }
    };

    fetchPlayersData();
  }, []);

  const filteredPlayers = playersData.filter(player => {
    const matchesSearch = player.name && player.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesPosition = positionFilter === 'all' || player.position === positionFilter;
    return matchesSearch && matchesPosition;
  });

  const positions = ['all', ...new Set(playersData.map(player => player.position).filter(Boolean))];

  return (
    <div className="card players-card">
      <div className="card-header">
        <h2>球员信息</h2>
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
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>号码</th>
                  <th>姓名</th>
                  <th>位置</th>
                  <th>年龄</th>
                  <th>国籍</th>
                  <th>身高</th>
                  <th>体重</th>
                </tr>
              </thead>
              <tbody>
                {filteredPlayers.map((player, index) => (
                  <tr key={player.id || index}>
                    <td>{player.number || '-'}</td>
                    <td>{player.name || '-'}</td>
                    <td>{player.position || '-'}</td>
                    <td>{player.age || '-'}</td>
                    <td>{player.nationality || '-'}</td>
                    <td>{player.height || '-'}</td>
                    <td>{player.weight || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Players;