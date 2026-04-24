import { useState, useEffect } from 'react';
import { api } from '../api/client';
import './MarketPanel.css';

interface MarketListing {
  id: number;
  seller_id: number;
  seller_name: string;
  item_name: string;
  quantity: number;
  price: number;
  created_at: string;
}

export default function MarketPanel() {
  const [listings, setListings] = useState<MarketListing[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMarket();
  }, []);

  const loadMarket = async () => {
    try {
      const res = await api.getMarket();
      setListings(res.data);
    } catch (error) {
      console.error('加载市场失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleBuy = async (listingId: number) => {
    try {
      await api.acceptTrade(listingId);
      alert('购买成功！');
      loadMarket();
    } catch (error: any) {
      alert(error.response?.data?.detail || '购买失败');
    }
  };

  const getItemIcon = (itemName: string) => {
    const icons: Record<string, string> = {
      wood: '🪵',
      stone: '🪨',
      iron: '⚙️',
      gold: '💰',
      food: '🍖',
      potion: '🧪',
      sword: '⚔️',
      armor: '🛡️',
    };
    return icons[itemName.toLowerCase()] || '📦';
  };

  if (loading) {
    return <div className="market-panel loading">加载中...</div>;
  }

  return (
    <div className="market-panel">
      <div className="market-header">
        <h2>🏪 交易市场</h2>
        <div className="market-count">{listings.length} 个商品</div>
      </div>

      <div className="market-list">
        {listings.map(listing => (
          <div key={listing.id} className="market-card">
            <div className="item-icon">{getItemIcon(listing.item_name)}</div>
            <div className="item-info">
              <h3>{listing.item_name}</h3>
              <div className="item-meta">
                <span className="item-quantity">数量: {listing.quantity}</span>
                <span className="item-seller">卖家: {listing.seller_name}</span>
              </div>
              <div className="item-price">
                <span className="price-label">单价:</span>
                <span className="price-value">💰 {listing.price}</span>
              </div>
            </div>
            <button onClick={() => handleBuy(listing.id)} className="buy-btn">
              购买
            </button>
          </div>
        ))}
        {listings.length === 0 && (
          <div className="empty-state">市场暂无商品</div>
        )}
      </div>
    </div>
  );
}
