/**
 * Store de Sprints y SLA - CoreStream
 *
 * Responsabilidades:
 * - Planificación de Sprints (período de trabajo, INDEPENDIENTE de la Épica)
 * - Asociar/quitar Tickets existentes a un Sprint y definir su esfuerzo
 * - Métricas de avance, Velocity y SLA agregado por Sprint
 * - Estado de SLA por TICKET (tiempo transcurrido/restante, alertas)
 *
 * El SLA NO depende del Sprint: se calcula por ticket según su prioridad y los
 * objetivos que configura el ADMIN. Aquí se mantiene un mapa ticketId -> SLA
 * para que el Builder, el Workbench y el Command Center lo muestren en cada
 * tarjeta de ticket sin peticiones extra.
 */

import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { api } from '@/services/api'
import type {
  SlaConfig,
  SlaSummary,
  Sprint,
  SprintPayload,
  TicketSlaStatus
} from '@/types/sprint'

const EMPTY_SUMMARY: SlaSummary = {
  total: 0,
  onTrack: 0,
  atRisk: 0,
  breached: 0,
  met: 0,
  complianceRate: 0,
  breachRate: 0
}

export const useSprintsStore = defineStore('sprints', () => {
  // ========== ESTADO REACTIVO ==========

  /** Sprints cargados (con métricas de avance, Velocity y SLA) */
  const sprints = ref<Sprint[]>([])

  /** Sprint seleccionado en la vista de planificación (detalle con tablero) */
  const selectedSprint = ref<Sprint | null>(null)

  /** Estado de SLA por ticket: ticketId -> estado */
  const slaByTicket = ref<Record<string, TicketSlaStatus>>({})

  /** Resumen agregado de SLA de la última consulta */
  const slaSummary = ref<SlaSummary>({ ...EMPTY_SUMMARY })

  /** Configuración de SLA por prioridad (la edita el ADMIN) */
  const slaConfigs = ref<SlaConfig[]>([])

  /** Tickets próximos a vencer o incumplidos */
  const slaAlerts = ref<TicketSlaStatus[]>([])

  const isLoading = ref(false)
  const isSaving = ref(false)
  const error = ref<string | null>(null)

  // ========== GETTERS ==========

  /** Sprints activos (en curso) */
  const activeSprints = computed((): Sprint[] =>
    sprints.value.filter((sprint) => sprint.status === 'ACTIVE')
  )

  /** Sprints no cerrados (planificados o activos) */
  const openSprints = computed((): Sprint[] =>
    sprints.value.filter((sprint) => sprint.status !== 'COMPLETED')
  )

  /** Sprints cerrados con su Velocity calculada */
  const completedSprints = computed((): Sprint[] =>
    sprints.value.filter((sprint) => sprint.status === 'COMPLETED')
  )

  /** Velocity promedio de los Sprints cerrados (0 si no hay datos) */
  const averageVelocity = computed((): number => {
    const done = completedSprints.value
    if (!done.length) return 0
    return Number(
      (done.reduce((sum, sprint) => sum + (sprint.velocity || 0), 0) / done.length).toFixed(2)
    )
  })

  /** Sprints de un proyecto concreto */
  const byApplication = (applicationId: string): Sprint[] =>
    sprints.value.filter((sprint) => sprint.applicationId === applicationId)

  /** Estado de SLA de un ticket (undefined si no se ha calculado) */
  const slaForTicket = (ticketId?: string | null): TicketSlaStatus | undefined =>
    ticketId ? slaByTicket.value[ticketId] : undefined

  /** Total de alertas de SLA (próximos a vencer + incumplidos) */
  const alertCount = computed((): number => slaAlerts.value.length)

  // ========== ACCIONES: SPRINTS ==========

  /** Carga los Sprints (opcionalmente filtrados por proyecto) */
  const fetchSprints = async (filters?: {
    applicationId?: string
    status?: string
  }): Promise<void> => {
    isLoading.value = true
    error.value = null
    try {
      sprints.value = await api.sprints.list(filters)
    } catch (err: any) {
      error.value = err?.response?.data?.detail || 'No se pudieron cargar los Sprints'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /** Carga el detalle de un Sprint (tickets + tablero) y lo deja seleccionado */
  const fetchSprint = async (sprintId: string): Promise<Sprint | null> => {
    isLoading.value = true
    error.value = null
    try {
      const sprint = await api.sprints.getById(sprintId)
      applySprint(sprint)
      selectedSprint.value = sprint
      return sprint
    } catch (err: any) {
      error.value = err?.response?.data?.detail || 'No se pudo cargar el Sprint'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /** Crea un Sprint (ADMIN / GROUP_LEADER) */
  const createSprint = async (payload: SprintPayload): Promise<Sprint> => {
    isSaving.value = true
    error.value = null
    try {
      const sprint = await api.sprints.create(payload)
      sprints.value = [sprint, ...sprints.value]
      selectedSprint.value = sprint
      return sprint
    } catch (err: any) {
      error.value = err?.response?.data?.detail || 'No se pudo crear el Sprint'
      throw err
    } finally {
      isSaving.value = false
    }
  }

  /** Edita un Sprint existente */
  const updateSprint = async (sprintId: string, payload: SprintPayload): Promise<Sprint> => {
    isSaving.value = true
    error.value = null
    try {
      const sprint = await api.sprints.update(sprintId, payload)
      applySprint(sprint)
      return sprint
    } catch (err: any) {
      error.value = err?.response?.data?.detail || 'No se pudo actualizar el Sprint'
      throw err
    } finally {
      isSaving.value = false
    }
  }

  /** Elimina un Sprint (los tickets NO se borran) */
  const deleteSprint = async (sprintId: string): Promise<void> => {
    isSaving.value = true
    error.value = null
    try {
      await api.sprints.remove(sprintId)
      sprints.value = sprints.value.filter((sprint) => sprint.id !== sprintId)
      if (selectedSprint.value?.id === sprintId) selectedSprint.value = null
    } catch (err: any) {
      error.value = err?.response?.data?.detail || 'No se pudo eliminar el Sprint'
      throw err
    } finally {
      isSaving.value = false
    }
  }

  /** Asocia tickets existentes al Sprint */
  const assignTickets = async (sprintId: string, ticketIds: string[]): Promise<Sprint> => {
    isSaving.value = true
    error.value = null
    try {
      const sprint = await api.sprints.assignTickets(sprintId, ticketIds)
      applySprint(sprint)
      return sprint
    } catch (err: any) {
      error.value = err?.response?.data?.detail || 'No se pudieron asociar los tickets'
      throw err
    } finally {
      isSaving.value = false
    }
  }

  /** Quita un ticket del Sprint */
  const removeTicket = async (sprintId: string, ticketId: string): Promise<Sprint> => {
    isSaving.value = true
    error.value = null
    try {
      const sprint = await api.sprints.removeTicket(sprintId, ticketId)
      applySprint(sprint)
      return sprint
    } catch (err: any) {
      error.value = err?.response?.data?.detail || 'No se pudo quitar el ticket del Sprint'
      throw err
    } finally {
      isSaving.value = false
    }
  }

  /** Define los puntos de esfuerzo de un ticket planificado */
  const setStoryPoints = async (
    sprintId: string,
    ticketId: string,
    storyPoints: number
  ): Promise<Sprint> => {
    isSaving.value = true
    error.value = null
    try {
      const sprint = await api.sprints.setStoryPoints(sprintId, ticketId, storyPoints)
      applySprint(sprint)
      return sprint
    } catch (err: any) {
      error.value = err?.response?.data?.detail || 'No se pudieron guardar los puntos'
      throw err
    } finally {
      isSaving.value = false
    }
  }

  /** Cierra el Sprint y guarda su Velocity calculada */
  const completeSprint = async (sprintId: string): Promise<void> => {
    isSaving.value = true
    error.value = null
    try {
      await api.sprints.complete(sprintId)
      await fetchSprint(sprintId)
      await fetchSprints()
    } catch (err: any) {
      error.value = err?.response?.data?.detail || 'No se pudo cerrar el Sprint'
      throw err
    } finally {
      isSaving.value = false
    }
  }

  // ========== ACCIONES: SLA ==========

  /**
   * Carga el estado de SLA de los tickets y construye el mapa ticketId -> SLA.
   */
  const fetchSlaStatuses = async (filters?: {
    applicationId?: string
    sprintId?: string
    epicId?: string
    onlyAlerts?: boolean
    includeResolved?: boolean
    limit?: number
  }): Promise<void> => {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.sla.statuses(filters)
      slaSummary.value = response.summary
      const map: Record<string, TicketSlaStatus> = {}
      for (const status of response.statuses) map[status.ticketId] = status
      slaByTicket.value = map
    } catch (err: any) {
      error.value = err?.response?.data?.detail || 'No se pudo calcular el SLA'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /** Carga las alertas de SLA (próximos a vencer / incumplidos) */
  const fetchSlaAlerts = async (filters?: {
    applicationId?: string
    sprintId?: string
    limit?: number
  }): Promise<void> => {
    try {
      slaAlerts.value = await api.sla.alerts(filters)
    } catch (err: any) {
      error.value = err?.response?.data?.detail || 'No se pudieron cargar las alertas de SLA'
      throw err
    }
  }

  /** Carga la configuración de SLA por prioridad */
  const fetchSlaConfigs = async (): Promise<void> => {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.sla.configs()
      slaConfigs.value = response.configs
    } catch (err: any) {
      error.value = err?.response?.data?.detail || 'No se pudo cargar la configuración de SLA'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /** Actualiza los objetivos de SLA de una prioridad (ADMIN) */
  const updateSlaConfig = async (
    priority: string,
    payload: Partial<
      Pick<SlaConfig, 'responseMinutes' | 'resolutionMinutes' | 'warnThresholdPercent' | 'isActive'>
    >
  ): Promise<void> => {
    isSaving.value = true
    error.value = null
    try {
      const updated = await api.sla.updateConfig(priority, payload)
      const index = slaConfigs.value.findIndex((config) => config.priority === priority)
      if (index >= 0) slaConfigs.value[index] = updated
      else slaConfigs.value.push(updated)
    } catch (err: any) {
      error.value = err?.response?.data?.detail || 'No se pudo actualizar la configuración de SLA'
      throw err
    } finally {
      isSaving.value = false
    }
  }

  // ========== UTILIDADES ==========

  /** Limpia el error actual */
  const clearError = (): void => {
    error.value = null
  }

  /** Reemplaza un Sprint en la lista (y en la selección si es el mismo) */
  const applySprint = (sprint: Sprint): void => {
    const index = sprints.value.findIndex((item) => item.id === sprint.id)
    if (index >= 0) sprints.value[index] = sprint
    else sprints.value.unshift(sprint)
    if (selectedSprint.value?.id === sprint.id) selectedSprint.value = sprint
  }

  return {
    // estado
    sprints,
    selectedSprint,
    slaByTicket,
    slaSummary,
    slaConfigs,
    slaAlerts,
    isLoading,
    isSaving,
    error,
    // getters
    activeSprints,
    openSprints,
    completedSprints,
    averageVelocity,
    alertCount,
    byApplication,
    slaForTicket,
    // acciones
    fetchSprints,
    fetchSprint,
    createSprint,
    updateSprint,
    deleteSprint,
    assignTickets,
    removeTicket,
    setStoryPoints,
    completeSprint,
    fetchSlaStatuses,
    fetchSlaAlerts,
    fetchSlaConfigs,
    updateSlaConfig,
    clearError
  }
})
