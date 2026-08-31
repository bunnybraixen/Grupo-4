/**
 * @file types/incidents.ts
 * @description Definiciones de tipos e interfaces para el módulo de incidentes.
 * Incluye enums para categorías, estados, severidades y la estructura completa
 * de incidentes, comentarios y datos del dashboard.
 */

/**
 * Enumeración de categorías de incidente.
 * Representa los tipos de problemas o solicitudes que se pueden reportar.
 */
export enum IncidentCategory {
  NEW_FEATURE = 'NEW_FEATURE',
  CRITICAL_ERROR = 'CRITICAL_ERROR',
  NON_CRITICAL_ERROR = 'NON_CRITICAL_ERROR',
  USABILITY_ISSUE = 'USABILITY_ISSUE',
}

/**
 * Enumeración de estados de incidente.
 * Define el ciclo de vida de un incidente desde su creación hasta su cierre.
 */
export enum IncidentStatus {
  OPEN = 'OPEN',
  IN_PROGRESS = 'IN_PROGRESS',
  UNDER_REVIEW = 'UNDER_REVIEW',
  RESOLVED = 'RESOLVED',
  CLOSED = 'CLOSED',
  REOPENED = 'REOPENED',
}

/**
 * Enumeración de severidades de incidente.
 * Indica el impacto y urgencia del incidente.
 */
export enum IncidentSeverity {
  CRITICAL = 'CRITICAL',
  HIGH = 'HIGH',
  MEDIUM = 'MEDIUM',
  LOW = 'LOW',
}

/**
 * Interfaz para información del usuario (reporter o assignee).
 * Contiene datos básicos del usuario para mostrar en la UI.
 */
export interface User {
  id: string;
  name: string;
  fullName: string;
  email: string;
  avatar?: string;
  role?: string;
}

/**
 * Interfaz principal de Incidente.
 * Representa un ticket de incidente/issue en la plataforma.
 * Contiene toda la información necesaria para gestionar y resolver incidentes.
 */
export interface Incident {
  // Identificadores y relaciones
  id: string;
  applicationId: string;
  applicationName?: string;

  // Información básica
  title: string;
  description: string;
  category: IncidentCategory;
  status: IncidentStatus;
  severity: IncidentSeverity;

  // Asignación y responsabilidad
  assigneeId?: string;
  assignee?: User | null;
  reporterId: string;
  reporter: User;

  // Resolución y seguimiento
  priorityOrder: number;
  resolutionNotes?: string;
  environment?: string;

  // Detalles técnicos para reproducir
  stepsToReproduce?: string;
  expectedBehavior?: string;
  actualBehavior?: string;

  // Información de versiones
  affectedVersion?: string;
  fixedInVersion?: string;

  // Timestamps
  dueDate?: string; // ISO 8601 date string
  resolvedAt?: string;
  closedAt?: string;
  createdAt: string;
  updatedAt: string;

  // Campos calculados/dinámicos
  commentCount?: number;
  daysOpen?: number;
  isOverdue?: boolean;
}

/**
 * Interfaz para comentarios en incidentes.
 * Permite a usuarios comentar y proporcionar actualizaciones sobre incidentes.
 */
export interface IncidentComment {
  id: string;
  incidentId: string;
  userId: string;
  userName: string;
  userAvatar?: string;
  content: string;
  createdAt: string;
}

/**
 * Interfaz para el dashboard de incidentes.
 * Proporciona estadísticas resumidas para visualizaciones en la UI.
 */
export interface IncidentDashboard {
  // Conteos por estado
  totalByStatus: Record<IncidentStatus, number>;

  // Conteos por severidad
  totalBySeverity: Record<IncidentSeverity, number>;

  // Conteos por categoría
  totalByCategory: Record<IncidentCategory, number>;

  // Métricas de resolución
  avgResolutionHours: number;

  // Incidentes vencidos
  overdueCount: number;

  // Total de incidentes abiertos
  totalOpen: number;
}

/**
 * Interfaz para filtros de búsqueda de incidentes.
 * Permite filtrar incidentes por múltiples criterios.
 */
export interface IncidentFilters {
  category?: IncidentCategory;
  severity?: IncidentSeverity;
  status?: IncidentStatus;
  assigneeId?: string;
  applicationId?: string;
  search?: string;
}

/**
 * Interfaz para datos de incidentes agrupados por equipo.
 * Utilizado en vistas que muestran incidentes por desarrollador/equipo.
 */
export interface IncidentsByTeam {
  userId: string;
  userName: string;
  userAvatar?: string;
  incidents: Incident[];
  incidentCount: number;
  overallSeverity: IncidentSeverity;
}

/**
 * Interfaz para la creación de un nuevo incidente.
 * Contiene los datos mínimos necesarios para crear un incidente.
 */
export interface CreateIncidentPayload {
  title: string;
  description: string;
  applicationId: string;
  category: IncidentCategory;
  severity: IncidentSeverity;
  assigneeId?: string;
  dueDate?: string;
  environment?: string;
  stepsToReproduce?: string;
  expectedBehavior?: string;
  actualBehavior?: string;
  affectedVersion?: string;
}

/**
 * Interfaz para actualizar un incidente existente.
 * Contiene los campos que pueden ser modificados.
 */
