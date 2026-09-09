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

/**
 * Theme Store: gestión de tema claro/oscuro
 * Se importa aquí para inicializar antes de montar la app
 */
import { useThemeStore } from '@/stores/theme'

/**
 * Vue i18n: internacionalización
 * Proporciona soporte multiidioma
 * Permite cambiar entre idiomas sin recargar la página
 */
import i18n from '@/i18n'
import { vCan } from '@/directives'

/**
 * Iconos (Iconify): registro offline
 *
 * @iconify/vue por defecto, si un icono no está precargado, lo busca en
 * APIs públicas (api.iconify.design, api.unisvg.com, api.simplesvg.com) —
 * viola connect-src 'self' de la CSP del contenedor y deja el ícono roto en
 * producción (sin acceso a internet saliente). mdi-subset.json contiene los
 * datos de los ~33 íconos "mdi:*" que usa la app (generados una vez desde
 * @iconify-json/mdi, ver git log), registrados aquí antes de montar.
 */
import { addCollection } from '@iconify/vue'
import mdiSubset from '@/assets/icons/mdi-subset.json'
addCollection(mdiSubset as any)

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
 * ========================================
 * INICIALIZACIÓN DEL TEMA
 * ========================================
 *
 * Inicializa el theme store para aplicar el tema al documento
 * Se hace ANTES de montar la app para evitar flash de tema incorrecto
 * El store se encarga de:
 * - Leer preferencia de localStorage
 * - Aplicar data-theme="light|dark" al <html>
 * - Default: 'light' (modo claro como muestra el manual de usuario)
 */
const themeStore = useThemeStore()
themeStore.applyTheme(themeStore.getTheme())

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
 * Directiva global RBAC
 * Uso: v-can="['ADMIN', 'TEAM_LEADER']" o v-can="'ADMIN'"
 */
app.directive('can', vCan)

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
