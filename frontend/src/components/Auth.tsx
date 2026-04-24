import { useState } from 'react';
import { api } from '../api/client';
import { useGameStore } from '../store/gameStore';
import './Auth.css';

export const Auth = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    job_type: 'merchant',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { setToken, setPlayer } = useGameStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        const { data } = await api.login({
          email: formData.email,
          password: formData.password,
        });
        setToken(data.access_token);
        setPlayer(data.player);
      } else {
        const { data } = await api.register(formData);
        setToken(data.access_token);
        setPlayer(data.player);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || '操作失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-box">
        <h1 className="auth-title">🌍 Oasis</h1>
        <p className="auth-subtitle">第二国度</p>

        <div className="auth-tabs">
          <button
            className={isLogin ? 'active' : ''}
            onClick={() => setIsLogin(true)}
          >
            登录
          </button>
          <button
            className={!isLogin ? 'active' : ''}
            onClick={() => setIsLogin(false)}
          >
            注册
          </button>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {!isLogin && (
            <input
              type="text"
              placeholder="用户名"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              required
            />
          )}

          <input
            type="email"
            placeholder="邮箱"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            required
          />

          <input
            type="password"
            placeholder="密码"
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            required
          />

          {!isLogin && (
            <select
              value={formData.job_type}
              onChange={(e) => setFormData({ ...formData, job_type: e.target.value })}
            >
              <option value="merchant">商人 (Merchant)</option>
              <option value="warrior">战士 (Warrior)</option>
              <option value="crafter">工匠 (Crafter)</option>
              <option value="scholar">学者 (Scholar)</option>
            </select>
          )}

          {error && <div className="auth-error">{error}</div>}

          <button type="submit" disabled={loading} className="auth-submit">
            {loading ? '处理中...' : isLogin ? '登录' : '注册'}
          </button>
        </form>
      </div>
    </div>
  );
};