export interface UpdateIncidentPayload {
  title?: string;
  description?: string;
  category?: IncidentCategory;
  severity?: IncidentSeverity;
  status?: IncidentStatus;
  assigneeId?: string;
  priorityOrder?: number;
  dueDate?: string;
  environment?: string;
  stepsToReproduce?: string;
  expectedBehavior?: string;
  actualBehavior?: string;
  affectedVersion?: string;
  fixedInVersion?: string;
  resolutionNotes?: string;
}

// ============================================================================
// CONSTANTES DE CONFIGURACIÓN VISUAL
// ============================================================================
// Estas constantes definen la apariencia de cada categoría, severidad y estado
// en toda la UI de incidentes (tarjetas Kanban, badges, filtros, etc.).
// Se exportan para mantener consistencia visual entre todos los componentes.
// ============================================================================

/**
 * Configuración visual para cada categoría de incidente.
 * Define icono, colores de fondo/texto y etiqueta para badges y filtros.
 */
export const CATEGORY_CONFIG: Record<IncidentCategory, {
  icon: string;
  label: string;
  bgColor: string;
  textColor: string;
}> = {
  [IncidentCategory.NEW_FEATURE]: {
    icon: '★',
    label: 'Nueva Funcionalidad',
    bgColor: 'bg-blue-100 dark:bg-blue-900/40',
    textColor: 'text-blue-700 dark:text-blue-300',
  },
  [IncidentCategory.CRITICAL_ERROR]: {
    icon: '🐛',
    label: 'Error Crítico',
    bgColor: 'bg-red-100 dark:bg-red-900/40',
    textColor: 'text-red-700 dark:text-red-300',
  },
  [IncidentCategory.NON_CRITICAL_ERROR]: {
    icon: '⚠',
    label: 'Error No Crítico',
    bgColor: 'bg-orange-100 dark:bg-orange-900/40',
    textColor: 'text-orange-700 dark:text-orange-300',
  },
  [IncidentCategory.USABILITY_ISSUE]: {
    icon: '👁',
    label: 'Problema de Usabilidad',
    bgColor: 'bg-purple-100 dark:bg-purple-900/40',
    textColor: 'text-purple-700 dark:text-purple-300',
  },
};

/**
 * Configuración visual para cada nivel de severidad.
 * Define colores del punto indicador, borde lateral, y etiqueta.
 */
export const SEVERITY_CONFIG: Record<IncidentSeverity, {
  label: string;
  dotClass: string;
  borderClass: string;
  bgClass: string;
  textClass: string;
}> = {
  [IncidentSeverity.CRITICAL]: {
    label: 'Crítico',
    dotClass: 'bg-red-500 animate-pulse',
    borderClass: 'border-l-red-500',
    bgClass: 'bg-red-100 dark:bg-red-900/40',
    textClass: 'text-red-700 dark:text-red-300',
  },
  [IncidentSeverity.HIGH]: {
    label: 'Alto',
    dotClass: 'bg-orange-500',
    borderClass: 'border-l-orange-500',
    bgClass: 'bg-orange-100 dark:bg-orange-900/40',
    textClass: 'text-orange-700 dark:text-orange-300',
  },
  [IncidentSeverity.MEDIUM]: {
    label: 'Medio',
    dotClass: 'bg-yellow-400',
    borderClass: 'border-l-yellow-400',
    bgClass: 'bg-yellow-100 dark:bg-yellow-900/40',
    textClass: 'text-yellow-700 dark:text-yellow-300',
  },
  [IncidentSeverity.LOW]: {
    label: 'Bajo',
    dotClass: 'bg-green-400',
    borderClass: 'border-l-green-400',
    bgClass: 'bg-green-100 dark:bg-green-900/40',
    textClass: 'text-green-700 dark:text-green-300',
  },
};

/**
 * Configuración visual para cada estado de incidente.
 * Define colores de fondo/texto para badges de estado.
 */
export const STATUS_CONFIG: Record<IncidentStatus, {
  label: string;
  bgClass: string;
  textClass: string;
}> = {
  [IncidentStatus.OPEN]: {
    label: 'Abierto',
    bgClass: 'bg-blue-100 dark:bg-blue-900/40',
    textClass: 'text-blue-700 dark:text-blue-300',
  },
  [IncidentStatus.IN_PROGRESS]: {
    label: 'En Progreso',
    bgClass: 'bg-yellow-100 dark:bg-yellow-900/40',
    textClass: 'text-yellow-700 dark:text-yellow-300',
  },
  [IncidentStatus.UNDER_REVIEW]: {
    label: 'En Revisión',
    bgClass: 'bg-purple-100 dark:bg-purple-900/40',
    textClass: 'text-purple-700 dark:text-purple-300',
  },
  [IncidentStatus.RESOLVED]: {
    label: 'Resuelto',
    bgClass: 'bg-green-100 dark:bg-green-900/40',
    textClass: 'text-green-700 dark:text-green-300',
  },
  [IncidentStatus.CLOSED]: {
    label: 'Cerrado',
    bgClass: 'bg-gray-100 dark:bg-gray-700',
    textClass: 'text-gray-600 dark:text-gray-300',
  },
  [IncidentStatus.REOPENED]: {
    label: 'Reabierto',
    bgClass: 'bg-orange-100 dark:bg-orange-900/40',
    textClass: 'text-orange-700 dark:text-orange-300',
  },
};
