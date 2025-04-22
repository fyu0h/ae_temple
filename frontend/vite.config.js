import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://0.0.0.0:8000',
        changeOrigin: true,
      },
      '/media': {
        target: 'http://0.0.0.0:8000',
        changeOrigin: true,
      }
    },
    allowedHosts: [
      'localhost',
      '127.0.0.1',
      'home.iinin.me'
    ]
  }
}) 