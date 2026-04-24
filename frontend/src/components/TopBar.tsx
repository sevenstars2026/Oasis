import { useGameStore } from '../store/gameStore';
import './TopBar.css';

export const TopBar = () => {
  const { player, logout } = useGameStore();

  if (!player) return null;

  return (
    <div className="top-bar">
      <div className="top-bar-left">
        <h1 className="logo">🌍 Oasis</h1>
      </div>

      <div className="top-bar-center">
        <div className="player-info">
          <span className="player-name">{player.name}</span>
          <span className="player-job">{player.job}</span>
        </div>
      </div>

      <div className="top-bar-right">
        <div className="gold-display">
          💰 {player.gold.toFixed(0)} 金币
        </div>
        <button onClick={logout} className="logout-btn">
          退出
        </button>
      </div>
    </div>
  );
};
