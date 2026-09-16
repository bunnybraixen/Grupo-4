/**
 * Configuración de Vite para CoreStream Frontend
 * 
 * Este archivo configura el servidor de desarrollo Vite con:
 * - Plugin de Vue 3 para procesar archivos .vue
 * - Resolución de alias (@/ -> src/) para importaciones limpias
 * - Proxy de API hacia el backend de FastAPI (dinámico según entorno)
 * - Proxy de WebSocket para comunicación en tiempo real
 * 
 * VARIABLES DE ENTORNO:
 * - VITE_API_BASE_URL: URL del backend (ej: http://backend:8000 en Docker, http://localhost:8000 en local)
 */

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import os from 'os'

// Obtener la dirección IP local (no localhost para compatibilidad)
const getLocalIP = () => {
  const interfaces = os.networkInterfaces()
  for (const [, addresses] of Object.entries(interfaces)) {
    for (const addr of addresses) {
      if (addr.family === 'IPv4' && !addr.internal) {
        return addr.address
      }
    }
  }
  return 'localhost'
}

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
      '@': path.resolve(__dirname, './src'),

      /**
       * @iconify/vue por defecto, ante un ícono no precargado, intenta
       * buscarlo en APIs públicas (api.iconify.design y espejos) — viola la
       * CSP `connect-src 'self'` del contenedor. La build "offline" del
       * mismo paquete no incluye ese código de red en absoluto: los íconos
       * deben registrarse a mano (ver main.ts, addCollection + mdi-subset).
       * Este alias hace que los `import { Icon } from '@iconify/vue'`
       * existentes en toda la app resuelvan a esa build sin tocar cada
       * componente.
       */
      '@iconify/vue': path.resolve(__dirname, './node_modules/@iconify/vue/dist/offline.mjs')
    }
  },

  // Configuración del servidor de desarrollo
  server: {
    // Puerto en el que corre el servidor de desarrollo
    port: 5173,
    // Host para permitir acceso desde otros contenedores Docker
    host: '0.0.0.0',
    // Permitir que encuentre el puerto dinámicamente
    strictPort: false,

    // Configurar HMR para permitir cualquier puerto
    hmr: {
      protocol: 'ws'
    },

    // Proxy de API hacia el backend. Ambos contenedores viven en la misma
    // red bridge de Docker (docker-compose.dev.yml, sin network_mode: host
    // desde la fase 6), así que el backend se alcanza por su nombre de
    // servicio ("backend"), no por localhost — dentro de este contenedor,
    // localhost es el propio frontend.
    proxy: {
      '/api': {
        target: process.env.VITE_API_TARGET ?? 'http://backend:8000',
        changeOrigin: false,
        ws: true,
        rewrite: (path) => path
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
