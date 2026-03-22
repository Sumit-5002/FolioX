"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import axios from "axios";
import {
  TrendingUp, Shield, Zap, Search,
  ArrowRight,
} from "lucide-react";
import FileUpload from "@/components/FileUpload";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const FEATURES = [
  { icon: "📊", title: "True XIRR", desc: "Your real return, not the inflated number Groww shows" },
  { icon: "🎭", title: "Diversification X-Ray", desc: "See your actual unique stock exposure across all funds" },
  { icon: "💸", title: "Expense Drain", desc: "₹ cost of staying on Regular Plans over 10 years" },
  { icon: "🎯", title: "Tax Harvesting", desc: "Losses you can book before March 31 to save tax" },
  { icon: "📈", title: "Goal Meter", desc: "Probability of reaching your financial goal" },
  { icon: "🤖", title: "AI Advisor", desc: "Gemini Flash + Groq Llama 3.3 live portfolio chat" },
];

const STATS = [
  { value: "₹2.1Cr", label: "Avg expense drain found" },
  { value: "41", label: "Avg unique stocks across 7 funds" },
  { value: "2.5%", label: "Typical XIRR gap from app claims" },
];

export default function HomePage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [goalName, setGoalName] = useState("Retirement");
  const [targetAmount, setTargetAmount] = useState("5000000");
  const [yearsToGoal, setYearsToGoal] = useState("10");
  const [monthlySip, setMonthlySip] = useState("10000");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleAnalyze = async () => {
    if (!file) { setError("Please upload your CAMS statement PDF first."); return; }
    setError("");
    setIsLoading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("goal_name", goalName);
      formData.append("target_amount", targetAmount);
      formData.append("years_to_goal", yearsToGoal);
      formData.append("monthly_sip", monthlySip);

      const { data } = await axios.post(`${API_URL}/api/analyze`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 60000,
      });

      sessionStorage.setItem("mf_xray_result", JSON.stringify(data));
      router.push("/analyze");
    } catch (err: any) {
      const msg = err.response?.data?.detail || "Analysis failed. Please try again or use the demo.";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemo = async () => {
    setIsLoading(true);
    setError("");
    try {
      const { data } = await axios.post(`${API_URL}/api/analyze/demo`, {
        goal_name: goalName,
        target_amount: parseFloat(targetAmount),
        years_to_goal: parseInt(yearsToGoal),
        monthly_sip: parseFloat(monthlySip),
      });
      sessionStorage.setItem("mf_xray_result", JSON.stringify(data));
      router.push("/analyze");
    } catch (e: any) {
      setError("Demo failed. Is the backend running at " + API_URL + "?");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-dark-900 overflow-x-hidden">
      {/* ── Nav ── */}
      <nav className="border-b border-dark-600 px-6 py-4 flex items-center justify-between max-w-7xl mx-auto">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-brand-500/20 flex items-center justify-center">
            <Search className="w-4 h-4 text-brand-400" />
          </div>
          <span className="font-black text-white text-lg tracking-tight">MF X-Ray</span>
          <span className="badge-green text-[10px] ml-1">AI</span>
        </div>
        <div className="flex items-center gap-3">
          <a
            href="https://camsonline.com"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-ghost text-xs py-2 px-4"
          >
            Get CAMS PDF
          </a>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className="max-w-7xl mx-auto px-6 pt-16 pb-12">
        <div className="grid lg:grid-cols-2 gap-12 items-start">
          {/* Left: Hero text */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-brand-500/30 bg-brand-500/10 mb-6">
              <div className="w-1.5 h-1.5 rounded-full bg-brand-400 animate-pulse" />
              <span className="text-xs text-brand-300 font-medium">AI-Powered Portfolio Analysis · Free</span>
            </div>

            <h1 className="text-5xl lg:text-6xl font-black text-white leading-[1.08] mb-6">
              Your Mutual Fund{" "}
              <span className="gradient-text">Portfolio X-Ray</span>
            </h1>
            <p className="text-xl text-gray-400 leading-relaxed mb-8 max-w-lg">
              Upload your CAMS statement → Get your{" "}
              <strong className="text-white">true XIRR</strong>,{" "}
              <strong className="text-white">hidden fees</strong>, tax savings, and AI-powered advice in{" "}
              <strong className="text-brand-400">10 seconds</strong>.
            </p>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-4 mb-8">
              {STATS.map((s, i) => (
                <motion.div
                  key={s.label}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 + i * 0.1 }}
                  className="bg-dark-700 rounded-xl p-3 border border-dark-500 text-center"
                >
                  <p className="text-lg font-black text-brand-400">{s.value}</p>
                  <p className="text-[10px] text-gray-500 mt-0.5">{s.label}</p>
                </motion.div>
              ))}
            </div>

            {/* Features grid */}
            <div className="grid grid-cols-2 gap-3">
              {FEATURES.map((f, i) => (
                <motion.div
                  key={f.title}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 + i * 0.07 }}
                  className="flex items-start gap-3 p-3 rounded-xl bg-dark-800 border border-dark-600 hover:border-dark-400 transition-colors"
                >
                  <span className="text-xl">{f.icon}</span>
                  <div>
                    <p className="text-xs font-bold text-white">{f.title}</p>
                    <p className="text-[10px] text-gray-500 mt-0.5">{f.desc}</p>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Privacy note */}
            <div className="mt-6 flex items-center gap-2 text-xs text-gray-600">
              <Shield className="w-3.5 h-3.5" />
              <span>PDF processed in-memory · Never stored · 100% private</span>
            </div>
          </motion.div>

          {/* Right: Upload Card */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <div className="glass-card p-6 sticky top-8">
              <h2 className="text-lg font-bold text-white mb-2">Analyze Your Portfolio</h2>
              <p className="text-sm text-gray-400 mb-5">Upload CAMS PDF + set your goal → instant analysis</p>

              {/* File Upload */}
              <FileUpload onFileSelect={setFile} isLoading={isLoading} />

              {/* Goal inputs */}
              <div className="mt-5 space-y-3">
                <p className="text-xs text-gray-500 uppercase tracking-wide font-medium">Your Financial Goal</p>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs text-gray-500 mb-1 block">Goal Name</label>
                    <input
                      type="text"
                      value={goalName}
                      onChange={(e) => setGoalName(e.target.value)}
                      placeholder="e.g. Retirement"
                      className="w-full bg-dark-700 border border-dark-400 rounded-xl px-3 py-2.5 text-sm text-white placeholder-gray-600 outline-none focus:border-brand-500/50 transition-colors"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-gray-500 mb-1 block">Target (₹)</label>
                    <input
                      type="number"
                      value={targetAmount}
                      onChange={(e) => setTargetAmount(e.target.value)}
                      className="w-full bg-dark-700 border border-dark-400 rounded-xl px-3 py-2.5 text-sm text-white outline-none focus:border-brand-500/50 transition-colors"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-gray-500 mb-1 block">Timeline (years)</label>
                    <input
                      type="number"
                      value={yearsToGoal}
                      onChange={(e) => setYearsToGoal(e.target.value)}
                      className="w-full bg-dark-700 border border-dark-400 rounded-xl px-3 py-2.5 text-sm text-white outline-none focus:border-brand-500/50 transition-colors"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-gray-500 mb-1 block">Monthly SIP (₹)</label>
                    <input
                      type="number"
                      value={monthlySip}
                      onChange={(e) => setMonthlySip(e.target.value)}
                      className="w-full bg-dark-700 border border-dark-400 rounded-xl px-3 py-2.5 text-sm text-white outline-none focus:border-brand-500/50 transition-colors"
                    />
                  </div>
                </div>
              </div>

              {error && (
                <p className="mt-3 text-red-400 text-xs text-center">⚠️ {error}</p>
              )}

              {/* CTA Buttons */}
              <div className="mt-5 flex flex-col gap-3">
                <button
                  id="analyze-btn"
                  onClick={handleAnalyze}
                  disabled={isLoading}
                  className="btn-primary w-full py-4 text-base"
                >
                  {isLoading ? (
                    <>Analyzing… <span className="ml-2 animate-spin">⚙️</span></>
                  ) : (
                    <>Analyze My Portfolio <ArrowRight className="w-4 h-4" /></>
                  )}
                </button>

                <div className="flex items-center gap-3">
                  <div className="flex-1 h-px bg-dark-500" />
                  <span className="text-xs text-gray-600">or</span>
                  <div className="flex-1 h-px bg-dark-500" />
                </div>

                <button
                  id="demo-btn"
                  onClick={handleDemo}
                  disabled={isLoading}
                  className="btn-ghost w-full py-3 text-sm"
                >
                  <Zap className="w-4 h-4 text-brand-400" />
                  Try Demo Portfolio (instant)
                </button>
              </div>

              <p className="mt-3 text-center text-[10px] text-gray-600">
                Demo uses a realistic pre-built Indian MF portfolio. No PDF needed.
              </p>
            </div>
          </motion.div>
        </div>
      </section>

      {/* ── How it works ── */}
      <section className="max-w-7xl mx-auto px-6 py-12 border-t border-dark-700">
        <h2 className="text-2xl font-black text-white text-center mb-8">How It Works</h2>
        <div className="grid grid-cols-3 gap-6">
          {[
            { step: "01", icon: "📄", title: "Upload CAMS PDF", desc: "Download from camsonline.com and drag it in" },
            { step: "02", icon: "⚡", title: "AI Analysis in 10s", desc: "XIRR, overlap, fees, tax, goal probability — all calculated" },
            { step: "03", icon: "🎯", title: "Act on Insights", desc: "Get specific actions ranked by impact in rupees" },
          ].map((s) => (
            <div key={s.step} className="text-center">
              <div className="w-12 h-12 rounded-2xl bg-brand-500/10 border border-brand-500/20 flex items-center justify-center text-2xl mx-auto mb-3">
                {s.icon}
              </div>
              <div className="text-brand-400 text-xs font-bold mb-1">{s.step}</div>
              <p className="text-white font-bold mb-1">{s.title}</p>
              <p className="text-gray-500 text-sm">{s.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="border-t border-dark-700 px-6 py-6 text-center">
        <p className="text-gray-600 text-xs">
          Built for ET Hackathon · Powered by Gemini Flash + Groq Llama 3.3 + mfapi.in · MIT License
        </p>
      </footer>
    </main>
  );
}
