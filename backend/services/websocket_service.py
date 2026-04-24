from typing import Dict, Set, Optional
from fastapi import WebSocket
import json
from datetime import datetime

class ConnectionManager:
    def __init__(self):
        # player_id -> WebSocket
        self.active_connections: Dict[int, WebSocket] = {}
        # location_id -> Set[player_id]
        self.location_players: Dict[int, Set[int]] = {}
        # player_id -> {x, y, location_id, activity}
        self.player_positions: Dict[int, dict] = {}

    async def connect(self, websocket: WebSocket, player_id: int):
        await websocket.accept()
        self.active_connections[player_id] = websocket

    def disconnect(self, player_id: int):
        if player_id in self.active_connections:
            del self.active_connections[player_id]

        # 从所有位置移除
        for location_id in self.location_players:
            self.location_players[location_id].discard(player_id)

    def update_player_location(self, player_id: int, old_location_id: int, new_location_id: int):
        if old_location_id in self.location_players:
            self.location_players[old_location_id].discard(player_id)

        if new_location_id not in self.location_players:
            self.location_players[new_location_id] = set()
        self.location_players[new_location_id].add(player_id)

    async def send_personal_message(self, message: dict, player_id: int):
        if player_id in self.active_connections:
            try:
                await self.active_connections[player_id].send_json(message)
            except:
                self.disconnect(player_id)

    async def broadcast_to_location(self, message: dict, location_id: int, exclude_player_id: int = None):
        if location_id not in self.location_players:
            return

        for player_id in list(self.location_players[location_id]):
            if player_id != exclude_player_id:
                await self.send_personal_message(message, player_id)

    async def broadcast_global(self, message: dict, exclude_player_id: int = None):
        for player_id in list(self.active_connections.keys()):
            if player_id != exclude_player_id:
                await self.send_personal_message(message, player_id)

    def get_online_players_at_location(self, location_id: int) -> list:
        if location_id not in self.location_players:
            return []
        return list(self.location_players[location_id])

    def get_all_online_players(self) -> list:
        return list(self.active_connections.keys())

    def update_player_position(self, player_id: int, x: float, y: float, location_id: int, activity: str = "idle"):
        """更新玩家位置"""
        self.player_positions[player_id] = {
            "player_id": player_id,
            "x": x,
            "y": y,
            "location_id": location_id,
            "activity": activity,
            "timestamp": datetime.now().isoformat()
        }

    def get_player_position(self, player_id: int) -> Optional[dict]:
        """获取玩家位置"""
        return self.player_positions.get(player_id)

    def get_nearby_players(self, location_id: int, exclude_player_id: int = None) -> list:
        """获取同一地点的所有玩家位置"""
        nearby = []
        if location_id in self.location_players:
            for pid in self.location_players[location_id]:
                if pid != exclude_player_id and pid in self.player_positions:
                    nearby.append(self.player_positions[pid])
        return nearby

    async def broadcast_position_update(self, player_id: int, location_id: int):
        """广播玩家位置更新到同一地点的其他玩家"""
        if player_id in self.player_positions:
            position = self.player_positions[player_id]
            message = {
                "type": "player_move",
                "data": position
            }
            await self.broadcast_to_location(message, location_id, exclude_player_id=player_id)

manager = ConnectionManager()
