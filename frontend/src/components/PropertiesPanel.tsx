import { useState, useEffect } from 'react';
import { api } from '../api/client';
import './PropertiesPanel.css';

interface Property {
  id: number;
  name: string;
  property_type: string;
  location_id: number;
  price: number;
  rent_price: number;
  capacity: number;
  status: string;
  owner_id: number | null;
}

export default function PropertiesPanel() {
  const [forSale, setForSale] = useState<Property[]>([]);
  const [myProperties, setMyProperties] = useState<Property[]>([]);
  const [activeTab, setActiveTab] = useState<'market' | 'owned'>('market');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [saleRes, myRes] = await Promise.all([
        api.getPropertiesForSale(),
        api.getMyProperties(),
      ]);
      setForSale(saleRes.data);
      setMyProperties(myRes.data);
    } catch (error) {
      console.error('加载房产失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleBuy = async (propertyId: number) => {
    try {
      await api.buyProperty({ property_id: propertyId });
      alert('购买成功！');
      loadData();
    } catch (error: any) {
      alert(error.response?.data?.detail || '购买失败');
    }
  };

  const handleRent = async (propertyId: number) => {
    try {
      await api.rentProperty({ property_id: propertyId });
      alert('租赁成功！');
      loadData();
    } catch (error: any) {
      alert(error.response?.data?.detail || '租赁失败');
    }
  };

  const getPropertyIcon = (type: string) => {
    const icons: Record<string, string> = {
      apartment: '🏢',
      house: '🏠',
      villa: '🏰',
      shop: '🏪',
      warehouse: '🏭',
    };
    return icons[type] || '🏠';
  };

  if (loading) {
    return <div className="properties-panel loading">加载中...</div>;
  }

  return (
    <div className="properties-panel">
      <div className="properties-header">
        <h2>🏠 房产系统</h2>
        <div className="tab-buttons">
          <button
            className={`tab-btn ${activeTab === 'market' ? 'active' : ''}`}
            onClick={() => setActiveTab('market')}
          >
            市场 ({forSale.length})
          </button>
          <button
            className={`tab-btn ${activeTab === 'owned' ? 'active' : ''}`}
            onClick={() => setActiveTab('owned')}
          >
            我的房产 ({myProperties.length})
          </button>
        </div>
      </div>

      {activeTab === 'market' && (
        <div className="properties-list">
          {forSale.map(property => (
            <div key={property.id} className="property-card">
              <div className="property-icon">{getPropertyIcon(property.property_type)}</div>
              <div className="property-info">
                <h3>{property.name}</h3>
                <div className="property-meta">
                  <span className="property-type">{property.property_type}</span>
                  <span className="property-capacity">容量: {property.capacity}</span>
                </div>
                <div className="property-prices">
                  <div className="price-item">
                    <span className="price-label">售价:</span>
                    <span className="price-value">💰 {property.price}</span>
                  </div>
                  <div className="price-item">
                    <span className="price-label">租金:</span>
                    <span className="price-value">💰 {property.rent_price}/月</span>
                  </div>
                </div>
              </div>
              <div className="property-actions">
                <button onClick={() => handleBuy(property.id)} className="buy-btn">
                  购买
                </button>
                <button onClick={() => handleRent(property.id)} className="rent-btn">
                  租赁
                </button>
              </div>
            </div>
          ))}
          {forSale.length === 0 && (
            <div className="empty-state">暂无可售房产</div>
          )}
        </div>
      )}

      {activeTab === 'owned' && (
        <div className="properties-list">
          {myProperties.map(property => (
            <div key={property.id} className="property-card owned">
              <div className="property-icon">{getPropertyIcon(property.property_type)}</div>
              <div className="property-info">
                <h3>{property.name}</h3>
                <div className="property-meta">
                  <span className="property-type">{property.property_type}</span>
                  <span className="property-status">{property.status}</span>
                </div>
                <div className="property-value">
                  <span className="value-label">价值:</span>
                  <span className="value-amount">💰 {property.price}</span>
                </div>
              </div>
            </div>
          ))}
          {myProperties.length === 0 && (
            <div className="empty-state">您还没有房产</div>
          )}
        </div>
      )}
    </div>
  );
}
