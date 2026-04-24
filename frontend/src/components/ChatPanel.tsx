import { useState, useEffect, useRef } from 'react';
import { wsService } from '../services/websocket';
import './ChatPanel.css';

interface ChatMessage {
  id: number;
  player_name: string;
  content: string;
  timestamp: string;
  chat_type: 'global' | 'private';
}

export default function ChatPanel() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleChat = (data: any) => {
      if (data.type === 'chat') {
        setMessages(prev => [...prev, data]);
      }
    };

    wsService.on('chat', handleChat);

    return () => {
      wsService.off('chat', handleChat);
    };
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
    if (input.trim()) {
      wsService.sendChat(input.trim());
      setInput('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-panel">
      <div className="chat-header">全球聊天</div>

      <div className="chat-messages">
        {messages.map((msg, index) => (
          <div key={index} className="chat-message">
            <span className="chat-player">{msg.player_name}:</span>
            <span className="chat-content">{msg.content}</span>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-container">
        <input
          type="text"
          className="chat-input"
          placeholder="输入消息..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
        />
        <button className="chat-send-btn" onClick={handleSend}>
          发送
        </button>
      </div>
    </div>
  );
}
