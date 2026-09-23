/**
 * Servicio de API para CoreStream
 * 
 * Centraliza toda la comunicación con el backend de FastAPI.
 * Proporciona:
 * - Instancia de Axios configurada con base URL, headers por defecto, etc.
 * - Interceptores para manejo automático de tokens JWT y renovación
 * - Métodos tipados para cada endpoint del API
 * - Manejo de errores consistente
 * 
 * Todas las llamadas al API deben ir a través de este servicio.
 */

import axios, { AxiosInstance, AxiosError, AxiosResponse } from 'axios'
import { UserRole } from '@/types'
import type {
  User,
  Application,
  Epic,
  Ticket,
  Subtask,
  TicketStatus,
  TicketPriority,
  Notification,
  Document,
  AnalyticsSummary,
  AuthTokens,
  ApiResponse,
  AuthResponse,
  LoginRequest,
  RegisterRequest,
  TicketFilters,
  PaginatedResponse,
  UserPerformance,
  HeatmapData,
  BurndownData
} from '@/types'

/**
 * Interfaz para estado de autenticación
 * Se utiliza en el store de Pinia para mantener tokens
 */
interface AuthState {
  accessToken: string | null
  refreshToken: string | null
}

/**
 * Variable global para almacenar tokens
 * En una aplicación real, esto vendría del store de Pinia
 * Aquí se mantiene por simplicidad
 */
/**
 * Claves de localStorage usadas por la sesión.
 *
 * El backend (routers/auth.py) devuelve los tokens en snake_case PLANO
 * (`{ access_token, refresh_token, token_type }`), sin envoltorio
 * `{ success, data }` ni anidado `{ tokens }`. Además, el guard del router
 * (src/router/index.ts) y App.vue leen `accessToken`/`refreshToken` como
 * claves sueltas. Antes NADA escribía esas claves: solo se guardaba
 * `authTokens`, así que tras cualquier recarga la sesión se perdía y las
 * peticiones salían sin cabecera Authorization -> FastAPI respondía
 * 403 "Not authenticated" (HTTPBearer) en /api/applications/, /api/epics/, etc.
 */
const AUTH_TOKENS_KEY = 'authTokens'
const ACCESS_TOKEN_KEY = 'accessToken'
const REFRESH_TOKEN_KEY = 'refreshToken'

/**
 * Normaliza el rol que devuelve el backend para que coincida con los
 * valores que espera el frontend (ADMIN, TEAM_LEADER, GROUP_LEADER, DEVELOPER).
 */
const normalizeRole = (role: unknown): UserRole => {
  const value = String(role ?? '').toUpperCase()
  // El backend puede llamar TEAM_LEADER a lo que el frontend llama GROUP_LEADER.
  if (value === 'TEAM_LEADER') return UserRole.GROUP_LEADER
  if (value === 'GROUP_LEADER') return UserRole.GROUP_LEADER
  if (value === 'ADMIN') return UserRole.ADMIN
  return UserRole.DEVELOPER
}

/**
 * Normaliza la respuesta de usuario del backend (snake_case plano) al tipo
 * `User` que usa el frontend.
 */
const normalizeUser = (raw: any): User => {
  const source = raw?.data ?? raw ?? {}
  return {
    ...source,
    id: source.id,
    email: source.email,
    fullName: source.fullName ?? source.full_name ?? '',
    specialty: source.specialty ?? undefined,
    role: normalizeRole(source.role),
    avatarUrl: source.avatarUrl ?? source.avatar_url ?? undefined,
    isActive: source.isActive ?? source.is_active ?? true,
    createdAt: source.createdAt ?? source.created_at ?? undefined,
    updatedAt: source.updatedAt ?? source.updated_at ?? undefined
  } as User
}

/**
 * Normaliza los tokens del backend a `AuthTokens` (camelCase).
 * Acepta tanto la forma plana snake_case (`access_token`) como camelCase.
 */
const normalizeTokens = (raw: any): AuthTokens => {
  const source = raw?.tokens ?? raw?.data?.tokens ?? raw?.data ?? raw ?? {}
  return {
    accessToken: source.accessToken ?? source.access_token ?? '',
    refreshToken: source.refreshToken ?? source.refresh_token ?? '',
    tokenType: source.tokenType ?? source.token_type ?? 'Bearer',
    expiresIn: source.expiresIn ?? source.expires_in ?? undefined
  }
}

let authState: AuthState = {
  accessToken: null,
  refreshToken: null
}

/**
 * Hidrata el estado de autenticación desde localStorage al cargar el módulo.
 *
 * Sin esto, cualquier recarga de página dejaba `authState` vacío hasta que
 * algo llamase a `setAuthTokens()`, y las peticiones salían sin Bearer.
 */
const hydrateAuthState = (): void => {
  try {
    const stored = localStorage.getItem(AUTH_TOKENS_KEY)
    const parsed = stored ? JSON.parse(stored) : null
    const tokens = normalizeTokens(parsed)

    authState.accessToken =
      tokens.accessToken || localStorage.getItem(ACCESS_TOKEN_KEY) || null
    authState.refreshToken =
      tokens.refreshToken || localStorage.getItem(REFRESH_TOKEN_KEY) || null
  } catch {
    // localStorage no disponible o contenido corrupto: se ignora y se
    // seguirá el flujo normal (login) sin sesión restaurada.
  }
}

hydrateAuthState()

/**
 * Crea y configura la instancia de Axios
 * 
 * Configuración:
 * - Base URL: /api (se usa proxy de Vite para redirigir a localhost:8000)
 * - Timeout: 30 segundos
 * - Headers por defecto: Content-Type application/json
 * 
 * @returns Instancia de Axios configurada
 */
