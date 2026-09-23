export enum IncidentStatus {
  OPEN = 'OPEN',
  IN_PROGRESS = 'IN_PROGRESS',
  UNDER_REVIEW = 'UNDER_REVIEW',
  RESOLVED = 'RESOLVED',
  CLOSED = 'CLOSED',
  REOPENED = 'REOPENED'
}

export type IncidentSeverity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW'
export type IncidentCategory = 'PERFORMANCE' | 'BUG' | 'SECURITY' | 'INFRASTRUCTURE' | 'UX' | 'DATA'

export interface Incident {
  id: string
  title: string
  description?: string
  status: IncidentStatus
  severity: IncidentSeverity
  category?: IncidentCategory
  priorityOrder: number
  dueDate?: string | null
  assigneeId?: string | null
  resolvedAt?: string | null
  updatedAt?: string | null
  mitigationState?: string
  applicationId?: string | null
  createdAt?: string | null
}

export interface IncidentFilters {
  search?: string
  status?: IncidentStatus
  severity?: IncidentSeverity
  category?: IncidentCategory
}
