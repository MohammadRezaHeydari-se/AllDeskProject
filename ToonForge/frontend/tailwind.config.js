/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        surface: {
          DEFAULT: '#1a1b2e',
          alt: '#222340',
          hover: '#2a2b4a',
        },
        primary: {
          DEFAULT: '#6c5ce7',
          hover: '#7c6cf7',
        },
        accent: {
          DEFAULT: '#00cec9',
          hover: '#00ddd8',
        },
      },
    },
  },
  plugins: [],
}
