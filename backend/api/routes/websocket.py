from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session
from services.websocket_service import manager
from utils.database import get_db
from models import Player, PlayerState
from utils.auth import get_current_user_ws
import json
from datetime import datetime

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    player = None
    try:
        # 验证 token
        player = await get_current_user_ws(token, db)
        if not player:
            await websocket.close(code=1008)
            return

        # 连接
        await manager.connect(websocket, player.id)

        # 更新玩家在线状态
        player_state = db.query(PlayerState).filter(PlayerState.player_id == player.id).first()
        if not player_state:
            player_state = PlayerState(player_id=player.id, location_id=1, is_online=True)
            db.add(player_state)
        else:
            player_state.is_online = True
            player_state.last_seen = datetime.utcnow()
        db.commit()

        # 更新位置映射
        manager.update_player_location(player.id, 0, player_state.location_id)

        # 广播玩家上线
        await manager.broadcast_global({
            "type": "player_online",
            "player_id": player.id,
            "username": player.username,
            "location_id": player_state.location_id,
            "timestamp": datetime.utcnow().isoformat()
        }, exclude_player_id=player.id)

        # 发送当前在线玩家列表
        online_players = []
        for pid in manager.get_all_online_players():
            p = db.query(Player).filter(Player.id == pid).first()
            ps = db.query(PlayerState).filter(PlayerState.player_id == pid).first()
            if p and ps:
                online_players.append({
                    "player_id": p.id,
                    "username": p.username,
                    "location_id": ps.location_id
                })

        await manager.send_personal_message({
            "type": "online_players",
            "players": online_players
        }, player.id)

        # 监听消息
        while True:
            data = await websocket.receive_json()
            await handle_message(data, player, db)

    except WebSocketDisconnect:
        if player:
            handle_disconnect(player.id, db)
    except Exception as e:
        print(f"WebSocket error: {e}")
        if player:
            handle_disconnect(player.id, db)

def handle_disconnect(player_id: int, db: Session):
    manager.disconnect(player_id)

    # 更新离线状态
    player_state = db.query(PlayerState).filter(PlayerState.player_id == player_id).first()
    if player_state:
        player_state.is_online = False
        player_state.last_seen = datetime.utcnow()
        db.commit()

    # 广播玩家离线
    player = db.query(Player).filter(Player.id == player_id).first()
    if player:
        import asyncio
        asyncio.create_task(manager.broadcast_global({
            "type": "player_offline",
            "player_id": player_id,
            "username": player.username,
            "timestamp": datetime.utcnow().isoformat()
        }))

async def handle_message(data: dict, player: Player, db: Session):
    msg_type = data.get("type")

    if msg_type == "chat":
        # 聊天消息
        content = data.get("content", "").strip()
        if not content:
            return

        chat_type = data.get("chat_type", "global")  # global 或 private
        target_player_id = data.get("target_player_id")

        message = {
            "type": "chat",
            "chat_type": chat_type,
            "player_id": player.id,
            "username": player.username,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }

        if chat_type == "private" and target_player_id:
            # 私聊
            message["target_player_id"] = target_player_id
            await manager.send_personal_message(message, target_player_id)
            await manager.send_personal_message(message, player.id)
        else:
            # 公屏
            await manager.broadcast_global(message)

    elif msg_type == "move":
        # 玩家移动
        new_location_id = data.get("location_id")
        if not new_location_id:
            return

        player_state = db.query(PlayerState).filter(PlayerState.player_id == player.id).first()
        if not player_state:
            return

        old_location_id = player_state.location_id
        player_state.location_id = new_location_id
        db.commit()

        # 更新位置映射
        manager.update_player_location(player.id, old_location_id, new_location_id)

        # 广播位置变化
        await manager.broadcast_global({
            "type": "player_move",
            "player_id": player.id,
            "username": player.username,
            "old_location_id": old_location_id,
            "new_location_id": new_location_id,
            "timestamp": datetime.utcnow().isoformat()
        }, exclude_player_id=player.id)
