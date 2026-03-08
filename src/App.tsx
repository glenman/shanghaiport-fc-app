import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Switch, Link } from 'react-router-dom';
import './App.css';
import Schedule from './components/Schedule';
import Players from './components/Players';
import Seasons from './components/Seasons';
import Stats from './components/Stats';
import MatchReport from './components/MatchReport';

function App() {
  const [activeTab, setActiveTab] = useState('schedule');

  return (
    <Router>
      <div className="app">
        <header className="app-header">
          <h1>上海海港足球俱乐部数据查询</h1>
        </header>
        <nav className="app-nav">
          <Link to="/" style={{ textDecoration: 'none' }}>
            <button 
              className={activeTab === 'schedule' ? 'active' : ''}
              onClick={() => setActiveTab('schedule')}
            >
              球队赛程
            </button>
          </Link>
          <Link to="/players" style={{ textDecoration: 'none' }}>
            <button 
              className={activeTab === 'players' ? 'active' : ''}
              onClick={() => setActiveTab('players')}
            >
              球员信息
            </button>
          </Link>
          <Link to="/seasons" style={{ textDecoration: 'none' }}>
            <button 
              className={activeTab === 'seasons' ? 'active' : ''}
              onClick={() => setActiveTab('seasons')}
            >
              历史赛季
            </button>
          </Link>
          <Link to="/stats" style={{ textDecoration: 'none' }}>
            <button 
              className={activeTab === 'stats' ? 'active' : ''}
              onClick={() => setActiveTab('stats')}
            >
              数据统计
            </button>
          </Link>
        </nav>
        <main className="app-content">
          <Switch>
            <Route exact path="/" component={Schedule} />
            <Route path="/players" component={Players} />
            <Route path="/seasons" component={Seasons} />
            <Route path="/stats" component={Stats} />
            <Route path="/match/:id" component={MatchReport} />
          </Switch>
        </main>
      </div>
    </Router>
  );
}

export default App;