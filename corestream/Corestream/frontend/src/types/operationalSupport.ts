/**
 * Tipos de los tickets operacionales de Soporte.
 *
 * Van en snake_case porque `api.operationalSupport` no pasa por el interceptor
 * de conversión de claves (mismo criterio que el módulo incidents).
 */

export type OperationalTicketStatus = 'OPEN' | 'RESOLVED'

export interface OperationalTicketUser {
  id: string
  fullName: string
  email: string
}

export interface OperationalTicket {
  id: string
  title: string
  problem: string
  status: OperationalTicketStatus
  timer_started_at: string
  resolved_at: string | null
  /** Segundos congelados al resolver (0 si sigue abierto) */
  elapsed_seconds: number
  /** Segundos a mostrar: congelados si está resuelto, en vivo si no */
  current_elapsed_seconds: number
  resolution_notes: string | null
  created_by: OperationalTicketUser | null
  resolved_by: OperationalTicketUser | null
  /** Usuario al que se redirigió el ticket (null si está sin asignar) */
  assignee: OperationalTicketUser | null
  created_at: string
}

/** Payload para redirigir (asignar) un ticket operacional. */
export interface OperationalTicketAssign {
  assignee_id: string | null
}
