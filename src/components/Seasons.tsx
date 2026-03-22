import React, { useState, useEffect, useRef } from 'react';

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
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const [chartWidth, setChartWidth] = useState(800);
  const [isMobile, setIsMobile] = useState(false);

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

  useEffect(() => {
    const checkMobile = () => {
      const width = window.innerWidth;
      setIsMobile(width < 768);
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);

    return () => {
      window.removeEventListener('resize', checkMobile);
    };
  }, []);

  useEffect(() => {
    const handleResize = () => {
      if (chartContainerRef.current) {
        const containerWidth = chartContainerRef.current.clientWidth;
        const newWidth = Math.max(600, Math.min(containerWidth - 40, 1200));
        console.log('容器宽度:', containerWidth, '图表宽度:', newWidth, '是否移动端:', isMobile);
        setChartWidth(newWidth);
      }
    };

    handleResize();
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  const filteredSeasons = seasonsData.filter(season => {
    const matchesSearch = searchTerm === '' || 
      (season.season && season.season.includes(searchTerm)) ||
      (season.league && season.league.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (season.rank && season.rank.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (season.notes && season.notes.toLowerCase().includes(searchTerm.toLowerCase()));
    return matchesSearch;
  });

  const getRankIcon = (rank: string) => {
    if (rank === '冠军') return '🏆';
    if (rank === '亚军') return '🥈';
    if (rank === '季军') return '🥉';
    return '';
  };

  const getRankColor = (rank: string) => {
    if (rank === '冠军') return '#ffd700';
    if (rank === '亚军') return '#c0c0c0';
    if (rank === '季军') return '#cd7f32';
    return '#c00010';
  };

  const render = () => {
    if (seasonsData.length === 0) return null;
    
    const sortedSeasons = [...seasonsData].sort((a, b) => parseInt(a.season) - parseInt(b.season));
    const maxPoints = Math.max(...sortedSeasons.map(s => s.points));
    const minPoints = Math.min(...sortedSeasons.map(s => s.points));
    const pointsRange = maxPoints - minPoints || 1;

    const chartHeight = 200;
    const padding = 40;
    const effectiveWidth = chartWidth - padding * 2;
    const effectiveHeight = chartHeight - padding * 2;

    const points = sortedSeasons.map((season, index) => {
      const x = padding + (index / (sortedSeasons.length - 1)) * effectiveWidth;
      const y = padding + effectiveHeight - ((season.points - minPoints) / pointsRange) * effectiveHeight;
      return { x, y, season };
    });

    const pathD = points.map((p, i) => 
      `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`
    ).join(' ');

    const scale = chartWidth / 800;
    const fontSize = Math.max(8, Math.min(12, 12 * scale));
    const iconSize = Math.max(12, Math.min(16, 16 * scale));
    const circleRadius = Math.max(4, Math.min(6, 6 * scale));
    const textOffset = Math.max(10, Math.min(15, 15 * scale));
    const seasonOffset = Math.max(18, Math.min(25, 25 * scale));
    const iconOffset = Math.max(25, Math.min(35, 35 * scale));

    return (
      <div ref={chartContainerRef} style={{ marginBottom: '1.5rem', padding: '1rem', backgroundColor: '#333', borderRadius: '8px' }}>
        <h3 style={{ color: '#fff', marginBottom: '1rem', fontSize: Math.max(0.9, 1.1 * scale) }}>📈 赛季成绩走向</h3>
        <svg width={chartWidth} height={chartHeight} style={{ backgroundColor: '#2a2a2a', borderRadius: '4px' }}>
          <defs>
            <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#c00010" />
              <stop offset="100%" stopColor="#ff4757" />
            </linearGradient>
          </defs>
          
          <line
            x1={padding}
            y1={padding}
            x2={padding}
            y2={chartHeight - padding}
            stroke="#555"
            strokeWidth={Math.max(0.5, 1 * scale)}
          />
          <line
            x1={padding}
            y1={chartHeight - padding}
            x2={chartWidth - padding}
            y2={chartHeight - padding}
            stroke="#555"
            strokeWidth={Math.max(0.5, 1 * scale)}
          />

          <path
            d={pathD}
            fill="none"
            stroke="url(#lineGradient)"
            strokeWidth={Math.max(2, 3 * scale)}
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {points.map((p, i) => {
            const seasonData = sortedSeasons[i];
            const icon = getRankIcon(seasonData.rank);
            return (
              <g key={i}>
                <circle
                  cx={p.x}
                  cy={p.y}
                  r={circleRadius}
                  fill="#c00010"
                  stroke="#fff"
                  strokeWidth={Math.max(1, 2 * scale)}
                />
                <text
                  x={p.x}
                  y={p.y - textOffset}
                  textAnchor="middle"
                  fill="#fff"
                  fontSize={fontSize}
                  fontWeight="bold"
                >
                  {seasonData.points}分
                </text>
                <text
                  x={p.x}
                  y={chartHeight - padding + seasonOffset}
                  textAnchor="middle"
                  fill="#888"
                  fontSize={Math.max(9, 10 * scale)}
                >
                  {seasonData.season}
                </text>
                {icon && (
                  <text
                    x={p.x}
                    y={p.y - iconOffset}
                    textAnchor="middle"
                    fontSize={iconSize}
                  >
                    {icon}
                  </text>
                )}
              </g>
            );
          })}
        </svg>
      </div>
    );
  };

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
        {render()}
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
                {filteredSeasons.map((season, index) => {
                  const rankIcon = getRankIcon(season.rank);
                  const rankColor = getRankColor(season.rank);
                  
                  return (
                    <tr key={season.id || index}>
                      <td style={{ fontWeight: 'bold', color: '#c00010' }}>{season.season || '-'}</td>
                      <td>{season.league || '-'}</td>
                      <td style={{ 
                        fontWeight: 'bold', 
                        color: rankColor,
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.3rem'
                      }}>
                        {rankIcon && <span style={{ marginRight: '0.3rem' }}>{rankIcon}</span>}
                        {season.rank || '-'}
                      </td>
                      <td>{season.matches || '-'}</td>
                      <td style={{ color: '#4caf50', fontWeight: 'bold' }}>{season.wins || '-'}</td>
                      <td style={{ color: '#ffc107', fontWeight: 'bold' }}>{season.draws || '-'}</td>
                      <td style={{ color: '#f44336', fontWeight: 'bold' }}>{season.losses || '-'}</td>
                      <td style={{ color: '#4caf50' }}>{season.goalsFor || '-'}</td>
                      <td style={{ color: '#f44336' }}>{season.goalsAgainst || '-'}</td>
                      <td style={{ 
                        fontWeight: 'bold', 
                        color: '#c00010',
                        fontSize: '1.1rem'
                      }}>
                        {season.points || '-'}
                      </td>
                      <td style={{ fontSize: '0.85rem', color: '#888' }}>{season.notes || '-'}</td>
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

export default Seasons;