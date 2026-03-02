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
        void: "#0a0a0b",
        surface: "#111113",
        border: "#1f1f23",
        muted: "#71717a",
        accent: "#06b6d4",
        podcast: "#eab308",
        "podcast-muted": "#a16207",
        amber: "#f59e0b",
        fox: "#c084fc",
        bear: "#38bdf8",
        beaver: "#a78bfa",
      },
      fontFamily: {
        mono: ["ui-monospace", "SF Mono", "Monaco", "monospace"],
        sans: ["system-ui", "sans-serif"],
      },
      animation: {
        "pulse-soft": "pulse-soft 2s ease-in-out infinite",
        "glow": "glow 2s ease-in-out infinite alternate",
      },
      keyframes: {
        "pulse-soft": {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.85" },
        },
        "glow": {
          "0%": { boxShadow: "0 0 12px rgba(6, 182, 212, 0.3)" },
          "100%": { boxShadow: "0 0 20px rgba(6, 182, 212, 0.5)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
