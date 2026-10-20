/**
 * Tipos e Interfaces de TypeScript para CoreStream
 * 
 * Este archivo centraliza todas las definiciones de tipos de datos utilizadas
 * en la aplicación. Proporciona autocompletado, validación en tiempo de compilación
 * y documentación clara de las estructuras de datos.
 * 
 * Los tipos están organizados por dominio: usuarios, aplicaciones, tareas, etc.
 */

/**
 * ENUMERACIONES Y TIPOS PRIMITIVOS
 * ================================
 */

/**
 * Roles de usuario en el sistema CoreStream
 * Define los niveles de acceso y permisos disponibles
 */
export enum UserRole {
  /**
   * Administrador del sistema
   * Tiene acceso total a todas las funciones, gestión de usuarios y configuración
   */
  ADMIN = 'ADMIN',

  /**
   * Líder de grupo
   * Puede gestionar miembros del equipo, asignar tareas y ver análisis del equipo
   */
  GROUP_LEADER = 'GROUP_LEADER',

  /**
   * Desarrollador estándar
   * Puede trabajar en tareas asignadas y reportar progreso
   */
  DEVELOPER = 'DEVELOPER'
}

/**
 * Estados posibles de una tarea/ticket en su ciclo de vida
 * Define el flujo de trabajo de gestión de tareas
 */
export enum TicketStatus {
  /**
   * Tarea creada pero no iniciada
   */
  TODO = 'TODO',

  /**
   * Tarea actualmente en desarrollo
   */
  IN_PROGRESS = 'IN_PROGRESS',

  /**
   * Tarea bloqueada por una dependencia o problema
   */
  BLOCKED = 'BLOCKED',

  /**
   * Tarea redirigida a otro desarrollador o equipo
   */
  REDIRECTED = 'REDIRECTED',

  /**
   * Tarea completada satisfactoriamente
   */
  DONE = 'DONE'
}

/**
 * Niveles de prioridad para las tareas
 * Determina el orden de ejecución y la urgencia
 */
export enum TicketPriority {
  /**
   * Baja prioridad: puede ser completada cuando hay tiempo disponible
   */
  LOW = 'LOW',

  /**
   * Prioridad media: debe completarse en el próximo sprint
   */
  MEDIUM = 'MEDIUM',

  /**
   * Alta prioridad: debe completarse pronto
   */
  HIGH = 'HIGH',

  /**
   * Urgente: debe completarse inmediatamente
   */
  URGENT = 'URGENT'
}

/**
 * ENTIDADES DE USUARIO
 * ====================
 */

/**
 * Representa un usuario en el sistema CoreStream
 * Contiene información personal, credenciales y estado del usuario
 */
export interface User {
  /**
   * Identificador único del usuario en la base de datos
   */
  id: string

  /**
   * Correo electrónico del usuario (utilizado para autenticación)
   */
  email: string

  /**
   * Nombre completo del usuario
   */
  fullName: string

  /**
   * Rol del usuario en el sistema (ADMIN, GROUP_LEADER, DEVELOPER)
   */
  role: UserRole

  /**
   * Especialidad o área de enfoque del desarrollador
   * Ejemplos: 'Frontend', 'Backend', 'DevOps', 'QA'
   */
  specialty?: string

  /**
   * URL del avatar/foto de perfil del usuario
   */
  avatarUrl?: string

  /**
   * Indica si el usuario está activo en el sistema
   */
  isActive: boolean

  /**
   * Timestamp de cuando se creó la cuenta
   */
  createdAt?: string

  /**
   * Timestamp de la última actualización
   */
  updatedAt?: string
}

/**
 * Campos que un usuario puede cambiar de su propio perfil (PUT /auth/me).
 * El backend (UserSelfUpdate) no acepta rol, correo ni contraseña.
 */
export interface UserProfileUpdate {
  fullName?: string
  specialty?: string
  avatarUrl?: string
}

/**
 * Datos de rendimiento del usuario
 * Métricas de productividad y eficiencia
 */
export interface UserPerformance {
  /**
   * ID del usuario
   */
  userId: string

  /**
   * Nombre del usuario
   */
  userName: string

