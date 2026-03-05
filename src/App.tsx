import React, { useState } from 'react';
import './App.css';
import Schedule from './components/Schedule';
import Players from './components/Players';
import Seasons from './components/Seasons';
import Stats from './components/Stats';

function App() {
  const [activeTab, setActiveTab] = useState('schedule');

  return (
    <div className="app">
      <header className="app-header">
        <h1>上海海港足球俱乐部数据查询</h1>
      </header>
      <nav className="app-nav">
        <button 
          className={activeTab === 'schedule' ? 'active' : ''}
          onClick={() => setActiveTab('schedule')}
        >
          球队赛程
        </button>
        <button 
          className={activeTab === 'players' ? 'active' : ''}
          onClick={() => setActiveTab('players')}
        >
          球员信息
        </button>
        <button 
          className={activeTab === 'seasons' ? 'active' : ''}
          onClick={() => setActiveTab('seasons')}
        >
          历史赛季
        </button>
        <button 
          className={activeTab === 'stats' ? 'active' : ''}
          onClick={() => setActiveTab('stats')}
        >
          数据统计
        </button>
      </nav>
      <main className="app-content">
        {activeTab === 'schedule' && <Schedule />}
        {activeTab === 'players' && <Players />}
        {activeTab === 'seasons' && <Seasons />}
        {activeTab === 'stats' && <Stats />}
      </main>
    </div>
  );
}

export default App;