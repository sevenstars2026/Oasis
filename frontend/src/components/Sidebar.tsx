import { useGameStore } from '../store/gameStore';
import './Sidebar.css';

export const Sidebar = () => {
  const { activePanel, setActivePanel, currentLocation } = useGameStore();

  const panels = [
    { id: 'map', icon: '🗺️', label: '地图' },
    { id: 'jobs', icon: '💼', label: '工作' },
    { id: 'properties', icon: '🏠', label: '房产' },
    { id: 'market', icon: '🏪', label: '市场' },
    { id: 'inventory', icon: '🎒', label: '背包' },
  ];

  return (
    <div className="sidebar">
      <div className="sidebar-location">
        <div className="location-label">当前位置</div>
        <div className="location-name">
          {currentLocation?.display_name || '未知'}
        </div>
      </div>

      <div className="sidebar-nav">
        {panels.map((panel) => (
          <button
            key={panel.id}
            className={`sidebar-btn ${activePanel === panel.id ? 'active' : ''}`}
            onClick={() => setActivePanel(panel.id as any)}
          >
            <span className="sidebar-icon">{panel.icon}</span>
            <span className="sidebar-label">{panel.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
};
