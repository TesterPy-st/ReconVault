/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Dark cyber theme colors
        'cyber-dark': '#0a0e27',
        'cyber-darker': '#050818',
        'cyber-light': '#1a1f3a',
        'cyber-lighter': '#2a2f4a',
        'neon-green': '#00ff88',
        'neon-blue': '#00d4ff',
        'neon-purple': '#b100ff',
        'neon-pink': '#ff00aa',
        'cyber-gray': '#888888',
        'cyber-border': '#3a3f5a',
      },
      fontFamily: {
        'cyber': ['"Orbitron"', 'sans-serif'],
        'mono': ['"Share Tech Mono"', 'monospace'],
      },
      boxShadow: {
        'neon': '0 0 10px #00ff88, 0 0 20px #00d4ff',
        'neon-glow': '0 0 5px #00ff88, 0 0 15px #00d4ff, 0 0 30px #b100ff',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        glow: {
          'from': {
            boxShadow: '0 0 10px #00ff88, 0 0 20px #00d4ff',
          },
          'to': {
            boxShadow: '0 0 20px #00ff88, 0 0 40px #00d4ff, 0 0 60px #b100ff',
          }
        }
      }
    },
  },
  plugins: [],
}
