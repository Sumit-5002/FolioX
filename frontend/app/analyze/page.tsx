"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Search, ArrowLeft } from "lucide-react";
import XirrCard from "@/components/XirrCard";
import OverlapChart from "@/components/OverlapChart";
import ExpenseDrain from "@/components/ExpenseDrain";
import TaxHarvest from "@/components/TaxHarvest";
import GoalMeter from "@/components/GoalMeter";
import AIInsights from "@/components/AIInsights";
import ChatBot from "@/components/ChatBot";

interface AnalysisResult {
  investor: { name?: string; email?: string };
  total_value: number;
  total_invested: number;
  num_funds: number;
  funds: any[];
  xirr: number;
  simple_return: number;
  apparent_return: number;
  xirr_gap_rupees: number;
  overlap: any;
  expense: any;
  tax: any;
  goal: any;
  benchmark: any;
  insights: any;
  session_id?: string;
  is_demo?: boolean;
}

function LoadingSkeleton() {
  return (
    <div className="space-y-4">
      {[...Array(5)].map((_, i) => (
        <div key={i} className="glass-card p-6">
          <div className="shimmer h-6 w-48 rounded-lg mb-4" />
          <div className="shimmer h-24 rounded-lg" />
        </div>
      ))}
    </div>
  );
}

function formatINR(n: number) {
  if (n >= 10000000) return `₹${(n / 10000000).toFixed(1)}Cr`;
  if (n >= 100000) return `₹${(n / 100000).toFixed(1)}L`;
  if (n >= 1000) return `₹${(n / 1000).toFixed(0)}K`;
  return `₹${n.toFixed(0)}`;
}

