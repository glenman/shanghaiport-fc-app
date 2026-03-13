import React, { useState, useEffect } from 'react';
import { useHistory, useLocation } from 'react-router-dom';

const MatchReport: React.FC = () => {
  const history = useHistory();
  const location = useLocation();
  const [match, setMatch] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMatchData = async () => {
      try {
        setLoading(true);
        // 从 URL 参数中获取比赛信息
        const params = new URLSearchParams(location.search);
        const date = params.get('date');
        const type = params.get('type');
        const round = params.get('round');

        if (!date || !type || !round) {
          throw new Error('缺少比赛信息参数');
        }

        // 构建 JSON 文件路径
        const year = date.substring(0, 4);
        const fileName = `${date}-${type}-${round}.json`;
        const filePath = `/data/history/${year}/${fileName}`;

        // 从 JSON 文件中获取数据
        const response = await fetch(filePath);
        if (!response.ok) {
          throw new Error('Failed to fetch match data');
        }
        const data = await response.json();
        setMatch(data);
        setError(null);
      } catch (err) {
        setError('无法加载赛事数据');
        console.error('Error fetching match data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchMatchData();
  }, [location.search]);

  if (loading) {
    return (
      <div className="card">
        <h2>赛事报告</h2>
        <p>加载中...</p>
      </div>
    );
  }

  if (error || !match) {
    return (
      <div className="card">
        <h2>赛事报告</h2>
        <p>{error || '未找到该比赛的赛事报告'}</p>
        <button 
          onClick={() => history.goBack()}
          style={{
            padding: '0.8rem 1.2rem',
            borderRadius: '20px',
            border: '1px solid #444',
            backgroundColor: 'rgba(40, 40, 40, 0.8)',
            color: '#fff',
            cursor: 'pointer',
            marginTop: '1rem',
            transition: 'all 0.3s ease'
          }}
        >
          返回
        </button>
      </div>
    );
  }

  return (
    <div className="card">
      <h2>赛事报告</h2>
      <div style={{ marginBottom: '2rem' }}>
        <h3 style={{ color: '#c00010', marginBottom: '1rem' }}>
          {match.match.homeTeam} {match.match.result} {match.match.awayTeam}
        </h3>
        <p><strong>轮次:</strong> {match.match.round}</p>
        <p><strong>日期:</strong> {match.match.date}</p>
        <p><strong>时间:</strong> {match.match.time}</p>
        <p><strong>场地:</strong> {match.match.venue}</p>
        <p><strong>城市:</strong> {match.match.city}</p>
      </div>

      <div style={{ marginBottom: '2rem' }}>
        <h3 style={{ color: '#c00010', marginBottom: '1rem' }}>比赛 summary</h3>
        <p>{match.summary}</p>
      </div>

      <div style={{ marginBottom: '2rem' }}>
        <h3 style={{ color: '#c00010', marginBottom: '1rem' }}>比赛亮点</h3>
        <ul style={{ listStyle: 'disc', paddingLeft: '2rem' }}>
          {match.highlights.map((highlight: any, index: number) => (
            <li key={index} style={{ marginBottom: '0.5rem' }}>{highlight.description}</li>
          ))}
        </ul>
      </div>

      <div style={{ marginBottom: '2rem' }}>
        <h3 style={{ color: '#c00010', marginBottom: '1rem' }}>阵容</h3>
        <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
          <div>
            <h4 style={{ marginBottom: '0.5rem' }}>{match.match.homeTeam}</h4>
            <ul style={{ listStyle: 'none', paddingLeft: '1rem' }}>
              {match.lineups.home.players.map((player: any, index: number) => (
                <li key={index} style={{ marginBottom: '0.3rem' }}>
                  {player.position}: {player.name}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h4 style={{ marginBottom: '0.5rem' }}>{match.match.awayTeam}</h4>
            <ul style={{ listStyle: 'none', paddingLeft: '1rem' }}>
              {match.lineups.away.players.map((player: any, index: number) => (
                <li key={index} style={{ marginBottom: '0.3rem' }}>
                  {player.position}: {player.name}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      <div style={{ marginBottom: '2rem' }}>
        <h3 style={{ color: '#c00010', marginBottom: '1rem' }}>比赛统计</h3>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={{ textAlign: 'left', padding: '0.5rem', borderBottom: '1px solid #444' }}>统计项</th>
              <th style={{ textAlign: 'left', padding: '0.5rem', borderBottom: '1px solid #444' }}>{match.match.homeTeam}</th>
              <th style={{ textAlign: 'left', padding: '0.5rem', borderBottom: '1px solid #444' }}>{match.match.awayTeam}</th>
            </tr>
          </thead>
          <tbody>
            {match.statistics.map((stat: any, index: number) => (
              <tr key={index}>
                <td style={{ padding: '0.5rem', borderBottom: '1px solid #444' }}>{stat.name}</td>
                <td style={{ padding: '0.5rem', borderBottom: '1px solid #444' }}>{stat.home}</td>
                <td style={{ padding: '0.5rem', borderBottom: '1px solid #444' }}>{stat.away}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <button 
        onClick={() => history.goBack()}
        style={{
          padding: '0.8rem 1.2rem',
          borderRadius: '20px',
          border: '1px solid #444',
          backgroundColor: 'rgba(40, 40, 40, 0.8)',
          color: '#fff',
          cursor: 'pointer',
          transition: 'all 0.3s ease'
        }}
      >
        返回
      </button>
    </div>
  );
};

export default MatchReport;