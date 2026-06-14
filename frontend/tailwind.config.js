/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#F8F6F1",
        primary: "#2D7A6B",
        "primary-light": "#E8F5F2",
        "primary-dark": "#1F5A4E",
        accent: "#E8A838",
        "text-primary": "#1A1A2E",
        "text-secondary": "#6B7280",
        border: "#E5E1D8",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
}
