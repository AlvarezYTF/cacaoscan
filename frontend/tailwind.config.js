/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      maxWidth: {
        '4xl': '56rem',  // 896px
        '5xl': '64rem',  // 1024px
        '6xl': '72rem',  // 1152px
        '7xl': '80rem',  // 1280px
      },
    },
  },
  plugins: [],
}
