/**
 * Punto de entrada principal de la aplicación CoreStream
 * 
 * Este archivo es responsable de:
 * - Crear la instancia de Vue
 * - Instalar plugins globales (Router, Pinia, i18n)
 * - Importar estilos globales (Tailwind CSS)
 * - Montar la aplicación en el DOM
 */

import { createApp } from 'vue'

/**
 * Componente raíz de la aplicación
 * Contiene la lógica compartida por todas las páginas
 */
import App from './App.vue'

/**
 * Vue Router: sistema de enrutamiento
 * Permite navegar entre diferentes vistas/páginas
 */
import router from '@/router'

/**
 * Pinia: gestor de estado centralizado
 * Similar a Vuex pero más moderno y con mejor soporte de TypeScript
 * Se utiliza para almacenar estado global (usuario, autenticación, preferencias)
 */
import { createPinia } from 'pinia'

import i18n from '@/i18n'

/**
 * Estilos globales: Tailwind CSS
 * Se importa como un archivo normal, no como módulo CSS
 * Vite se encargará de procesarlo a través de PostCSS
 * Incluye:
 * - Reset y normalización de estilos
 * - Clases de utilidad (flex, text-center, etc.)
 * - Estilos personalizados de CoreStream (colores, temas, etc.)
 */
import '@/assets/styles/global.css'

/**
 * ========================================
 * CREACIÓN DE LA INSTANCIA DE VUE
 * ========================================
 * 
 * createApp crea la instancia raíz de la aplicación Vue 3
 * Proporciona métodos para instalar plugins y montar la aplicación
 */
const app = createApp(App)

/**
 * Instala el gestor de estado Pinia
 * Permite acceder a stores desde cualquier componente
 */
app.use(createPinia())

/**
 * Instala Vue Router
 * Habilita sistema de enrutamiento e inyecta router global
 */
app.use(router)

/**
 * Instala Vue i18n
 * Habilita traducción e inyecta $t global para acceder a mensajes
 */
app.use(i18n)

/**
 * ========================================
 * MONTAJE DE LA APLICACIÓN
 * ========================================
 * 
 * Monta la aplicación en el elemento DOM con id="app"
 * Este elemento está definido en index.html
 * 
 * A partir de este punto, Vue toma el control de toda la interfaz
 * y actualiza reactivamente los cambios
 */
app.mount('#app')
