import React from 'react';

interface SparklineProps {
  data: number[];
  width?: number;
  height?: number;
  stroke?: string;
  strokeWidth?: number;
  fill?: string;
}

const Sparkline: React.FC<SparklineProps> = ({ data, width = 120, height = 32, stroke = '#2563eb', strokeWidth = 2, fill = 'none' }) => {
  if (!data || data.length === 0) return <svg width={width} height={height}></svg>;

  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const step = width / (data.length - 1 || 1);

  const points = data.map((v, i) => {
    const x = i * step;
    const y = height - ((v - min) / range) * height;
    return `${x},${y}`;
  }).join(' ');

  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none">
      <polyline fill={fill} stroke={stroke} strokeWidth={strokeWidth} points={points} strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
};

export default Sparkline;
