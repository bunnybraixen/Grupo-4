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

  /**
   * Comprueba si el usuario tiene rol de administrador
   */
  const isAdmin = computed(() => user.value?.role === 'ADMIN')

  /**
   * Comprueba si el usuario tiene rol de desarrollador
   */
  const isDeveloper = computed(() => user.value?.role === 'DEVELOPER')

  /**
   * Comprueba si el usuario tiene rol de líder de grupo
   */
  const isGroupLeader = computed(() => user.value?.role === 'GROUP_LEADER')

  /**
   * Líder de equipo, aceptando los dos nombres que usa el proyecto:
   * `GROUP_LEADER` (enum de `users.role`) y `TEAM_LEADER` (docs/RBAC.md y la
   * tabla `roles`). Con solo uno de ellos, un líder real quedaba sin permisos
   * de gestión en la interfaz (mismo desajuste que había en el backend).
   */
  const isTeamLeader = computed(() => {
    const role = String(user.value?.role ?? localStorage.getItem('userRole') ?? '').toUpperCase()
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

  /**
   * Comprueba si el access token está próximo a expirar (menos de 5 minutos)
   */
  const isTokenExpiringSoon = computed(() => {
    if (!tokens.value?.expiresAt) return false
    const expiringTime = tokens.value.expiresAt - 5 * 60 * 1000
    return Date.now() > expiringTime
  })

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
        tokens.value = JSON.parse(storedTokens)
        isAuthenticated.value = true
        /**
         * Rehidrata el estado del cliente HTTP (Authorization: Bearer) a
         * partir de los tokens persistidos. Sin esta llamada, tras recargar
         * la página el interceptor no enviaba el token y la API respondía
         * 403 "Not authenticated".
         */
        setAuthTokens(tokens.value)
        // El fetchMe() será llamado por el composable de autenticación
      }
    } catch (err) {
      console.error('Error al inicializar autenticación desde localStorage:', err)
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
      console.error('Error en login:', err)
      clearSession()
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Registra un nuevo usuario en el sistema
   * 
   * @param data - Datos de registro {email, password, fullName, departament?}
   * @returns Promise<User> - Usuario creado
   * 
   * Nota: Generalmente no autentica automáticamente, requiere login posterior
   */
  const register = async (data: {
    email: string
    password: string
    fullName: string
    department?: string
  }): Promise<User> => {
    isLoading.value = true
    error.value = null

    try {
      const response = await api.auth.register(data)
      
      // Opcionalmente autoautenticar
      if (response.tokens) {
        tokens.value = response.tokens
        setAuthTokens(response.tokens)
        localStorage.setItem('authTokens', JSON.stringify(response.tokens))
        localStorage.setItem('accessToken', response.tokens.accessToken)
        localStorage.setItem('refreshToken', response.tokens.refreshToken)
        isAuthenticated.value = true
        await fetchMe()
      }

      return response.user
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al registrarse'
      error.value = message
      console.error('Error en register:', err)
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
      console.error('Error al obtener datos del usuario:', err)
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
      console.error('Error al refrescar token:', err)
      clearSession()
      throw err
    }
  }

  /**
   * Actualiza el perfil del usuario autenticado
   * 
   * @param data - Datos a actualizar {fullName?, email?, phone?, avatar?}
   * @returns Promise<User> - Usuario actualizado
   */
  const updateProfile = async (data: Partial<User>): Promise<User> => {
    isLoading.value = true
    error.value = null

    try {
      const updated = await api.auth.updateProfile(data)
      user.value = updated
      return updated
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al actualizar perfil'
      error.value = message
      console.error('Error en updateProfile:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Cambia la contraseña del usuario autenticado
   * 
   * @param oldPassword - Contraseña actual
   * @param newPassword - Nueva contraseña
   * @returns Promise<void>
   */
  const changePassword = async (oldPassword: string, newPassword: string): Promise<void> => {
    isLoading.value = true
    error.value = null

    try {
      await api.auth.changePassword({ oldPassword, newPassword })
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al cambiar contraseña'
      error.value = message
      console.error('Error en changePassword:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Cierra la sesión del usuario
   * 
   * Flujo:
   * 1. Llama a api.auth.logout para invalidar sesión en servidor
   * 2. Limpia todos los datos locales
   * 3. Elimina tokens de localStorage
   * 4. Redirige a página de login (manejado por router)
   */
  const logout = async (): Promise<void> => {
    try {
      // Intentar notificar al servidor
      await api.auth.logout()
    } catch (err) {
      console.error('Error al notificar logout al servidor:', err)
      // Continuar con limpieza local incluso si falla
    } finally {
      clearSession()
    }
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

  /**
   * Solicita reset de contraseña por email
   * 
   * @param email - Email del usuario
   * @returns Promise<void>
   */
  const requestPasswordReset = async (email: string): Promise<void> => {
    isLoading.value = true
    error.value = null

    try {
      await api.auth.requestPasswordReset({ email })
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al solicitar reset de contraseña'
      error.value = message
      console.error('Error en requestPasswordReset:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Confirma el reset de contraseña con token
   * 
   * @param token - Token recibido en email
   * @param newPassword - Nueva contraseña
   * @returns Promise<void>
   */
  const confirmPasswordReset = async (token: string, newPassword: string): Promise<void> => {
    isLoading.value = true
    error.value = null

    try {
      await api.auth.confirmPasswordReset({ token, newPassword })
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al confirmar reset de contraseña'
      error.value = message
      console.error('Error en confirmPasswordReset:', err)
      throw err
    } finally {
      isLoading.value = false
    }
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
    isTokenExpiringSoon,
    // Acciones
    initialize,
    login,
    register,
    fetchMe,
    refreshToken,
    updateProfile,
    changePassword,
    logout,
    clearSession,
    requestPasswordReset,
    confirmPasswordReset,
  }
})