  /**
   * Número total de tareas completadas
   */
  completedTickets: number

  /**
   * Promedio de horas dedicadas por tarea
   */
  averageHoursPerTicket: number

  /**
   * Número de tareas actualmente en progreso
   */
  activeTickets: number

  /**
   * Porcentaje de tareas bloqueadas
   */
  blockedPercentage: number

  /**
   * Velocidad promedio (tareas completadas por semana)
   */
  velocity: number

  /**
   * Puntuación general de rendimiento (0-100)
   */
  performanceScore: number
}

/**
 * ENTIDADES DE APLICACIÓN Y ÉPICAS
 * =================================
 */

/**
 * Representa una aplicación/proyecto en CoreStream
 * Es el contenedor de nivel superior que agrupa épicas y tareas
 */
export interface Application {
  /**
   * Identificador único de la aplicación
   */
  id: string

  /**
   * Nombre de la aplicación
   */
  name: string

  /**
   * Descripción detallada de los objetivos de la aplicación
   */
  description: string

  /**
   * Color representativo de la aplicación (en formato hexadecimal o nombre)
   * Utilizado en la interfaz para distinguir visualmente las aplicaciones
   */
  color: string

  /**
   * Ícono de la aplicación (nombre de ícono o URL)
   */
  icon: string

  /**
   * ID del usuario que creó/posee la aplicación
   */
  ownerId: string

  /**
   * Indica si la aplicación está activa
   */
  isActive: boolean

  /**
   * Número total de épicas en la aplicación
   */
  epicCount: number

  /**
   * Número total de tareas/tickets en la aplicación
   */
  ticketCount: number

  /**
   * Número de tareas pendientes (TODO)
   */
  pendingCount: number

  /**
   * Número de tareas retrasadas (pasaron su fecha de vencimiento)
   */
  delayedCount: number

  /**
   * Timestamp de creación
   */
  createdAt?: string

  /**
   * Timestamp de última actualización
   */
  updatedAt?: string
}

/**
 * Payload para crear una aplicación (ApplicationCreate del backend)
 */
export interface ApplicationCreatePayload {
  name: string
  description?: string
  color?: string
  icon?: string
}

/**
 * Representa una épica (conjunto de tareas relacionadas) dentro de una aplicación
 * Las épicas agrupan tareas que contribuyen a un objetivo común
 */
export interface Epic {
  /**
   * Identificador único de la épica
   */
  id: string

  /**
   * Título/nombre de la épica
   */
  title: string

  /**
   * Descripción detallada del objetivo de la épica
   */
  description: string

  /**
   * ID de la aplicación a la que pertenece esta épica
   */
  applicationId: string

  /**
   * Índice de orden visual en la lista de épicas
   * Permite reordenar épicas sin una columna de "orden" adicional
   */
  orderIndex: number

  /**
   * Fecha de vencimiento estimada para la épica
   */
  dueDate?: string

  /**
   * Indica si la épica está colapsada en la interfaz (oculta sus tareas)
   */
  isCollapsed: boolean

  /**
   * Porcentaje de progreso (0-100) basado en tareas completadas
   */
  progress: number

  /**
   * Número total de tareas en la épica
   */
  totalTickets: number

  /**
   * Número de tareas completadas en la épica
   */
  completedTickets: number

  /**
   * Array de tareas asociadas a la épica (cargadas opcionalmente)
   */
  tickets?: Ticket[]

  /**
   * Timestamp de creación
   */
  createdAt?: string

  /**
   * Timestamp de última actualización
   */
  updatedAt?: string
}

/**
 * Payload para crear una épica; `applicationId` lo añade `api.epics.create`
 */
export interface EpicCreatePayload {
  title: string
  description?: string
  dueDate?: string
}

/**
 * ENTIDADES DE TAREAS Y SUBTAREAS
 * ===============================
 */

/**
 * Representa una tarea/ticket individual
 * Es la unidad de trabajo más pequeña y granular del sistema
 */
export interface Ticket {
  /**
   * Identificador único del ticket
   */
  id: string

  /**
   * Título/descripción breve de la tarea
   */
  title: string

