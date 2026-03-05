import React from 'react';

// 模拟历史赛季数据
const seasonsData = [
  {
    id: 1,
    season: '2023',
    league: '中超联赛',
    rank: 2,
    matches: 30,
    wins: 18,
    draws: 7,
    losses: 5,
    goalsFor: 61,
    goalsAgainst: 28,
    points: 61
  },
  {
    id: 2,
    season: '2022',
    league: '中超联赛',
    rank: 4,
    matches: 34,
    wins: 17,
    draws: 8,
    losses: 9,
    goalsFor: 65,
    goalsAgainst: 45,
    points: 59
  },
  {
    id: 3,
    season: '2021',
    league: '中超联赛',
    rank: 1,
    matches: 22,
    wins: 17,
    draws: 3,
    losses: 2,
    goalsFor: 42,
    goalsAgainst: 14,
    points: 54
  },
  {
    id: 4,
    season: '2020',
    league: '中超联赛',
    rank: 4,
    matches: 20,
    wins: 9,
    draws: 5,
    losses: 6,
    goalsFor: 32,
    goalsAgainst: 26,
    points: 32
  },
  {
    id: 5,
    season: '2019',
    league: '中超联赛',
    rank: 1,
    matches: 30,
    wins: 25,
    draws: 2,
    losses: 3,
    goalsFor: 72,
    goalsAgainst: 29,
    points: 77
  }
];

const Seasons: React.FC = () => {
  return (
    <div className="card">
      <h2>历史赛季成绩</h2>
      <table>
        <thead>
          <tr>
            <th>赛季</th>
            <th>联赛</th>
            <th>排名</th>
            <th>比赛</th>
            <th>胜</th>
            <th>平</th>
            <th>负</th>
            <th>进球</th>
            <th>失球</th>
            <th>积分</th>
          </tr>
        </thead>
        <tbody>
          {seasonsData.map(season => (
            <tr key={season.id}>
              <td>{season.season}</td>
              <td>{season.league}</td>
              <td>{season.rank}</td>
              <td>{season.matches}</td>
              <td>{season.wins}</td>
              <td>{season.draws}</td>
              <td>{season.losses}</td>
              <td>{season.goalsFor}</td>
              <td>{season.goalsAgainst}</td>
              <td>{season.points}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Seasons;