/**
 * Store de Autenticación - CoreStream
 * Gestiona la sesión JWT, usuario actual y permisos RBAC
 * 
 * Responsabilidades:
 * - Autenticación (login, logout, registro)
 * - Gestión de tokens (almacenamiento, refresco)
 * - Control de acceso basado en roles
 * - Persistencia de sesión en localStorage
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, AuthTokens, UserRole } from '@/types'
import { api, setAuthTokens, clearAuthTokens } from '@/services/api'

/**
 * Resumen de un error para la consola. Nunca se registra el objeto completo:
 * un AxiosError incluye el body de la petición, es decir, la contraseña.
 */
const errorSummary = (err: unknown): string | number =>
  (err as any)?.response?.status ?? (err instanceof Error ? err.message : String(err))

export const useAuthStore = defineStore('auth', () => {
  // ========== ESTADO REACTIVO ==========
  
  /**
   * Usuario actualmente autenticado
   * null si no hay sesión activa
   */
  const user = ref<User | null>(null)

  /**
   * Tokens de autenticación (access y refresh)
   * Se persiste en localStorage para mantener sesión
   */
  const tokens = ref<AuthTokens | null>(null)

  /**
   * Indica si el usuario está autenticado
   * Derivado del estado de tokens y usuario
   */
  const isAuthenticated = ref(false)

  /**
   * Flag de carga durante operaciones async
   * Previene múltiples llamadas simultáneas
   */
  const isLoading = ref(false)

  /**
   * Mensaje de error de la última operación fallida
   */
  const error = ref<string | null>(null)

  // ========== GETTERS COMPUTADOS ==========

  const normalizeRole = (role?: string | null) =>
    String(role ?? '').trim().toUpperCase().replace('USERROLE.', '').replace('-', '_')

  /**
   * Comprueba si el usuario tiene rol de administrador
   */
  const isAdmin = computed(() => normalizeRole(user.value?.role ?? localStorage.getItem('userRole')) === 'ADMIN')

  /**
   * Comprueba si el usuario tiene rol de desarrollador
   */
  const isDeveloper = computed(() => normalizeRole(user.value?.role ?? localStorage.getItem('userRole')) === 'DEVELOPER')

  /**
   * Comprueba si el usuario tiene rol de líder de grupo
   */
  const isGroupLeader = computed(() => normalizeRole(user.value?.role ?? localStorage.getItem('userRole')) === 'GROUP_LEADER')

  /**
   * Líder de equipo, aceptando los dos nombres que usa el proyecto:
   * `GROUP_LEADER` (enum de `users.role`) y `TEAM_LEADER` (docs/RBAC.md y la
   * tabla `roles`). Con solo uno de ellos, un líder real quedaba sin permisos
   * de gestión en la interfaz (mismo desajuste que había en el backend).
   */
  const isTeamLeader = computed(() => {
    const role = normalizeRole(user.value?.role ?? localStorage.getItem('userRole'))
    return role === 'GROUP_LEADER' || role === 'TEAM_LEADER'
  })

  /**
   * Retorna el rol actual del usuario
   */
  const userRole = computed((): UserRole | undefined => user.value?.role)

  /**
   * Retorna el nombre completo del usuario autenticado
   */
  const fullName = computed(() => user.value?.fullName ?? '')

  /**
   * Retorna el email del usuario autenticado
   */
  const userEmail = computed(() => user.value?.email ?? '')

  // ========== ACCIONES ==========

  /**
   * Inicializa el store desde localStorage
   * Se ejecuta cuando la aplicación carga
   * Restaura sesión anterior si existen tokens válidos
   */
  const initialize = () => {
    try {
      const storedTokens = localStorage.getItem('authTokens')
      if (storedTokens) {
        const parsed: AuthTokens = JSON.parse(storedTokens)
        tokens.value = parsed
        isAuthenticated.value = true
        /**
         * Rehidrata el estado del cliente HTTP (Authorization: Bearer) a
         * partir de los tokens persistidos. Sin esta llamada, tras recargar
         * la página el interceptor no enviaba el token y la API respondía
         * 403 "Not authenticated".
         */
        setAuthTokens(parsed)
        // El fetchMe() será llamado por el composable de autenticación
      }
    } catch (err) {
      console.error('Error al inicializar autenticación desde localStorage:', errorSummary(err))
      clearSession()
    }
  }

  /**
   * Autentica al usuario con email y contraseña
   * 
   * @param email - Email del usuario
   * @param password - Contraseña en texto plano
   * @returns Promise<User> - Datos del usuario autenticado
   * 
   * Flujo:
   * 1. Llama a api.auth.login(email, password)
   * 2. Almacena tokens en localStorage
   * 3. Marca isAuthenticated = true
   * 4. Obtiene datos completos del usuario con fetchMe()
   */
  const login = async (email: string, password: string): Promise<User> => {
    isLoading.value = true
    error.value = null

    try {
      const response = await api.auth.login({ email, password })
      
      // Guardar tokens y activarlos en el cliente HTTP
      tokens.value = response.tokens
      setAuthTokens(response.tokens)
      localStorage.setItem('authTokens', JSON.stringify(response.tokens))
      localStorage.setItem('accessToken', response.tokens.accessToken)
      localStorage.setItem('refreshToken', response.tokens.refreshToken)

      isAuthenticated.value = true

      // Obtener datos completos del usuario
      await fetchMe()

      return user.value!
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al iniciar sesión'
      error.value = message
      console.error('Error en login:', errorSummary(err))
      clearSession()
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Obtiene los datos actuales del usuario autenticado
   * Se ejecuta después del login para obtener información completa
   * 
   * @returns Promise<User>
   */
  const fetchMe = async (): Promise<User> => {
    try {
      /**
       * `api.auth.getMe()` devuelve el usuario ya normalizado a camelCase
       * (antes se llamaba a `api.auth.me`, que no existía y hacía fallar el
       * login con un TypeError).
       */
      const userData = await api.auth.getMe()
      user.value = userData
      return userData
    } catch (err) {
      console.error('Error al obtener datos del usuario:', errorSummary(err))
      clearSession()
      throw err
    }
  }

  /**
   * Refresca el access token usando el refresh token
   * Se debe ejecutar automáticamente cuando el token está próximo a expirar
   * 
   * @returns Promise<AuthTokens> - Nuevos tokens
   */
  const refreshToken = async (): Promise<AuthTokens> => {
    if (!tokens.value?.refreshToken) {
      throw new Error('No hay refresh token disponible')
    }

    try {
      const newTokens = await api.auth.refresh(tokens.value.refreshToken)
      tokens.value = newTokens
      setAuthTokens(newTokens)
      localStorage.setItem('authTokens', JSON.stringify(newTokens))
      localStorage.setItem('accessToken', newTokens.accessToken)
      localStorage.setItem('refreshToken', newTokens.refreshToken)
      return newTokens
    } catch (err) {
      console.error('Error al refrescar token:', errorSummary(err))
      clearSession()
      throw err
    }
  }

  /**
   * Cierra la sesión del usuario
   *
   * Los JWT no tienen estado en el servidor (no existe /auth/logout), así
   * que cerrar sesión es limpiar los tokens y los datos locales. La
   * redirección al login la hace quien llama.
   */
  const logout = async (): Promise<void> => {
    clearSession()
  }

  /**
   * Limpia toda la información de sesión
   * Función auxiliar llamada por logout e initialize en caso de error
   */
  const clearSession = (): void => {
    user.value = null
    tokens.value = null
    isAuthenticated.value = false
    error.value = null
    // Limpia también el estado y la persistencia del cliente HTTP
    clearAuthTokens()
    localStorage.removeItem('authTokens')
  }

  return {
    // Estado
    user,
    tokens,
    isAuthenticated,
    isLoading,
    error,
    // Getters
    isAdmin,
    isDeveloper,
    isGroupLeader,
    isTeamLeader,
    userRole,
    fullName,
    userEmail,
    // Acciones
    initialize,
    login,
    fetchMe,
    refreshToken,
    logout,
    clearSession,
  }
})
