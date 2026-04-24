import { useEffect, useState } from 'react';
import { api } from '../api/client';
import { wsService } from '../services/websocket';
import './MapView.css';

interface Location {
  id: number;
  name: string;
  display_name: string;
  x: number;
  y: number;
  zone_type: string;
  current_players: number;
  capacity: number;
  is_unlocked: boolean;
}

interface MapViewProps {
  onLocationSelect?: (location: Location) => void;
}

export default function MapView({ onLocationSelect }: MapViewProps) {
  const [locations, setLocations] = useState<Location[]>([]);
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLocations();
  }, []);

  const loadLocations = async () => {
    try {
      const { data } = await api.getLocations();
      setLocations(data);
    } catch (error) {
      console.error('加载地图失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLocationClick = async (location: Location) => {
    if (!location.is_unlocked) {
      alert('该区域尚未解锁');
      return;
    }

    setSelectedLocation(location);

    try {
      await api.movePlayer({ location_id: location.id });
      wsService.sendMove(location.id);
      onLocationSelect?.(location);
    } catch (error: any) {
      alert(error.response?.data?.detail || '移动失败');
    }
  };

  const getZoneColor = (zoneType: string) => {
    const colors: Record<string, string> = {
      commercial: '#10b981',
      residential: '#3b82f6',
      industrial: '#f59e0b',
      wilderness: '#84cc16',
    };
    return colors[zoneType] || '#6b7280';
  };

  if (loading) {
    return (
      <div className="map-view loading">
        <div className="loading-spinner"></div>
        <p>加载地图中...</p>
      </div>
    );
  }

  return (
    <div className="map-view">
      <svg className="map-svg" viewBox="-400 -400 800 800">
        {/* 网格背景 */}
        <defs>
          <pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse">
            <path d="M 50 0 L 0 0 0 50" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="1"/>
          </pattern>
        </defs>
        <rect x="-400" y="-400" width="800" height="800" fill="url(#grid)" />

        {/* 连接线 */}
        {locations.map((loc, i) =>
          locations.slice(i + 1).map((other) => (
            <line
              key={`${loc.id}-${other.id}`}
              x1={loc.x * 2}
              y1={-loc.y * 2}
              x2={other.x * 2}
              y2={-other.y * 2}
              stroke="rgba(255,255,255,0.1)"
              strokeWidth="1"
            />
          ))
        )}

        {/* 位置节点 */}
        {locations.map((loc) => (
          <g
            key={loc.id}
            transform={`translate(${loc.x * 2}, ${-loc.y * 2})`}
            onClick={() => handleLocationClick(loc)}
            className={`location-node ${!loc.is_unlocked ? 'locked' : ''} ${selectedLocation?.id === loc.id ? 'selected' : ''}`}
            style={{ cursor: loc.is_unlocked ? 'pointer' : 'not-allowed' }}
          >
            <circle
              r="30"
              fill={loc.is_unlocked ? getZoneColor(loc.zone_type) : '#4b5563'}
              opacity={loc.is_unlocked ? 0.8 : 0.3}
              stroke={selectedLocation?.id === loc.id ? '#fff' : 'rgba(255,255,255,0.3)'}
              strokeWidth={selectedLocation?.id === loc.id ? 3 : 2}
            />

            {!loc.is_unlocked && (
              <text
                y="5"
                textAnchor="middle"
                fill="#fff"
                fontSize="20"
              >
                🔒
              </text>
            )}

            <text
              y="50"
              textAnchor="middle"
              fill="#fff"
              fontSize="14"
              fontWeight="600"
            >
              {loc.display_name}
            </text>

            {loc.current_players > 0 && (
              <text
                y="70"
                textAnchor="middle"
                fill="#a78bfa"
                fontSize="12"
              >
                👥 {loc.current_players}
              </text>
            )}
          </g>
        ))}
      </svg>

      {selectedLocation && (
        <div className="location-info">
          <h3>{selectedLocation.display_name}</h3>
          <div className="info-row">
            <span className="label">类型:</span>
            <span className="value">{selectedLocation.zone_type}</span>
          </div>
          <div className="info-row">
            <span className="label">在线:</span>
            <span className="value">{selectedLocation.current_players} / {selectedLocation.capacity}</span>
          </div>
        </div>
      )}
    </div>
  );
}
