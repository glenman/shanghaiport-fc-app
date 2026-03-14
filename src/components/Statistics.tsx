import React, { useState, useEffect } from 'react';

interface GoalDetail {
  id: number;
  season: string;
  match_date: string;
  match_type: string;
  match_round: string;
  home_team: string;
  away_team: string;
  goal_player: string;
  assist_player: string;
  minute: string;
  score: string;
}

interface PlayerStat {
  name: string;
  league: number;
  faCup: number;
  superCup: number;
  afc: number;
  total: number;
}

const Statistics: React.FC = () => {
  const [selectedSeason, setSelectedSeason] = useState('2025');
  const [statisticsType, setStatisticsType] = useState('goals'); // goals or assists
  const [data, setData] = useState<GoalDetail[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchGoalDetails = async () => {
      try {
        const response = await fetch('data/goal_details.json');
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const goalData = await response.json();
        setData(goalData);
        setLoading(false);
      } catch (error) {
        console.error('Error loading goal details:', error);
        setError('加载数据失败，请刷新页面重试');
        setLoading(false);
      }
    };

    fetchGoalDetails();
  }, []);

  // 处理数据统计
  const processStatistics = () => {
    if (loading || error || data.length === 0) return { seasons: [], currentData: [] };

    // 提取所有赛季
    const seasonsSet = new Set(data.map(item => item.season));
    const seasons = Array.from(seasonsSet).sort().reverse();

    // 按赛季和类型统计
    const statsBySeason: Record<string, { goals: PlayerStat[]; assists: PlayerStat[] }> = {};
    
    seasons.forEach(season => {
      statsBySeason[season] = {
        goals: [],
        assists: []
      };
    });

    // 统计进球
    const goalStats: Record<string, Record<string, PlayerStat>> = {};
    data.forEach(item => {
      const player = item.goal_player;
      const season = item.season;
      const matchType = item.match_type;
      
      if (!goalStats[player]) {
        goalStats[player] = {};
      }
      if (!goalStats[player][season]) {
        goalStats[player][season] = {
          name: player,
          league: 0,
          faCup: 0,
          superCup: 0,
          afc: 0,
          total: 0
        };
      }
      
      // 根据比赛类型统计
      if (matchType.includes('中超')) {
        goalStats[player][season].league += 1;
      } else if (matchType.includes('足协杯')) {
        goalStats[player][season].faCup += 1;
      } else if (matchType.includes('超级杯')) {
        goalStats[player][season].superCup += 1;
      } else if (matchType.includes('亚冠')) {
        goalStats[player][season].afc += 1;
      }
      goalStats[player][season].total += 1;
    });

    // 统计助攻
    const assistStats: Record<string, Record<string, PlayerStat>> = {};
    data.forEach(item => {
      const player = item.assist_player;
      if (!player || player === '—' || player === '？') return;
      
      const season = item.season;
      const matchType = item.match_type;
      
      if (!assistStats[player]) {
        assistStats[player] = {};
      }
      if (!assistStats[player][season]) {
        assistStats[player][season] = {
          name: player,
          league: 0,
          faCup: 0,
          superCup: 0,
          afc: 0,
          total: 0
        };
      }
      
      // 根据比赛类型统计
      if (matchType.includes('中超')) {
        assistStats[player][season].league += 1;
      } else if (matchType.includes('足协杯')) {
        assistStats[player][season].faCup += 1;
      } else if (matchType.includes('超级杯')) {
        assistStats[player][season].superCup += 1;
      } else if (matchType.includes('亚冠')) {
        assistStats[player][season].afc += 1;
      }
      assistStats[player][season].total += 1;
    });

    // 转换为排名格式
    seasons.forEach(season => {
      // 进球排名
      const seasonGoalStats: PlayerStat[] = [];
      Object.entries(goalStats).forEach(([player, stats]) => {
        if (stats[season]) {
          seasonGoalStats.push(stats[season]);
        }
      });
      
      // 按总进球数排序
      seasonGoalStats.sort((a, b) => b.total - a.total);
      statsBySeason[season].goals = seasonGoalStats;

      // 助攻排名
      const seasonAssistStats: PlayerStat[] = [];
      Object.entries(assistStats).forEach(([player, stats]) => {
        if (stats[season]) {
          seasonAssistStats.push(stats[season]);
        }
      });
      
      // 按总助攻数排序
      seasonAssistStats.sort((a, b) => b.total - a.total);
      statsBySeason[season].assists = seasonAssistStats;
    });

    return {
      seasons,
      currentData: statisticsType === 'goals' ? statsBySeason[selectedSeason]?.goals || [] : statsBySeason[selectedSeason]?.assists || []
    };
  };

  const { seasons, currentData } = processStatistics();

  return (
    <div className="card">
      <div className="card-header">
        <h2>进球助攻榜</h2>
        <div className="player-filters" style={{ marginTop: '1rem' }}>
          <select
            value={selectedSeason}
            onChange={(e) => setSelectedSeason(e.target.value)}
            className="position-filter"
          >
            {seasons.map(season => (
              <option key={season} value={season}>
                {season}赛季
              </option>
            ))}
          </select>
          <div className="filter-buttons">
            <button 
              className={statisticsType === 'goals' ? 'active' : ''}
              onClick={() => setStatisticsType('goals')}
            >
              进球统计
            </button>
            <button 
              className={statisticsType === 'assists' ? 'active' : ''}
              onClick={() => setStatisticsType('assists')}
            >
              助攻统计
            </button>
          </div>
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
        ) : currentData.length > 0 ? (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>排名</th>
                  <th>球员</th>
                  <th>中超联赛</th>
                  <th>足协杯</th>
                  <th>超级杯</th>
                  <th>亚冠联赛</th>
                  <th>合计</th>
                </tr>
              </thead>
              <tbody>
                {currentData.map((player, index) => (
                  <tr key={player.name}>
                    <td>{index + 1}</td>
                    <td>{player.name}</td>
                    <td>{player.league}</td>
                    <td>{player.faCup}</td>
                    <td>{player.superCup}</td>
                    <td>{player.afc}</td>
                    <td>{player.total}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '300px' }}>
            <div style={{ fontSize: '1.2rem', color: '#888' }}>暂无数据</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Statistics;