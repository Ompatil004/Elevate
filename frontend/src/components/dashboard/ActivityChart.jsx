/**
 * BUG-F2/F8: ActivityChart.jsx
 *
 * Extracted from Dashboard.jsx (was at line 1361-1485).
 * A memoized SVG line/area chart with hover tooltips for tracking
 * daily/weekly fitness metrics (workout, water, sleep, meal, calories).
 *
 * Props
 * -----
 * data       : number[]   — data points to plot
 * mode       : 'all' | 'water' | 'sleep' | 'meal' | 'workout'
 * period     : 'week' | 'month'
 * xLabels    : string[]   — optional custom x-axis labels (default: Mon-Sun)
 */

import React, { useState } from 'react';

const isSamePrimitiveArray = (a, b) => {
  if (a === b) return true;
  if (!Array.isArray(a) || !Array.isArray(b)) return false;
  if (a.length !== b.length) return false;
  for (let i = 0; i < a.length; i++) {
    if (a[i] !== b[i]) return false;
  }
  return true;
};

const ActivityChart = React.memo(({ data, mode, period, xLabels: propXLabels }) => {
  const [hoveredPoint, setHoveredPoint] = useState(null);
  if (!data || data.length === 0) return null;

  const xLabels = propXLabels || (period === 'week' ? ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] : ['W1', 'W2', 'W3', 'W4']);

  const width = 1000;
  const height = 300;
  const padding = { top: 10, right: 30, bottom: 40, left: 60 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  let yMax = Math.max(...data) * 1.2;
  let yMin = 0;
  let unit = '';
  const steps = 4;

  const modeConfig = {
    all:     { unit: '%',    yMax: 100,  color1: '#6366f1', color2: '#a855f7', gradId: 'allGrad' },
    water:   { unit: ' L',   yMax: 4,    color1: '#38bdf8', color2: '#0ea5e9', gradId: 'waterGrad' },
    sleep:   { unit: ' h',   yMax: 12,   color1: '#a78bfa', color2: '#8b5cf6', gradId: 'sleepGrad' },
    meal:    { unit: '',     yMax: 3000, color1: '#f472b6', color2: '#ec4899', gradId: 'mealGrad' },
    workout: { unit: ' min', yMax: 120,  color1: '#34d399', color2: '#10b981', gradId: 'workoutGrad' },
  };
  const cfg = modeConfig[mode] || modeConfig.workout;
  unit = cfg.unit;
  yMax = Math.max(cfg.yMax, Math.max(...data) * 1.2);

  const yRange = Math.max(yMax - yMin, 1);
  const stepX = chartWidth / Math.max(data.length - 1, 1);

  const getPoint = (i) => {
    const x = padding.left + i * stepX;
    const y = padding.top + chartHeight - (((data[i] - yMin) / yRange) * chartHeight);
    return [x, y];
  };

  const [startX, startY] = getPoint(0);
  let d = `M ${startX} ${startY}`;

  for (let i = 0; i < data.length - 1; i++) {
    const [x0, y0] = getPoint(Math.max(i - 1, 0));
    const [x1, y1] = getPoint(i);
    const [x2, y2] = getPoint(i + 1);
    const [x3, y3] = getPoint(Math.min(i + 2, data.length - 1));

    const cp1x = x1 + (x2 - x0) / 6;
    const cp1y = y1 + (y2 - y0) / 6;
    const cp2x = x2 - (x3 - x1) / 6;
    const cp2y = y2 - (y3 - y1) / 6;
    d += ` C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${x2} ${y2}`;
  }

  const areaPath = `${d} L ${padding.left + chartWidth} ${padding.top + chartHeight} L ${padding.left} ${padding.top + chartHeight} Z`;

  const yLabels = [];
  for (let i = 0; i <= steps; i++) {
    const val = yMin + (yRange / steps) * i;
    const labelVal = (mode === 'water' || mode === 'sleep') ? val.toFixed(1) : Math.round(val);
    yLabels.push({ y: padding.top + chartHeight - (i * (chartHeight / steps)), val: labelVal });
  }

  return (
    <div style={{ flex: 1, position: 'relative', width: '100%', cursor: 'crosshair', overflow: 'hidden' }}>
      <svg key={`${mode}-${data.length}`} viewBox={`0 0 ${width} ${height}`} style={{ width: '100%', height: '100%', overflow: 'visible', animation: 'fadeIn 0.6s ease' }}>
        <defs>
          <linearGradient id={cfg.gradId} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={cfg.color1} stopOpacity="0.5" />
            <stop offset="100%" stopColor={cfg.color1} stopOpacity="0" />
          </linearGradient>
        </defs>

        {yLabels.map((label, i) => (
          <g key={i}>
            <line x1={padding.left} y1={label.y} x2={width - padding.right} y2={label.y} stroke="rgba(255,255,255,0.05)" strokeWidth="1" />
            <text x={padding.left - 15} y={label.y + 4} textAnchor="end" fill="#a1a1aa" fontSize="12" fontFamily="'Inter', sans-serif" fontWeight="500">{label.val}{unit}</text>
          </g>
        ))}

        {xLabels.map((day, i) => {
          const xPos = padding.left + i * stepX;
          return (<text key={i} x={xPos} y={height - 10} textAnchor="middle" fill="#a1a1aa" fontSize="12" fontFamily="'Inter', sans-serif" fontWeight="500">{day}</text>);
        })}

        <path d={areaPath} fill={`url(#${cfg.gradId})`} />
        <path d={d} fill="none" stroke={cfg.color2} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />

        {data.map((val, i) => {
          const [cx, cy] = getPoint(i);
          return (
            <g key={i} onMouseEnter={() => setHoveredPoint(i)} onMouseLeave={() => setHoveredPoint(null)}>
              <rect x={cx - stepX / 2} y={padding.top} width={stepX} height={chartHeight} fill="transparent" />
              <circle cx={cx} cy={cy} r={hoveredPoint === i ? 6 : 0} fill="#09090b" stroke={cfg.color1} strokeWidth="2"
                style={{ transition: 'all 0.15s ease-out', filter: `drop-shadow(0 0 6px ${cfg.color1})` }} />
            </g>
          );
        })}
      </svg>

      <div style={{ position: 'absolute', left: 0, top: 0, width: '100%', height: '100%', pointerEvents: 'none', opacity: hoveredPoint !== null ? 1 : 0, transition: 'opacity 0.2s ease' }}>
        {hoveredPoint !== null && (() => {
          const [cx, cy] = getPoint(hoveredPoint);
          const val = (mode === 'water' || mode === 'sleep') ? data[hoveredPoint].toFixed(1) : Math.round(data[hoveredPoint]);
          const dayLabel = xLabels[hoveredPoint] || '';
          return (
            <div style={{ position: 'absolute', left: `${(cx / width) * 100}%`, top: `${(cy / height) * 100}%`, transform: 'translate(-50%, -130%)', transition: 'left 0.1s linear, top 0.1s linear', background: 'rgba(24, 24, 27, 0.95)', border: `1px solid ${cfg.color1}40`, borderRadius: '8px', padding: '8px 16px', boxShadow: `0 4px 20px rgba(0,0,0,0.5)`, textAlign: 'center', minWidth: '70px', backdropFilter: 'blur(8px)' }}>
              <div style={{ fontSize: '10px', color: '#a1a1aa', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '2px' }}>{dayLabel}</div>
              <div style={{ fontSize: '16px', fontWeight: '700', color: '#fff', fontFamily: 'sans-serif' }}>
                {val}<span style={{ fontSize: '12px', color: cfg.color1, marginLeft: '2px' }}>{unit}</span>
              </div>
              <div style={{ position: 'absolute', bottom: '-5px', left: '50%', transform: 'translateX(-50%) rotate(45deg)', width: '10px', height: '10px', background: 'rgba(24,24,27,0.95)', borderRight: `1px solid ${cfg.color1}40`, borderBottom: `1px solid ${cfg.color1}40` }} />
            </div>
          );
        })()}
      </div>
    </div>
  );
}, (prevProps, nextProps) => {
  return (
    isSamePrimitiveArray(prevProps.data, nextProps.data) &&
    prevProps.mode === nextProps.mode &&
    prevProps.period === nextProps.period &&
    isSamePrimitiveArray(prevProps.xLabels, nextProps.xLabels)
  );
});

ActivityChart.displayName = 'ActivityChart';

export default ActivityChart;
