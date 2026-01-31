/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        'brand-dark': '#2D3E50',
        'brand-accent': '#FF9F56',
        'brand-bg': '#EAEFEF',
      },
      animation: {
        'shimmer': 'shimmer 4s infinite linear',
        'scroll-line': 'scroll-line 1s infinite ease-in-out',
        // Speed kam karne ke liye 45s set kiya hai
        'marquee': 'marquee 10s linear infinite', 
      },
      keyframes: {
        shimmer: {
          '0%': { transform: 'translateX(-150%)' },
          '100%': { transform: 'translateX(150%)' },
        },
        'scroll-line': {
          '0%': { transform: 'translateY(-100%)' },
          '50%': { transform: 'translateY(100%)' },
          '100%': { transform: 'translateY(200%)' },
        },
        marquee: {
          '0%': { transform: 'translateX(0%)' },
          '100%': { transform: 'translateX(-50%)' },
        }
      }
    },
  },
  plugins: [],
}