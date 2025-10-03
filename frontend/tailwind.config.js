/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'rift-gold': '#C89B3C',
        'rift-blue': '#0596AA',
        'rift-dark': '#0F2027',
        'rift-purple': '#785EF0'
      },
      fontFamily: {
        'league': ['Cinzel', 'serif']
      }
    },
  },
  plugins: [],
}