export default function AnalyzePage() {
  const router = useRouter();
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    const raw = sessionStorage.getItem("mf_xray_result");
    if (!raw) {
      router.push("/");
      return;
    }
    try {
      const parsed = JSON.parse(raw);
      setResult(parsed);
      setIsLoaded(true);
    } catch {
      router.push("/");
    }
  }, [router]);

  if (!isLoaded || !result) {
    return (
      <main className="min-h-screen bg-dark-900 p-6">
        <div className="max-w-4xl mx-auto">
          <LoadingSkeleton />
        </div>
      </main>
    );
  }

  const { investor, total_value, total_invested, num_funds, xirr, apparent_return,
    xirr_gap_rupees, simple_return, overlap, expense, tax, goal, benchmark, insights,
    session_id, is_demo } = result;

  return (
    <main className="min-h-screen bg-dark-900 pb-24">
      {/* ── Top bar ── */}
      <div className="sticky top-0 z-40 bg-dark-900/90 backdrop-blur-md border-b border-dark-600">
        <div className="max-w-5xl mx-auto px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => router.push("/")}
              className="p-2 rounded-lg hover:bg-dark-700 text-gray-400 hover:text-white transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
            </button>
            <div className="flex items-center gap-2">
              <Search className="w-4 h-4 text-brand-400" />
              <span className="font-black text-white text-base">Portfolio X-Ray</span>
            </div>
            {is_demo && <span className="badge-amber text-[10px]">DEMO</span>}
          </div>

          <div className="flex items-center gap-2">
            <div className="hidden sm:flex items-center gap-4 mr-4">
              <div className="text-right">
                <p className="text-xs text-gray-500">Portfolio Value</p>
                <p className="text-sm font-bold text-white">{formatINR(total_value)}</p>
              </div>
              <div className="text-right">
                <p className="text-xs text-gray-500">True XIRR</p>
                <p className={`text-sm font-bold ${xirr >= 12 ? "text-brand-400" : xirr >= 8 ? "text-amber-400" : "text-red-400"}`}>
                  {xirr.toFixed(1)}%
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ── Investor header ── */}
      <div className="max-w-5xl mx-auto px-6 pt-8 pb-4">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between"
        >
          <div>
            <h1 className="text-2xl font-black text-white">
              {investor?.name ? `${investor.name}'s Portfolio` : "Your Portfolio Analysis"}
            </h1>
            <p className="text-gray-500 text-sm mt-1">
              {num_funds} funds · Total invested: {formatINR(total_invested)} · Current: {formatINR(total_value)}
            </p>
          </div>
          {is_demo && (
            <div className="hidden sm:block text-right">
              <p className="text-xs text-amber-400 font-medium">Demo Portfolio</p>
              <p className="text-xs text-gray-600">Upload your CAMS PDF for real analysis</p>
            </div>
          )}
        </motion.div>
      </div>

      {/* ── Dashboard grid ── */}
      <div className="max-w-5xl mx-auto px-6 space-y-5">
        {/* Row 1: XIRR */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.05 }}
        >
          <XirrCard
            xirr={xirr}
            apparentReturn={apparent_return}
            gapRupees={xirr_gap_rupees}
            simpleReturn={simple_return}
            totalInvested={total_invested}
            totalValue={total_value}
            benchmark={benchmark}
          />
        </motion.div>

        {/* Row 2: Overlap + Expense side by side on lg */}
        <div className="grid lg:grid-cols-2 gap-5">
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <OverlapChart
              uniqueStocks={overlap?.unique_stocks ?? 0}
              topHoldings={overlap?.top_holdings ?? []}
              top3Concentration={overlap?.top_3_concentration ?? 0}
              numFunds={overlap?.num_funds ?? 0}
              verdict={overlap?.verdict ?? {}}
              fundDetails={overlap?.fund_details ?? []}
              overlapScore={overlap?.overlap_score ?? 0}
            />
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
            <ExpenseDrain
              fundBreakdown={expense?.fund_breakdown ?? []}
              totalAnnualDrain={expense?.total_annual_drain ?? 0}
              totalDrainOverHorizon={expense?.total_drain_over_horizon ?? 0}
              horizonYears={expense?.horizon_years ?? 10}
              numRegularPlans={expense?.num_regular_plans ?? 0}
              numDirectPlans={expense?.num_direct_plans ?? 0}
              verdict={expense?.verdict ?? {}}
            />
          </motion.div>
        </div>

        {/* Row 3: Tax */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <TaxHarvest
            opportunities={tax?.opportunities ?? []}
            totalHarvestableLoss={tax?.total_harvestable_loss ?? 0}
            totalTaxSaving={tax?.total_tax_saving ?? 0}
            daysToFyEnd={tax?.days_to_fy_end ?? 365}
            isUrgent={tax?.is_urgent ?? false}
            hasOpportunities={tax?.has_opportunities ?? false}
            verdict={tax?.verdict ?? {}}
          />
        </motion.div>

        {/* Row 4: Goal Meter */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
          <GoalMeter
            goalName={goal?.goal_name ?? "Goal"}
            targetAmount={goal?.target_amount ?? 0}
            yearsToGoal={goal?.years_to_goal ?? 10}
            totalFutureValue={goal?.total_future_value ?? 0}
            totalFutureValueOptimized={goal?.total_future_value_optimized ?? 0}
            probability={goal?.probability ?? 0}
            probabilityOptimized={goal?.probability_optimized ?? 0}
            gap={goal?.gap ?? 0}
            monthlySipNeeded={goal?.monthly_sip_needed ?? 0}
            sipIncreaseNeeded={goal?.sip_increase_needed ?? 0}
            currentEquityPct={goal?.current_equity_pct ?? 80}
            optimalEquityPct={goal?.optimal_equity_pct ?? 80}
            blendedReturn={goal?.blended_return ?? 11}
            rebalancingActions={goal?.rebalancing_actions ?? []}
            verdict={goal?.verdict ?? {}}
          />
        </motion.div>

        {/* Row 5: AI Insights */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <AIInsights
            summary={insights?.summary ?? ""}
            keyFindings={insights?.key_findings ?? ""}
            rebalancing={insights?.rebalancing ?? ""}
            actionItems={insights?.action_items ?? []}
            model={insights?.model ?? ""}
            isDemo={is_demo}
          />
        </motion.div>

        {/* Bottom CTA */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="glass-card p-6 text-center"
        >
          <p className="text-white font-bold text-lg mb-2">Want analysis on your real portfolio?</p>
          <p className="text-gray-400 text-sm mb-4">
            This was a demo. Upload your CAMS statement for your actual XIRR, fees, and tax data.
          </p>
          <button
            onClick={() => router.push("/")}
            className="btn-primary mx-auto"
          >
            Upload My CAMS PDF <ArrowLeft className="w-4 h-4 rotate-180" />
          </button>
        </motion.div>
      </div>

      {/* ── Floating AI Chat ── */}
      <ChatBot
        sessionId={session_id}
        isOpen={isChatOpen}
        onToggle={() => setIsChatOpen(!isChatOpen)}
      />
    </main>
  );
}
