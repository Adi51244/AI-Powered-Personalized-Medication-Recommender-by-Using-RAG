/**
 * SHAP feature importance visualization with Recharts
 */

'use client';

import { ShapValue } from '@/lib/types';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface ShapChartProps {
  shapValues: ShapValue[];
  topK?: number;
}

export default function ShapChart({ shapValues, topK = 10 }: ShapChartProps) {
  // Sort by absolute contribution and take top K
  const sortedValues = [...shapValues]
    .sort((a, b) => Math.abs(b.contribution) - Math.abs(a.contribution))
    .slice(0, topK);

  // Transform data for Recharts
  const chartData = sortedValues.map(sv => ({
    feature: sv.feature,
    contribution: sv.contribution,
    absContribution: Math.abs(sv.contribution)
  }));

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white border border-gray-200 shadow-lg rounded-lg p-3">
          <p className="font-medium text-gray-900 mb-1">{data.feature}</p>
          <p className={`text-sm ${data.contribution > 0 ? 'text-green-600' : 'text-red-600'}`}>
            Contribution: {data.contribution > 0 ? '+' : ''}{data.contribution.toFixed(4)}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={Math.max(300, topK * 40)}>
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 5, right: 30, left: 120, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} />
          <XAxis type="number" />
          <YAxis type="category" dataKey="feature" width={110} tick={{ fontSize: 12 }} />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="contribution" radius={[0, 4, 4, 0]}>
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={entry.contribution > 0 ? '#10B981' : '#EF4444'}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Legend */}
      <div className="flex items-center justify-center gap-6 mt-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-green-500 rounded" />
          <span className="text-gray-600">Positive contribution (increases risk)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-red-500 rounded" />
          <span className="text-gray-600">Negative contribution (decreases risk)</span>
        </div>
      </div>
    </div>
  );
}
