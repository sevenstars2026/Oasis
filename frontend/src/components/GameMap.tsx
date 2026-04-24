import { useEffect, useRef } from 'react';
import { useGameStore } from '../store/gameStore';
import './GameMap.css';

interface Location {
  id: number;
  name: string;
  display_name: string;
  x: number;
  y: number;
  zone_type: string;
  current_players: number;
}

export const GameMap = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { locations, currentLocation } = useGameStore();

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || locations.length === 0) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // 清空画布
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 设置坐标系（中心为原点）
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const scale = 1.5;

    // 绘制网格
    ctx.strokeStyle = '#f0f0f0';
    ctx.lineWidth = 1;
    for (let i = -300; i <= 300; i += 50) {
      ctx.beginPath();
      ctx.moveTo(0, centerY + i * scale);
      ctx.lineTo(canvas.width, centerY + i * scale);
      ctx.stroke();

      ctx.beginPath();
      ctx.moveTo(centerX + i * scale, 0);
      ctx.lineTo(centerX + i * scale, canvas.height);
      ctx.stroke();
    }

    // 绘制位置点
    locations.forEach((loc: Location) => {
      const x = centerX + loc.x * scale;
      const y = centerY - loc.y * scale; // Y轴反转

      // 根据区域类型选择颜色
      const colors: Record<string, string> = {
        commercial: '#4CAF50',
        residential: '#2196F3',
        industrial: '#FF9800',
        wilderness: '#8BC34A',
      };
      const color = colors[loc.zone_type] || '#9E9E9E';

      // 绘制位置圆圈
      ctx.beginPath();
      ctx.arc(x, y, 20, 0, Math.PI * 2);
      ctx.fillStyle = loc.id === currentLocation?.id ? color : `${color}88`;
      ctx.fill();
      ctx.strokeStyle = loc.id === currentLocation?.id ? '#333' : color;
      ctx.lineWidth = loc.id === currentLocation?.id ? 3 : 2;
      ctx.stroke();

      // 绘制位置名称
      ctx.fillStyle = '#333';
      ctx.font = 'bold 14px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(loc.display_name, x, y - 30);

      // 绘制玩家数量
      if (loc.current_players > 0) {
        ctx.fillStyle = '#666';
        ctx.font = '12px sans-serif';
        ctx.fillText(`👥 ${loc.current_players}`, x, y + 40);
      }
    });

    // 绘制当前位置标记
    if (currentLocation) {
      const x = centerX + currentLocation.x * scale;
      const y = centerY - currentLocation.y * scale;

      ctx.beginPath();
      ctx.arc(x, y, 30, 0, Math.PI * 2);
      ctx.strokeStyle = '#FF5722';
      ctx.lineWidth = 3;
      ctx.setLineDash([5, 5]);
      ctx.stroke();
      ctx.setLineDash([]);
    }
  }, [locations, currentLocation]);

  return (
    <div className="game-map">
      <canvas
        ref={canvasRef}
        width={800}
        height={600}
        className="map-canvas"
      />
    </div>
  );
};
