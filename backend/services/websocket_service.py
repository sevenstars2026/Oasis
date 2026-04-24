from typing import Dict, Set
from fastapi import WebSocket
import json
from datetime import datetime

class ConnectionManager:
    def __init__(self):
        # player_id -> WebSocket
        self.active_connections: Dict[int, WebSocket] = {}
        # location_id -> Set[player_id]
        self.location_players: Dict[int, Set[int]] = {}

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

manager = ConnectionManager()
