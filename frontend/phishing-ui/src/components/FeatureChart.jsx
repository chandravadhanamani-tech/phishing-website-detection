import React from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, Cell, ReferenceLine,
} from 'recharts';

/**
 * FeatureChart - Horizontal bar chart showing SHAP or importance values.
 *
 * Props:
 *   features: Array of { feature_name, shap_value, direction }
 *             shap_value > 0 → phishing (red bar)
 *             shap_value < 0 → legitimate (green bar)
 *             OR all positive values for global importance (all cyan)
 */
export default function FeatureChart({ features = [] }) {
  if (!features || features.length === 0) return null;

  // Detect if this is SHAP (mixed +/-) or importance (all positive)
  const hasNegative = features.some(f => f.shap_value < 0);

  const data = features
    .slice(0, 12)
    .map(f => ({
      name:      f.feature_name.replace(/_/g, ' '),
      value:     parseFloat(f.shap_value?.toFixed(4)),
      direction: f.direction || (f.shap_value >= 0 ? 'phishing' : 'legitimate'),
    }))
    .sort((a, b) => Math.abs(b.value) - Math.abs(a.value));

  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload?.[0]) return null;
    const { name, value, direction } = payload[0].payload;
    return (
      <div style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-default)',
        borderRadius: 8,
        padding: '0.625rem 0.875rem',
        fontSize: '0.8125rem',
      }}>
        <div style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.25rem' }}>{name}</div>
        <div style={{ color: direction === 'phishing' ? '#f87171' : '#34d399' }}>
          {hasNegative ? 'SHAP: ' : 'Importance: '}{value >= 0 ? '+' : ''}{value}
        </div>
        <div style={{ color: 'var(--text-muted)', marginTop: '0.2rem' }}>
          → {direction === 'phishing' ? 'Phishing signal' : 'Legitimate signal'}
        </div>
      </div>
    );
  };

  return (
    <ResponsiveContainer width="100%" height={Math.max(200, data.length * 32 + 40)}>
      <BarChart
        data={data}
        layout="vertical"
        margin={{ top: 5, right: 30, left: 120, bottom: 5 }}
      >
        <XAxis
          type="number"
          tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
          tickLine={false}
          axisLine={{ stroke: 'rgba(255,255,255,0.06)' }}
        />
        <YAxis
          type="category"
          dataKey="name"
          width={115}
          tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
          tickLine={false}
          axisLine={false}
        />
        <Tooltip content={<CustomTooltip />} />
        {hasNegative && (
          <ReferenceLine x={0} stroke="rgba(255,255,255,0.15)" />
        )}
        <Bar dataKey="value" radius={[0, 4, 4, 0]} maxBarSize={18}>
          {data.map((entry, i) => (
            <Cell
              key={i}
              fill={
                !hasNegative ? '#00d4ff' :
                entry.value >= 0 ? '#ef4444' : '#10b981'
              }
              fillOpacity={0.85}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
