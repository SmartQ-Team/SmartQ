/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ufh: {
          blue: '#003087',
          dark: '#001f5c',
          deep: '#00123d',
          soft: '#e8eefb',
          gold: '#FFB81C',
          goldDark: '#d99a0b',
          bg: '#f4f7fc',
          text: '#1c2540',
        },
      },
      fontFamily: {
        sans: ['Inter', 'Segoe UI', 'system-ui', 'sans-serif'],
        display: ['"Space Grotesk"', 'Inter', 'sans-serif'],
      },
      boxShadow: {
        soft: '0 2px 12px rgba(0, 48, 135, 0.12)',
        float: '0 20px 60px -15px rgba(0, 48, 135, 0.28)',
        glass: '0 8px 32px rgba(0, 26, 77, 0.10)',
        glow: '0 0 0 12px rgba(255, 184, 28, 0.25)',
      },
      keyframes: {
        flash: {
          '0%,100%': { boxShadow: '0 0 0 0 rgba(255,184,28,0)' },
          '50%': { boxShadow: '0 0 0 12px rgba(255,184,28,.25)' },
        },
        pulseRing: {
          '0%': { transform: 'scale(1)', opacity: '0.7' },
          '100%': { transform: 'scale(1.6)', opacity: '0' },
        },
      },
      animation: {
        flash: 'flash 1.4s ease-in-out infinite',
        pulseRing: 'pulseRing 2s cubic-bezier(0.4,0,0.6,1) infinite',
      },
    },
  },
  plugins: [],
};