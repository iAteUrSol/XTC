/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'crypto-green': '#00c853',
        'crypto-red': '#ff3d00',
        'primary': '#3b82f6',
        'secondary': '#6b7280',
        'background': '#0f172a',
        'card': '#1e293b',
        'text-primary': '#f8fafc',
        'text-secondary': '#94a3b8',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
