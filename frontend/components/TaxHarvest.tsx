"use client";

import { motion } from "framer-motion";
import { AlertTriangle, TrendingDown, Calendar } from "lucide-react";

interface TaxOpportunity {
  fund: string;
  purchase_date: string;
  days_held: number;
  loss_type: string;
  unrealized_loss: number;
  tax_saving: number;
  action: string;
}

interface TaxVerdict {
  level: string;
  color: string;
  headline: string;
  message: string;
}

interface TaxHarvestProps {
  opportunities: TaxOpportunity[];
  totalHarvestableLoss: number;
  totalTaxSaving: number;
  daysToFyEnd: number;
  isUrgent: boolean;
  hasOpportunities: boolean;
  verdict: TaxVerdict;
}

function formatINR(n: number) {
  if (n >= 100000) return `₹${(n / 100000).toFixed(1)}L`;
  if (n >= 1000) return `₹${(n / 1000).toFixed(1)}K`;
  return `₹${n.toFixed(0)}`;
}

export default function TaxHarvest({
  opportunities,
  totalHarvestableLoss,
  totalTaxSaving,
  daysToFyEnd,
  isUrgent,
  hasOpportunities,
  verdict,
}: TaxHarvestProps) {
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
        <div className="section-icon bg-red-500/15">🎯</div>
        <div className="flex-1">
          <h2 className="text-white font-bold text-lg">Tax Harvesting Scanner</h2>
          <p className="text-gray-400 text-sm">Unrealized losses you can book to save tax</p>
        </div>
        {/* FY countdown */}
        <div className={`flex items-center gap-2 px-3 py-2 rounded-xl border text-xs font-semibold ${
          isUrgent ? "bg-red-500/10 border-red-500/30 text-red-300" : "bg-dark-600 border-dark-400 text-gray-400"
        }`}>
          <Calendar className="w-3.5 h-3.5" />
          {daysToFyEnd}d to FY end
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

      {hasOpportunities ? (
        <>
          {/* Summary stats */}
          <div className="grid grid-cols-2 gap-3 mb-5">
            <div className="bg-dark-700 rounded-xl p-4 border border-dark-500 text-center">
              <p className="text-2xl font-black text-red-400">{formatINR(totalHarvestableLoss)}</p>
              <p className="text-xs text-gray-500 mt-1">Harvestable Losses</p>
            </div>
            <div className="bg-dark-700 rounded-xl p-4 border border-dark-500 text-center">
              <p className="text-2xl font-black text-brand-400">{formatINR(totalTaxSaving)}</p>
              <p className="text-xs text-gray-500 mt-1">Tax You Can Save</p>
            </div>
          </div>

          {/* Opportunities table */}
          <div className="rounded-xl border border-dark-500 overflow-hidden">
            <div className="grid grid-cols-5 gap-2 px-4 py-2 bg-dark-700 text-xs text-gray-500 font-medium">
              <span className="col-span-2">Fund</span>
              <span className="text-center">Type</span>
              <span className="text-right">Loss</span>
              <span className="text-right">Tax Saved</span>
            </div>

            {opportunities.map((opp, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.06 }}
                className="grid grid-cols-5 gap-2 px-4 py-3 border-t border-dark-600 hover:bg-dark-700/40 transition-colors"
              >
                <div className="col-span-2">
                  <p className="text-xs text-white truncate max-w-[130px]">{opp.fund}</p>
                  <p className="text-[10px] text-gray-600">{opp.purchase_date} · {opp.days_held}d</p>
                </div>
                <div className="flex items-center justify-center">
                  <span className={`stat-pill text-[10px] font-bold ${
                    opp.loss_type === "LTCL" ? "badge-amber" : "badge-red"
                  }`}>
                    {opp.loss_type}
                  </span>
                </div>
                <p className="text-xs font-bold text-right text-red-400 self-center">
                  -{formatINR(opp.unrealized_loss)}
                </p>
                <p className="text-xs font-bold text-right text-brand-400 self-center">
                  +{formatINR(opp.tax_saving)}
                </p>
              </motion.div>
            ))}

            {/* Total */}
            <div className="grid grid-cols-5 gap-2 px-4 py-3 bg-brand-500/5 border-t border-brand-500/20">
              <span className="col-span-3 text-xs font-bold text-brand-300">TOTAL SAVINGS</span>
              <span className="text-xs font-black text-right text-red-400">{formatINR(totalHarvestableLoss)}</span>
              <span className="text-xs font-black text-right text-brand-400">+{formatINR(totalTaxSaving)}</span>
            </div>
          </div>

          {/* Action note */}
          <p className="mt-3 text-xs text-gray-500 flex items-start gap-2">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400 flex-shrink-0 mt-0.5" />
            Redeem these units now, reinvest after 30 days to maintain your allocation. Losses offset capital gains from other investments.
          </p>
        </>
      ) : (
        <div className="text-center py-8">
          <div className="w-12 h-12 rounded-2xl bg-brand-500/10 flex items-center justify-center mx-auto mb-3">
            <TrendingDown className="w-6 h-6 text-brand-400" />
          </div>
          <p className="text-white font-semibold">No loss harvesting available</p>
          <p className="text-gray-500 text-sm mt-1">Your portfolio is all in profit — great position!</p>
          <p className="text-brand-400 text-xs mt-2">Consider booking gains within ₹1.25L LTCG exemption limit.</p>
        </div>
      )}
    </div>
  );
}
