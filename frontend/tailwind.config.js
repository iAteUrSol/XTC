/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'crypto-green': '#16c784',
        'crypto-red': '#ea3943',
        'crypto-blue': '#3861fb',
        'crypto-gray': '#222531',
        'crypto-light-gray': '#323546',
        'crypto-dark': '#0d1117',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
