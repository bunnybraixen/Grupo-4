
/**
 * Configuración de Vite para CoreStream Frontend
 */

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import { existsSync } from 'node:fs'

const BACKEND_TARGET = existsSync('/.dockerenv')
  ? 'http://backend:8000'
  : 'http://localhost:8000'

export default defineConfig({
  plugins: [vue()],

  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@iconify/vue': path.resolve(
        __dirname,
        './src/components/common/IconFallback.vue'
      )
    }
  },

  server: {
    host: '0.0.0.0',
    port: 5173,

    // Permitir el dominio público del Frontend en Railway
    allowedHosts: ['frontend-production-dcf4.up.railway.app'],

    proxy: {
      '/api': {
        target: BACKEND_TARGET,
        changeOrigin: true,
        secure: false
      },

      '/ws': {
        target: BACKEND_TARGET.replace(/^http/, 'ws'),
        changeOrigin: true,
        ws: true,
        secure: false
      }
    }
  },

  build: {
    outDir: 'dist',
    emptyOutDir: true
  }
})
