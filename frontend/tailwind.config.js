/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0F1117",
        surface: "#1A1D27",
        "surface-2": "#222636",
        primary: "#4ADE80",
        "primary-light": "#1A2E22",
        "primary-dark": "#22C55E",
        accent: "#F59E0B",
        "text-primary": "#F1F5F9",
        "text-secondary": "#94A3B8",
        border: "#2D3148",
        "user-bubble": "#1E3A2F",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
}