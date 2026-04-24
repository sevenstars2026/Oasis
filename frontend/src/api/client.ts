import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器：添加 token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器：处理错误
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// API 方法
export const api = {
  // 玩家相关
  register: (data: { username: string; email: string; password: string; job_type: string }) =>
    apiClient.post('/players/register', data),

  login: (data: { email: string; password: string }) =>
    apiClient.post('/players/login', data),

  getMe: () => apiClient.get('/players/me'),

  // 地图相关
  getLocations: () => apiClient.get('/map/locations'),

  getLocationDetails: (locationId: number) =>
    apiClient.get(`/map/locations/${locationId}`),

  movePlayer: (data: { location_id: number; x?: number; y?: number }) =>
    apiClient.post('/map/move', data),

  harvestResource: (data: { resource_id: number; duration_minutes: number }) =>
    apiClient.post('/map/harvest', data),

  // 工作相关
  getAvailableJobs: (params?: { location_id?: number; job_class?: string }) =>
    apiClient.get('/jobs/available', { params }),

  startWork: (data: { job_id: number }) =>
    apiClient.post('/jobs/start', data),

  endWork: (data: { work_session_id: number }) =>
    apiClient.post('/jobs/end', data),

  getCurrentWork: () => apiClient.get('/jobs/current'),

  getWorkHistory: () => apiClient.get('/jobs/history'),

  // 房产相关
  getPropertiesForSale: (params?: { location_id?: number; property_type?: string }) =>
    apiClient.get('/properties/for-sale', { params }),

  getMyProperties: () => apiClient.get('/properties/my-properties'),

  buyProperty: (data: { property_id: number }) =>
    apiClient.post('/properties/buy', data),

  rentProperty: (data: { property_id: number }) =>
    apiClient.post('/properties/rent', data),

  upgradeProperty: (data: { property_id: number; upgrade_type: string }) =>
    apiClient.post('/properties/upgrade', data),

  // 交易相关
  getMarket: (params?: { status?: string; item_name?: string }) =>
    apiClient.get('/trades/market', { params }),

  createTrade: (data: { item_name: string; quantity: number; price: number; trade_type: string }) =>
    apiClient.post('/trades/create', data),

  acceptTrade: (tradeId: number) =>
    apiClient.post(`/trades/${tradeId}/accept`),
};
