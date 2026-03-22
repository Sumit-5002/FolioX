"use client";

import { motion } from "framer-motion";
import { Sparkles, AlertCircle } from "lucide-react";

interface AIInsightsProps {
  summary: string;
  keyFindings: string;
  rebalancing: string;
  actionItems: string[];
  model: string;
  isDemo?: boolean;
}

export default function AIInsights({
  summary,
  keyFindings,
  rebalancing,
  actionItems,
  model,
  isDemo,
}: AIInsightsProps) {
  const findings = keyFindings
    .split("\n")
    .map((l) => l.replace(/^[•\-\*]\s*/, "").trim())
    .filter(Boolean);

  return (
    <div className="glass-card p-6 animate-slide-up">
      {/* Header */}
      <div className="section-header">
        <div className="section-icon bg-purple-500/15">
          <Sparkles className="w-5 h-5 text-purple-400" />
        </div>
        <div className="flex-1">
          <h2 className="text-white font-bold text-lg">AI Advisor Analysis</h2>
          <p className="text-gray-400 text-sm">Powered by Gemini Flash · Personalized for your portfolio</p>
        </div>
        <span className="badge-purple text-[10px]">
          {model === "fallback" ? "Built-in AI" : "Gemini Flash"}
        </span>
      </div>

      {/* Demo notice */}
      {isDemo && (
        <div className="flex items-start gap-2 px-4 py-3 rounded-xl bg-amber-500/8 border border-amber-500/20 mb-4">
          <AlertCircle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
          <p className="text-xs text-amber-300">
            Showing analysis for <strong>demo portfolio</strong>. Upload your CAMS PDF for personalized insights.
          </p>
        </div>
      )}

      {/* Summary */}
      {summary && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-5"
        >
          <p className="text-xs text-gray-500 uppercase tracking-wide font-medium mb-2">Portfolio Summary</p>
          <p className="text-gray-300 text-sm leading-relaxed">{summary}</p>
        </motion.div>
      )}

      {/* Key Findings */}
      {findings.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-5"
        >
          <p className="text-xs text-gray-500 uppercase tracking-wide font-medium mb-3">Key Findings</p>
          <div className="space-y-2">
            {findings.map((f, i) => (
              <div key={i} className="flex items-start gap-3 px-4 py-3 rounded-xl bg-dark-700 border border-dark-600">
                <span className="text-base flex-shrink-0">{f.startsWith("•") ? "" : ""}</span>
                <p className="text-sm text-gray-300 leading-relaxed">{f}</p>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Rebalancing */}
      {rebalancing && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mb-5"
        >
          <p className="text-xs text-gray-500 uppercase tracking-wide font-medium mb-2">Rebalancing Strategy</p>
          <div className="px-4 py-3 rounded-xl bg-blue-500/8 border border-blue-500/20">
            <p className="text-sm text-gray-300 leading-relaxed">{rebalancing}</p>
          </div>
        </motion.div>
      )}

      {/* Priority Action Items */}
      {actionItems.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <p className="text-xs text-gray-500 uppercase tracking-wide font-medium mb-3">
            Priority Actions
          </p>
          <div className="space-y-2">
            {actionItems.map((item, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 + i * 0.1 }}
                className="flex items-start gap-3 px-4 py-3 rounded-xl border border-brand-500/20 bg-brand-500/5"
              >
                <div className="w-5 h-5 rounded-full bg-brand-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-[10px] font-black text-brand-400">{i + 1}</span>
                </div>
                <p className="text-sm text-gray-200 leading-relaxed">{item}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
}
