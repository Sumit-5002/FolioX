"use client";

import { motion } from "framer-motion";
import { Target, ArrowRight, TrendingUp } from "lucide-react";

interface RebalancingAction {
  type: string;
  priority: string;
  action: string;
  amount?: number;
}

interface GoalVerdict {
  color: string;
  icon: string;
  status: string;
  headline: string;
  message: string;
}

interface GoalMeterProps {
  goalName: string;
  targetAmount: number;
  yearsToGoal: number;
  totalFutureValue: number;
  totalFutureValueOptimized: number;
  probability: number;
  probabilityOptimized: number;
  gap: number;
  monthlySipNeeded: number;
  sipIncreaseNeeded: number;
  currentEquityPct: number;
  optimalEquityPct: number;
  blendedReturn: number;
  rebalancingActions: RebalancingAction[];
  verdict: GoalVerdict;
}

function formatINR(n: number) {
  if (n >= 10000000) return `₹${(n / 10000000).toFixed(1)}Cr`;
  if (n >= 100000) return `₹${(n / 100000).toFixed(1)}L`;
  if (n >= 1000) return `₹${(n / 1000).toFixed(0)}K`;
  return `₹${n.toFixed(0)}`;
}

function ProbabilityBar({ value, color, label }: { value: number; color: string; label: string }) {
  const clampedValue = Math.min(value, 100);
  return (
    <div className="mb-3">
      <div className="flex justify-between mb-1.5">
        <span className="text-xs text-gray-400">{label}</span>
        <span className={`text-xs font-bold ${
          value >= 100 ? "text-brand-400" : value >= 75 ? "text-amber-400" : "text-red-400"
        }`}>
          {value.toFixed(0)}%{value >= 100 ? " ✅" : ""}
        </span>
      </div>
      <div className="progress-bar">
        <motion.div
          className="progress-fill"
          style={{ background: color }}
          initial={{ width: "0%" }}
          animate={{ width: `${clampedValue}%` }}
          transition={{ duration: 1.2, ease: "easeOut" }}
        />
      </div>
    </div>
  );
}

export default function GoalMeter({
  goalName,
  targetAmount,
  yearsToGoal,
  totalFutureValue,
  totalFutureValueOptimized,
  probability,
  probabilityOptimized,
  gap,
  monthlySipNeeded,
  sipIncreaseNeeded,
  currentEquityPct,
  optimalEquityPct,
  blendedReturn,
  rebalancingActions,
  verdict,
}: GoalMeterProps) {
  const verdictBg =
    verdict.color === "green" ? "bg-brand-500/10 border-brand-500/25" :
    verdict.color === "amber" ? "bg-amber-500/10 border-amber-500/25" :
    "bg-red-500/10 border-red-500/25";
  const verdictText =
    verdict.color === "green" ? "text-brand-300" :
    verdict.color === "amber" ? "text-amber-300" :
    "text-red-300";

  return (
    <div className="glass-card p-6 animate-slide-up">
      {/* Header */}
      <div className="section-header">
        <div className="section-icon bg-brand-500/15">📊</div>
        <div className="flex-1">
          <h2 className="text-white font-bold text-lg">Goal Probability Meter</h2>
          <p className="text-gray-400 text-sm">Will you reach your financial goal?</p>
        </div>
        <div className="text-right">
          <p className="text-lg font-black text-white">{goalName}</p>
          <p className="text-xs text-gray-500">{yearsToGoal} years · {formatINR(targetAmount)}</p>
        </div>
      </div>

      {/* Verdict */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className={`rounded-xl p-4 border mb-5 ${verdictBg}`}
      >
        <p className={`font-semibold ${verdictText}`}>{verdict.icon} {verdict.headline}</p>
        <p className="text-gray-400 text-xs mt-1">{verdict.message}</p>
      </motion.div>

      {/* Progress bars */}
      <div className="mb-5">
        <ProbabilityBar
          value={probability}
          color={probability >= 100 ? "#10b981" : probability >= 75 ? "#f59e0b" : "#ef4444"}
          label="Current trajectory"
        />
        <ProbabilityBar
          value={probabilityOptimized}
          color="#10b981"
          label="After rebalancing"
        />
      </div>

      {/* Future value comparison */}
      <div className="grid grid-cols-2 gap-3 mb-5">
        <div className="bg-dark-700 rounded-xl p-4 border border-dark-500">
          <p className="text-xs text-gray-500 mb-1">Target Corpus</p>
          <p className="text-xl font-black text-white">{formatINR(targetAmount)}</p>
        </div>
        <div className="bg-dark-700 rounded-xl p-4 border border-dark-500">
          <p className="text-xs text-gray-500 mb-1">Projected Value</p>
          <p className={`text-xl font-black ${totalFutureValue >= targetAmount ? "text-brand-400" : "text-amber-400"}`}>
            {formatINR(totalFutureValue)}
          </p>
        </div>
        <div className="bg-dark-700 rounded-xl p-4 border border-dark-500">
          <p className="text-xs text-gray-500 mb-1">After Rebalancing</p>
          <p className="text-xl font-black text-brand-400">{formatINR(totalFutureValueOptimized)}</p>
        </div>
        <div className="bg-dark-700 rounded-xl p-4 border border-dark-500">
          <p className="text-xs text-gray-500 mb-1">Shortfall</p>
          <p className={`text-xl font-black ${gap === 0 ? "text-brand-400" : "text-red-400"}`}>
            {gap === 0 ? "None ✅" : `-${formatINR(gap)}`}
          </p>
        </div>
      </div>

      {/* Allocation info */}
      <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-dark-700 border border-dark-500 mb-5">
        <TrendingUp className="w-4 h-4 text-brand-400 flex-shrink-0" />
        <div className="flex-1 text-xs">
          <span className="text-gray-400">Current equity: </span>
          <span className="text-white font-bold">{currentEquityPct.toFixed(0)}%</span>
          <span className="text-gray-400"> → Suggested: </span>
          <span className="text-brand-400 font-bold">{optimalEquityPct.toFixed(0)}%</span>
          <span className="text-gray-400"> → Expected return: </span>
          <span className="text-white font-bold">{blendedReturn.toFixed(1)}% p.a.</span>
        </div>
      </div>

      {/* Rebalancing actions */}
      <div>
        <p className="text-xs text-gray-500 uppercase tracking-wide font-medium mb-3">Recommended Actions</p>
        <div className="space-y-2">
          {rebalancingActions.map((action, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.1 }}
              className="flex items-start gap-3 px-4 py-3 rounded-xl bg-dark-700 border border-dark-600"
            >
              <span className={`mt-0.5 w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold flex-shrink-0 ${
                action.priority === "HIGH" ? "bg-brand-500/20 text-brand-400" : "bg-dark-500 text-gray-400"
              }`}>
                {i + 1}
              </span>
              <p className="text-xs text-gray-300 leading-relaxed">{action.action}</p>
            </motion.div>
          ))}
        </div>
      </div>

      {/* SIP suggestion */}
      {sipIncreaseNeeded > 0 && (
        <div className="mt-4 flex items-center justify-between px-4 py-3 rounded-xl bg-amber-500/5 border border-amber-500/20">
          <div>
            <p className="text-xs text-amber-300 font-semibold">Increase Monthly SIP</p>
            <p className="text-xs text-gray-500">To close the shortfall faster</p>
          </div>
          <div className="text-right">
            <p className="text-lg font-black text-amber-400">+{formatINR(sipIncreaseNeeded)}</p>
            <p className="text-xs text-gray-500">per month</p>
          </div>
        </div>
      )}
    </div>
  );
}
