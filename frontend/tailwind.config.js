/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["'Inter'", "ui-sans-serif", "system-ui"],
      },
      colors: {
        primary: {
          DEFAULT: "#4c1d95",
          50: "#ede9fe",
          100: "#ddd6fe",
          200: "#c4b5fd",
          300: "#a78bfa",
          400: "#8b5cf6",
          500: "#7c3aed",
          600: "#6d28d9",
          700: "#5b21b6",
          800: "#4c1d95",
          900: "#3b0764",
        },
        neutral: {
          50: "#f8fafc",
          100: "#f1f5f9",
          200: "#e2e8f0",
          300: "#cbd5f5",
          400: "#94a3b8",
          500: "#64748b",
          600: "#475569",
          700: "#334155",
          800: "#1e293b",
          900: "#0f172a",
        },
        success: "#16a34a",
        warning: "#f59e0b",
        danger: "#dc2626",
      },
      boxShadow: {
        card: "0 20px 45px -25px rgba(79, 70, 229, 0.45)",
      },
    },
  },
  plugins: [],
};
