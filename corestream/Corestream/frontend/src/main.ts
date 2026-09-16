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
 * Vue i18n: internacionalización
 * Proporciona soporte multiidioma
 * Permite cambiar entre idiomas sin recargar la página
 */
import { createI18n } from 'vue-i18n'

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
 * CONFIGURACIÓN DE i18n (INTERNACIONALIZACIÓN)
 * ========================================
 * 
 * Define los idiomas soportados y los mensajes de traducción.
 * En una aplicación real, los mensajes se cargarían desde archivos JSON separados.
 */
const i18n = createI18n({
  /**
   * Idioma por defecto de la aplicación
   * Se usa si el idioma del navegador no es soportado
   */
  locale: 'es',

  /**
   * Fallback: idioma alternativo si una traducción no existe
   */
  fallbackLocale: 'es',

  /**
   * Mensajes de traducción
   * Estructura: { idioma: { clave: valor } }
   * En una aplicación real, esto estaría en archivos separados:
   * - src/locales/es.json
   * - src/locales/en.json
   * - etc.
   */
  messages: {
    /**
     * Textos en español (es)
     * Son los textos por defecto de la aplicación
     */
    es: {
      /**
       * Etiquetas comunes
       */
      common: {
        save: 'Guardar',
        cancel: 'Cancelar',
        delete: 'Eliminar',
        edit: 'Editar',
        create: 'Crear',
        loading: 'Cargando...',
        error: 'Error',
        success: 'Éxito',
        close: 'Cerrar'
      },

      /**
       * Mensajes de navegación
       */
      navigation: {
        dashboard: 'Dashboard',
        projects: 'Proyectos',
        team: 'Equipo',
        analytics: 'Analítica',
        settings: 'Configuración'
      },

      /**
       * Mensajes de autenticación
       */
      auth: {
        login: 'Iniciar Sesión',
        logout: 'Cerrar Sesión',
        register: 'Registrarse',
        email: 'Correo Electrónico',
        password: 'Contraseña',
        rememberMe: 'Recuérdame',
        forgotPassword: 'Olvidé mi contraseña'
      },

      /**
       * Mensajes de validación
       */
      validation: {
        required: 'Este campo es requerido',
        email: 'Ingresa un correo electrónico válido',
        passwordTooShort: 'La contraseña debe tener al menos 8 caracteres',
        passwordsDoNotMatch: 'Las contraseñas no coinciden'
      }
    },

    /**
     * Textos en inglés (en)
     * Traducción de los textos al inglés
     */
    en: {
      common: {
        save: 'Save',
        cancel: 'Cancel',
        delete: 'Delete',
        edit: 'Edit',
        create: 'Create',
        loading: 'Loading...',
        error: 'Error',
        success: 'Success',
        close: 'Close'
      },
      navigation: {
        dashboard: 'Dashboard',
        projects: 'Projects',
        team: 'Team',
        analytics: 'Analytics',
        settings: 'Settings'
      },
      auth: {
        login: 'Sign In',
        logout: 'Sign Out',
        register: 'Sign Up',
        email: 'Email',
        password: 'Password',
        rememberMe: 'Remember me',
        forgotPassword: 'Forgot password'
      },
      validation: {
        required: 'This field is required',
        email: 'Enter a valid email address',
        passwordTooShort: 'Password must be at least 8 characters',
        passwordsDoNotMatch: 'Passwords do not match'
      }
    }
  },

  /**
   * Configuración global de i18n
   */
  globalInjection: true,
  legacy: false
})

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
