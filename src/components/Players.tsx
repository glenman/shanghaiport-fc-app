import React, { useState } from 'react';

// 模拟球员数据
const playersData = [
  {
    id: 1,
    name: '颜骏凌',
    position: '守门员',
    number: 1,
    age: 32,
    nationality: '中国',
    height: '191cm',
    weight: '83kg'
  },
  {
    id: 2,
    name: '张琳芃',
    position: '后卫',
    number: 5,
    age: 34,
    nationality: '中国',
    height: '186cm',
    weight: '78kg'
  },
  {
    id: 3,
    name: '奥斯卡',
    position: '中场',
    number: 8,
    age: 32,
    nationality: '巴西',
    height: '180cm',
    weight: '72kg'
  },
  {
    id: 4,
    name: '武磊',
    position: '前锋',
    number: 7,
    age: 32,
    nationality: '中国',
    height: '174cm',
    weight: '66kg'
  },
  {
    id: 5,
    name: '巴尔加斯',
    position: '中场',
    number: 10,
    age: 25,
    nationality: '阿根廷',
    height: '170cm',
    weight: '68kg'
  },
  {
    id: 6,
    name: '蒋光太',
    position: '后卫',
    number: 4,
    age: 29,
    nationality: '中国',
    height: '187cm',
    weight: '80kg'
  },
  {
    id: 7,
    name: '吕文君',
    position: '前锋',
    number: 11,
    age: 34,
    nationality: '中国',
    height: '185cm',
    weight: '75kg'
  },
  {
    id: 8,
    name: '蔡慧康',
    position: '中场',
    number: 6,
    age: 33,
    nationality: '中国',
    height: '184cm',
    weight: '82kg'
  }
];

const Players: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [positionFilter, setPositionFilter] = useState('all');

  const filteredPlayers = playersData.filter(player => {
    const matchesSearch = player.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesPosition = positionFilter === 'all' || player.position === positionFilter;
    return matchesSearch && matchesPosition;
  });

  const positions = ['all', ...new Set(playersData.map(player => player.position))];

  return (
    <div className="card">
      <h2>球员信息</h2>
      <div className="player-filters">
        <input
          type="text"
          placeholder="搜索球员..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />
        <select
          value={positionFilter}
          onChange={(e) => setPositionFilter(e.target.value)}
          className="position-filter"
        >
          {positions.map(position => (
            <option key={position} value={position}>
              {position === 'all' ? '全部位置' : position}
            </option>
          ))}
        </select>
      </div>
      <table>
        <thead>
          <tr>
            <th>号码</th>
            <th>姓名</th>
            <th>位置</th>
            <th>年龄</th>
            <th>国籍</th>
            <th>身高</th>
            <th>体重</th>
          </tr>
        </thead>
        <tbody>
          {filteredPlayers.map(player => (
            <tr key={player.id}>
              <td>{player.number}</td>
              <td>{player.name}</td>
              <td>{player.position}</td>
              <td>{player.age}</td>
              <td>{player.nationality}</td>
              <td>{player.height}</td>
              <td>{player.weight}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Players;