/**
 * ADAPTADOR camelCase <-> snake_case (WEB-08)
 *
 * El frontend trabaja con claves camelCase (epicId, dueDate, prLink...)
 * y el backend FastAPI con snake_case (epic_id, due_date, pr_link...).
 * Los interceptores de abajo aplican estas conversiones SOLO a los
 * módulos de épicas/tickets/aplicaciones/subtareas, dejando intacto
 * el resto (por ejemplo /auth) para no romper flujos existentes.
 */
const CONVERTIBLE_URL_RE = /\/(tickets|epics|applications|subtasks)(\/|\?|$)/

const shouldConvertCase = (url?: string): boolean =>
  !!url && CONVERTIBLE_URL_RE.test(url)

/** Convierte una clave snake_case a camelCase ('due_date' -> 'dueDate') */
const toCamelKey = (key: string): string =>
  key.replace(/_([a-z0-9])/g, (_, c: string) => c.toUpperCase())

/** Convierte una clave camelCase a snake_case ('dueDate' -> 'due_date') */
const toSnakeKey = (key: string): string =>
  key.replace(/[A-Z0-9]/g, (c) => '_' + c.toLowerCase())

/** Transforma recursivamente todas las claves de un objeto/array */
const deepMapKeys = (value: any, mapper: (key: string) => string): any => {
  if (Array.isArray(value)) {
    return value.map((item) => deepMapKeys(item, mapper))
  }
  if (value !== null && typeof value === 'object') {
    const result: Record<string, any> = {}
    for (const [key, val] of Object.entries(value)) {
      result[mapper(key)] = deepMapKeys(val, mapper)
    }
    return result
  }
  return value
}

const snakeToCamelDeep = (value: any): any => deepMapKeys(value, toCamelKey)
const camelToSnakeDeep = (value: any): any => deepMapKeys(value, toSnakeKey)

const createApiClient = (): AxiosInstance => {
  const instance = axios.create({
    /**
     * Base URL para todas las solicitudes
     * Las URLs relativas se combinarán con esta base
     * El proxy de Vite redirigirá /api a http://localhost:8000
     */
    baseURL: '/api',

    /**
     * Timeout en milisegundos para todas las solicitudes
     */
    timeout: 30000,

    /**
     * Headers por defecto para todas las solicitudes
     */
    headers: {
      /**
       * Content-Type: especifica que estamos enviando JSON
       */
      'Content-Type': 'application/json'
    }
  })

  /**
   * INTERCEPTOR DE REQUEST
   * 
   * Se ejecuta antes de que se envíe cada solicitud.
   * Aquí agregamos el token JWT en el header Authorization si existe.
   */
  instance.interceptors.request.use(
    (config) => {
      /**
       * Si existe un token de acceso, lo agregamos al header Authorization
       * Formato: Bearer <token>
       */
      if (authState.accessToken) {
        config.headers.Authorization = `Bearer ${authState.accessToken}`
      }

      return config
    },

    /**
     * En caso de error en la preparación de la solicitud
     */
    (error) => {
      return Promise.reject(error)
    }
  )

  /**
   * INTERCEPTOR DE REQUEST (WEB-08): payload camelCase -> snake_case
   *
   * Solo para las rutas de épicas/tickets/aplicaciones/subtareas, que son
   * los módulos alineados al backend FastAPI (que espera snake_case).
   */
  instance.interceptors.request.use((config) => {
    if (!shouldConvertCase(config.url)) return config

    if (config.data !== undefined && config.data !== null) {
      config.data = camelToSnakeDeep(config.data)
    }
    if (config.params !== undefined && config.params !== null) {
      config.params = camelToSnakeDeep(config.params)
    }
    return config
  })

  /**
   * INTERCEPTOR DE RESPONSE
   * 
   * Se ejecuta cuando se recibe una respuesta.
   * Maneja:
   * - Errores 401 (Unauthorized): intenta renovar el token
   * - Otros errores: propaga el error
   */
  instance.interceptors.response.use(
    /**
     * Respuesta exitosa: retorna tal cual
     */
    (response) => {
      /**
       * WEB-08: respuesta snake_case -> camelCase para los módulos
       * alineados (épicas, tickets, aplicaciones, subtareas). El resto
       * de módulos se deja tal cual para no romper flujos existentes.
       */
      if (
        response.data !== undefined &&
        response.data !== null &&
        shouldConvertCase(response.config?.url)
      ) {
        response.data = snakeToCamelDeep(response.data)
      }
      return response
    },

    /**
     * Respuesta con error
     * Principalmente maneja tokens expirados
     */
    async (error: AxiosError) => {
      /**
       * Obtiene la solicitud original que falló
       * Se puede usar para reintentar
       */
      const originalRequest = error.config as any

      /**
       * Si el error es 401 (Unauthorized) y no hemos intentado renovar ya
       * (para evitar loops infinitos)
       */
      if (error.response?.status === 401 && !originalRequest._retry) {
        /**
         * Marca que ya hemos intentado renovar este request
         */
        originalRequest._retry = true

        /**
         * Intenta renovar el token usando el refresh token
         */
        if (authState.refreshToken) {
          try {
            /**
             * Solicitud especial para renovar el token
             * Usa directamente axios (no la instancia con interceptores)
             * para evitar recursión infinita.
             *
             * El backend espera `{ refresh_token }` y responde plano
             * (`{ access_token, refresh_token, token_type }`).
             */
            const response = await axios.post('/api/auth/refresh', {
              refresh_token: authState.refreshToken
            })

            const newTokens = normalizeTokens(response.data)

            if (newTokens.accessToken) {
              /**
               * Guarda los tokens normalizados (persiste en localStorage y
               * actualiza el estado del interceptor).
               */
              setAuthTokens(newTokens)

              /**
               * Actualiza el header Authorization del request original
               */
              originalRequest.headers.Authorization = `Bearer ${newTokens.accessToken}`

              /**
               * Reintenta el request original con el nuevo token
               */
              return instance(originalRequest)
            }
          } catch (refreshError) {
            /**
             * Si la renovación falla (refresh token expirado),
             * limpia los tokens y rechaza la promesa
             * El usuario será redirigido a login
             */
            authState.accessToken = null
            authState.refreshToken = null

            return Promise.reject(refreshError)
          }
        } else {
          /**
           * No hay refresh token disponible
           * Limpia tokens y rechaza
           */
          authState.accessToken = null
          authState.refreshToken = null
        }
      }

      /**
       * Propaga el error para que sea manejado por quien llamó
       */
      return Promise.reject(error)
    }
  )

  return instance
}

