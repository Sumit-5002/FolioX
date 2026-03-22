"use client";

import { motion } from "framer-motion";
import { ArrowRight, CheckCircle } from "lucide-react";

interface FundExpense {
  fund: string;
  is_direct: boolean;
  expense_ratio: number;
  annual_drain?: number;
  drain_over_horizon?: number;
  current_value: number;
  category: string;
}

interface ExpenseVerdict {
  status: string;
  color: string;
  headline: string;
  message: string;
}

interface ExpenseDrainProps {
  fundBreakdown: FundExpense[];
  totalAnnualDrain: number;
  totalDrainOverHorizon: number;
  horizonYears: number;
  numRegularPlans: number;
  numDirectPlans: number;
  verdict: ExpenseVerdict;
}

function formatINR(n: number) {
  if (n >= 10000000) return `₹${(n / 10000000).toFixed(1)}Cr`;
  if (n >= 100000) return `₹${(n / 100000).toFixed(1)}L`;
  if (n >= 1000) return `₹${(n / 1000).toFixed(0)}K`;
  return `₹${n.toFixed(0)}`;
}

export default function ExpenseDrain({
  fundBreakdown,
  totalAnnualDrain,
  totalDrainOverHorizon,
  horizonYears,
  numRegularPlans,
  verdict,
}: ExpenseDrainProps) {
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
        <div className="section-icon bg-amber-500/15">💸</div>
        <div>
          <h2 className="text-white font-bold text-lg">Expense Ratio Drain</h2>
          <p className="text-gray-400 text-sm">How much you're losing to Regular Plan commissions</p>
        </div>
      </div>

      {/* Verdict */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className={`rounded-xl p-4 border mb-5 ${verdictBg}`}
      >
        <p className={`font-semibold ${verdictText}`}>{verdict.headline}</p>
        <p className="text-gray-400 text-xs mt-1">{verdict.message}</p>
      </motion.div>

      {/* 3 big stats */}
      <div className="grid grid-cols-3 gap-3 mb-5">
        <div className="bg-dark-700 rounded-xl p-4 border border-dark-500 text-center">
          <p className="text-2xl font-black text-red-400">{numRegularPlans}</p>
          <p className="text-xs text-gray-500 mt-1">Regular Plans</p>
        </div>
        <div className="bg-dark-700 rounded-xl p-4 border border-dark-500 text-center">
          <p className="text-2xl font-black text-red-400">{formatINR(totalAnnualDrain)}</p>
          <p className="text-xs text-gray-500 mt-1">Annual Fee Leak</p>
        </div>
        <div className="bg-dark-700 rounded-xl p-4 border border-dark-500 text-center">
          <p className="text-2xl font-black text-red-400">{formatINR(totalDrainOverHorizon)}</p>
          <p className="text-xs text-gray-500 mt-1">{horizonYears}Y Total Drain</p>
        </div>
      </div>

      {/* Fund table */}
      <div className="mb-4">
        <p className="text-xs text-gray-500 uppercase tracking-wide font-medium mb-3">Fund-by-Fund Breakdown</p>
        <div className="space-y-0 rounded-xl border border-dark-500 overflow-hidden">
          {/* Header */}
          <div className="grid grid-cols-4 gap-2 px-4 py-2 bg-dark-700 text-xs text-gray-500 font-medium">
            <span className="col-span-2">Fund</span>
            <span className="text-right">Annual Loss</span>
            <span className="text-right">{horizonYears}Y Loss</span>
          </div>

          {fundBreakdown.map((f, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05 }}
              className="grid grid-cols-4 gap-2 px-4 py-3 border-t border-dark-600 hover:bg-dark-700/50 transition-colors"
            >
              <div className="col-span-2 flex items-center gap-2">
                {f.is_direct ? (
                  <CheckCircle className="w-3.5 h-3.5 text-brand-400 flex-shrink-0" />
                ) : (
                  <span className="w-3.5 h-3.5 rounded-full bg-red-500/30 border border-red-500/50 flex-shrink-0" />
                )}
                <div>
                  <p className="text-xs text-white truncate max-w-[140px]">{f.fund}</p>
                  <p className="text-[10px] text-gray-600">{f.expense_ratio}% ER · {f.category}</p>
                </div>
              </div>
              <p className={`text-xs font-bold text-right self-center ${f.is_direct ? "text-brand-400" : "text-red-400"}`}>
                {f.is_direct ? "Direct ✓" : `-${formatINR(f.annual_drain ?? 0)}`}
              </p>
              <p className={`text-xs font-bold text-right self-center ${f.is_direct ? "text-gray-500" : "text-red-400"}`}>
                {f.is_direct ? "—" : `-${formatINR(f.drain_over_horizon ?? 0)}`}
              </p>
            </motion.div>
          ))}

          {/* Total row */}
          <div className="grid grid-cols-4 gap-2 px-4 py-3 bg-red-500/5 border-t border-red-500/20">
            <span className="col-span-2 text-xs font-bold text-red-300">TOTAL DRAIN</span>
            <span className="text-xs font-black text-right text-red-400">{formatINR(totalAnnualDrain)}/yr</span>
            <span className="text-xs font-black text-right text-red-400">{formatINR(totalDrainOverHorizon)}</span>
          </div>
        </div>
      </div>

      {/* CTA */}
      {numRegularPlans > 0 && (
        <div className="flex items-center gap-2 text-xs text-brand-400 font-medium hover:text-brand-300 transition-colors cursor-pointer group">
          <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
          Switch to Direct via MF Central, Kuvera, or Zerodha Coin — saves {formatINR(totalDrainOverHorizon)} over {horizonYears} years
        </div>
      )}
    </div>
  );
}
