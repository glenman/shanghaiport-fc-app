import React, { useState } from 'react';

// 模拟球员统计数据
const playerStatsData = [
  {
    id: 1,
    name: '武磊',
    position: '前锋',
    matches: 28,
    goals: 18,
    assists: 5,
    yellowCards: 3,
    redCards: 0
  },
  {
    id: 2,
    name: '奥斯卡',
    position: '中场',
    matches: 26,
    goals: 8,
    assists: 15,
    yellowCards: 4,
    redCards: 0
  },
  {
    id: 3,
    name: '巴尔加斯',
    position: '中场',
    matches: 24,
    goals: 10,
    assists: 12,
    yellowCards: 2,
    redCards: 0
  },
  {
    id: 4,
    name: '吕文君',
    position: '前锋',
    matches: 22,
    goals: 7,
    assists: 3,
    yellowCards: 2,
    redCards: 0
  },
  {
    id: 5,
    name: '张琳芃',
    position: '后卫',
    matches: 25,
    goals: 2,
    assists: 1,
    yellowCards: 5,
    redCards: 1
  }
];

// 模拟球队比赛统计数据
const teamStatsData = [
  {
    category: '主场',
    matches: 15,
    wins: 12,
    draws: 2,
    losses: 1,
    goalsFor: 38,
    goalsAgainst: 12
  },
  {
    category: '客场',
    matches: 15,
    wins: 6,
    draws: 5,
    losses: 4,
    goalsFor: 23,
    goalsAgainst: 16
  },
  {
    category: '总计',
    matches: 30,
    wins: 18,
    draws: 7,
    losses: 5,
    goalsFor: 61,
    goalsAgainst: 28
  }
];

const Stats: React.FC = () => {
  const [activeTab, setActiveTab] = useState('players');

  return (
    <div className="card">
      <h2>数据统计</h2>
      <div className="stats-tabs">
        <button 
          className={activeTab === 'players' ? 'active' : ''}
          onClick={() => setActiveTab('players')}
        >
          球员数据
        </button>
        <button 
          className={activeTab === 'team' ? 'active' : ''}
          onClick={() => setActiveTab('team')}
        >
          球队成绩
        </button>
      </div>
      
      {activeTab === 'players' && (
        <table>
          <thead>
            <tr>
              <th>球员</th>
              <th>位置</th>
              <th>出场</th>
              <th>进球</th>
              <th>助攻</th>
              <th>黄牌</th>
              <th>红牌</th>
            </tr>
          </thead>
          <tbody>
            {playerStatsData.map(player => (
              <tr key={player.id}>
                <td>{player.name}</td>
                <td>{player.position}</td>
                <td>{player.matches}</td>
                <td>{player.goals}</td>
                <td>{player.assists}</td>
                <td>{player.yellowCards}</td>
                <td>{player.redCards}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      
      {activeTab === 'team' && (
        <table>
          <thead>
            <tr>
              <th>类别</th>
              <th>比赛</th>
              <th>胜</th>
              <th>平</th>
              <th>负</th>
              <th>进球</th>
              <th>失球</th>
            </tr>
          </thead>
          <tbody>
            {teamStatsData.map((team, index) => (
              <tr key={index}>
                <td>{team.category}</td>
                <td>{team.matches}</td>
                <td>{team.wins}</td>
                <td>{team.draws}</td>
                <td>{team.losses}</td>
                <td>{team.goalsFor}</td>
                <td>{team.goalsAgainst}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default Stats;