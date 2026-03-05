import React, { useState } from 'react';

// 模拟赛程数据
const scheduleData = [
  {
    id: 1,
    date: '2024-03-01',
    time: '19:35',
    homeTeam: '上海海港',
    awayTeam: '北京国安',
    venue: '上海体育场',
    result: '2-0',
    status: '已结束'
  },
  {
    id: 2,
    date: '2024-03-08',
    time: '19:35',
    homeTeam: '上海海港',
    awayTeam: '山东泰山',
    venue: '上海体育场',
    result: '-',
    status: '未开始'
  },
  {
    id: 3,
    date: '2024-03-15',
    time: '15:30',
    homeTeam: '广州队',
    awayTeam: '上海海港',
    venue: '广州天河体育场',
    result: '-',
    status: '未开始'
  },
  {
    id: 4,
    date: '2024-03-22',
    time: '19:35',
    homeTeam: '上海海港',
    awayTeam: '深圳队',
    venue: '上海体育场',
    result: '-',
    status: '未开始'
  },
  {
    id: 5,
    date: '2024-03-29',
    time: '15:30',
    homeTeam: '武汉三镇',
    awayTeam: '上海海港',
    venue: '武汉体育中心',
    result: '-',
    status: '未开始'
  }
];

const Schedule: React.FC = () => {
  const [filter, setFilter] = useState('all');

  const filteredSchedule = filter === 'all' 
    ? scheduleData 
    : scheduleData.filter(item => item.status === filter);

  return (
    <div className="card">
      <h2>球队赛程</h2>
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
      <table>
        <thead>
          <tr>
            <th>日期</th>
            <th>时间</th>
            <th>主队</th>
            <th>客队</th>
            <th>场地</th>
            <th>赛果</th>
            <th>状态</th>
          </tr>
        </thead>
        <tbody>
          {filteredSchedule.map(match => (
            <tr key={match.id}>
              <td>{match.date}</td>
              <td>{match.time}</td>
              <td>{match.homeTeam}</td>
              <td>{match.awayTeam}</td>
              <td>{match.venue}</td>
              <td>{match.result}</td>
              <td>{match.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Schedule;