import React, { useState, useEffect } from 'react';

interface Season {
  id: number;
  season: string;
  league: string;
  rank: string;
  matches: number;
  wins: number;
  draws: number;
  losses: number;
  goalsFor: number;
  goalsAgainst: number;
  points: number;
  notes: string;
}

const Seasons: React.FC = () => {
  const [seasonsData, setSeasonsData] = useState<Season[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSeasonsData = async () => {
      try {
        const response = await fetch('data/seasons.json');
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        setSeasonsData(data);
        setLoading(false);
      } catch (error) {
        console.error('Error loading seasons data:', error);
        setError('加载赛季数据失败，请刷新页面重试');
        setLoading(false);
      }
    };

    fetchSeasonsData();
  }, []);

  const filteredSeasons = seasonsData.filter(season => {
    const matchesSearch = searchTerm === '' || 
      (season.season && season.season.includes(searchTerm)) ||
      (season.league && season.league.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (season.rank && season.rank.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (season.notes && season.notes.toLowerCase().includes(searchTerm.toLowerCase()));
    return matchesSearch;
  });

  return (
    <div className="card">
      <div className="card-header">
        <h2>历史赛季排名</h2>
        <div className="player-filters">
          <input
            type="text"
            placeholder="搜索赛季、联赛、排名或备注..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
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
                  <th>赛季</th>
                  <th>联赛</th>
                  <th>排名</th>
                  <th>场次</th>
                  <th>胜</th>
                  <th>平</th>
                  <th>负</th>
                  <th>进球</th>
                  <th>失球</th>
                  <th>积分</th>
                  <th>备注</th>
                </tr>
              </thead>
              <tbody>
                {filteredSeasons.map((season, index) => (
                  <tr key={season.id || index}>
                    <td>{season.season || '-'}</td>
                    <td>{season.league || '-'}</td>
                    <td>{season.rank || '-'}</td>
                    <td>{season.matches || '-'}</td>
                    <td>{season.wins || '-'}</td>
                    <td>{season.draws || '-'}</td>
                    <td>{season.losses || '-'}</td>
                    <td>{season.goalsFor || '-'}</td>
                    <td>{season.goalsAgainst || '-'}</td>
                    <td>{season.points || '-'}</td>
                    <td>{season.notes || '-'}</td>
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

export default Seasons;