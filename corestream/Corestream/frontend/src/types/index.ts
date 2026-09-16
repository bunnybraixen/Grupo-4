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
 * Tipos de eventos que pueden ocurrir en una tarea
 * Se registran para auditoría y análisis del flujo de trabajo
 */
export enum EventType {
  /**
   * Tarea fue creada
   */
  CREATED = 'CREATED',

  /**
   * Estado de la tarea cambió
   */
  STATUS_CHANGED = 'STATUS_CHANGED',

  /**
   * Prioridad de la tarea cambió
   */
  PRIORITY_CHANGED = 'PRIORITY_CHANGED',

  /**
   * Asignación de la tarea cambió
   */
  ASSIGNMENT_CHANGED = 'ASSIGNMENT_CHANGED',

  /**
   * Se añadió un comentario o pregunta a la tarea
   */
  COMMENT_ADDED = 'COMMENT_ADDED',

  /**
   * Se resolvió una pregunta o comentario
   */
  QUESTION_RESOLVED = 'QUESTION_RESOLVED',

  /**
   * Se creó una subtarea
   */
  SUBTASK_CREATED = 'SUBTASK_CREATED',

  /**
   * Se completó una subtarea
   */
  SUBTASK_COMPLETED = 'SUBTASK_COMPLETED',

  /**
   * Se enlazó un pull request a la tarea
   */
  PR_LINKED = 'PR_LINKED',

  /**
   * Se registró tiempo en la tarea
   */
  TIME_LOGGED = 'TIME_LOGGED',

  /**
   * La tarea fue bloqueada
   */
  BLOCKED = 'BLOCKED',

  /**
   * El bloqueo de la tarea fue resuelto
   */
  UNBLOCKED = 'UNBLOCKED'
}

/**
 * Tipos de notificaciones del sistema
 * Categoriza las notificaciones por tipo de evento
 */
export enum NotificationType {
  /**
   * Notificación sobre cambios en asignación de tareas
   */
  ASSIGNMENT = 'ASSIGNMENT',

  /**
   * Notificación sobre cambio de estado
   */
  STATUS_CHANGE = 'STATUS_CHANGE',

  /**
   * Notificación de comentario o pregunta
   */
  COMMENT = 'COMMENT',

  /**
   * Notificación de tarea bloqueada
   */
  BLOCKED = 'BLOCKED',

  /**
   * Notificación general del sistema
   */
  SYSTEM = 'SYSTEM'
}

/**
 * Tipos de documentos que se pueden cargar
 */
export enum DocumentType {
  /**
   * Especificación de requisitos o diseño
   */
  SPECIFICATION = 'SPECIFICATION',

  /**
   * Documento de prueba o QA
   */
  TEST_CASE = 'TEST_CASE',

  /**
   * Captura de pantalla o imagen de referencia
   */
  SCREENSHOT = 'SCREENSHOT',

  /**
   * Archivo de código fuente
   */
  SOURCE_CODE = 'SOURCE_CODE',

  /**
   * Documento de configuración
   */
  CONFIG = 'CONFIG',

  /**
   * Otro tipo de documento
   */
  OTHER = 'OTHER'
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
 * Registra un evento que ocurrió en una tarea
 * Se utiliza para auditoría y análisis del flujo de trabajo
 */
export interface TicketEvent {
  /**
   * Identificador único del evento
   */
  id: string

  /**
   * ID del ticket en el que ocurrió el evento
   */
  ticketId: string

  /**
   * ID del usuario que causó el evento
   */
  userId: string

  /**
   * Tipo de evento que ocurrió
   */
  eventType: EventType

  /**
   * Detalles adicionales del evento
   * Puede contener valores antes/después, comentarios, etc.
   */
  detail?: string

  /**
   * Timestamp de cuando ocurrió el evento
   */
  createdAt: string
}

/**
 * ENTIDADES DE NOTIFICACIONES
 * ===========================
 */

/**
 * Representa una notificación para un usuario
 * Se utiliza para mantener informados a los usuarios sobre cambios relevantes
 */
export interface Notification {
  /**
   * Identificador único de la notificación
   */
  id: string

  /**
   * ID del usuario destinatario de la notificación
   */
  userId: string

  /**
   * Título breve de la notificación
   */
  title: string

  /**
   * Mensaje detallado de la notificación
   */
  message: string

  /**
   * Tipo de notificación
   */
  type: NotificationType

  /**
   * Indica si el usuario ya ha leído la notificación
   */
  isRead: boolean

  /**
   * ID del ticket relacionado (si aplica)
   */
  ticketId?: string

  /**
   * Timestamp de creación de la notificación
   */
  createdAt: string