/**
 * Instancia de Axios lista para usar
 */
const apiClient = createApiClient()

/**
 * OBJETO API
 * 
 * Contiene todos los métodos para comunicarse con el backend.
 * Los métodos están organizados por dominio (auth, users, applications, etc.)
 * para mantener orden y facilitar el mantenimiento.
 * 
 * Todos los métodos retornan Promesas tipadas con tipos de TypeScript.
 */
export const api = {
  /**
   * ========================================
   * MÓDULO DE AUTENTICACIÓN
   * ========================================
   * 
   * Maneja login, registro, tokens y sesión del usuario
   */
  auth: {
    /**
     * Autentica un usuario con correo y contraseña
     * 
     * @param credentials - Email y contraseña del usuario
     * @returns Respuesta con usuario y tokens de autenticación
     * 
     * @example
     * const response = await api.auth.login({ email: 'user@example.com', password: '123456' })
     * // Guarda tokens en el store y redirige al dashboard
     */
    login: async (credentials: LoginRequest): Promise<{ tokens: AuthTokens; user?: User }> => {
      /**
       * El backend responde `{ access_token, refresh_token, token_type }`
       * (snake_case plano, sin envoltorio). Se normaliza a camelCase y se
       * deja activo en el interceptor para que el resto de peticiones
       * (applications, epics, tickets) viajen con Authorization: Bearer.
       */
      const response = await apiClient.post('/auth/login', credentials)
      const tokens = normalizeTokens(response.data)

      if (!tokens.accessToken) {
        throw new Error('El servidor no devolvió un access token válido')
      }

      setAuthTokens(tokens)
      return { tokens }
    },

    /**
     * Registra un nuevo usuario en el sistema
     * 
     * @param data - Datos del nuevo usuario (email, password, nombre, rol)
     * @returns Respuesta con usuario creado y tokens de autenticación
     */
    register: async (data: RegisterRequest): Promise<{ tokens?: AuthTokens; user: User }> => {
      /**
       * El backend devuelve el usuario creado (snake_case plano) y NO inicia
       * sesión, así que aquí solo se normaliza el usuario.
       */
      const response = await apiClient.post('/auth/register', data)
      return { user: normalizeUser(response.data) }
    },

    /**
     * Renueva el token de acceso usando el refresh token
     * Se llama automáticamente desde el interceptor cuando el token expira
     * 
     * @param refreshToken - Token de renovación
     * @returns Nuevos tokens de autenticación
     */
    refresh: async (refreshToken: string): Promise<AuthTokens> => {
      /**
       * El backend espera `{ refresh_token }` y responde plano
       * `{ access_token, refresh_token, token_type }`.
       */
      const response = await apiClient.post('/auth/refresh', {
        refresh_token: refreshToken
      })
      const tokens = normalizeTokens(response.data)

      // Si el backend no rota el refresh token, se conserva el actual para
      // no dejar la sesión sin forma de renovarse.
      if (!tokens.refreshToken) tokens.refreshToken = refreshToken

      setAuthTokens(tokens)
      return tokens
    },

    /**
     * Obtiene los datos del usuario autenticado actualmente
     * 
     * @returns Objeto usuario con toda la información
     * 
     * @example
     * const currentUser = await api.auth.getMe()
     * // Útil al inicializar la aplicación para verificar si está autenticado
     */
    getMe: async (): Promise<User> => {
      /**
       * El backend devuelve el usuario en snake_case plano
       * (`{ id, email, full_name, role, ... }`), sin envoltorio ApiResponse.
       */
      const response = await apiClient.get('/auth/me')
      return normalizeUser(response.data)
    },

    /**
     * Alias de `getMe` — el store de auth (`stores/auth.ts`) llama
     * `api.auth.me()`. Sin este alias el método era `undefined` y el login
     * fallaba con TypeError justo después de autenticar.
     */
    me: async (): Promise<User> => {
      return api.auth.getMe()
    },

    /**
     * Actualiza los datos del usuario autenticado
     * 
     * @param data - Campos a actualizar (nombre, especialidad, avatar, etc.)
     * @returns Usuario actualizado
     * 
     * @example
     * await api.auth.updateMe({ fullName: 'Nuevo Nombre', specialty: 'Backend' })
     */
    updateMe: async (data: Partial<User>): Promise<ApiResponse<User>> => {
      const response = await apiClient.put<ApiResponse<User>>(
        '/auth/me',
        data
      )
      return response.data
    },

    /**
     * Cierra sesión y invalida los tokens
     * Debería llamarse antes de limpiar los tokens en el cliente
     */
    logout: async (): Promise<ApiResponse<void>> => {
      const response = await apiClient.post<ApiResponse<void>>('/auth/logout')
      return response.data
    }
  },

  /**
   * ========================================
   * MÓDULO DE USUARIOS
   * ========================================
   * 
   * Gestión de usuarios del sistema (solo para administradores)
   */
  users: {
    /**
     * Obtiene lista de todos los usuarios del sistema
     * 
     * @param filters - Filtros opcionales (página, límite, rol, búsqueda)
     * @returns Array paginado de usuarios
     * 
     * @example
     * const { items: usuarios } = await api.users.list({ limit: 20, page: 1 })
     */
    list: async (filters?: {
      page?: number
      limit?: number
      role?: UserRole
      search?: string
    }): Promise<ApiResponse<PaginatedResponse<User>>> => {
      const response = await apiClient.get<ApiResponse<PaginatedResponse<User>>>(
        '/users',
        { params: filters }
      )
      return response.data
    },

    /**
     * Obtiene los detalles de un usuario específico
     * 
     * @param userId - ID del usuario
     * @returns Objeto usuario
     */
    getById: async (userId: string): Promise<ApiResponse<User>> => {
      const response = await apiClient.get<ApiResponse<User>>(`/users/${userId}`)
      return response.data
    },

    /**
     * Actualiza un usuario existente
     * Solo administradores pueden actualizar otros usuarios
     * 
     * @param userId - ID del usuario
     * @param data - Campos a actualizar
     * @returns Usuario actualizado
     */
    update: async (userId: string, data: Partial<User>): Promise<ApiResponse<User>> => {
      const response = await apiClient.put<ApiResponse<User>>(
        `/users/${userId}`,
        data
      )
      return response.data
    },

    /**
     * Elimina (desactiva) un usuario del sistema
     * 
     * @param userId - ID del usuario a eliminar
     */
    delete: async (userId: string): Promise<ApiResponse<void>> => {
      const response = await apiClient.delete<ApiResponse<void>>(`/users/${userId}`)
      return response.data
    },

    /**
     * Cambia el rol de un usuario
     * Solo administradores pueden cambiar roles
     * 
     * @param userId - ID del usuario
     * @param newRole - Nuevo rol (ADMIN, GROUP_LEADER, DEVELOPER)
     * @returns Usuario con rol actualizado
     */
    changeRole: async (userId: string, newRole: UserRole): Promise<ApiResponse<User>> => {
      const response = await apiClient.post<ApiResponse<User>>(
        `/users/${userId}/change-role`,
        { role: newRole }
      )
      return response.data
    },

    /**
     * Obtiene estadísticas de rendimiento de un usuario
     * 
     * @param userId - ID del usuario
     * @returns Métricas de rendimiento
     */
    getStats: async (userId: string): Promise<ApiResponse<UserPerformance>> => {
      const response = await apiClient.get<ApiResponse<UserPerformance>>(
        `/users/${userId}/stats`
      )
      return response.data
    }
  },

  /**
   * ========================================
   * MÓDULO DE APLICACIONES
   * ========================================
   * 
   * CRUD de aplicaciones (proyectos)
   */
  applications: {
    /**
     * Obtiene lista de todas las aplicaciones
     * 
     * @param filters - Filtros opcionales
     * @returns Array de aplicaciones
     * 
     * @example
     * const aplicaciones = await api.applications.list()
     */
    list: async (filters?: {
      page?: number
      limit?: number
    }): Promise<ApiResponse<PaginatedResponse<Application>>> => {
      const response = await apiClient.get<ApiResponse<PaginatedResponse<Application>>>(
        '/applications/',
        { params: filters }
      )
      return response.data
    },

    /**
     * Crea una nueva aplicación
     * 
     * @param data - Datos de la nueva aplicación
     * @returns Aplicación creada
     * 
     * @example
     * const app = await api.applications.create({
     *   name: 'Mi Aplicación',
     *   description: 'Descripción...',
     *   color: '#2563EB',
     *   icon: 'star'
     * })
     */
    create: async (data: Omit<Application, 'id' | 'createdAt' | 'updatedAt' | 'ticketCount' | 'epicCount' | 'pendingCount' | 'delayedCount'>): Promise<ApiResponse<Application>> => {
      const response = await apiClient.post<ApiResponse<Application>>(
        '/applications/',
        data
      )
      return response.data
    },

    /**
     * Obtiene detalles de una aplicación específica
     * 
     * @param appId - ID de la aplicación
     * @returns Aplicación con todos sus detalles
     */
    getById: async (appId: string): Promise<ApiResponse<Application>> => {
      const response = await apiClient.get<ApiResponse<Application>>(
        `/applications/${appId}`
      )
      return response.data
    },

    /**
     * Actualiza una aplicación existente
     * 
     * @param appId - ID de la aplicación
     * @param data - Campos a actualizar
     * @returns Aplicación actualizada
     */
    update: async (appId: string, data: Partial<Application>): Promise<ApiResponse<Application>> => {
      const response = await apiClient.put<ApiResponse<Application>>(
        `/applications/${appId}`,
        data
      )
      return response.data
    },

    /**
     * Elimina una aplicación
     * 
     * @param appId - ID de la aplicación
     */
    delete: async (appId: string): Promise<ApiResponse<void>> => {
      const response = await apiClient.delete<ApiResponse<void>>(
        `/applications/${appId}`
      )
      return response.data
    }
  },

  /**
   * ========================================
   * MÓDULO DE ÉPICAS
   * ========================================
   * 
   * CRUD de épicas dentro de aplicaciones
   */
  epics: {
    /**
     * Alias compatible con el código legacy del frontend.
     * Algunas vistas llaman a `listByApplication` en lugar de `list`.
     */
    listByApplication: async (appId: string, filters?: {
      page?: number
      limit?: number
    }): Promise<ApiResponse<PaginatedResponse<Epic>>> => {
      const listFn = typeof api.epics?.list === 'function' ? api.epics.list : null
      if (!listFn) {
        throw new Error('La API de épicas no tiene el método list disponible')
      }
      return listFn(appId, filters)
    },

    /**
     * Obtiene lista de épicas de una aplicación
     * 
     * @param appId - ID de la aplicación
     * @param filters - Filtros opcionales
     * @returns Array de épicas
     * 
     * @example
     * const epicas = await api.epics.list('app-123')
     */
    list: async (appId: string, filters?: {
      page?: number
      limit?: number
    }): Promise<ApiResponse<PaginatedResponse<Epic>>> => {
      const response = await apiClient.get<ApiResponse<PaginatedResponse<Epic>>>(
        `/epics/by-app/${appId}`,
        { params: filters }
      )
      return response.data
    },

    /**
     * Crea una nueva épica
     * 
     * @param appId - ID de la aplicación
     * @param data - Datos de la nueva épica
     * @returns Épica creada
     */
    create: async (appId: string, data: Omit<Epic, 'id' | 'createdAt' | 'updatedAt' | 'applicationId' | 'progress' | 'totalTickets' | 'completedTickets'>): Promise<ApiResponse<Epic>> => {
      const response = await apiClient.post<ApiResponse<Epic>>(
        '/epics/',
        { ...data, applicationId: appId }
      )
      return response.data
    },

    /**
     * Obtiene detalles de una épica específica
     * 
     * @param appId - ID de la aplicación
     * @param epicId - ID de la épica
     * @returns Épica con sus tareas asociadas
     */
    getById: async (appId: string, epicId: string): Promise<ApiResponse<Epic>> => {
      const response = await apiClient.get<ApiResponse<Epic>>(
        `/epics/${epicId}`
      )
      return response.data
    },

    /**
     * Actualiza una épica existente
     * 
     * @param epicId - ID de la épica
     * @param data - Campos a actualizar
     * @returns Épica actualizada
     */
    update: async (epicId: string, data: Partial<Epic>): Promise<ApiResponse<Epic>> => {
      const response = await apiClient.put<ApiResponse<Epic>>(
        `/epics/${epicId}`,
        data
      )
      return response.data
    },

    /**
     * Elimina una épica
     * 
     * @param epicId - ID de la épica
     */
    delete: async (epicId: string): Promise<ApiResponse<void>> => {
      const response = await apiClient.delete<ApiResponse<void>>(
        `/epics/${epicId}`
      )
      return response.data
    },

    /**
     * Reordena una épica dentro de la aplicación
     * Se utiliza con drag & drop
     */
    reorder: async (data: { epicId: string; newIndex: number }): Promise<ApiResponse<Epic>> => {
      const response = await apiClient.patch<ApiResponse<Epic>>(
        `/epics/${data.epicId}/reorder`,
        { new_index: data.newIndex }
      )
      return response.data
    },

    /**
     * Carga un documento asociado a una épica
     * 
     * @param appId - ID de la aplicación
     * @param epicId - ID de la épica
     * @param file - Archivo a cargar
     * @returns Documento creado
     */
    uploadDoc: async (appId: string, epicId: string, file: File): Promise<ApiResponse<Document>> => {
      const formData = new FormData()
      formData.append('file', file)

      const response = await apiClient.post<ApiResponse<Document>>(
        `/epics/${epicId}/documents`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      )
      return response.data
    }
  },

  /**
   * ========================================
   * MÓDULO DE TICKETS
   * ========================================
   * 
   * CRUD de tareas/tickets
   */
  tickets: {
    /**
     * Obtiene lista de tickets con filtros opcionales
     * 
     * @param filters - Filtros para búsqueda y paginación
     * @returns Array paginado de tickets
     * 
     * @example
     * const tickets = await api.tickets.list({
     *   applicationId: 'app-123',
     *   status: 'TODO',
     *   assigneeId: 'user-456'
     * })
     */
    createSubtask: async (ticketId: string, title: string): Promise<ApiResponse<Subtask>> => {
      const response = await apiClient.post<ApiResponse<Subtask>>(
        '/subtasks/',
        { ticket_id: ticketId, title }
      )
      return response.data
    },

    updateSubtask: async (ticketId: string, subtaskId: string, data: Partial<Subtask>): Promise<ApiResponse<Subtask>> => {
      const payload: Record<string, any> = {}
      if ('title' in data && data.title !== undefined) payload.title = data.title
      if ('isCompleted' in data && data.isCompleted !== undefined) payload.is_completed = data.isCompleted
      const response = await apiClient.put<ApiResponse<Subtask>>(
        `/subtasks/${subtaskId}`,
        payload
      )
      return response.data
    },

    deleteSubtask: async (_ticketId: string, subtaskId: string): Promise<ApiResponse<void>> => {
      const response = await apiClient.delete<ApiResponse<void>>(
        `/subtasks/${subtaskId}`
      )
      return response.data
    },

    reorderSubtasks: async (_ticketId: string, subtaskIds: string[]): Promise<ApiResponse<Subtask[]>> => {
      const response = await apiClient.patch<ApiResponse<Subtask[]>>(
        '/subtasks/reorder',
        { subtask_ids: subtaskIds }
      )
      return response.data
    },

    list: async (filters?: TicketFilters): Promise<ApiResponse<PaginatedResponse<Ticket>>> => {
      /**
       * WEB-08: la barra final es OBLIGATORIA.
       *
       * `routers/tickets.py` registra la lista como `@router.get("/")` sobre el
       * prefijo `/api/tickets`, es decir la ruta real es `/api/tickets/`. Si se
       * llama sin la barra, FastAPI/Starlette responde un 307 hacia
       * `/api/tickets/` y, como el proxy de Vite usa `changeOrigin: true`, el
       * `Location` sale con el host interno (`http://backend:8000/...`). El
       * navegador no puede resolver `backend`, así que la petición falla con
       * "DNS Resolution System / Transferred 0 B".
       */
      const response = await apiClient.get<ApiResponse<PaginatedResponse<Ticket>>>(
        '/tickets/',
        { params: filters }
      )
      return response.data
    },

    /**
     * Crea un nuevo ticket
     * 
     * @param data - Datos del nuevo ticket
     * @returns Ticket creado
     */
    create: async (data: Omit<Ticket, 'id' | 'createdAt' | 'updatedAt' | 'createdById'>): Promise<ApiResponse<Ticket>> => {
      /**
       * La barra final es OBLIGATORIA (mismo motivo que en `list`).
       *
       * `routers/tickets.py` expone `POST /api/tickets/`; sin la barra FastAPI
       * devuelve 307 y el navegador termina intentando ir a `backend:8000`
       * (host interno de la red Docker), que no puede resolver -> crear ticket
       * falla. Épicas (`'/epics/'`) y aplicaciones (`'/applications/'`) ya
       * llamaban con barra final, por eso ellas sí funcionaban.
       */
      const response = await apiClient.post<ApiResponse<Ticket>>(
        '/tickets/',
        data
      )
      return response.data
    },

    /**
     * Obtiene detalles de un ticket específico
     * 
     * @param ticketId - ID del ticket
     * @returns Ticket con detalles completos (subtareas, eventos, etc.)
     */
    getById: async (ticketId: string): Promise<ApiResponse<Ticket>> => {
      const response = await apiClient.get<ApiResponse<Ticket>>(
        `/tickets/${ticketId}`
      )
      return response.data
    },

    /**
     * Actualiza un ticket existente
     * 
     * @param ticketId - ID del ticket
     * @param data - Campos a actualizar
     * @returns Ticket actualizado
     */
    update: async (ticketId: string, data: Partial<Ticket>): Promise<ApiResponse<Ticket>> => {
      const response = await apiClient.put<ApiResponse<Ticket>>(
        `/tickets/${ticketId}`,
        data
      )
      return response.data
    },

    /**
     * Elimina un ticket
     * 
     * @param ticketId - ID del ticket
     */
    delete: async (ticketId: string): Promise<ApiResponse<void>> => {
      const response = await apiClient.delete<ApiResponse<void>>(
        `/tickets/${ticketId}`
      )
      return response.data
    },

    /**
     * Mueve un ticket a otra épica
     * Se utiliza con drag & drop entre épicas
     * 
     * @param ticketId - ID del ticket
     * @param newEpicId - ID de la nueva épica
     * @param newOrderIndex - Nuevo índice de orden
     * @returns Ticket actualizado
     */
    move: async (ticketId: string, newEpicId: string): Promise<ApiResponse<Ticket>> => {
      const response = await apiClient.patch<ApiResponse<Ticket>>(
        `/tickets/${ticketId}/move`,
        { epic_id: newEpicId }
      )
      return response.data
    },

    /**
     * Mueve un ticket a otra épica (recibe objeto, usado por el store)
     */
    moveToEpic: async (data: { ticketId: string; newEpicId: string }): Promise<ApiResponse<Ticket>> => {
      return api.tickets.move(data.ticketId, data.newEpicId)
    },

    /**
     * Marca un ticket como completado
     * 
     * @param ticketId - ID del ticket
     * @returns Ticket actualizado
     */
    complete: async (ticketId: string, prLink: string): Promise<ApiResponse<Ticket>> => {
      const response = await apiClient.post<ApiResponse<Ticket>>(
        `/tickets/${ticketId}/complete`,
        { pr_link: prLink }
      )
      return response.data
    },

    /**
     * Plantea una pregunta sobre un ticket (genera evento de pregunta)
     * 
     * @param ticketId - ID del ticket
     * @param question - Texto de la pregunta
     * @returns Evento de pregunta creado
     */
    question: async (ticketId: string, question: string): Promise<ApiResponse<any>> => {
      const response = await apiClient.post<ApiResponse<any>>(
        `/tickets/${ticketId}/question`,
        { question_text: question }
      )
      return response.data
    },

    /**
     * Resuelve una pregunta sobre un ticket
     * 
     * @param ticketId - ID del ticket
     * @param questionId - ID de la pregunta
     * @param answer - Respuesta a la pregunta
     * @returns Evento de resolución
     */
    resolveQuestion: async (ticketId: string, resolution: string = 'Pregunta resuelta'): Promise<ApiResponse<Ticket>> => {
      const response = await apiClient.post<ApiResponse<Ticket>>(
        `/tickets/${ticketId}/resolve-question`,
        { resolution }
      )
      return response.data
    },

    /**
     * Redirige un ticket a otro desarrollador/equipo
     * 
     * @param ticketId - ID del ticket
     * @param newAssigneeId - ID del nuevo asignado
     * @param reason - Razón de la redirección
     * @returns Ticket actualizado
     */
    redirect: async (
      ticketId: string,
      data: { toUserId?: string; targetUserId?: string; reason: string }
    ): Promise<ApiResponse<Ticket>> => {
      const response = await apiClient.post<ApiResponse<Ticket>>(
        `/tickets/${ticketId}/redirect`,
        {
          target_user_id: data.targetUserId ?? data.toUserId,
          reason: data.reason
        }
      )
      return response.data
    },

    /**
     * Marca un ticket como iniciado (cambia estado a IN_PROGRESS)
     * 
     * @param ticketId - ID del ticket
     * @returns Ticket actualizado
     */
    start: async (ticketId: string): Promise<ApiResponse<Ticket>> => {
      const response = await apiClient.post<ApiResponse<Ticket>>(
        `/tickets/${ticketId}/start`
      )
      return response.data
    },

    /**
     * Obtiene el workbench del usuario actual
     * Lista todas sus tareas activas y pendientes
     * 
     * @returns Array de tickets asignados al usuario actual
     */
    getMyWorkbench: async (): Promise<ApiResponse<Ticket[]>> => {
      const response = await apiClient.get<ApiResponse<Ticket[]>>(
        '/tickets/my-workbench'
      )
      return response.data
    },

    /**
     * Lista los tickets de una épica (usado por el store de tickets)
     */
    listByEpic: async (epicId: string, filters?: { status?: string }): Promise<ApiResponse<Ticket[]>> => {
      const response = await apiClient.get<ApiResponse<Ticket[]>>(
        `/tickets/by-epic/${epicId}`,
        { params: filters }
      )
      return response.data
    },

    /**
     * Banco de trabajo del usuario actual (alias de getMyWorkbench)
     */
    listMyWorkbench: async (): Promise<ApiResponse<Ticket[]>> => {
      return api.tickets.getMyWorkbench()
    },

    /**
     * Cambia el estado de un ticket a IN_PROGRESS.
     * El resto de transiciones tiene endpoint propio (complete, question, redirect...)
     */
    updateStatus: async (ticketId: string, newStatus: string): Promise<ApiResponse<Ticket>> => {
      if (newStatus === 'IN_PROGRESS') {
        return api.tickets.start(ticketId)
      }
      throw new Error(
        `Transición de estado no soportada por la API: ${newStatus}. Use complete() o start().`
      )
    },

    /**
     * Plantea una pregunta bloqueante (alias de question, usado por el store)
     */
    raiseQuestion: async (ticketId: string, questionText: string): Promise<ApiResponse<Ticket>> => {
      const response = await apiClient.post<ApiResponse<Ticket>>(
        `/tickets/${ticketId}/question`,
        { question_text: questionText }
      )
      return response.data
    }
  },

  /**
   * ========================================
   * MÓDULO DE SUBTAREAS
   * ========================================
   * 
   * CRUD de subtareas dentro de tickets
   */
  subtasks: {
    /**
     * Crea una nueva subtarea
     * 
     * @param ticketId - ID del ticket padre
     * @param data - Datos de la subtarea
     * @returns Subtarea creada
     */
    create: async (ticketId: string, data: Omit<Subtask, 'id' | 'createdAt'>): Promise<ApiResponse<Subtask>> => {
      const response = await apiClient.post<ApiResponse<Subtask>>(
        `/tickets/${ticketId}/subtasks`,
        data
      )
      return response.data
    },

    /**
     * Actualiza una subtarea
     * 
     * @param ticketId - ID del ticket padre
     * @param subtaskId - ID de la subtarea
     * @param data - Campos a actualizar
     * @returns Subtarea actualizada
     */
    update: async (ticketId: string, subtaskId: string, data: Partial<Subtask>): Promise<ApiResponse<Subtask>> => {
      const response = await apiClient.put<ApiResponse<Subtask>>(
        `/tickets/${ticketId}/subtasks/${subtaskId}`,
        data
      )
      return response.data
    },

    /**
     * Elimina una subtarea
     * 
     * @param ticketId - ID del ticket padre
     * @param subtaskId - ID de la subtarea
     */
    delete: async (ticketId: string, subtaskId: string): Promise<ApiResponse<void>> => {
      const response = await apiClient.delete<ApiResponse<void>>(
        `/tickets/${ticketId}/subtasks/${subtaskId}`
      )
      return response.data
    },

    /**
     * Reordena las subtareas de un ticket
     * 
     * @param ticketId - ID del ticket
     * @param subtaskIds - Array de IDs en el nuevo orden
     * @returns Subtareas reordenadas
     */
    reorder: async (ticketId: string, subtaskIds: string[]): Promise<ApiResponse<Subtask[]>> => {
      const response = await apiClient.post<ApiResponse<Subtask[]>>(
        `/tickets/${ticketId}/subtasks/reorder`,
        { subtaskIds }
      )
      return response.data
    }
  },

  /**
   * ========================================
   * MÓDULO DE ANÁLISIS Y REPORTES
   * ========================================
   * 
   * Obtiene datos agregados para análisis y dashboards
   */
  analytics: {
    /**
     * Obtiene resumen general de analítica
     * Incluye métricas globales, rendimiento del equipo, gráficos
     * 
     * @param filters - Filtros opcionales (rango de fechas, etc.)
     * @returns Resumen de analítica
     */
    getSummary: async (filters?: {
      startDate?: string
      endDate?: string
      applicationId?: string
    }): Promise<ApiResponse<AnalyticsSummary>> => {
      const response = await apiClient.get<ApiResponse<AnalyticsSummary>>(
        '/analytics/summary',
        { params: filters }
      )
      return response.data
    },

    /**
     * Obtiene datos de rendimiento de usuarios
     * 
     * @param filters - Filtros opcionales
     * @returns Array de rendimiento por usuario
     */
    getPerformance: async (filters?: {
      userId?: string
      startDate?: string
      endDate?: string
    }): Promise<ApiResponse<UserPerformance[]>> => {
      const response = await apiClient.get<ApiResponse<UserPerformance[]>>(
        '/analytics/performance',
        { params: filters }
      )
      return response.data
    },

    /**
     * Obtiene datos del mapa de calor (heatmap)
     * Muestra actividad de desarrolladores en el tiempo
     * 
     * @param filters - Filtros opcionales
     * @returns Array de datos de mapa de calor
     */
    getHeatmap: async (filters?: {
      startDate?: string
      endDate?: string
    }): Promise<ApiResponse<HeatmapData[]>> => {
      const response = await apiClient.get<ApiResponse<HeatmapData[]>>(
        '/analytics/heatmap',
        { params: filters }
      )
      return response.data
    },

    /**
     * Obtiene datos del gráfico de quemado (burndown)
     * Muestra progreso de trabajo a lo largo del tiempo
     * 
     * @param applicationId - ID de la aplicación
     * @param filters - Filtros opcionales (rango de fechas)
     * @returns Datos de burndown
     */
    getBurndown: async (applicationId: string, filters?: {
      startDate?: string
      endDate?: string
    }): Promise<ApiResponse<BurndownData>> => {
      const response = await apiClient.get<ApiResponse<BurndownData>>(
        `/analytics/burndown/${applicationId}`,
        { params: filters }
      )
      return response.data
    },

    /**
     * Exporta datos de analítica a CSV
     * 
     * @param filters - Filtros para qué datos exportar
     * @returns Blob con contenido CSV
     */
    exportCsv: async (filters?: {
      applicationId?: string
      startDate?: string
      endDate?: string
    }): Promise<Blob> => {
      const response = await apiClient.get<Blob>(
        '/analytics/export/csv',
        {
          params: filters,
          responseType: 'blob'
        }
      )
      return response.data
    }
  },

  /**
   * ========================================
   * MÓDULO DE DOCUMENTOS
   * ========================================
   * 
   * Gestión de archivos adjuntos
   */
  documents: {
    /**
     * Obtiene lista de documentos de un ticket o épica
     * 
     * @param filters - Filtros para qué documentos obtener
     * @returns Array de documentos
     */
    list: async (filters?: {
      ticketId?: string
      epicId?: string
    }): Promise<ApiResponse<Document[]>> => {
      const response = await apiClient.get<ApiResponse<Document[]>>(
        '/documents',
        { params: filters }
      )
      return response.data
    },

    /**
     * Carga un nuevo documento
     * 
     * @param file - Archivo a cargar
     * @param data - Metadatos del documento (ticketId, epicId, docType, etc.)
     * @returns Documento creado
     */
    upload: async (file: File, data: {
      ticketId?: string
      epicId?: string
      docType?: string
    }): Promise<ApiResponse<Document>> => {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('ticketId', data.ticketId || '')
      formData.append('epicId', data.epicId || '')
      formData.append('docType', data.docType || 'OTHER')

      const response = await apiClient.post<ApiResponse<Document>>(
        '/documents',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      )
      return response.data
    },

    /**
     * Descarga un documento
     * Abre en nueva pestaña o descarga según el navegador
     * 
     * @param documentId - ID del documento
     */
    download: async (documentId: string): Promise<void> => {
      const response = await apiClient.get<Blob>(
        `/documents/${documentId}/download`,
        { responseType: 'blob' }
      )

      // Crea un link temporal para descargar
      const url = window.URL.createObjectURL(response.data)
      const link = document.createElement('a')
      link.href = url
      link.click()
      window.URL.revokeObjectURL(url)
    },

    /**
     * Elimina un documento
     * 
     * @param documentId - ID del documento
     */
    delete: async (documentId: string): Promise<ApiResponse<void>> => {
      const response = await apiClient.delete<ApiResponse<void>>(
        `/documents/${documentId}`
      )
      return response.data
    },

    /**
     * Traduce un documento a otro idioma
     * Usa IA/servicio de traducción del backend
     * 
     * @param documentId - ID del documento
     * @param targetLanguage - Idioma destino (es, en, fr, etc.)
     * @returns Documento traducido
     */
    translate: async (documentId: string, targetLanguage: string): Promise<ApiResponse<Document>> => {
      const response = await apiClient.post<ApiResponse<Document>>(
        `/documents/${documentId}/translate`,
        { targetLanguage }
      )
      return response.data
    }
  },

  /**
   * ========================================
   * MÓDULO DE NOTIFICACIONES
   * ========================================
   * 
   * Sistema de notificaciones del usuario
   */
  notifications: {
    /**
     * Obtiene lista de notificaciones del usuario
     * 
     * @param filters - Filtros opcionales (leídas/no leídas, tipo, etc.)
     * @returns Array de notificaciones
     */
    list: async (filters?: {
      unreadOnly?: boolean
      type?: string
      page?: number
      limit?: number
    }): Promise<ApiResponse<PaginatedResponse<Notification>>> => {
      const response = await apiClient.get<ApiResponse<PaginatedResponse<Notification>>>(
        '/notifications',
        { params: filters }
      )
      return response.data
    },

    /**
     * Obtiene el número de notificaciones no leídas
     * Útil para mostrar un badge en la interfaz
     * 
     * @returns Número de notificaciones no leídas
     */
    getUnreadCount: async (): Promise<ApiResponse<{ count: number }>> => {
      const response = await apiClient.get<ApiResponse<{ count: number }>>(
        '/notifications/unread-count'
      )
      return response.data
    },

    /**
     * Marca una notificación como leída
     * 
     * @param notificationId - ID de la notificación
     * @returns Notificación actualizada
     */
    markRead: async (notificationId: string): Promise<ApiResponse<Notification>> => {
      const response = await apiClient.put<ApiResponse<Notification>>(
        `/notifications/${notificationId}/read`
      )
      return response.data
    },

    /**
     * Marca todas las notificaciones como leídas
     * 
     * @returns Número de notificaciones marcadas
     */
    markAllRead: async (): Promise<ApiResponse<{ markedCount: number }>> => {
      const response = await apiClient.post<ApiResponse<{ markedCount: number }>>(
        '/notifications/mark-all-read'
      )
      return response.data
    }
  }
}

