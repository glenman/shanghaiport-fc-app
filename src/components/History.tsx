import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const History: React.FC = () => {
  const [matches, setMatches] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [season, setSeason] = useState('2025');
  const [matchType, setMatchType] = useState('all');

  // 加载历史比赛数据
  useEffect(() => {
    console.log('History component: Loading matches...');
    const loadMatches = async () => {
      try {
        setLoading(true);
        setError(null);
        console.log('History component: Fetching data...');
        const response = await fetch('/data/history_schedule_2025.json');
        if (!response.ok) {
          throw new Error('Failed to fetch history schedule');
        }
        const data = await response.json();
        console.log('History component: Loaded matches:', data.length);
        // 过滤出2025赛季的中超比赛
        const filtered2025 = data.filter((match: any) => match.season === '2025' && match.match_type === '中超联赛');
        console.log('History component: 2025中超比赛数量:', filtered2025.length);
        setMatches(data);
      } catch (err) {
        console.error('History component: Error loading matches:', err);
        setError('加载历史比赛数据失败');
      } finally {
        setLoading(false);
        console.log('History component: Loading complete');
      }
    };

    loadMatches();
  }, []);

  // 过滤比赛数据
  const filteredMatches = matches.filter(match => {
    const seasonMatch = match.season === season;
    const typeMatch = matchType === 'all' || match.match_type === matchType;
    return seasonMatch && typeMatch;
  });
  
  // 调试信息
  console.log('Season:', season);
  console.log('Match type:', matchType);
  console.log('Filtered matches:', filteredMatches.length);
  if (filteredMatches.length > 0) {
    console.log('First match:', filteredMatches[0]);
  }

  // 获取所有赛季
  const seasons = [...new Set(matches.map(match => match.season))].sort((a, b) => parseInt(b) - parseInt(a));

  // 获取所有比赛类型
  const matchTypes = ['all', ...new Set(matches.map(match => match.match_type))];

  // 生成赛事报告链接
  const generateReportLink = (match: any) => {
    // 从match对象中提取日期、赛事类型和轮次，添加默认值
    const date = match.date || '';
    const match_type = match.match_type || '';
    const round = match.round || '';
    // 转换赛事类型为简短名称
    const typeMap: Record<string, string> = {
      '中超联赛': '中超',
      '中甲联赛': '中甲',
      '中乙南区预赛': '中乙',
      '中乙北区预赛': '中乙',
      '中乙总决赛': '中乙',
      '足协杯': '足协杯'
    };
    const shortType = typeMap[match_type] || match_type;
    // 生成链接参数
    return `/match/report?date=${date}&type=${shortType}&round=${round}`;
  };

  if (loading) {
    return <div className="card"><h2>历史比赛</h2><p>加载中...</p></div>;
  }

  if (error) {
    return <div className="card"><h2>历史比赛</h2><p>{error}</p></div>;
  }

  return (
    <div className="card">
      <h2>历史比赛</h2>
      <div className="filter-buttons">
        <select 
          value={season} 
          onChange={(e) => setSeason(e.target.value)}
          style={{ marginRight: '1rem', padding: '0.5rem' }}
        >
          {seasons.map(s => (
            <option key={s} value={s}>{s}赛季</option>
          ))}
        </select>
        <select 
          value={matchType} 
          onChange={(e) => setMatchType(e.target.value)}
          style={{ padding: '0.5rem' }}
        >
          {matchTypes.map(type => (
            <option key={type} value={type}>
              {type === 'all' ? '所有类型' : type}
            </option>
          ))}
        </select>
      </div>
      <table>
        <thead>
          <tr>
            <th>日期</th>
            <th>赛事类型</th>
            <th>轮次</th>
            <th>主队</th>
            <th>客队</th>
            <th>比分</th>
            <th>结果</th>
            <th>赛事报告</th>
          </tr>
        </thead>
        <tbody>
          {filteredMatches.map((match, index) => {
            console.log('History component: Rendering match:', match);
            console.log('History component: Match result:', match.result);
            console.log('History component: Should show link:', match.result && match.result !== '-');
            return (
              <tr key={index}>
                <td>{match.date}</td>
                <td>{match.match_type}</td>
                <td>{match.round}</td>
                <td>{match.home_team}</td>
                <td>{match.away_team}</td>
                <td>
                  <Link 
                    to={generateReportLink(match)} 
                    style={{ textDecoration: 'none', color: '#c00010', fontWeight: 'bold' }}
                  >
                    {match.result}
                  </Link>
                </td>
                <td>{match.win_loss}</td>
                <td>
                  <Link 
                    to={generateReportLink(match)} 
                    style={{ 
                      textDecoration: 'none', 
                      color: '#0066cc', 
                      fontWeight: 'bold',
                      padding: '0.2rem 0.5rem',
                      borderRadius: '4px',
                      backgroundColor: 'rgba(0, 102, 204, 0.1)'
                    }}
                  >
                    查看赛事报告
                  </Link>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default History;