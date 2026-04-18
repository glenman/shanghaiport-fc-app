import React, { useState } from 'react';
import './App.css';
import Players from './components/Players';
import Schedule from './components/Schedule';
import Seasons from './components/Seasons';
import Statistics from './components/Statistics';
import History from './components/History';
import CurrentStats from './components/CurrentStats';

interface Player {
  id: number;
  name: string;
  position: string;
  number: number;
  age: number;
  nationality: string;
  height?: string;
  weight?: string;
}

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

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('schedule');
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  const toggleSidebar = () => {
    setIsSidebarCollapsed(!isSidebarCollapsed);
  };

  return (
    <div className="app">
      <aside className={`sidebar ${isSidebarCollapsed ? 'collapsed' : ''}`}>
        <div className="sidebar-header">
          <h2 className="sidebar-title">菜单</h2>
        </div>
        <button className="toggle-btn" onClick={toggleSidebar}>
          {isSidebarCollapsed ? '→' : '←'}
        </button>
        <nav className="sidebar-menu">
          <div 
            className={`menu-item ${activeTab === 'players' ? 'active' : ''}`}
            onClick={() => setActiveTab('players')}
          >
            <span className="menu-icon">👥</span>
            <span className="menu-text">球队信息</span>
          </div>
          <div 
            className={`menu-item ${activeTab === 'schedule' ? 'active' : ''}`}
            onClick={() => setActiveTab('schedule')}
          >
            <span className="menu-icon">⚽</span>
            <span className="menu-text">球队赛程</span>
          </div>
          <div 
            className={`menu-item ${activeTab === 'currentStats' ? 'active' : ''}`}
            onClick={() => setActiveTab('currentStats')}
          >
            <span className="menu-icon">📈</span>
            <span className="menu-text">当季数据统计</span>
          </div>
          <div 
            className={`menu-item ${activeTab === 'seasons' ? 'active' : ''}`}
            onClick={() => setActiveTab('seasons')}
          >
            <span className="menu-icon">🏆</span>
            <span className="menu-text">历史赛季排名</span>
          </div>
          <div 
            className={`menu-item ${activeTab === 'statistics' ? 'active' : ''}`}
            onClick={() => setActiveTab('statistics')}
          >
            <span className="menu-icon">📊</span>
            <span className="menu-text">进球助攻榜</span>
          </div>
          <div 
            className={`menu-item ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
          >
            <span className="menu-icon">📅</span>
            <span className="menu-text">历史比赛</span>
          </div>
        </nav>
      </aside>
      
      <div className="main-content">
        <header className="app-header">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '1rem' }}>
            <img src="images/shanghaiport-logo.png" alt="上海海港队徽" style={{ width: '60px', height: '60px', borderRadius: '50%', boxShadow: '0 4px 8px rgba(0, 0, 0, 0.3)' }} />
            <div>
              <h1>上海海港足球俱乐部数据查询</h1>
              <h2>Shanghai Port FC Data Query</h2>
            </div>
          </div>
        </header>
        <main className="app-content">
          {activeTab === 'schedule' && <Schedule />}
          {activeTab === 'players' && <Players />}
          {activeTab === 'seasons' && <Seasons />}
          {activeTab === 'statistics' && <Statistics />}
          {activeTab === 'currentStats' && <CurrentStats />}
          {activeTab === 'history' && <History />}
        </main>
        <div className="app-footer">
          <div className="stars-container">
            <img src="images/shanghaiport-4star.jpg" alt="上海海港四星" className="stars-image" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;