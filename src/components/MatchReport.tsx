import React from 'react';
import { useParams, useHistory } from 'react-router-dom';

// 模拟赛事报告数据
const matchReports = {
  '1': {
    id: 1,
    round: '第1轮',
    date: '2026-03-07',
    time: '19:35',
    homeTeam: '上海海港',
    awayTeam: '河南俱乐部',
    venue: '上海体育场',
    city: '上海',
    result: '1-2',
    status: '已结束',
    report: {
      summary: '上海海港在主场1-2不敌河南俱乐部，遭遇赛季开门黑。',
      highlights: [
        '第25分钟，河南俱乐部球员张三破门，0-1',
        '第45分钟，上海海港球员李四扳平比分，1-1',
        '第85分钟，河南俱乐部球员王五打进绝杀球，1-2'
      ],
      lineups: {
        home: [
          '门将: 颜骏凌',
          '后卫: 王燊超, 蒋光太, 张琳芃, 李帅',
          '中场: 张源, 让克劳德, 维塔尔',
          '前锋: 武磊, 加布里埃尔, 莱昂纳多'
        ],
        away: [
          '门将: 王五',
          '后卫: 赵六, 钱七, 孙八, 周九',
          '中场: 吴十, 郑一, 王二',
          '前锋: 张三, 李四'
        ]
      },
      statistics: {
        possession: '58% - 42%',
        shots: '15 - 8',
        shotsOnTarget: '6 - 4',
        corners: '8 - 3',
        fouls: '12 - 15',
        yellowCards: '2 - 3',
        redCards: '0 - 0'
      }
    }
  }
};

const MatchReport: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const history = useHistory();
  const match = matchReports[id as keyof typeof matchReports];

  if (!match) {
    return (
      <div className="card">
        <h2>赛事报告</h2>
        <p>未找到该比赛的赛事报告</p>
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
          {match.homeTeam} {match.result} {match.awayTeam}
        </h3>
        <p><strong>轮次:</strong> {match.round}</p>
        <p><strong>日期:</strong> {match.date}</p>
        <p><strong>时间:</strong> {match.time}</p>
        <p><strong>场地:</strong> {match.venue}</p>
        <p><strong>城市:</strong> {match.city}</p>
      </div>

      <div style={{ marginBottom: '2rem' }}>
        <h3 style={{ color: '#c00010', marginBottom: '1rem' }}>比赛 summary</h3>
        <p>{match.report.summary}</p>
      </div>

      <div style={{ marginBottom: '2rem' }}>
        <h3 style={{ color: '#c00010', marginBottom: '1rem' }}>比赛亮点</h3>
        <ul style={{ listStyle: 'disc', paddingLeft: '2rem' }}>
          {match.report.highlights.map((highlight, index) => (
            <li key={index} style={{ marginBottom: '0.5rem' }}>{highlight}</li>
          ))}
        </ul>
      </div>

      <div style={{ marginBottom: '2rem' }}>
        <h3 style={{ color: '#c00010', marginBottom: '1rem' }}>阵容</h3>
        <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
          <div>
            <h4 style={{ marginBottom: '0.5rem' }}>{match.homeTeam}</h4>
            <ul style={{ listStyle: 'none', paddingLeft: '1rem' }}>
              {match.report.lineups.home.map((player, index) => (
                <li key={index} style={{ marginBottom: '0.3rem' }}>{player}</li>
              ))}
            </ul>
          </div>
          <div>
            <h4 style={{ marginBottom: '0.5rem' }}>{match.awayTeam}</h4>
            <ul style={{ listStyle: 'none', paddingLeft: '1rem' }}>
              {match.report.lineups.away.map((player, index) => (
                <li key={index} style={{ marginBottom: '0.3rem' }}>{player}</li>
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
              <th style={{ textAlign: 'left', padding: '0.5rem', borderBottom: '1px solid #444' }}>{match.homeTeam}</th>
              <th style={{ textAlign: 'left', padding: '0.5rem', borderBottom: '1px solid #444' }}>{match.awayTeam}</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style={{ padding: '0.5rem', borderBottom: '1px solid #444' }}>控球率</td>
              <td style={{ padding: '0.5rem', borderBottom: '1px solid #444' }}>{match.report.statistics.possession.split(' - ')[0]}</td>
              <td style={{ padding: '0.5rem', borderBottom: '1px solid #444' }}>{match.report.statistics.possession.split(' - ')[1]}</td>
            </tr>
            <tr>
              <td style={{ padding: '0.5rem', borderBottom: '1px solid #444' }}>射门</td>
              <td style={{ padding: '0.5rem', borderBottom: '1px solid #444' }}>{match.report.statistics.shots.split(' - ')[0]}</td>
              <td style={{ padding: '0.5rem', borderBottom: '1px solid #444' }}>{match.report.statistics.shots.split(' - ')[1]}</td>
            </tr>
            <tr>
              <td style={{ padding: '0.5rem', borderBottom: '1px solid #444' }}>射正</td>
              <td style={{ padding: '0.5rem', borderBottom: '1px solid #444' }}>{match.report.statistics.shotsOnTarget.split(' - ')[0]}</td>
              <td style={{ padding: '0.5rem', borderBottom: '1px solid #444' }}>{match.report.statistics.shotsOnTarget.split(' - ')[1]}</td>
            </tr>
            <tr>
              <td style={{ padding: '0.5rem', borderBottom: '1px solid #444' }}>角球</td>
              <td style={{ padding: '0.5rem', borderBottom: '1px solid #444' }}>{match.report.statistics.corners.split(' - ')[0]}</td>
              <td style={{ padding: '0.5rem', borderBottom: '1px solid #444' }}>{match.report.statistics.corners.split(' - ')[1]}</td>
            </tr>
            <tr>
              <td style={{ padding: '0.5rem', borderBottom: '1px solid #444' }}>犯规</td>
              <td style={{ padding: '0.5rem', borderBottom: '1px solid #444' }}>{match.report.statistics.fouls.split(' - ')[0]}</td>
              <td style={{ padding: '0.5rem', borderBottom: '1px solid #444' }}>{match.report.statistics.fouls.split(' - ')[1]}</td>
            </tr>
            <tr>
              <td style={{ padding: '0.5rem', borderBottom: '1px solid #444' }}>黄牌</td>
              <td style={{ padding: '0.5rem', borderBottom: '1px solid #444' }}>{match.report.statistics.yellowCards.split(' - ')[0]}</td>
              <td style={{ padding: '0.5rem', borderBottom: '1px solid #444' }}>{match.report.statistics.yellowCards.split(' - ')[1]}</td>
            </tr>
            <tr>
              <td style={{ padding: '0.5rem', borderBottom: '1px solid #444' }}>红牌</td>
              <td style={{ padding: '0.5rem', borderBottom: '1px solid #444' }}>{match.report.statistics.redCards.split(' - ')[0]}</td>
              <td style={{ padding: '0.5rem', borderBottom: '1px solid #444' }}>{match.report.statistics.redCards.split(' - ')[1]}</td>
            </tr>
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
        返回赛程
      </button>
    </div>
  );
};

export default MatchReport;