  /**
   * Descripción detallada de qué necesita hacerse
   */
  description: string

  /**
   * ID de la épica a la que pertenece este ticket
   */
  epicId: string

  /**
   * ID del usuario asignado a esta tarea
   * Null si la tarea no está asignada
   */
  assigneeId?: string

  /**
   * Estado actual de la tarea en su ciclo de vida
   */
  status: TicketStatus

  /**
   * Nivel de prioridad de la tarea
   */
  priority: TicketPriority

  /**
   * Índice de orden visual en la épica
   * Permite reordenar tareas mediante drag & drop
   */
  orderIndex: number

  /**
   * Fecha de vencimiento de la tarea
   */
  dueDate?: string

  /**
   * Enlace al pull request/merge request asociado
   */
  prLink?: string

  /**
   * Tiempo total dedicado en segundos
   */
  timeSpentSeconds: number

  /**
   * Tiempo total bloqueado en segundos
   * Representa el tiempo durante el cual la tarea estuvo en estado BLOCKED
   */
  blockedTimeSeconds: number

  /** Inicio de la sesión de trabajo actualmente activa. */
  timerStartedAt?: string | null

  /** Inicio del período de bloqueo actualmente activo. */
  blockedTimerStartedAt?: string | null

  /**
   * Timestamp de creación del ticket
   */
  createdAt: string

  /**
   * Timestamp de última actualización
   */
  updatedAt: string

  /**
   * ID del usuario que creó el ticket
   */
  createdById: string

  /**
   * Array de subtareas relacionadas
   */
  subtasks?: Subtask[]

  /**
   * Objeto de usuario asignado (cargado opcionalmente)
   */
  assignee?: User

  /**
   * Título de la épica a la que pertenece (cargado opcionalmente)
   */
  epicTitle?: string

  /**
   * Nombre de la aplicación (cargado opcionalmente)
   */
  appName?: string
  tags?: Tag[]

  /**
   * ID del Sprint (período de trabajo) al que está planificado el ticket.
   * Es INDEPENDIENTE de `epicId`: un ticket puede pertenecer a la vez a una
   * Épica y a un Sprint.
   */
  sprintId?: string

  /**
   * Nombre del Sprint al que está planificado el ticket
   */
  sprintName?: string

  /**
   * Puntos de historia/esfuerzo del ticket (alimentan la Velocity del Sprint)
   */
  storyPoints?: number

  /**
   * Momento en que se dio la primera respuesta al ticket (base del SLA)
   */
  firstResponseAt?: string

  /**
   * Estado del SLA del ticket (lo inyecta el frontend desde /sla/statuses)
   */
  sla?: import('./sprint').TicketSlaStatus
}

/**
 * Payload para crear un ticket (TicketCreate del backend). Se envía en
 * camelCase: el interceptor de `apiClient` lo convierte a snake_case.
 * `priority`/`status` aceptan el miembro del enum o su valor de texto
 * ('HIGH', 'TODO'...), que es lo que usan los formularios.
 */
export interface TicketCreatePayload {
  epicId: string
  title: string
  description?: string
  assigneeId?: string
  priority?: `${TicketPriority}`
  status?: `${TicketStatus}`
  dueDate?: string
  prLink?: string
  sprintId?: string
  storyPoints?: number
}

export interface Tag {
  id: string
  name: string
}

/**
 * Representa un comentario realizado sobre un ticket
 */
export interface TicketComment {
  /**
   * Identificador único del comentario
   */
  id: string

  /**
   * ID del ticket al que pertenece
   */
  ticketId: string

  /**
   * Usuario que realizó el comentario
   */
  user: User

  /**
   * Contenido del comentario
   */
  content: string

  /**
   * Fecha de creación
   */
  createdAt: string
}

export interface Notification {
  id: string
  userId: string
  title: string
  message: string
  type: string
  isRead: boolean
  ticketId?: string | null
  createdAt: string
}

/**
 * Representa una subtarea dentro de un ticket
 * Las subtareas son pasos más pequeños necesarios para completar un ticket
 */
export interface Subtask {
  /**
   * Identificador único de la subtarea
   */
  id: string

