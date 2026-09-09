/**
 * Store de Autenticación - CoreStream
 * Gestiona la sesión, usuario actual y permisos RBAC
 *
 * Responsabilidades:
 * - Autenticación (login, logout)
 * - Gestión del access token (en memoria, nunca en localStorage)
 * - Control de acceso basado en roles
 * - Conexión/desconexión del WebSocket de notificaciones en tiempo real
 *
 * El registro público se eliminó (plan 3.7): las cuentas se crean por
 * invitación, ver stores/team.ts (inviteMember) y views/InvitationAcceptView.vue.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { UserRole, type User, type AuthTokens } from '@/types'
import { api, setAuthTokens, clearAuthTokens } from '@/services/api'
import { useThemeStore } from '@/stores/theme'
import { useWebSocket } from '@/composables/useWebSocket'

export const useAuthStore = defineStore('auth', () => {
  // ========== ESTADO REACTIVO ==========

  const user = ref<User | null>(null)

  /**
   * Access token JWT. Vive solo en memoria — nunca en localStorage — para
   * que un XSS no pueda robar una sesión completa (antes tanto access como
   * refresh token estaban en localStorage; el refresh de 7 días era el
   * premio gordo). El refresh token ya no es visible aquí en absoluto: vive
   * en una cookie HttpOnly que solo el navegador puede adjuntar.
   */
  const accessToken = ref<string | null>(null)

  const isAuthenticated = ref(false)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // ========== GETTERS COMPUTADOS ==========

  const isAdmin = computed(() => user.value?.role === 'ADMIN')
  const isDeveloper = computed(() => user.value?.role === 'DEVELOPER')
  const isTeamLeader = computed(() => user.value?.role === 'TEAM_LEADER')
  const userRole = computed((): UserRole | undefined => user.value?.role)
  const fullName = computed(() => user.value?.fullName ?? '')
  const userEmail = computed(() => user.value?.email ?? '')
  const mustChangePassword = computed(() => user.value?.mustChangePassword ?? false)

  // ========== WEBSOCKET DE NOTIFICACIONES ==========

  /**
   * Conecta el WebSocket para el usuario actual. Requiere haber llamado
   * primero a fetchMe() (necesita user.value.id).
   *
   * No es crítico: si falla (p. ej. el backend no puede emitir un ticket),
   * solo se pierden las notificaciones en tiempo real, no la sesión.
   */
  const connectRealtime = (): void => {
    if (!user.value) return
    try {
      useWebSocket().connect(user.value.id)
    } catch (err) {
      console.error('No se pudo conectar el WebSocket de notificaciones:', err)
    }
  }

  const disconnectRealtime = (): void => {
    try {
      useWebSocket().disconnect()
    } catch {
      /* no-op */
    }
  }

  // ========== ACCIONES ==========

  /**
   * Restaura la sesión al cargar la aplicación.
   *
   * Como el access token vive solo en memoria, se pierde en cada recarga de
   * página. Para restaurarlo sin pedir credenciales de nuevo, se llama a
   * /auth/refresh sin argumentos: el navegador adjunta la cookie httpOnly
   * del refresh token solo. Si no hay cookie válida (primera visita, o
   * sesión expirada), esto falla con 401 y el caller (App.vue) redirige a
   * login — es el comportamiento esperado, no un error real.
   */
  const initialize = async (): Promise<void> => {
    try {
      const tokens = await api.auth.refresh()
      applyTokens(tokens)
      isAuthenticated.value = true
      await fetchMe()
      connectRealtime()
    } catch (err) {
      clearSession()
      throw err
    }
  }

  /**
   * Memoiza el intento de inicialización para que tanto App.vue (al montar)
   * como el guard del router (en la primera navegación) puedan esperarlo
   * sin disparar dos /auth/refresh en paralelo.
   *
   * Por qué hace falta esto: antes el guard leía accessToken de localStorage
   * — disponible de forma sincrónica en cuanto carga la página. Ahora el
   * access token vive solo en memoria y se restaura de forma asíncrona
   * (initialize(), arriba). En la primera navegación tras una recarga de
   * página, el guard puede ejecutarse ANTES de que App.vue monte y llame a
   * initialize() — por eso el propio guard debe poder dispararlo, no solo
   * esperarlo.
   */
  let initPromise: Promise<void> | null = null
  const ensureInitialized = (): Promise<void> => {
    if (!initPromise) {
      initPromise = initialize().catch(() => {
        /* sin sesión previa: estado normal, no un error a propagar aquí */
      })
    }
    return initPromise
  }

  /**
   * Autentica al usuario con email y contraseña.
   */
  const login = async (email: string, password: string): Promise<User> => {
    isLoading.value = true
    error.value = null

    try {
      const response = await api.auth.login({ email, password })
      applyTokens(response.tokens)
      isAuthenticated.value = true

      await fetchMe()
      connectRealtime()

      return user.value!
    } catch (err) {
      const message = (err as any)?.response?.data?.detail
        || (err as any)?.response?.data?.message
        || (err instanceof Error ? err.message : 'Error al iniciar sesión')
      clearSession()
      error.value = message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Aplica un AuthTokens recién recibido: guarda el access token en memoria
   * y lo registra en el cliente HTTP para que vaya como Bearer.
   */
  const applyTokens = (tokens: AuthTokens): void => {
    accessToken.value = tokens.accessToken
    setAuthTokens(tokens)
  }

  /**
   * Obtiene los datos del usuario autenticado.
   */
  const fetchMe = async (): Promise<User> => {
    try {
      const userData = await api.auth.getMe()
      user.value = userData

      const savedTheme = userData.preferences?.theme
      if (savedTheme === 'light' || savedTheme === 'dark') {
        useThemeStore().applyTheme(savedTheme)
      }

      return userData
    } catch (err) {
      clearSession()
      throw err
    }
  }

  /**
   * Refresca el access token. El refresh token va por cookie httpOnly, no
   * hace falta pasarlo — a diferencia de antes, donde vivía en el store.
   */
  const refreshToken = async (): Promise<AuthTokens> => {
    try {
      const newTokens = await api.auth.refresh()
      applyTokens(newTokens)
      return newTokens
    } catch (err) {
      clearSession()
      throw err
    }
  }

  /**
   * Actualiza el perfil del usuario autenticado.
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
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Cambia la contraseña del usuario autenticado. Al completarse, el
   * backend limpia must_change_password — se refleja pidiendo el perfil
   * de nuevo para que la UI deje de exigir el cambio forzado.
   */
  const changePassword = async (oldPassword: string, newPassword: string): Promise<void> => {
    isLoading.value = true
    error.value = null

    try {
      await api.auth.changePassword({ oldPassword, newPassword })
      await fetchMe()
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al cambiar contraseña'
      error.value = message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Cierra la sesión del usuario.
   *
   * Antes /auth/logout no existía (404) y esto solo borraba localStorage;
   * el access token seguía siendo válido hasta expirar por su cuenta. Ahora
   * el backend revoca de verdad access y refresh token (plan 3.3).
   */
  const logout = async (): Promise<void> => {
    try {
      await api.auth.logout()
    } catch (err) {
      console.error('Error al notificar logout al servidor:', err)
    } finally {
      clearSession()
    }
  }

  /**
   * Limpia toda la información de sesión en memoria.
   */
  const clearSession = (): void => {
    disconnectRealtime()
    user.value = null
    accessToken.value = null
    isAuthenticated.value = false
    error.value = null
    clearAuthTokens()
  }

  const requestPasswordReset = async (email: string): Promise<void> => {
    isLoading.value = true
    error.value = null
    try {
      await api.auth.requestPasswordReset({ email })
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al solicitar reset de contraseña'
      error.value = message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const confirmPasswordReset = async (token: string, newPassword: string): Promise<void> => {
    isLoading.value = true
    error.value = null
    try {
      await api.auth.confirmPasswordReset({ token, newPassword })
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al confirmar reset de contraseña'
      error.value = message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    // Estado
    user,
    accessToken,
    isAuthenticated,
    isLoading,
    error,
    // Getters
    isAdmin,
    isDeveloper,
    isTeamLeader,
    userRole,
    fullName,
    userEmail,
    mustChangePassword,
    // Acciones
    initialize,
    ensureInitialized,
    login,
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
