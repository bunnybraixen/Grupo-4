/**
 * Tipos del módulo de planificación de Sprints y SLA (Service Level Agreement).
 *
 * Épicas y Sprints son elementos de planificación INDEPENDIENTES:
 *   - Épica  -> área funcional / conjunto de trabajo del proyecto
 *   - Sprint -> período de trabajo (fechas de inicio y término)
 *   - Ticket -> puede pertenecer a la vez a una Épica (`epicId`) y a un Sprint
 *               (`sprintId`).
 *
 * El SLA se calcula a nivel de TICKET (prioridad/severidad + objetivos del
 * ADMIN) y se agrega por Sprint como métrica.
 */

import type { Ticket } from './index'

/** Estado del ciclo de vida de un Sprint */
export type SprintStatus = 'PLANNED' | 'ACTIVE' | 'COMPLETED'

/** Estado posible de un objetivo de SLA (respuesta o resolución) */
export type SlaState = 'ON_TRACK' | 'AT_RISK' | 'BREACHED' | 'MET' | 'NOT_APPLICABLE'

/** Métricas agregadas de SLA (Sprint o proyecto) */
export interface SlaSummary {
  total: number
  onTrack: number
  atRisk: number
  breached: number
  met: number
  /** % de tickets en plazo o cumplidos */
  complianceRate: number
  /** % de tickets incumplidos */
  breachRate: number
}

/** Objetivo de SLA configurado por el ADMIN para una prioridad */
export interface SlaConfig {
  id?: string
  priority: string
  responseMinutes: number
  resolutionMinutes: number
  warnThresholdPercent: number
  isActive: boolean
  /** true cuando aún no hay fila persistida (valores por defecto) */
  isDefault: boolean
  updatedAt?: string | null
}

/** Respuesta de GET /sla/configs */
export interface SlaConfigListResponse {
  configs: SlaConfig[]
}

/** Estado de SLA calculado de un ticket individual */
export interface TicketSlaStatus {
  ticketId: string
  title?: string | null
  ticketStatus?: string | null
  epicTitle?: string | null
  sprintId?: string | null
  sprintName?: string | null
  assigneeId?: string | null
  dueDate?: string | null

  priority: string
  responseTargetMinutes: number
  resolutionTargetMinutes: number
  warnThresholdPercent: number

  createdAt?: string | null
  firstResponseAt?: string | null
  responseDueAt?: string | null
  resolutionDueAt?: string | null

  responseElapsedMinutes: number
  resolutionElapsedMinutes: number
  responseRemainingMinutes: number
  resolutionRemainingMinutes: number

  responseState: SlaState
  resolutionState: SlaState
  state: SlaState

  isBreached: boolean
  isAtRisk: boolean
  isCompliant: boolean
  isResolved: boolean

  nextDeadlineAt?: string | null
  nextDeadlineMetric?: string | null
  minutesToNextDeadline?: number | null
}

/** Respuesta de GET /sla/statuses */
export interface SlaStatusListResponse {
  summary: SlaSummary
  statuses: TicketSlaStatus[]
}

/** Columna del tablero del Sprint (reutiliza el Kanban existente) */
export interface SprintBoardColumn {
  status: string
  label: string
  tickets: Ticket[]
}

/** Sprint con sus métricas de avance, Velocity y SLA agregado */
export interface Sprint {
  id: string
  name: string
  goal?: string | null
  applicationId: string
  applicationName?: string | null
  startDate: string
  endDate: string
  status: SprintStatus | string
  velocity: number
  createdAt?: string

  totalTickets: number
  pendingTickets: number
  inProgressTickets: number
  completedTickets: number
  blockedTickets: number
  redirectedTickets: number

  progress: number
  storyPointsTotal: number
  storyPointsCompleted: number

  durationDays: number
  daysRemaining: number
  isOverdue: boolean

  sla: SlaSummary

  tickets?: Ticket[]
  board?: SprintBoardColumn[]
}

/** Payload para crear/editar un Sprint */
export interface SprintPayload {
  name?: string
  goal?: string | null
  applicationId?: string
  startDate?: string
  endDate?: string
  status?: SprintStatus
}

/** Resultado del cierre de Sprint (cálculo automático de Velocity) */
export interface SprintVelocityResult {
  sprintId: string
  sprintName: string
  status: string
  velocity: number
  storyPointsCompleted: number
  completedTickets: number
  message: string
}
