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
  type: string;
}

type TeamTab = 'first' | 'b';

const Schedule: React.FC = () => {
  const [firstTeamSchedule, setFirstTeamSchedule] = useState<Match[]>([]);
  const [bTeamSchedule, setBTeamSchedule] = useState<Match[]>([]);
  const [activeTab, setActiveTab] = useState<TeamTab>('first');
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [matchType, setMatchType] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchScheduleData = async () => {
      try {
        const [firstTeamResponse, bTeamResponse] = await Promise.all([
          fetch('data/schedule.json'),
          fetch('data/schedule_b.json')
        ]);
        
        if (!firstTeamResponse.ok || !bTeamResponse.ok) {
          throw new Error('Network response was not ok');
        }
        
        const firstTeamData = await firstTeamResponse.json();
        const bTeamData = await bTeamResponse.json();
        
        setFirstTeamSchedule(firstTeamData);
        setBTeamSchedule(bTeamData);
        setLoading(false);
      } catch (error) {
        console.error('Error loading schedule data:', error);
        setError('加载赛程数据失败，请刷新页面重试');
        setLoading(false);
      }
    };

    fetchScheduleData();
  }, []);

  const currentSchedule = activeTab === 'first' ? firstTeamSchedule : bTeamSchedule;

  const filteredSchedule = currentSchedule.filter(match => {
    const matchesStatus = filter === 'all' || match.status === filter;
    const matchesSearch = searchTerm === '' || 
      (match.round && match.round.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (match.date && match.date.includes(searchTerm)) ||
      (match.homeTeam && match.homeTeam.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (match.awayTeam && match.awayTeam.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (match.city && match.city.toLowerCase().includes(searchTerm.toLowerCase()));
    const isFirstTeam = activeTab === 'first';
    const teamNames = isFirstTeam ? ['上海海港'] : ['上海海港B队', '上海海港富盛经开'];
    const matchesType = matchType === 'all' || 
      (matchType === 'home' && teamNames.includes(match.homeTeam)) ||
      (matchType === 'away' && teamNames.includes(match.awayTeam));
    return matchesStatus && matchesSearch && matchesType;
  });

  const handleTabChange = (tab: TeamTab) => {
    setActiveTab(tab);
    setFilter('all');
    setSearchTerm('');
    setMatchType('all');
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2>球队赛程</h2>
        <div className="team-tabs">
          <button
            className={`team-tab ${activeTab === 'first' ? 'active' : ''}`}
            onClick={() => handleTabChange('first')}
          >
            一线队 ({firstTeamSchedule.length}场)
          </button>
          <button
            className={`team-tab ${activeTab === 'b' ? 'active' : ''}`}
            onClick={() => handleTabChange('b')}
          >
            B队 ({bTeamSchedule.length}场)
          </button>
        </div>
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
          <>
            {activeTab === 'first' && (
              <div className="team-section">
                <h3 className="team-title">2026-2027赛季</h3>
                <div style={{ marginBottom: '15px', fontSize: '0.95rem', color: '#666' }}>
                  <span style={{ marginRight: '30px' }}>主教练：凯文·穆斯卡特</span>
                  <span>助理教练：托尼·维德马</span>
                </div>
                <div className="table-container">
                  <table>
                    <thead>
                      <tr>
                        <th>日期</th>
                        <th>星期</th>
                        <th>比赛类型</th>
                        <th>轮次</th>
                        <th>时间</th>
                        <th>主队</th>
                        <th>比分</th>
                        <th>客队</th>
                        <th>赛果</th>
                        <th>城市</th>
                        <th>状态</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredSchedule.map((match, index) => {
                        const getDayOfWeek = (dateString: string) => {
                          const date = new Date(dateString);
                          const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
                          return days[date.getDay()].substring(1);
                        };
                        
                        const getResultStatus = (match: Match) => {
                          if (match.status !== '已结束' || match.result === '-') return '-';
                          const [homeGoals, awayGoals] = match.result.split('-').map(Number);
                          const isHome = match.homeTeam === '上海海港';
                          if (isHome) {
                            if (homeGoals > awayGoals) return '胜';
                            if (homeGoals < awayGoals) return '负';
                            return '平';
                          } else {
                            if (awayGoals > homeGoals) return '胜';
                            if (awayGoals < homeGoals) return '负';
                            return '平';
                          }
                        };
                        
                        const resultStatus = getResultStatus(match);
                        const getResultColor = (status: string) => {
                          if (status === '胜') return '#dc3545';
                          if (status === '平') return '#ffffff';
                          if (status === '负') return '#28a745';
                          return 'inherit';
                        };
                        
                        return (
                          <tr key={match.id || index}>
                            <td>{match.date || '-'}</td>
                            <td>{match.date ? getDayOfWeek(match.date) : '-'}</td>
                            <td>{match.type || '-'}</td>
                            <td>{match.round || '-'}</td>
                            <td>{match.time || '-'}</td>
                            <td>{match.homeTeam || '-'}</td>
                            <td>
                              {match.status === '已结束' ? (
                                <a href={`match-report-v2.html?date=${match.date}&type=${encodeURIComponent(match.type)}&round=${encodeURIComponent(match.round)}`} style={{ textDecoration: 'none', color: '#c00010', fontWeight: 'bold' }}>
                                  {match.result}
                                </a>
                              ) : (
                                match.result
                              )}
                            </td>
                            <td>{match.awayTeam || '-'}</td>
                            <td style={{ color: getResultColor(resultStatus), fontWeight: resultStatus !== '-' ? 'bold' : 'normal' }}>{resultStatus}</td>
                            <td>{match.city || '-'}</td>
                            <td>{match.status || '-'}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
            {activeTab === 'b' && (
              <div className="team-section">
                <h3 className="team-title">2026赛季</h3>
                <div style={{ marginBottom: '15px', fontSize: '0.95rem', color: '#666' }}>
                  <span style={{ marginRight: '30px' }}>主教练：成耀东</span>
                  <span>助理教练：于海</span>
                </div>
                <div className="table-container">
                  <table>
                    <thead>
                      <tr>
                        <th>日期</th>
                        <th>星期</th>
                        <th>比赛类型</th>
                        <th>轮次</th>
                        <th>时间</th>
                        <th>主队</th>
                        <th>比分</th>
                        <th>客队</th>
                        <th>赛果</th>
                        <th>城市</th>
                        <th>状态</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredSchedule.map((match, index) => {
                        const getDayOfWeek = (dateString: string) => {
                          const date = new Date(dateString);
                          const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
                          return days[date.getDay()].substring(1);
                        };
                        
                        const getResultStatus = (match: Match) => {
                          if (match.status !== '已结束' || match.result === '-') return '-';
                          const [homeGoals, awayGoals] = match.result.split('-').map(Number);
                          const bTeamNames = ['上海海港B队', '上海海港富盛经开'];
                          const isHome = bTeamNames.includes(match.homeTeam);
                          if (isHome) {
                            if (homeGoals > awayGoals) return '胜';
                            if (homeGoals < awayGoals) return '负';
                            return '平';
                          } else {
                            if (awayGoals > homeGoals) return '胜';
                            if (awayGoals < homeGoals) return '负';
                            return '平';
                          }
                        };
                        
                        const resultStatus = getResultStatus(match);
                        const getResultColor = (status: string) => {
                          if (status === '胜') return '#dc3545';
                          if (status === '平') return '#ffffff';
                          if (status === '负') return '#28a745';
                          return 'inherit';
                        };
                        
                        return (
                          <tr key={match.id || index}>
                            <td>{match.date || '-'}</td>
                            <td>{match.date ? getDayOfWeek(match.date) : '-'}</td>
                            <td>{match.type || '-'}</td>
                            <td>{match.round || '-'}</td>
                            <td>{match.time || '-'}</td>
                            <td>{match.homeTeam || '-'}</td>
                            <td>
                              {match.status === '已结束' ? (
                                <a href={`match-report.html?date=${match.date}&type=${encodeURIComponent(match.type)}&round=${encodeURIComponent(match.round)}`} style={{ textDecoration: 'none', color: '#c00010', fontWeight: 'bold' }}>
                                  {match.result}
                                </a>
                              ) : (
                                match.result
                              )}
                            </td>
                            <td>{match.awayTeam || '-'}</td>
                            <td style={{ color: getResultColor(resultStatus), fontWeight: resultStatus !== '-' ? 'bold' : 'normal' }}>{resultStatus}</td>
                            <td>{match.city || '-'}</td>
                            <td>{match.status || '-'}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default Schedule;
