"use client";

import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, AlertTriangle } from "lucide-react";

interface XirrCardProps {
  xirr: number;
  apparentReturn: number;
  gapRupees: number;
  simpleReturn: number;
  totalInvested: number;
  totalValue: number;
  benchmark?: { cagr: number; index: string };
}

function AnimatedNumber({ value, prefix = "", suffix = "", decimals = 1 }: {
  value: number; prefix?: string; suffix?: string; decimals?: number;
}) {
  return (
    <motion.span
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="number-highlight"
    >
      {prefix}{value.toFixed(decimals)}{suffix}
    </motion.span>
  );
}

export default function XirrCard({
  xirr,
  apparentReturn,
  gapRupees,
  simpleReturn,
  totalInvested,
  totalValue,
  benchmark,
}: XirrCardProps) {
  const gap = apparentReturn - xirr;
  const pnl = totalValue - totalInvested;
  const isPnlPositive = pnl >= 0;

  return (
    <div className="glass-card p-6 animate-slide-up">
      {/* Header */}
      <div className="section-header">
        <div className="section-icon bg-blue-500/15">📊</div>
        <div>
          <h2 className="text-white font-bold text-lg">True XIRR vs What Apps Show</h2>
          <p className="text-gray-400 text-sm">Your real annualised return accounting for every SIP</p>
        </div>
      </div>

      {/* Two big numbers */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        {/* True XIRR */}
        <div className="gradient-border rounded-xl p-5">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs text-gray-400 font-medium uppercase tracking-wide">True XIRR</span>
          </div>
          <div className={`text-4xl font-black ${xirr >= 12 ? "text-brand-400" : xirr >= 8 ? "text-amber-400" : "text-red-400"}`}>
            <AnimatedNumber value={xirr} suffix="%" decimals={1} />
          </div>
          <p className="text-xs text-gray-500 mt-1">Your actual compounded return</p>
        </div>

        {/* What Groww shows */}
        <div className="bg-dark-700 rounded-xl p-5 border border-dark-500">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs text-gray-400 font-medium uppercase tracking-wide">Apps Show</span>
          </div>
          <div className="text-4xl font-black text-gray-300">
            <AnimatedNumber value={apparentReturn} suffix="%" decimals={1} />
          </div>
          <p className="text-xs text-gray-500 mt-1">Groww / Zerodha display</p>
        </div>
      </div>

      {/* Gap banner */}
      {gap > 0.5 && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-red-500/10 border border-red-500/25 rounded-xl p-4 mb-4 flex items-start gap-3"
        >
          <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-red-300 font-semibold text-sm">
              Gap: {gap.toFixed(1)}% = ₹{(gapRupees / 1000).toFixed(0)}K invisible loss over 5 years
            </p>
            <p className="text-red-400/70 text-xs mt-0.5">
              This gap exists due to SIP timing — apps measure from NAV inception, not your actual investment dates.
            </p>
          </div>
        </motion.div>
      )}

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-3">
        <StatBox
          label="Invested"
          value={`₹${formatLakh(totalInvested)}`}
          sub="Total capital deployed"
        />
        <StatBox
          label="Current Value"
          value={`₹${formatLakh(totalValue)}`}
          sub="As of today"
          highlight="brand"
        />
        <StatBox
          label="P&L"
          value={`${isPnlPositive ? "+" : ""}₹${formatLakh(Math.abs(pnl))}`}
          sub={`${simpleReturn.toFixed(1)}% absolute`}
          highlight={isPnlPositive ? "brand" : "red"}
        />
      </div>

      {/* Benchmark comparison */}
      {benchmark && (
        <div className="mt-4 flex items-center justify-between px-4 py-3 rounded-lg bg-dark-700 border border-dark-500">
          <span className="text-xs text-gray-400">vs {benchmark.index} (5Y CAGR)</span>
          <div className="flex items-center gap-2">
            <span className="text-sm font-bold text-amber-400">{benchmark.cagr.toFixed(1)}%</span>
            {xirr > benchmark.cagr ? (
              <span className="badge-green text-[10px]">
                <TrendingUp className="w-3 h-3" /> Beating index
              </span>
            ) : (
              <span className="badge-red text-[10px]">
                <TrendingDown className="w-3 h-3" /> Below index
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function StatBox({ label, value, sub, highlight }: {
  label: string; value: string; sub: string; highlight?: "brand" | "red";
}) {
  const valueColor =
    highlight === "brand" ? "text-brand-400" :
    highlight === "red" ? "text-red-400" :
    "text-white";

  return (
    <div className="bg-dark-700 rounded-xl p-3 border border-dark-500">
      <p className="text-xs text-gray-500 mb-1">{label}</p>
      <p className={`font-bold text-base ${valueColor}`}>{value}</p>
      <p className="text-xs text-gray-600 mt-0.5">{sub}</p>
    </div>
  );
}

function formatLakh(n: number): string {
  if (n >= 10000000) return `${(n / 10000000).toFixed(1)}Cr`;
  if (n >= 100000) return `${(n / 100000).toFixed(1)}L`;
  if (n >= 1000) return `${(n / 1000).toFixed(0)}K`;
  return n.toFixed(0);
}
