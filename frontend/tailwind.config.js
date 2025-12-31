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
        // Dark cyber theme colors
        'cyber-dark': '#0a0e27',
        'cyber-darker': '#050818',
        'cyber-light': '#1a1f3a',
        'cyber-lighter': '#2a2f4a',
        'cyber-border': '#3a3f5a',
        'neon-green': '#00ff88',
        'neon-blue': '#00d4ff',
        'neon-purple': '#b100ff',
        'neon-pink': '#ff00aa',
        'cyber-gray': '#888888',
      },
      fontFamily: {
        'cyber': ['"Orbitron"', 'sans-serif'],
        'mono': ['"Share Tech Mono"', 'monospace'],
      },
      boxShadow: {
        'neon': '0 0 10px #00ff88, 0 0 20px #00d4ff',
        'neon-glow': '0 0 5px #00ff88, 0 0 15px #00d4ff, 0 0 30px #b100ff',
        'neon-pink': '0 0 10px #ff00aa, 0 0 20px #ff00aa',
        'neon-purple': '0 0 10px #b100ff, 0 0 20px #b100ff',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'float': 'float 6s ease-in-out infinite',
        'scan': 'scan 3s linear infinite',
        'blink': 'blink 1s step-end infinite',
      },
      keyframes: {
        glow: {
          'from': {
            boxShadow: '0 0 10px #00ff88, 0 0 20px #00d4ff',
          },
          'to': {
            boxShadow: '0 0 20px #00ff88, 0 0 40px #00d4ff, 0 0 60px #b100ff',
          }
        },
        float: {
          '0%, 100%': {
            transform: 'translateY(0)',
          },
          '50%': {
            transform: 'translateY(-10px)',
          }
        },
        scan: {
          '0%': {
            transform: 'translateY(-100%)',
          },
          '100%': {
            transform: 'translateY(100vh)',
          }
        },
        blink: {
          '0%, 100%': {
            opacity: '1',
          },
          '50%': {
            opacity: '0',
          }
        }
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'cyber-grid': `
          linear-gradient(rgba(30, 30, 50, 0.1) 1px, transparent 1px),
          linear-gradient(90deg, rgba(30, 30, 50, 0.1) 1px, transparent 1px)
        `,
      },
      backgroundSize: {
        'cyber-grid': '20px 20px',
      },
      backdropBlur: {
        xs: '2px',
      },
      transitionDuration: {
        '2000': '2000ms',
      },
      zIndex: {
        '60': '60',
        '70': '70',
        '80': '80',
        '90': '90',
        '100': '100',
      },
    },
  },
  plugins: [],
}
