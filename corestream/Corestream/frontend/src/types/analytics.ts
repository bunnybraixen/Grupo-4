/**
 * Tipos específicos para exportación de reportes de analíticas
 * Adaptados de UserPerformance y datos del store
 */

import type { UserPerformance } from './index'

export interface TeamKPIs {
  efficiencyIndex: number
  blockRate: number
  redirectRate: number
}

export interface DeveloperMetrics extends UserPerformance {
  avatarInitials?: string
  processedTickets?: number
  editedTickets?: number
  questionsRaised?: number
  redirections?: number
  avgTimeMinutes?: number
}

export interface AnalyticsReport {
  teamKPIs: TeamKPIs
  developers: DeveloperMetrics[]
  period: string
}
