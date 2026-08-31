/**
 * Configuración de Vite para CoreStream Frontend
 * 
 * Este archivo configura el servidor de desarrollo Vite con:
 * - Plugin de Vue 3 para procesar archivos .vue
 * - Resolución de alias (@/ -> src/) para importaciones limpias
 * - Proxy de API hacia el backend de FastAPI en localhost:8000
 * - Proxy de WebSocket para comunicación en tiempo real
 */

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  // Plugins: activamos el plugin de Vue 3 para procesar componentes .vue
  plugins: [vue()],

  // Resolución de módulos: configuramos alias para importaciones más limpias
  resolve: {
    alias: {
      /**
       * Alias '@' apunta al directorio 'src/'
       * Permite escribir: import X from '@/components/...'
       * En lugar de: import X from '../../../components/...'
       */
      '@': path.resolve(__dirname, './src')
    }
  },

  // Configuración del servidor de desarrollo
  server: {
    // Puerto en el que corre el servidor de desarrollo
    port: 5173,

    // Proxy de solicitudes HTTP hacia el backend FastAPI
    proxy: {
      /**
       * Cualquier solicitud a /api/... será redirigida a localhost:8000/api/...
       * changeOrigin: true cambia el header 'Host' de la solicitud para que coincida con el servidor destino
       */
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },

      /**
       * WebSocket proxy para comunicación en tiempo real
       * Redirige conexiones ws://localhost:5173/ws a ws://localhost:8000/ws
       * ws: true activa el soporte de WebSocket
       */
      '/ws': {
        target: 'ws://localhost:8000',
        changeOrigin: true,
        ws: true
      }
    }
  },

  // Configuración de compilación para producción
  build: {
    // Directorio de salida
    outDir: 'dist',
    // Limpiar directorio antes de compilar
    emptyOutDir: true
  }
})
