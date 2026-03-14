import React, { useState, useEffect } from 'react';

interface Match {
  id: number;
  round: string;
  date: string;
  time: string;
  homeTeam: string;
  awayTeam: string;
  venue: string;
  city: string;
  result: string;
  status: string;
}

const Schedule: React.FC = () => {
  const [scheduleData, setScheduleData] = useState<Match[]>([]);
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [matchType, setMatchType] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchScheduleData = async () => {
      try {
        const response = await fetch('data/schedule.json');
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        setScheduleData(data);
        setLoading(false);
      } catch (error) {
        console.error('Error loading schedule data:', error);
        setError('加载赛程数据失败，请刷新页面重试');
        setLoading(false);
      }
    };

    fetchScheduleData();
  }, []);

  const filteredSchedule = scheduleData.filter(match => {
    const matchesStatus = filter === 'all' || match.status === filter;
    const matchesSearch = searchTerm === '' || 
      (match.round && match.round.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (match.date && match.date.includes(searchTerm)) ||
      (match.homeTeam && match.homeTeam.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (match.awayTeam && match.awayTeam.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (match.city && match.city.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesType = matchType === 'all' || 
      (matchType === 'home' && match.homeTeam === '上海海港') ||
      (matchType === 'away' && match.awayTeam === '上海海港');
    return matchesStatus && matchesSearch && matchesType;
  });

  return (
    <div className="card">
      <div className="card-header">
        <h2>2026赛季球队赛程</h2>
        <div className="schedule-filters">
          <input
            type="text"
            placeholder="搜索轮次、日期、对手或城市..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          <select
            value={matchType}
            onChange={(e) => setMatchType(e.target.value)}
            className="position-filter"
          >
            <option value="all">全部比赛</option>
            <option value="home">主场比赛</option>
            <option value="away">客场比赛</option>
          </select>
          <div className="filter-buttons">
            <button 
              className={filter === 'all' ? 'active' : ''}
              onClick={() => setFilter('all')}
            >
              全部
            </button>
            <button 
              className={filter === '已结束' ? 'active' : ''}
              onClick={() => setFilter('已结束')}
            >
              已结束
            </button>
            <button 
              className={filter === '未开始' ? 'active' : ''}
              onClick={() => setFilter('未开始')}
            >
              未开始
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
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>轮次</th>
                  <th>日期</th>
                  <th>星期</th>
                  <th>时间</th>
                  <th>主队</th>
                  <th>赛果</th>
                  <th>客队</th>
                  <th>城市</th>
                  <th>状态</th>
                </tr>
              </thead>
              <tbody>
                {filteredSchedule.map((match, index) => {
                  // 计算星期几，只显示最后一个字
                  const getDayOfWeek = (dateString: string) => {
                    const date = new Date(dateString);
                    const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
                    return days[date.getDay()].substring(1);
                  };
                  
                  return (
                    <tr key={match.id || index}>
                      <td>{match.round || '-'}</td>
                      <td>{match.date || '-'}</td>
                      <td>{match.date ? getDayOfWeek(match.date) : '-'}</td>
                      <td>{match.time || '-'}</td>
                      <td>{match.homeTeam || '-'}</td>
                      <td>
                        {match.status === '已结束' ? (
                          <a href={`match-report.html?date=${match.date}&type=${encodeURIComponent('中超')}&round=${encodeURIComponent(match.round)}`} style={{ textDecoration: 'none', color: '#c00010', fontWeight: 'bold' }}>
                            {match.result}
                          </a>
                        ) : (
                          match.result
                        )}
                      </td>
                      <td>{match.awayTeam || '-'}</td>
                      <td>{match.city || '-'}</td>
                      <td>{match.status || '-'}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Schedule;