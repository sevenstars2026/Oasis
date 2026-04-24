import { useEffect, useState } from 'react';
import { api } from '../api/client';
import { useGameStore } from '../store/gameStore';
import './LocationList.css';

interface Location {
  id: number;
  name: string;
  display_name: string;
  zone_type: string;
  current_players: number;
  capacity: number;
  is_unlocked: boolean;
}

export const LocationList = () => {
  const [locations, setLocations] = useState<Location[]>([]);
  const [loading, setLoading] = useState(false);
  const { setCurrentLocation, setLocations: setStoreLocations } = useGameStore();

  useEffect(() => {
    loadLocations();
  }, []);

  const loadLocations = async () => {
    setLoading(true);
    try {
      const { data } = await api.getLocations();
      setLocations(data);
      setStoreLocations(data);
      if (data.length > 0) {
        setCurrentLocation(data[0]);
      }
    } catch (err) {
      console.error('加载位置失败:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleMove = async (location: Location) => {
    try {
      await api.movePlayer({ location_id: location.id });
      setCurrentLocation(location);
      alert(`已移动到 ${location.display_name}`);
    } catch (err: any) {
      alert(err.response?.data?.detail || '移动失败');
    }
  };

  if (loading) return <div className="panel-loading">加载中...</div>;

  return (
    <div className="location-list">
      <h2>地图位置</h2>
      <div className="locations-grid">
        {locations.map((loc) => (
          <div key={loc.id} className="location-card">
            <div className="location-header">
              <h3>{loc.display_name}</h3>
              <span className={`zone-badge ${loc.zone_type}`}>
                {loc.zone_type}
              </span>
            </div>
            <div className="location-info">
              <div>👥 {loc.current_players} / {loc.capacity}</div>
              <div>{loc.is_unlocked ? '✅ 已解锁' : '🔒 未解锁'}</div>
            </div>
            <button
              onClick={() => handleMove(loc)}
              disabled={!loc.is_unlocked}
              className="move-btn"
            >
              前往
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};