  /**
   * Timestamp de cuando se marcó como leída
   */
  readAt?: string
}

/**
 * ENTIDADES DE DOCUMENTOS
 * =======================
 */

/**
 * Representa un archivo/documento cargado en el sistema
 * Puede estar asociado a una épica o a un ticket
 */
export interface Document {
  /**
   * Identificador único del documento
   */
  id: string

  /**
   * Nombre original del archivo
   */
  filename: string

  /**
   * Ruta de almacenamiento del archivo en el servidor
   */
  filePath: string

  /**
   * Tamaño del archivo en bytes
   */
  fileSize: number

  /**
   * Tipo MIME del archivo (application/pdf, image/png, etc.)
   */
  mimeType: string

  /**
   * ID de la épica asociada (si aplica)
   */
  epicId?: string

  /**
   * ID del ticket asociado (si aplica)
   */
  ticketId?: string

  /**
   * ID del usuario que cargó el documento
   */
  uploadedById: string

  /**
   * Categoría/tipo de documento
   */
  docType: DocumentType

  /**
   * Timestamp de creación
   */
  createdAt: string

  /**
   * Timestamp de última actualización
   */
  updatedAt?: string
}

/**
 * ENTIDADES DE ANÁLISIS Y REPORTES
 * ================================
 */

/**
 * Datos de un punto en el gráfico de quemado (Burndown)
 * Representa el progreso de trabajo a lo largo del tiempo
 */
export interface BurndownPoint {
  /**
   * Fecha del punto de datos
   */
  date: string

  /**
   * Número de tareas pendientes en esa fecha
   */
  remaining: number

  /**
   * Número de tareas completadas hasta esa fecha
   */
  completed: number
}

/**
 * Datos de gráfico de quemado completo
 * Muestra la tendencia de progreso a lo largo de un período
 */
export interface BurndownData {
  /**
   * Nombre del período (sprint, épica, etc.)
   */
  name: string

  /**
   * Array de puntos de datos
   */
  points: BurndownPoint[]

  /**
   * Línea de tendencia ideal
   */
  idealLine: BurndownPoint[]

  /**
   * Fecha de inicio del período
   */
  startDate: string

  /**
   * Fecha de fin del período
   */
  endDate: string
}

/**
 * Datos para un gráfico de mapa de calor
 * Muestra la actividad de los desarrolladores a lo largo del tiempo
 */
export interface HeatmapData {
  /**
   * Nombre del usuario
   */
  name: string

  /**
   * Array de valores de actividad por día/semana
   */
  values: number[]

  /**
   * Fechas correspondientes a cada valor
   */
  dates: string[]
}

/**
 * Resumen de análitica general
 * Proporciona métricas de alto nivel sobre el proyecto
 */
export interface AnalyticsSummary {
  /**
   * Número total de tareas completadas
   */
  totalCompleted: number

  /**
   * Número de tareas actualmente en progreso
   */
  totalActive: number

  /**
   * Número de tareas pendientes
   */
  totalPending: number

  /**
   * Número de tareas bloqueadas
   */
  totalBlocked: number

  /**
   * Porcentaje de tareas completadas a tiempo
   */
  onTimePercentage: number

  /**
   * Velocidad promedio del equipo (tareas por semana)
   */
  teamVelocity: number

  /**
   * Lista de rendimiento de cada miembro del equipo
   */
  teamPerformance: UserPerformance[]

  /**
   * Datos de gráfico de quemado
   */
  burndownData: BurndownData

  /**
   * Datos de mapa de calor de actividad
   */
  heatmapData: HeatmapData[]

  /**
   * Fecha de cálculo del resumen
   */
  generatedAt: string
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
 * Datos de registro de nuevo usuario
 */
export interface RegisterRequest extends LoginRequest {
  /**
   * Nombre completo del usuario
   */
  fullName: string

  /**
   * Rol que se desea para el nuevo usuario
   */
  role: UserRole
}

/**
 * Respuesta de autenticación exitosa
 */
export interface AuthResponse {
  /**
   * Información del usuario autenticado
   */
  user: User

  /**
   * Tokens de acceso
   */
  tokens: AuthTokens
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
   * ID de la aplicación para filtrar
   */
  applicationId?: string

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
   * Filtrar tareas asignadas al usuario actual
   */
  myTickets?: boolean

  /**
   * Filtrar tareas retrasadas
   */
  delayed?: boolean

  /**
   * Número de página (para paginación)
   */
  page?: number

  /**
   * Número de items por página
   */
  limit?: number

  /**
   * Campo para ordenar resultados
   */
  sortBy?: 'createdAt' | 'dueDate' | 'priority' | 'status'

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
