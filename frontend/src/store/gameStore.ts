import { create } from 'zustand';

interface Player {
  id: number;
  name: string;
  email: string;
  job: string;
  gold: number;
}

interface Location {
  id: number;
  name: string;
  display_name: string;
  x: number;
  y: number;
  zone_type: string;
  current_players: number;
  capacity: number;
}

interface GameState {
  // 认证
  token: string | null;
  player: Player | null;
  isAuthenticated: boolean;

  // 游戏数据
  locations: Location[];
  currentLocation: Location | null;

  // UI 状态
  activePanel: 'map' | 'jobs' | 'properties' | 'market' | 'inventory';

  // Actions
  setToken: (token: string) => void;
  setPlayer: (player: Player) => void;
  logout: () => void;
  setLocations: (locations: Location[]) => void;
  setCurrentLocation: (location: Location) => void;
  setActivePanel: (panel: GameState['activePanel']) => void;
  updatePlayerGold: (gold: number) => void;
}

export const useGameStore = create<GameState>((set) => ({
  // 初始状态
  token: localStorage.getItem('token'),
  player: null,
  isAuthenticated: !!localStorage.getItem('token'),
  locations: [],
  currentLocation: null,
  activePanel: 'map',

  // Actions
  setToken: (token) => {
    localStorage.setItem('token', token);
    set({ token, isAuthenticated: true });
  },

  setPlayer: (player) => set({ player }),

  logout: () => {
    localStorage.removeItem('token');
    set({ token: null, player: null, isAuthenticated: false });
  },

  setLocations: (locations) => set({ locations }),

  setCurrentLocation: (location) => set({ currentLocation: location }),

  setActivePanel: (panel) => set({ activePanel: panel }),

  updatePlayerGold: (gold) => set((state) => ({
    player: state.player ? { ...state.player, gold } : null
  })),
}));