/**
 * Función auxiliar para actualizar el estado de autenticación
 * Debe llamarse desde el store de Pinia cuando el usuario se autentica o renueva sesión
 * 
 * @param tokens - Nuevos tokens de autenticación
 */
export const setAuthTokens = (tokens: AuthTokens): void => {
  authState.accessToken = tokens.accessToken
  authState.refreshToken = tokens.refreshToken

  /**
   * Persistencia: se guarda el objeto completo (`authTokens`) y además las
   * claves sueltas `accessToken` / `refreshToken`, que son las que leen el
   * guard del router (src/router/index.ts) y App.vue. Sin esto, cualquier
   * recarga de página dejaba la SPA sin token y la API respondía 403.
   */
  try {
    localStorage.setItem(AUTH_TOKENS_KEY, JSON.stringify(tokens))
    localStorage.setItem(ACCESS_TOKEN_KEY, tokens.accessToken ?? '')
    localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refreshToken ?? '')
  } catch {
    // Modo privado / almacenamiento no disponible: la sesión seguirá viva
    // en memoria hasta que se recargue la página.
  }
}

/**
 * Función auxiliar para limpiar los tokens
 * Debe llamarse cuando el usuario cierra sesión
 */
export const clearAuthTokens = (): void => {
  authState.accessToken = null
  authState.refreshToken = null

  try {
    localStorage.removeItem(AUTH_TOKENS_KEY)
    localStorage.removeItem(ACCESS_TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
  } catch {
    // Ignorado: no hay nada que limpiar si el almacenamiento no está disponible.
  }
}

/**
 * Exporta la instancia de Axios por si se necesita usar directamente
 */
export default apiClient
