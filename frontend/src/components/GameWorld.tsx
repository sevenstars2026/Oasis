import { useEffect, useState } from 'react';
import { wsService } from '../services/websocket';
import { useGameStore } from '../store/gameStore';
import ChatPanel from './ChatPanel';
import MapView from './MapView';
import JobsPanel from './JobsPanel';
import PropertiesPanel from './PropertiesPanel';
import MarketPanel from './MarketPanel';
import './GameWorld.css';

interface OnlinePlayer {
  player_id: number;
  username: string;
  location_id: number;
}

export default function GameWorld() {
  const { token, player } = useGameStore();
  const [onlinePlayers, setOnlinePlayers] = useState<OnlinePlayer[]>([]);
  const [activeView, setActiveView] = useState<'map' | 'jobs' | 'properties' | 'market'>('map');

  useEffect(() => {
    if (token) {
      wsService.connect(token);

      wsService.on('online_players', (data) => {
        setOnlinePlayers(data.players);
      });

      wsService.on('player_online', (data) => {
        setOnlinePlayers(prev => [...prev, {
          player_id: data.player_id,
          username: data.username,
          location_id: data.location_id,
        }]);
      });

      wsService.on('player_offline', (data) => {
        setOnlinePlayers(prev => prev.filter(p => p.player_id !== data.player_id));
      });

      wsService.on('player_move', (data) => {
        setOnlinePlayers(prev => prev.map(p =>
          p.player_id === data.player_id
            ? { ...p, location_id: data.new_location_id }
            : p
        ));
      });

      return () => {
        wsService.disconnect();
      };
    }
  }, [token]);

  return (
    <div className="game-world">
      <div className="game-header">
        <div className="player-info">
          <span className="player-name">{player?.name}</span>
          <span className="player-balance">💰 {player?.gold?.toFixed(0) || 0}</span>
        </div>
        <div className="nav-buttons">
          <button
            className={`nav-btn ${activeView === 'map' ? 'active' : ''}`}
            onClick={() => setActiveView('map')}
          >
            🗺️ 地图
          </button>
          <button
            className={`nav-btn ${activeView === 'jobs' ? 'active' : ''}`}
            onClick={() => setActiveView('jobs')}
          >
            💼 工作
          </button>
          <button
            className={`nav-btn ${activeView === 'properties' ? 'active' : ''}`}
            onClick={() => setActiveView('properties')}
          >
            🏠 房产
          </button>
          <button
            className={`nav-btn ${activeView === 'market' ? 'active' : ''}`}
            onClick={() => setActiveView('market')}
          >
            🏪 市场
          </button>
        </div>
        <div className="online-count">
          在线玩家: {onlinePlayers.length}
        </div>
      </div>

      <div className="game-content">
        <div className="left-panel">
          <div className="online-players-panel">
            <div className="panel-header">在线玩家</div>
            <div className="players-list">
              {onlinePlayers.map(p => (
                <div key={p.player_id} className="player-item">
                  <span className="player-dot"></span>
                  <span className="player-username">{p.username}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="center-panel">
          <div className="map-container">
            {activeView === 'map' && <MapView />}
            {activeView === 'jobs' && <JobsPanel />}
            {activeView === 'properties' && <PropertiesPanel />}
            {activeView === 'market' && <MarketPanel />}
          </div>
        </div>

        <div className="right-panel">
          <ChatPanel />
        </div>
      </div>
    </div>
  );
}
