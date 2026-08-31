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
import type {
  User,
  UserRole,
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
let authState: AuthState = {
  accessToken: null,
  refreshToken: null
}

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
    (response) => response,

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
             * para evitar recursión infinita
             */
            const response = await axios.post('/api/auth/refresh', {
              refreshToken: authState.refreshToken
            })

            /**
             * Actualiza los tokens con la respuesta
             */
            if (response.data.data?.tokens) {
              authState.accessToken = response.data.data.tokens.accessToken
              authState.refreshToken = response.data.data.tokens.refreshToken

              /**
               * Actualiza el header Authorization del request original
               */
              originalRequest.headers.Authorization = `Bearer ${authState.accessToken}`

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
    login: async (credentials: LoginRequest): Promise<ApiResponse<AuthResponse>> => {
      const response = await apiClient.post<ApiResponse<AuthResponse>>(
        '/auth/login',
        credentials
      )
      return response.data
    },

    /**
     * Registra un nuevo usuario en el sistema
     * 
     * @param data - Datos del nuevo usuario (email, password, nombre, rol)
     * @returns Respuesta con usuario creado y tokens de autenticación
     */
    register: async (data: RegisterRequest): Promise<ApiResponse<AuthResponse>> => {
      const response = await apiClient.post<ApiResponse<AuthResponse>>(
        '/auth/register',
        data
      )
      return response.data
    },

    /**
     * Renueva el token de acceso usando el refresh token
     * Se llama automáticamente desde el interceptor cuando el token expira
     * 
     * @param refreshToken - Token de renovación
     * @returns Nuevos tokens de autenticación
     */
    refresh: async (refreshToken: string): Promise<ApiResponse<AuthTokens>> => {
      const response = await apiClient.post<ApiResponse<AuthTokens>>(
        '/auth/refresh',
        { refreshToken }
      )
      return response.data
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
    getMe: async (): Promise<ApiResponse<User>> => {
      const response = await apiClient.get<ApiResponse<User>>('/auth/me')
      return response.data
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
        '/applications',
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
        '/applications',
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
        `/applications/${appId}/epics`,
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
        `/applications/${appId}/epics`,
        data
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
        `/applications/${appId}/epics/${epicId}`
      )
      return response.data
    },

    /**
     * Actualiza una épica existente
     * 
     * @param appId - ID de la aplicación
     * @param epicId - ID de la épica
     * @param data - Campos a actualizar
     * @returns Épica actualizada
     */
    update: async (appId: string, epicId: string, data: Partial<Epic>): Promise<ApiResponse<Epic>> => {
      const response = await apiClient.put<ApiResponse<Epic>>(
        `/applications/${appId}/epics/${epicId}`,
        data
      )
      return response.data
    },

    /**
     * Elimina una épica
     * 
     * @param appId - ID de la aplicación
     * @param epicId - ID de la épica
     */
    delete: async (appId: string, epicId: string): Promise<ApiResponse<void>> => {
      const response = await apiClient.delete<ApiResponse<void>>(
        `/applications/${appId}/epics/${epicId}`
      )
      return response.data
    },

    /**
     * Reordena las épicas dentro de una aplicación
     * Se utiliza con drag & drop
     * 
     * @param appId - ID de la aplicación
     * @param epicIds - Array de IDs de épicas en el nuevo orden
     * @returns Épicas reordenadas
     */
    reorder: async (appId: string, epicIds: string[]): Promise<ApiResponse<Epic[]>> => {
      const response = await apiClient.post<ApiResponse<Epic[]>>(
        `/applications/${appId}/epics/reorder`,
        { epicIds }
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
        `/applications/${appId}/epics/${epicId}/documents`,
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
    list: async (filters?: TicketFilters): Promise<ApiResponse<PaginatedResponse<Ticket>>> => {
      const response = await apiClient.get<ApiResponse<PaginatedResponse<Ticket>>>(
        '/tickets',
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
      const response = await apiClient.post<ApiResponse<Ticket>>(
        '/tickets',
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
    move: async (ticketId: string, newEpicId: string, newOrderIndex: number): Promise<ApiResponse<Ticket>> => {
      const response = await apiClient.post<ApiResponse<Ticket>>(
        `/tickets/${ticketId}/move`,
        { epicId: newEpicId, orderIndex: newOrderIndex }
      )
      return response.data
    },

    /**
     * Marca un ticket como completado
     * 
     * @param ticketId - ID del ticket
     * @returns Ticket actualizado
     */
    complete: async (ticketId: string): Promise<ApiResponse<Ticket>> => {
      const response = await apiClient.post<ApiResponse<Ticket>>(
        `/tickets/${ticketId}/complete`
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
        { question }
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
    resolveQuestion: async (ticketId: string, questionId: string, answer: string): Promise<ApiResponse<any>> => {
      const response = await apiClient.post<ApiResponse<any>>(
        `/tickets/${ticketId}/resolve-question`,
        { questionId, answer }
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
    redirect: async (ticketId: string, newAssigneeId: string, reason: string): Promise<ApiResponse<Ticket>> => {
      const response = await apiClient.post<ApiResponse<Ticket>>(
        `/tickets/${ticketId}/redirect`,
        { assigneeId: newAssigneeId, reason }
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
        '/tickets/workbench'
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
}

/**
 * Función auxiliar para limpiar los tokens
 * Debe llamarse cuando el usuario cierra sesión
 */
export const clearAuthTokens = (): void => {
  authState.accessToken = null
  authState.refreshToken = null
}

/**
 * Exporta la instancia de Axios por si se necesita usar directamente
 */
export default apiClient
