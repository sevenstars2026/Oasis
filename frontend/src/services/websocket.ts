type MessageHandler = (data: any) => void;

class WebSocketService {
  private ws: WebSocket | null = null;
  private handlers: Map<string, MessageHandler[]> = new Map();
  private reconnectTimer: number | null = null;
  private token: string = '';

  connect(token: string) {
    this.token = token;
    const wsUrl = `ws://localhost:8000/ws?token=${token}`;

    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      if (this.reconnectTimer) {
        clearTimeout(this.reconnectTimer);
        this.reconnectTimer = null;
      }
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const handlers = this.handlers.get(data.type) || [];
        handlers.forEach(handler => handler(data));
      } catch (error) {
        console.error('WebSocket message error:', error);
      }
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      this.reconnect();
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  private reconnect() {
    if (this.reconnectTimer) return;

    this.reconnectTimer = window.setTimeout(() => {
      console.log('Reconnecting...');
      this.connect(this.token);
    }, 3000);
  }

  disconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  on(type: string, handler: MessageHandler) {
    if (!this.handlers.has(type)) {
      this.handlers.set(type, []);
    }
    this.handlers.get(type)!.push(handler);
  }

  off(type: string, handler: MessageHandler) {
    const handlers = this.handlers.get(type);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  send(data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  sendChat(content: string, chatType: 'global' | 'private' = 'global', targetPlayerId?: number) {
    this.send({
      type: 'chat',
      content,
      chat_type: chatType,
      target_player_id: targetPlayerId,
    });
  }

  sendMove(locationId: number) {
    this.send({
      type: 'move',
      location_id: locationId,
    });
  }
}

export const wsService = new WebSocketService();