  /**
   * Descripción de la subtarea
   */
  title: string

  /**
   * Indica si la subtarea ha sido completada
   */
  isCompleted: boolean

  /**
   * Índice de orden visual
   */
  orderIndex: number

  /**
   * Timestamp de cuando se completó la subtarea
   */
  completedAt?: string

  /**
   * Timestamp de creación
   */
  createdAt?: string

  /**
   * ID del ticket padre
   */
  ticketId?: string
}

/**
 * ENTIDADES DE AUDITORÍA Y EVENTOS
 * ================================
 */

/**
 * WEB-11: tipos de evento del historial de tickets tal como los devuelve la
 * API (coinciden con `TicketEventType` de app/models/ticket_event.py).
 */
export type TicketHistoryEventType =
  | 'CREATED'
  | 'ASSIGNED'
  | 'TICKET_ASSIGNED'
  | 'STATUS_CHANGED'
  | 'MOVED'
  | 'UPDATED'
  | 'QUESTION_RAISED'
  | 'QUESTION_RESOLVED'
  | 'REDIRECTED'
  | 'COMPLETED'
  | 'COMMENT'
  | 'SUBTASK_CREATED'
  | 'SUBTASK_COMPLETED'
  | 'SUBTASK_DELETED'
  | 'TIMER_START'
  | 'TIMER_PAUSE'

/**
 * WEB-11: evento del historial de un ticket (`GET /api/tickets/{id}/events`).
 *
 * Incluye el autor (`user`) y los datos relevantes de la acción (`detail`),
 * para poder mostrar la trazabilidad completa en el detalle del ticket.
 */
export interface TicketHistoryEvent {
  /** Identificador único del evento */
  id: string

  /** ID del ticket al que pertenece el evento */
  ticketId: string

  /** ID del usuario autor del evento */
  userId?: string | null

  /** Usuario autor (el backend lo incluye para mostrar nombre/email) */
  user?: User | null

  /** Tipo de evento */
  eventType: TicketHistoryEventType | string

  /** Datos relevantes: message, changes, from_status/to_status, tags… */
  detail?: Record<string, any> | null

  /** Usuario origen (redirecciones) */
  fromUserId?: string | null

  /** Usuario destino (redirecciones) */
  toUserId?: string | null

  /** Fecha y hora del evento (ISO 8601) */
  createdAt: string
}

/**
 * ENTIDADES DE DOCUMENTOS
 * =======================
 */

/**
 * Documento adjunto tal como lo devuelve `/api/documents/` (DocumentResponse).
 * Esa ruta no pasa por el adaptador de claves, así que llega en snake_case.
 */
export interface DocumentRecord {
  id: string
  filename: string
  file_size: number
  mime_type: string
  doc_type: string
  epic_id?: string | null
  ticket_id?: string | null
  uploaded_by_id?: string | null
  uploaded_by?: {
    id: string
    full_name?: string | null
    email?: string | null
  } | null
  created_at: string
}

/**
 * ENTIDADES DE ANÁLISIS Y REPORTES
 * ================================
 */

/**
 * Resumen de salud de una aplicación (respuesta de GET /api/analytics/summary/{app_id}).
 * Los nombres coinciden exactamente con los que devuelve el backend.
 */
export interface ApplicationSummary {
  application_id: string
  total_tickets: number
  completed_tickets: number
  avg_time_hours?: number
  avg_time?: number
  in_progress_tickets: number
  todo_tickets: number
  total_epics: number
  completion_percentage: number
  blocked_tickets: number
  blocked_percentage: number
  pending_tickets: number
  overdue_tickets: number
  redirected_tickets?: number
  redirection_events_count?: number
  redirection_events?: Array<{
    ticket_id: string
    ticket_title: string
    from_user_id?: string | null
    to_user_id?: string | null
    detail: Record<string, unknown>
    created_at?: string | null
  }>
  overdue_by_status?: Record<string, number>
  by_group_status?: Record<string, Record<string, number>>
  by_group_priority?: Record<string, Record<string, number>>
  bottlenecks?: Array<{
    status: string
    ticket_count: number
    average_hours: number
    max_hours: number
    tickets: Array<{
      ticket_id: string
      title: string
      status: string
      hours: number
    }>
  }>
  by_status: Record<string, number>
  by_priority: Record<string, number>
}
/**
 * ENTIDADES DE AUTENTICACIÓN
 * ==========================
 */

