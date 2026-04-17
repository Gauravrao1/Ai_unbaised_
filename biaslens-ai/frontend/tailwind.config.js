import forms from '@tailwindcss/forms'

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Manrope', 'sans-serif'],
        display: ['Space Grotesk', 'sans-serif'],
      },
      boxShadow: {
        glow: '0 24px 80px rgba(15, 23, 42, 0.3)',
      },
      colors: {
        canvas: '#08111f',
        panel: 'rgba(10, 16, 33, 0.8)',
        panelBorder: 'rgba(148, 163, 184, 0.18)',
        accent: {
          50: '#effef7',
          100: '#d6f8e7',
          200: '#a9eed1',
          300: '#79e3b4',
          400: '#47cc95',
          500: '#23ad78',
          600: '#188b60',
        },
        warning: {
          500: '#f59e0b',
          600: '#d97706',
        },
        danger: {
          500: '#ef4444',
          600: '#dc2626',
        },
        info: {
          500: '#38bdf8',
          600: '#0284c7',
        },
      },
      backgroundImage: {
        'hero-grid':
          'radial-gradient(circle at top left, rgba(56, 189, 248, 0.22), transparent 28%), radial-gradient(circle at top right, rgba(35, 173, 120, 0.2), transparent 24%), linear-gradient(180deg, #08111f 0%, #0e1729 48%, #0b1220 100%)',
      },
    },
  },
  plugins: [forms],
}
