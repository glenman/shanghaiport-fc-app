import React, { useState, useEffect, useMemo, useRef } from 'react';

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

const OUR_TEAM_NAMES = ['上海东亚', '上海上港', '上海海港'];

const History: React.FC = () => {
  const [historyData, setHistoryData] = useState<HistoryMatch[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedSeasons, setExpandedSeasons] = useState<Set<string>>(new Set(['2025']));
  const [selectedOpponent, setSelectedOpponent] = useState<string>('');
  const [showHeadToHead, setShowHeadToHead] = useState(false);
  const [opponentInput, setOpponentInput] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);

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

  const opponents = useMemo(() => {
    const opponentSet = new Set<string>();
    historyData.forEach(match => {
      if (!OUR_TEAM_NAMES.includes(match.home_team)) {
        opponentSet.add(match.home_team);
      }
      if (!OUR_TEAM_NAMES.includes(match.away_team)) {
        opponentSet.add(match.away_team);
      }
    });
    return Array.from(opponentSet).sort((a, b) => a.localeCompare(b, 'zh-CN'));
  }, [historyData]);

  const filteredOpponents = useMemo(() => {
    if (!opponentInput.trim()) return opponents.slice(0, 10);
    const input = opponentInput.toLowerCase();
    return opponents.filter(opponent => 
      opponent.toLowerCase().includes(input)
    ).slice(0, 10);
  }, [opponents, opponentInput]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        suggestionsRef.current && 
        !suggestionsRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleOpponentSelect = (opponent: string) => {
    setSelectedOpponent(opponent);
    setOpponentInput(opponent);
    setShowSuggestions(false);
  };

  const handleInputChange = (value: string) => {
    setOpponentInput(value);
    setSelectedOpponent('');
    setShowSuggestions(true);
  };

  const headToHeadMatches = useMemo(() => {
    if (!selectedOpponent) return [];
    return historyData
      .filter(match => 
        match.home_team === selectedOpponent || match.away_team === selectedOpponent
      )
      .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
  }, [historyData, selectedOpponent]);

  const headToHeadStats = useMemo(() => {
    if (headToHeadMatches.length === 0) return null;
    
    let wins = 0, draws = 0, losses = 0;
    let goalsFor = 0, goalsAgainst = 0;
    let homeWins = 0, homeDraws = 0, homeLosses = 0;
    let awayWins = 0, awayDraws = 0, awayLosses = 0;

    headToHeadMatches.forEach(match => {
      const isHome = OUR_TEAM_NAMES.includes(match.home_team);
      const [ourGoals, theirGoals] = isHome 
        ? match.result.split('-').map(Number)
        : match.result.split('-').map(Number).reverse();
      
      goalsFor += ourGoals || 0;
      goalsAgainst += theirGoals || 0;

      if (match.win_loss === '胜') {
        wins++;
        if (isHome) homeWins++; else awayWins++;
      } else if (match.win_loss === '平') {
        draws++;
        if (isHome) homeDraws++; else awayDraws++;
      } else if (match.win_loss === '负') {
        losses++;
        if (isHome) homeLosses++; else awayLosses++;
      }
    });

    return {
      total: headToHeadMatches.length,
      wins, draws, losses,
      goalsFor, goalsAgainst,
      home: { wins: homeWins, draws: homeDraws, losses: homeLosses },
      away: { wins: awayWins, draws: awayDraws, losses: awayLosses }
    };
  }, [headToHeadMatches]);

  const displayMatches = showHeadToHead && selectedOpponent ? headToHeadMatches : historyData;

  const groupedBySeason = displayMatches.reduce((groups, match) => {
    const season = match.season;
    if (!groups[season]) {
      groups[season] = [];
    }
    groups[season].push(match);
    return groups;
  }, {} as Record<string, HistoryMatch[]>);

  const seasons = Object.keys(groupedBySeason).sort((a, b) => parseInt(b) - parseInt(a));

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
        <div style={{ 
          marginBottom: '1.5rem', 
          padding: '1rem', 
          backgroundColor: '#333', 
          borderRadius: '8px' 
        }}>
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '1rem', 
            flexWrap: 'wrap' 
          }}>
            <label style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '0.5rem',
              fontWeight: 'bold',
              color: '#fff'
            }}>
              <input
                type="checkbox"
                checked={showHeadToHead}
                onChange={(e) => {
                  setShowHeadToHead(e.target.checked);
                  if (!e.target.checked) {
                    setSelectedOpponent('');
                    setOpponentInput('');
                    setShowSuggestions(false);
                  }
                }}
                style={{ width: '18px', height: '18px', accentColor: '#c00010' }}
              />
              查询历史交锋
            </label>
            
            {showHeadToHead && (
              <div style={{ position: 'relative' }}>
                <input
                  ref={inputRef}
                  type="text"
                  value={opponentInput}
                  onChange={(e) => handleInputChange(e.target.value)}
                  onFocus={() => setShowSuggestions(true)}
                  placeholder="输入对手球队名称..."
                  style={{
                    padding: '0.6rem 1rem',
                    borderRadius: '6px',
                    border: '1px solid #555',
                    backgroundColor: '#222',
                    color: '#fff',
                    fontSize: '1rem',
                    minWidth: '220px',
                    outline: 'none'
                  }}
                />
                
                {showSuggestions && filteredOpponents.length > 0 && (
                  <div
                    ref={suggestionsRef}
                    style={{
                      position: 'absolute',
                      top: '100%',
                      left: 0,
                      right: 0,
                      backgroundColor: '#2a2a2a',
                      border: '1px solid #555',
                      borderRadius: '6px',
                      marginTop: '4px',
                      maxHeight: '250px',
                      overflowY: 'auto',
                      zIndex: 1000,
                      boxShadow: '0 4px 12px rgba(0,0,0,0.3)'
                    }}
                  >
                    {filteredOpponents.map(opponent => (
                      <div
                        key={opponent}
                        onClick={() => handleOpponentSelect(opponent)}
                        style={{
                          padding: '0.6rem 1rem',
                          cursor: 'pointer',
                          backgroundColor: selectedOpponent === opponent ? '#444' : 'transparent',
                          borderBottom: '1px solid #333',
                          transition: 'background-color 0.15s'
                        }}
                        onMouseEnter={(e) => {
                          (e.target as HTMLDivElement).style.backgroundColor = '#444';
                        }}
                        onMouseLeave={(e) => {
                          (e.target as HTMLDivElement).style.backgroundColor = selectedOpponent === opponent ? '#444' : 'transparent';
                        }}
                      >
                        {opponent}
                      </div>
                    ))}
                  </div>
                )}
                
                {showSuggestions && opponentInput && filteredOpponents.length === 0 && (
                  <div
                    style={{
                      position: 'absolute',
                      top: '100%',
                      left: 0,
                      right: 0,
                      backgroundColor: '#2a2a2a',
                      border: '1px solid #555',
                      borderRadius: '6px',
                      marginTop: '4px',
                      padding: '0.6rem 1rem',
                      color: '#888',
                      zIndex: 1000
                    }}
                  >
                    未找到匹配的球队
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {showHeadToHead && selectedOpponent && headToHeadStats && (
          <div style={{ 
            marginBottom: '1rem', 
            padding: '0.75rem', 
            backgroundColor: '#2a2a2a', 
            borderRadius: '8px',
            border: '1px solid #c00010'
          }}>
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'space-between',
              marginBottom: '0.5rem'
            }}>
              <span style={{ color: '#c00010', fontWeight: 'bold', fontSize: '0.95rem' }}>
                vs {selectedOpponent}
              </span>
              <span style={{ color: '#888', fontSize: '0.85rem' }}>
                {headToHeadStats.total}场
              </span>
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
              <div style={{ display: 'flex', gap: '0.35rem' }}>
                <div style={{ 
                  flex: 1, 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  padding: '0.4rem 0.3rem', 
                  backgroundColor: '#1a4d1a', 
                  borderRadius: '4px',
                  gap: '0.3rem'
                }}>
                  <span style={{ fontSize: '0.75rem', color: '#88cc88' }}>胜</span>
                  <span style={{ fontSize: '1rem', fontWeight: 'bold', color: '#4caf50' }}>{headToHeadStats.wins}</span>
                </div>
                <div style={{ 
                  flex: 1, 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  padding: '0.4rem 0.3rem', 
                  backgroundColor: '#4d4d1a', 
                  borderRadius: '4px',
                  gap: '0.3rem'
                }}>
                  <span style={{ fontSize: '0.75rem', color: '#cccc88' }}>平</span>
                  <span style={{ fontSize: '1rem', fontWeight: 'bold', color: '#ffc107' }}>{headToHeadStats.draws}</span>
                </div>
                <div style={{ 
                  flex: 1, 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  padding: '0.4rem 0.3rem', 
                  backgroundColor: '#4d1a1a', 
                  borderRadius: '4px',
                  gap: '0.3rem'
                }}>
                  <span style={{ fontSize: '0.75rem', color: '#cc8888' }}>负</span>
                  <span style={{ fontSize: '1rem', fontWeight: 'bold', color: '#f44336' }}>{headToHeadStats.losses}</span>
                </div>
              </div>

              <div style={{ display: 'flex', gap: '0.35rem' }}>
                <div style={{ 
                  flex: 1, 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  padding: '0.4rem 0.3rem', 
                  backgroundColor: '#333', 
                  borderRadius: '4px',
                  gap: '0.3rem'
                }}>
                  <span style={{ fontSize: '0.75rem', color: '#888' }}>进球</span>
                  <span style={{ fontSize: '1rem', fontWeight: 'bold', color: '#4caf50' }}>{headToHeadStats.goalsFor}</span>
                </div>
                <div style={{ 
                  flex: 1, 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  padding: '0.4rem 0.3rem', 
                  backgroundColor: '#333', 
                  borderRadius: '4px',
                  gap: '0.3rem'
                }}>
                  <span style={{ fontSize: '0.75rem', color: '#888' }}>失球</span>
                  <span style={{ fontSize: '1rem', fontWeight: 'bold', color: '#f44336' }}>{headToHeadStats.goalsAgainst}</span>
                </div>
                <div style={{ 
                  flex: 1, 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  padding: '0.4rem 0.3rem', 
                  backgroundColor: '#333', 
                  borderRadius: '4px',
                  gap: '0.3rem'
                }}>
                  <span style={{ fontSize: '0.75rem', color: '#888' }}>净胜</span>
                  <span style={{ 
                    fontSize: '1rem', 
                    fontWeight: 'bold', 
                    color: headToHeadStats.goalsFor - headToHeadStats.goalsAgainst >= 0 ? '#4caf50' : '#f44336'
                  }}>
                    {headToHeadStats.goalsFor - headToHeadStats.goalsAgainst >= 0 ? '+' : ''}{headToHeadStats.goalsFor - headToHeadStats.goalsAgainst}
                  </span>
                </div>
              </div>

              <div style={{ display: 'flex', gap: '0.35rem' }}>
                <div style={{ 
                  flex: 1, 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  padding: '0.4rem 0.3rem', 
                  backgroundColor: '#333', 
                  borderRadius: '4px',
                  gap: '0.25rem'
                }}>
                  <span style={{ fontSize: '0.7rem', color: '#888' }}>主场</span>
                  <span style={{ fontSize: '0.85rem', fontWeight: 'bold', color: '#4caf50' }}>{headToHeadStats.home.wins}</span>
                  <span style={{ fontSize: '0.85rem', color: '#ffc107' }}>{headToHeadStats.home.draws}</span>
                  <span style={{ fontSize: '0.85rem', color: '#f44336' }}>{headToHeadStats.home.losses}</span>
                </div>
                <div style={{ 
                  flex: 1, 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  padding: '0.4rem 0.3rem', 
                  backgroundColor: '#333', 
                  borderRadius: '4px',
                  gap: '0.25rem'
                }}>
                  <span style={{ fontSize: '0.7rem', color: '#888' }}>客场</span>
                  <span style={{ fontSize: '0.85rem', fontWeight: 'bold', color: '#4caf50' }}>{headToHeadStats.away.wins}</span>
                  <span style={{ fontSize: '0.85rem', color: '#ffc107' }}>{headToHeadStats.away.draws}</span>
                  <span style={{ fontSize: '0.85rem', color: '#f44336' }}>{headToHeadStats.away.losses}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {loading ? (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '300px' }}>
            <div style={{ fontSize: '1.2rem', color: '#c00010' }}>加载数据中...</div>
          </div>
        ) : error ? (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '300px' }}>
            <div style={{ fontSize: '1.2rem', color: '#ff4444' }}>{error}</div>
          </div>
        ) : showHeadToHead && selectedOpponent && headToHeadMatches.length === 0 ? (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '200px' }}>
            <div style={{ fontSize: '1.2rem', color: '#888' }}>暂无与 {selectedOpponent} 的交锋记录</div>
          </div>
        ) : showHeadToHead && selectedOpponent && headToHeadMatches.length > 0 ? (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>日期</th>
                  <th>赛季</th>
                  <th>类型</th>
                  <th>轮次</th>
                  <th>主队</th>
                  <th>客队</th>
                  <th>比分</th>
                  <th>结果</th>
                  <th>报告</th>
                </tr>
              </thead>
              <tbody>
                {headToHeadMatches.map((match, index) => {
                  const isOurTeamHome = OUR_TEAM_NAMES.includes(match.home_team);
                  const isOurTeamAway = OUR_TEAM_NAMES.includes(match.away_team);
                  
                  return (
                    <tr key={index}>
                      <td style={{ whiteSpace: 'nowrap' }}>{match.date || '-'}</td>
                      <td>{match.season || '-'}</td>
                      <td style={{ fontSize: '0.85rem' }}>{match.match_type || '-'}</td>
                      <td style={{ fontSize: '0.85rem' }}>{match.round || '-'}</td>
                      <td style={{ 
                        fontWeight: isOurTeamHome ? 'bold' : 'normal',
                        color: isOurTeamHome ? '#c00010' : 'inherit'
                      }}>
                        {match.home_team || '-'}
                      </td>
                      <td style={{ 
                        fontWeight: isOurTeamAway ? 'bold' : 'normal',
                        color: isOurTeamAway ? '#c00010' : 'inherit'
                      }}>
                        {match.away_team || '-'}
                      </td>
                      <td style={{ fontWeight: 'bold' }}>{match.result || '-'}</td>
                      <td style={{
                        fontWeight: 'bold',
                        color: match.win_loss === '胜' ? '#4caf50' : 
                               match.win_loss === '负' ? '#f44336' : 
                               match.win_loss === '平' ? '#ffc107' : 'inherit'
                      }}>
                        {match.win_loss || '-'}
                      </td>
                      <td>
                        <a 
                          href={`match-report.html?date=${match.date}&type=${encodeURIComponent(match.match_type)}&round=${encodeURIComponent(match.round)}&source=h`}
                          style={{ textDecoration: 'none', color: '#c00010', fontWeight: 'bold', fontSize: '0.85rem' }}
                        >
                          查看
                        </a>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
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
                          {matches.map((match, index) => {
                            const isOurTeamHome = OUR_TEAM_NAMES.includes(match.home_team);
                            const isOurTeamAway = OUR_TEAM_NAMES.includes(match.away_team);
                            
                            return (
                              <tr key={index}>
                                <td>{match.date || '-'}</td>
                                <td>{match.match_type || '-'}</td>
                                <td>{match.round || '-'}</td>
                                <td style={{ 
                                  fontWeight: isOurTeamHome ? 'bold' : 'normal',
                                  color: isOurTeamHome ? '#c00010' : 'inherit'
                                }}>
                                  {match.home_team || '-'}
                                </td>
                                <td style={{ 
                                  fontWeight: isOurTeamAway ? 'bold' : 'normal',
                                  color: isOurTeamAway ? '#c00010' : 'inherit'
                                }}>
                                  {match.away_team || '-'}
                                </td>
                                <td>{match.result || '-'}</td>
                                <td style={{
                                  fontWeight: 'bold',
                                  color: match.win_loss === '胜' ? '#4caf50' : 
                                         match.win_loss === '负' ? '#f44336' : 
                                         match.win_loss === '平' ? '#ffc107' : 'inherit'
                                }}>
                                  {match.win_loss || '-'}
                                </td>
                                <td>
                                  <a 
                                    href={`match-report.html?date=${match.date}&type=${encodeURIComponent(match.match_type)}&round=${encodeURIComponent(match.round)}&source=h`}
                                    style={{ textDecoration: 'none', color: '#c00010', fontWeight: 'bold' }}
                                  >
                                    查看
                                  </a>
                                </td>
                              </tr>
                            );
                          })}
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
