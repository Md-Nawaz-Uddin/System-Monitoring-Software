// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        primary: '#1B2431',       // sidebar background
        secondary: '#2D3B50',     // active link or hover
        accent: '#1CA7EC',        // optional accent color
        lightbg: '#F0F2F5',       // page background
        sidebarText: '#FFFFFF',   // text color in sidebar
      },
    },
  },
  plugins: [],
};
