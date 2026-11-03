import React, { useEffect, useRef } from 'react';

const COLORS = {
  'Very Low': '#10b981',
  'Low':      '#3b82f6',
  'Medium':   '#f59e0b',
  'High':     '#f97316',
  'Critical': '#ef4444',
};

/**
 * RiskMeter - Animated SVG arc gauge showing a risk score 0–100.
 *
 * Props:
 *   score     (number) - 0 to 100
 *   riskLevel (string) - "Very Low" | "Low" | "Medium" | "High" | "Critical"
 */
export default function RiskMeter({ score = 0, riskLevel = 'Very Low' }) {
  const color    = COLORS[riskLevel] || '#10b981';
  const radius   = 80;
  const cx = 100, cy = 100;
  const strokeWidth = 14;

  // Arc goes from 210° to 330° (240° sweep) — a bottom-open semicircle
  const startAngle  = 210;  // degrees
  const sweepAngle  = 240;  // total sweep

  const toRad = (deg) => (deg * Math.PI) / 180;

  // Convert polar → Cartesian
  const polarToXY = (angle) => ({
    x: cx + radius * Math.cos(toRad(angle)),
    y: cy + radius * Math.sin(toRad(angle)),
  });

  // Background arc (full 240°)
  const bgStart = polarToXY(startAngle);
  const bgEnd   = polarToXY(startAngle + sweepAngle);
  const bgPath  = `M ${bgStart.x} ${bgStart.y} A ${radius} ${radius} 0 1 1 ${bgEnd.x} ${bgEnd.y}`;

  // Value arc
  const valueAngle = startAngle + (score / 100) * sweepAngle;
  const valEnd     = polarToXY(valueAngle);
  const largeArc   = score / 100 > 0.5 ? 1 : 0;
  const valPath    = score > 0
    ? `M ${bgStart.x} ${bgStart.y} A ${radius} ${radius} 0 ${largeArc} 1 ${valEnd.x} ${valEnd.y}`
    : '';

  return (
    <div style={{ textAlign: 'center' }}>
      <svg width="200" height="160" viewBox="0 0 200 160" style={{ overflow: 'visible' }}>
        {/* Background arc */}
        <path
          d={bgPath}
          fill="none"
          stroke="rgba(255,255,255,0.07)"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />

        {/* Value arc */}
        {score > 0 && (
          <path
            d={valPath}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            style={{
              filter: `drop-shadow(0 0 8px ${color}80)`,
              transition: 'all 0.8s ease',
            }}
          />
        )}

        {/* Score text */}
        <text x={cx} y={cy + 8} textAnchor="middle" fill="white"
          fontSize="28" fontWeight="800" fontFamily="Inter, sans-serif">
          {Math.round(score)}
        </text>
        <text x={cx} y={cy + 24} textAnchor="middle" fill="rgba(255,255,255,0.4)"
          fontSize="11" fontFamily="Inter, sans-serif">
          / 100
        </text>
      </svg>

      {/* Risk Level Badge */}
      <div style={{
        display: 'inline-block',
        background: `${color}20`,
        border: `1px solid ${color}50`,
        borderRadius: '999px',
        padding: '0.3rem 1rem',
        color: color,
        fontWeight: 700,
        fontSize: '0.9375rem',
        letterSpacing: '0.05em',
        marginTop: '-0.5rem',
      }}>
        {riskLevel}
      </div>
    </div>
  );
}
