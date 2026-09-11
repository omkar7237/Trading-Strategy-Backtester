import React from 'react';
import { Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, ComposedChart } from 'recharts';
import type { OHLCVPoint } from '../types';

interface PriceChartProps {
  data: OHLCVPoint[];
  showBuyHold?: boolean;
  buyHoldData?: OHLCVPoint[];
  height?: number;
}

export const PriceChart: React.FC<PriceChartProps> = ({ 
  data, 
  showBuyHold = false, 
  buyHoldData,
  height = 400 
}) => {
  const formatXAxis = (tickItem: string) => {
    const date = new Date(tickItem);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const formatYAxis = (value: number) => {
    if (value >= 1e6) return `$${(value / 1e6).toFixed(1)}M`;
    if (value >= 1e3) return `$${(value / 1e3).toFixed(0)}K`;
    return `$${value.toFixed(2)}`;
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="text-sm font-semibold text-gray-900 mb-2">
            {new Date(label).toLocaleDateString('en-US', { 
              weekday: 'short', 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric' 
            })}
          </p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: ${entry.value.toFixed(2)}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <ResponsiveContainer width="100%" height={height}>
      <ComposedChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis 
          dataKey="date" 
          tickFormatter={formatXAxis}
          angle={-45}
          textAnchor="end"
          interval={Math.floor(data.length / 10)}
          tick={{ fontSize: 12 }}
        />
        <YAxis 
          tickFormatter={formatYAxis}
          tick={{ fontSize: 12 }}
        />
        <Tooltip content={<CustomTooltip />} />
        <Area 
          type="monotone" 
          dataKey="close" 
          stroke="#0ea5e9" 
          fill="#0ea5e9" 
          fillOpacity={0.1}
          name="Price"
          strokeWidth={2}
        />
        {showBuyHold && buyHoldData && (
          <Line 
            type="monotone" 
            dataKey="close" 
            data={buyHoldData}
            stroke="#10b981" 
            strokeWidth={2}
            strokeDasharray="5 5"
            name="Buy & Hold"
            dot={false}
          />
        )}
      </ComposedChart>
    </ResponsiveContainer>
  );
};
