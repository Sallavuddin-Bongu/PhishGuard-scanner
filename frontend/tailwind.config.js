/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        navy: { 950: "#050b1a", 900: "#0a1530", 800: "#10203f", 700: "#172b52" },
        brand: { 400: "#4da3ff", 500: "#2d8cff", 600: "#1d6fd6" },
      },
    },
  },
  plugins: [],
};
