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
import { existsSync } from 'node:fs'

/**
 * WEB-08: destino del proxy hacia el backend.
 * 
 * Importante: el navegador siempre debe llamar a localhost:5173 y luego
 * Vite proxy redirige /api internamente a la red Docker. Si el navegador
 * alcanza directamente a backend:8000, significa que la app está usando
 * un build viejo o una URL absoluta hardcodeada.
 *
 * - Dentro de Docker: el servicio Vite debe apuntar al nombre 'backend'
 *   porque es la red interna de Docker.
 * - Fuera de Docker: el backend está en localhost:8000.
 */
const BACKEND_TARGET = existsSync('/.dockerenv')
  ? 'http://backend:8000'
  : 'http://localhost:8000'

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
    host: '0.0.0.0',
    port: 5173,

    // Proxy de solicitudes HTTP hacia el backend FastAPI.
    // El navegador nunca debe apuntar directamente a backend:8000.
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

  // Configuración de compilación para producción
  build: {
    // Directorio de salida
    outDir: 'dist',
    // Limpiar directorio antes de compilar
    emptyOutDir: true
  }
})
