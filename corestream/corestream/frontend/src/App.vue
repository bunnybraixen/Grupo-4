<!--
  Componente raíz de la aplicación CoreStream

  Este componente es el punto de entrada visual de la aplicación.
  Es responsable de:
  - Renderizar la RouterView (ruta actual)
  - Aplicar layouts globales
  - Validar autenticación
  - Gestionar tema oscuro/claro
  - Mostrar notificaciones globales

  Se monta en el elemento #app del index.html
-->
<template>
  <!--
    Elemento raíz: aquí rendizamos toda la aplicación
    Aplicamos clases de Tailwind para modo oscuro si está activado
  -->
  <div class="min-h-screen bg-white dark:bg-gray-950 transition-colors duration-200">
    <!--
      RouterView renderiza el componente correspondiente a la ruta actual
      Cambios en la ruta actualizarán automáticamente este componente
    -->
    <RouterView />

    <!--
      Componente global para mostrar notificaciones Toast
      Cualquier componente puede disparar notificaciones que aparecerán aquí
    -->
    <NotificationContainer v-if="showNotifications" />
  </div>
</template>

<script setup lang="ts">
/**
 * Configuración del componente con Composition API + Setup
 */

import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api, setAuthTokens, clearAuthTokens } from '@/services/api'
import NotificationContainer from '@/components/NotificationContainer.vue'

/**
 * ========================================
 * REFERENCIAS Y ESTADO
 * ========================================
 */

/**
 * Indica si se deben mostrar notificaciones
 * Se inicializa en true después del componente esté montado
 */
const showNotifications = ref(false)

/**
 * Obtiene la instancia del router para navegación y acceso a información de rutas
 */
const router = useRouter()

/**
 * ========================================
 * MÉTODOS
 * ========================================
 */

/**
 * Inicializa la aplicación al cargar
 * 
 * Tareas:
 * - Valida si el usuario está autenticado
 * - Recupera información del usuario actual
 * - Restaura preferencias guardadas (tema, idioma)
 * - Configura listeners globales
 */
const initializeApp = async (): Promise<void> => {
  try {
    /**
     * Obtiene tokens del localStorage
     * Se guardan después de login o cuando se renuevan
     */
    const accessToken = localStorage.getItem('accessToken')
    const refreshToken = localStorage.getItem('refreshToken')

    /**
     * Si no hay tokens, el usuario no está autenticado
     * El router guard lo redirigirá a login automáticamente
     */
    if (!accessToken || !refreshToken) {
      return
    }

    /**
     * Restaura los tokens en el servicio de API
     * Necesario para que los interceptores funcionen
     */
    setAuthTokens({
      accessToken,
      refreshToken,
      tokenType: 'Bearer'
    })

    /**
     * Obtiene información del usuario actual del backend
     * Valida que el token sea válido y el usuario exista
     */
    const response = await api.auth.getMe()

    if (response.success && response.data) {
      /**
       * Guarda información del usuario en localStorage
       * Se usa en guards de navegación y lógica de permisos
       */
      localStorage.setItem('userRole', response.data.role)
      localStorage.setItem('userId', response.data.id)
      localStorage.setItem('userName', response.data.fullName)
    }
  } catch (error) {
    /**
     * Si falla la obtención del usuario, limpia tokens y redirige a login
     * Probablemente el token expiró o es inválido
     */
    clearAuthTokens()
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('userRole')
    localStorage.removeItem('userId')

    /**
     * Redirige a login solo si no está ya ahí
     */
    if (router.currentRoute.value.name !== 'Login') {
      await router.push({ name: 'Login' })
    }
  }
}

/**
 * Aplica el modo oscuro si está guardado en preferencias
 * 
 * El modo oscuro se controla agregando la clase 'dark' al elemento <html>
 * Los estilos de Tailwind se ajustan automáticamente con selectores dark:
 */
const initializeDarkMode = (): void => {
  /**
   * Obtiene la preferencia de tema guardada
   * Valores: 'dark', 'light', o null (seguir sistema)
   */
  const savedTheme = localStorage.getItem('theme')

  /**
   * Obtiene la preferencia del sistema operativo
   */
  const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches

  /**
   * Determina si debe aplicarse modo oscuro
   * Prioridad: preferencia guardada > preferencia del sistema
   */
  const isDark = savedTheme ? savedTheme === 'dark' : systemPrefersDark

  /**
   * Aplica o remueve la clase 'dark' del elemento html
   * Tailwind CSS usa esta clase para aplicar estilos oscuros
   */
  if (isDark) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}

/**
 * Escucha cambios en la preferencia de tema del sistema
 * Cuando el usuario cambia su preferencia OS, la aplicación se adapta
 */
const setupDarkModeListener = (): void => {
  /**
   * Crea un listener para cambios en preferencia de tema del sistema
   */
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')

  /**
   * Handler que se ejecuta cuando la preferencia cambia
   */
  const handleChange = (e: MediaQueryListEvent | MediaQueryList): void => {
    /**
     * Solo se aplica si el usuario no ha guardado una preferencia manual
     */
    if (!localStorage.getItem('theme')) {
      if (e.matches) {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
    }
  }

  /**
   * Agrega el listener (sintaxis moderna)
   * En navegadores antiguos se usa addEventListener como fallback
   */
  if (mediaQuery.addEventListener) {
    mediaQuery.addEventListener('change', handleChange)
  }

  /**
   * Retorna función para limpiar el listener (se usa en onUnmounted)
   */
  return () => {
    if (mediaQuery.removeEventListener) {
      mediaQuery.removeEventListener('change', handleChange)
    }
  }
}

/**
 * ========================================
 * HOOKS DEL CICLO DE VIDA
 * ========================================
 */

/**
 * onMounted: se ejecuta cuando el componente está montado en el DOM
 * Lugar ideal para inicializaciones que requieren el DOM disponible
 */
onMounted(async () => {
  /**
   * Inicializa modo oscuro
   */
  initializeDarkMode()

  /**
   * Configura listener para cambios en preferencia del sistema
   */
  setupDarkModeListener()

  /**
   * Inicializa la aplicación (autenticación, usuario, preferencias)
   */
  await initializeApp()

  /**
   * Habilita notificaciones después de inicializar
   */
  showNotifications.value = true
})

/**
 * onUnmounted: se ejecuta cuando el componente se desmonta
 * Se usa para limpiar listeners y recursos
 */
onUnmounted(() => {
  /**
   * El listener del tema se limpia automáticamente al desmontar
   * (Vue maneja la limpieza de efectos secundarios en Composition API)
   */
})
</script>

<style scoped>
/**
 * Estilos locales del componente App
 * 
 * Normalmente este componente no necesita estilos locales
 * Los estilos globales de Tailwind en main.ts se aplican automáticamente
 */
</style>
