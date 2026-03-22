"use client";

import { motion } from "framer-motion";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from "recharts";

interface Holding { company: string; weight: number; }
interface FundDetail { name: string; portfolio_weight: number; }
interface Verdict { level: string; color: string; message: string; detail: string; }

interface OverlapChartProps {
  uniqueStocks: number;
  topHoldings: Holding[];
  top3Concentration: number;
  numFunds: number;
  verdict: Verdict;
  fundDetails: FundDetail[];
  overlapScore: number;
}

const COLORS = [
  "#10b981","#3b82f6","#8b5cf6","#f59e0b","#ef4444",
  "#06b6d4","#ec4899","#84cc16","#f97316","#a78bfa",
];

const CustomTooltip = ({ active, payload }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="custom-tooltip">
      <p className="font-semibold text-white">{payload[0].payload.company}</p>
      <p className="text-brand-400">{payload[0].value.toFixed(2)}% of portfolio</p>
    </div>
  );
};

export default function OverlapChart({
  uniqueStocks,
  topHoldings,
  top3Concentration,
  numFunds,
  verdict,
  fundDetails,
  overlapScore,
}: OverlapChartProps) {
  const verdictBg =
    verdict.color === "red" ? "bg-red-500/10 border-red-500/25" :
    verdict.color === "amber" ? "bg-amber-500/10 border-amber-500/25" :
    "bg-brand-500/10 border-brand-500/25";

  const verdictText =
    verdict.color === "red" ? "text-red-300" :
    verdict.color === "amber" ? "text-amber-300" :
    "text-brand-300";

  return (
    <div className="glass-card p-6 animate-slide-up">
      {/* Header */}
      <div className="section-header">
        <div className="section-icon bg-purple-500/15">🎭</div>
        <div>
          <h2 className="text-white font-bold text-lg">Illusion of Diversification</h2>
          <p className="text-gray-400 text-sm">Your actual stock exposure across all funds</p>
        </div>
      </div>

      {/* Verdict banner */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className={`rounded-xl p-4 border mb-6 ${verdictBg}`}
      >
        <p className={`font-semibold ${verdictText}`}>{verdict.message}</p>
        <p className="text-gray-400 text-xs mt-1">{verdict.detail}</p>
      </motion.div>

      {/* 3 stat pills */}
      <div className="grid grid-cols-3 gap-3 mb-6">
        <div className="bg-dark-700 rounded-xl p-4 border border-dark-500 text-center">
          <p className="text-2xl font-black text-white">{numFunds}</p>
          <p className="text-xs text-gray-500 mt-1">Funds Held</p>
        </div>
        <div className="bg-dark-700 rounded-xl p-4 border border-dark-500 text-center">
          <p className="text-2xl font-black text-amber-400">{uniqueStocks}</p>
          <p className="text-xs text-gray-500 mt-1">Unique Stocks</p>
        </div>
        <div className="bg-dark-700 rounded-xl p-4 border border-dark-500 text-center">
          <p className={`text-2xl font-black ${top3Concentration > 20 ? "text-red-400" : "text-brand-400"}`}>
            {top3Concentration.toFixed(0)}%
          </p>
          <p className="text-xs text-gray-500 mt-1">Top 3 Stocks</p>
        </div>
      </div>

      {/* Bar chart */}
      <div className="mb-4">
        <p className="text-sm text-gray-400 mb-3 font-medium">Top 10 Holdings by Combined Weight</p>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart
            data={topHoldings}
            layout="vertical"
            margin={{ top: 0, right: 10, left: 0, bottom: 0 }}
          >
            <XAxis type="number" tick={{ fill: "#6b7280", fontSize: 11 }} tickFormatter={(v) => `${v}%`} />
            <YAxis
              type="category"
              dataKey="company"
              width={120}
              tick={{ fill: "#9ca3af", fontSize: 11 }}
              tickLine={false}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(255,255,255,0.03)" }} />
            <Bar dataKey="weight" radius={[0, 4, 4, 0]}>
              {topHoldings.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} opacity={0.85} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Fund weight breakdown */}
      {fundDetails.length > 0 && (
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wide font-medium mb-2">Fund Distribution</p>
          <div className="space-y-2">
            {fundDetails.map((f, i) => (
              <div key={i} className="flex items-center gap-3">
                <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: COLORS[i % COLORS.length] }} />
                <span className="text-xs text-gray-400 flex-1 truncate">{f.name.split(" - ")[0]}</span>
                <span className="text-xs font-bold text-white">{f.portfolio_weight}%</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
