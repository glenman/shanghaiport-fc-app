import React, { useState, useEffect } from 'react';

interface HistoryMatch {
  season: string;
  match_type: string;
  match_name: string;
  round: string;
  date: string;
  home_team: string;
  away_team: string;
  result: string;
  win_loss: string;
}

const History: React.FC = () => {
  const [historyData, setHistoryData] = useState<HistoryMatch[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedSeasons, setExpandedSeasons] = useState<Set<string>>(new Set(['2025']));

  useEffect(() => {
    const fetchHistoryData = async () => {
      try {
        const response = await fetch('data/history_schedule.json');
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        setHistoryData(data);
        setLoading(false);
      } catch (error) {
        console.error('Error loading history data:', error);
        setError('加载历史数据失败，请刷新页面重试');
        setLoading(false);
      }
    };

    fetchHistoryData();
  }, []);

  // 按赛季分组
  const groupedBySeason = historyData.reduce((groups, match) => {
    const season = match.season;
    if (!groups[season]) {
      groups[season] = [];
    }
    groups[season].push(match);
    return groups;
  }, {} as Record<string, HistoryMatch[]>);

  // 按赛季降序排序
  const seasons = Object.keys(groupedBySeason).sort((a, b) => parseInt(b) - parseInt(a));

  // 切换赛季展开/折叠
  const toggleSeason = (season: string) => {
    const newExpandedSeasons = new Set(expandedSeasons);
    if (newExpandedSeasons.has(season)) {
      newExpandedSeasons.delete(season);
    } else {
      newExpandedSeasons.add(season);
    }
    setExpandedSeasons(newExpandedSeasons);
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2>历史比赛</h2>
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
        ) : seasons.length > 0 ? (
          <div>
            {seasons.map(season => {
              const matches = groupedBySeason[season];
              const isExpanded = expandedSeasons.has(season);
              
              return (
                <div key={season} style={{ marginBottom: '1rem' }}>
                  <div 
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      padding: '0.8rem',
                      backgroundColor: '#444',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      marginBottom: '0.5rem'
                    }}
                    onClick={() => toggleSeason(season)}
                  >
                    <h3 style={{ margin: 0, color: '#c00010' }}>{season}赛季</h3>
                    <span style={{ fontSize: '1.2rem' }}>{isExpanded ? '▼' : '▶'}</span>
                  </div>
                  
                  {isExpanded && (
                    <div className="table-container">
                      <table>
                        <thead>
                          <tr>
                            <th>日期</th>
                            <th>类型</th>
                            <th>轮次</th>
                            <th>主队</th>
                            <th>客队</th>
                            <th>赛果</th>
                            <th>状态</th>
                            <th>赛事报告</th>
                          </tr>
                        </thead>
                        <tbody>
                          {matches.map((match, index) => (
                            <tr key={index}>
                              <td>{match.date || '-'}</td>
                              <td>{match.match_type || '-'}</td>
                              <td>{match.round || '-'}</td>
                              <td>{match.home_team || '-'}</td>
                              <td>{match.away_team || '-'}</td>
                              <td>{match.result || '-'}</td>
                              <td>{match.win_loss || '-'}</td>
                              <td>
                                <a 
                                  href={`match-report.html?date=${match.date}&type=${encodeURIComponent(match.match_type)}&round=${encodeURIComponent(match.round)}&source=h`}
                                  style={{ textDecoration: 'none', color: '#c00010', fontWeight: 'bold' }}
                                >
                                  查看
                                </a>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        ) : (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '300px' }}>
            <div style={{ fontSize: '1.2rem', color: '#888' }}>暂无历史比赛数据</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default History;