/**
 * Tokens de autenticación utilizados para validar requests
 * El accessToken se envía en cada request autorizado
 * El refreshToken se utiliza para obtener un nuevo accessToken cuando expira
 */
export interface AuthTokens {
  /**
   * Token JWT utilizado para autenticar requests
   * Se envía en el header Authorization: Bearer <accessToken>
   * Tiene una vida útil corta (típicamente 15-30 minutos)
   */
  accessToken: string

  /**
   * Token utilizado para obtener un nuevo accessToken
   * Tiene una vida útil más larga (típicamente días o semanas)
   */
  refreshToken: string

  /**
   * Tipo de token (generalmente 'Bearer')
   */
  tokenType: string

  /**
   * Segundos hasta que el accessToken expira
   */
  expiresIn?: number
}

/**
 * GENÉRICOS Y UTILITARIOS
 * =======================
 */

/**
 * Respuesta genérica del API
 * Envuelve todas las respuestas del servidor para consistencia
 * Permite errores tipados y manejo uniforme en toda la aplicación
 * 
 * @template T Tipo de datos contenido en la respuesta
 */
export interface ApiResponse<T> {
  /**
   * Indica si la operación fue exitosa
   */
  success: boolean

  /**
   * Datos de la respuesta (si success es true)
   */
  data?: T

  /**
   * Mensaje de error (si success es false)
   */
  message?: string

  /**
   * Código de error específico (para manejo granular de errores)
   */
  errorCode?: string

  /**
   * Detalles adicionales del error
   */
  details?: Record<string, any>
}

/**
 * Datos de login/registro
 */
export interface LoginRequest {
  /**
   * Correo electrónico del usuario
   */
  email: string

  /**
   * Contraseña del usuario
   */
  password: string
}

/**
 * Datos de registro de nuevo usuario (UserCreate del backend).
 * El backend siempre registra con rol DEVELOPER; el rol se cambia después
 * con `api.users.changeRole`.
 */
export interface RegisterRequest extends LoginRequest {
  /**
   * Nombre completo del usuario
   */
  fullName: string

  /**
   * Especialidad técnica (opcional)
   */
  specialty?: string
}

/**
 * Parámetros de filtrado para listar tareas
 */
export interface TicketFilters {
  /**
   * ID de la épica para filtrar
   */
  epicId?: string

  /**
   * ID del Sprint para filtrar
   */
  sprintId?: string

  /**
   * Búsqueda libre por título o descripción
   */
  search?: string

  /**
   * Estado(s) para filtrar
   */
  status?: TicketStatus | TicketStatus[]

  /**
   * Prioridad(es) para filtrar
   */
  priority?: TicketPriority | TicketPriority[]

  /**
   * ID del asignado para filtrar
   */
  assigneeId?: string

  /**
   * IDs de varios asignados para filtrar
   */
  assigneeIds?: string[]

  /**
   * Filtrar por una o más etiquetas reutilizables (NEW-03).
   * El backend las recibe como `tag_ids` repetidos en el query string.
   */
  tagIds?: string[]

  /**
   * Número de items a saltar (paginación)
   */
  skip?: number

  /**
   * Número de items por página
   */
  limit?: number

  /**
   * Campo para ordenar resultados (valor tal cual lo espera el backend)
   */
  sortBy?: 'created_at' | 'updated_at' | 'due_date' | 'priority' | 'status' | 'title'

  /**
   * Dirección de ordenamiento (asc o desc)
   */
  sortOrder?: 'asc' | 'desc'
}

/**
 * Respuesta paginada genérica
 */
export interface PaginatedResponse<T> {
  /**
   * Array de items
   */
  items: T[]

  /**
   * Número total de items
   */
  total: number

  /**
   * Página actual
   */
  page: number

  /**
   * Items por página
   */
  limit: number

  /**
   * Número total de páginas
   */
  totalPages: number
}
