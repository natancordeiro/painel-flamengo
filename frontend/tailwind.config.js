/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{ts,tsx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "1rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        flamengoRed: "#C8102E",
        flamengoBlack: "#111111",
        flamengoGray: "#1f1f1f"
      }
    },
  },
  plugins: [],
}
