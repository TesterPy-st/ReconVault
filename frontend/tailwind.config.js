/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Dark cyber theme palette
        dark: {
          900: '#0a0e27',
          800: '#1a1f3a',
          700: '#252b4a',
          600: '#303860',
        },
        neon: {
          green: '#00ff88',
          blue: '#00d4ff',
          purple: '#a855f7',
          pink: '#ec4899',
        },
        accent: {
          primary: '#00ff88',
          secondary: '#00d4ff',
        }
      },
      boxShadow: {
        'neon-green': '0 0 10px rgba(0, 255, 136, 0.5), 0 0 20px rgba(0, 255, 136, 0.3)',
        'neon-blue': '0 0 10px rgba(0, 212, 255, 0.5), 0 0 20px rgba(0, 212, 255, 0.3)',
      },
      fontFamily: {
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 10px rgba(0, 255, 136, 0.5)' },
          '100%': { boxShadow: '0 0 20px rgba(0, 255, 136, 0.8), 0 0 30px rgba(0, 212, 255, 0.4)' },
        }
      }
    },
  },
  plugins: [],
}
