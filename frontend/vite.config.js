import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  },
  preview: {
    port: 5173,
    host: '0.0.0.0'
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          graph: ['react-force-graph']
        }
      },
      external: [],
      onwarn(warning, warn) {
        // Skip specific warnings for VR/AR dependencies
        if (warning.code === 'UNUSED_EXTERNAL_IMPORT' && warning.message.includes('aframe')) {
          return;
        }
        if (warning.code === 'UNRESOLVED_IMPORT' && warning.message.includes('aframe')) {
          return;
        }
        warn(warning);
      }
    }
  },
  optimizeDeps: {
    exclude: [
      '3d-force-graph-vr',
      '3d-force-graph-ar',
      'aframe-extras',
      'aframe'
    ]
  }
})
