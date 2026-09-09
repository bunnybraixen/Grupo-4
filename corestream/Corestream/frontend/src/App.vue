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
      NO se muestra en la página de login
    -->
    <NotificationContainer 
      v-if="showNotifications && router.currentRoute.value.name !== 'Login'" 
    />
    <GlobalDialog />
  </div>
</template>

<script setup lang="ts">
/**
 * Configuración del componente con Composition API + Setup
 */

import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import NotificationContainer from '@/components/NotificationContainer.vue'
import GlobalDialog from '@/components/common/GlobalDialog.vue'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'

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
  const authStore = useAuthStore()
  try {
    await authStore.initialize()
  } catch (error) {
    console.warn('Failed to initialize auth, clearing session', error)
    // initialize() falla en CUALQUIER visita sin sesión (primera carga sin
    // cookie, sesión expirada, etc.) — no es un error real, ver comentario
    // en authStore.initialize(). Antes esto mandaba a /login comparando por
    // nombre de ruta ('Login'), así que cualquier OTRA ruta pública (p. ej.
    // /invite/:token, donde el invitado nunca tuvo sesión) también terminaba
    // ahí. Se compara contra requiresAuth en vez de listar rutas públicas a
    // mano, para que cubra cualquier ruta pública presente o futura.
    if (router.currentRoute.value.meta.requiresAuth) {
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
  const themeStore = useThemeStore()
  const savedTheme = localStorage.getItem('corestream-theme')
  
  if (!savedTheme) {
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    themeStore.applyTheme(systemPrefersDark ? 'dark' : 'light')
  } else {
    themeStore.applyTheme(savedTheme as 'dark' | 'light')
  }
}

const setupDarkModeListener = (): (() => void) => {
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  const themeStore = useThemeStore()

  const handleChange = (e: MediaQueryListEvent | MediaQueryList): void => {
    if (!localStorage.getItem('corestream-theme')) {
      themeStore.applyTheme(e.matches ? 'dark' : 'light')
    }
  }

  if (mediaQuery.addEventListener) {
    mediaQuery.addEventListener('change', handleChange)
  }

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
