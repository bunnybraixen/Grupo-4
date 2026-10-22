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

import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { clearAuthTokens } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
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
 * Store de autenticación: centraliza tokens, usuario y persistencia.
 * Se usa aquí para restaurar la sesión tras recargar la página.
 */
const authStore = useAuthStore()
useThemeStore()

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
     * Restaura la sesión desde localStorage (`authTokens`, `accessToken`,
     * `refreshToken`) y reactiva el token en el cliente HTTP. Antes este
     * método leía claves que NADIE escribía y se salía sin restaurar nada.
     */
    authStore.initialize()

    if (!authStore.tokens?.accessToken) {
      /**
       * Sin sesión persistida: el guard del router mandará a /login.
       */
      return
    }

    /**
     * Obtiene información del usuario actual del backend.
     * Valida que el token sea válido y devuelve el usuario normalizado.
     */
    const user = await authStore.fetchMe()

    /**
     * Guarda información del usuario en localStorage
     * Se usa en guards de navegación y lógica de permisos
     */
    localStorage.setItem('userRole', user.role)
    localStorage.setItem('userId', user.id)
    localStorage.setItem('userName', user.fullName ?? '')
    localStorage.setItem('userEmail', user.email ?? '')
  } catch (error) {
    /**
     * Si falla la obtención del usuario, limpia tokens y redirige a login
     * Probablemente el token expiró o es inválido
     */
    clearAuthTokens()
    localStorage.removeItem('userRole')
    localStorage.removeItem('userId')
    localStorage.removeItem('userName')

    /**
     * Redirige a login solo si no está ya ahí
     */
    if (router.currentRoute.value.name !== 'Login') {
      await router.push({ name: 'Login' })
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
   * Inicializa la aplicación (autenticación, usuario, preferencias)
   */
  await initializeApp()

  /**
   * Habilita notificaciones después de inicializar
   */
  showNotifications.value = true
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
