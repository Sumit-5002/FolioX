import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        brand: {
          50:  "#ecfdf5",
          100: "#d1fae5",
          400: "#34d399",
          500: "#10b981",
          600: "#059669",
          700: "#047857",
        },
        dark: {
          900: "#070b14",
          800: "#0d1321",
          700: "#111827",
          600: "#1c2a3a",
          500: "#243042",
          400: "#2d3a4f",
          300: "#3d4f68",
        },
        accent: {
          blue:   "#3b82f6",
          purple: "#8b5cf6",
          amber:  "#f59e0b",
          red:    "#ef4444",
          cyan:   "#06b6d4",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      animation: {
        "fade-in":     "fadeIn 0.5s ease-out",
        "slide-up":    "slideUp 0.4s ease-out",
        "pulse-slow":  "pulse 3s ease-in-out infinite",
        "count-up":    "fadeIn 0.8s ease-out",
        "shimmer":     "shimmer 2s infinite",
        "glow":        "glow 2s ease-in-out infinite alternate",
      },
      keyframes: {
        fadeIn:  { from: { opacity: "0", transform: "translateY(8px)" }, to: { opacity: "1", transform: "translateY(0)" } },
        slideUp: { from: { opacity: "0", transform: "translateY(20px)" }, to: { opacity: "1", transform: "translateY(0)" } },
        shimmer: { "0%": { backgroundPosition: "-200% 0" }, "100%": { backgroundPosition: "200% 0" } },
        glow:    { from: { boxShadow: "0 0 10px #10b98133" }, to: { boxShadow: "0 0 25px #10b98166, 0 0 50px #10b98122" } },
      },
      backdropBlur: { xs: "2px" },
    },
  },
  plugins: [],
};
export default config;
