import { useEffect } from 'react';
import { Auth } from './components/Auth';
import GameWorld from './components/GameWorld';
import { useGameStore } from './store/gameStore';
import { api } from './api/client';
import './App.css';

function App() {
  const { isAuthenticated, setPlayer } = useGameStore();

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

  return <GameWorld />;
}

export default App;
