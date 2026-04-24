import { useEffect } from 'react';
import { Auth } from './components/Auth';
import { TopBar } from './components/TopBar';
import { Sidebar } from './components/Sidebar';
import { GameMap } from './components/GameMap';
import { LocationList } from './components/LocationList';
import { useGameStore } from './store/gameStore';
import { api } from './api/client';
import './App.css';

function App() {
  const { isAuthenticated, setPlayer, activePanel } = useGameStore();

  useEffect(() => {
    if (isAuthenticated) {
      loadPlayer();
    }
  }, [isAuthenticated]);

  const loadPlayer = async () => {
    try {
      const { data } = await api.getMe();
      setPlayer(data);
    } catch (err) {
      console.error('加载玩家信息失败:', err);
    }
  };

  if (!isAuthenticated) {
    return <Auth />;
  }

  return (
    <div className="app">
      <TopBar />
      <div className="app-content">
        <Sidebar />
        <div className="main-panel">
          {activePanel === 'map' && (
            <>
              <GameMap />
              <LocationList />
            </>
          )}
          {activePanel === 'jobs' && <div className="panel-placeholder">💼 工作系统（开发中）</div>}
          {activePanel === 'properties' && <div className="panel-placeholder">🏠 房产系统（开发中）</div>}
          {activePanel === 'market' && <div className="panel-placeholder">🏪 市场系统（开发中）</div>}
          {activePanel === 'inventory' && <div className="panel-placeholder">🎒 背包系统（开发中）</div>}
        </div>
      </div>
    </div>
  );
}

export default App;
