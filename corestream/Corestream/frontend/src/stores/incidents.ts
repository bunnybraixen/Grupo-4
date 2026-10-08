import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { api } from '@/services/api'
import type { Incident, IncidentFilters, IncidentStatus } from '@/types/incidents'

const normalizeIncident = (raw: any): Incident => ({
  id: String(raw.id),
  title: raw.title ?? '',
  description: raw.description ?? '',
  status: raw.status,
  severity: raw.severity,
  category: raw.category,
  priorityOrder: raw.priority_order ?? raw.priorityOrder ?? 0,
  dueDate: raw.due_date ?? raw.dueDate ?? null,
  assigneeId: raw.assignee?.id ?? raw.assignee_id ?? raw.assigneeId ?? null,
  assignee: raw.assignee ? {
    id: String(raw.assignee.id),
    fullName: raw.assignee.full_name ?? raw.assignee.fullName,
    email: raw.assignee.email,
  } : null,
  resolvedAt: raw.resolved_at ?? raw.resolvedAt ?? null,
  updatedAt: raw.updated_at ?? raw.updatedAt ?? null,
  mitigationState: raw.mitigation_state ?? raw.mitigationState,
  applicationId: raw.application_id ?? raw.applicationId ?? null,
  applicationName: raw.application_name ?? raw.applicationName ?? null,
  createdAt: raw.created_at ?? raw.createdAt ?? null,
  resolutionNotes: raw.resolution_notes ?? raw.resolutionNotes ?? null,
})

export const useIncidentsStore = defineStore('incidents', () => {
  const incidents = ref<Incident[]>([])
  const myIncidents = ref<Incident[]>([])
  const filteredIncidents = ref<Incident[]>([])
  const selectedIncident = ref<Incident | null>(null)
  const isLoading = ref(false)
  const filters = ref<IncidentFilters>({})
  const dashboard = ref<any>(null)

  const applyFilters = () => {
    const query = (filters.value.search ?? '').trim().toLowerCase()
    filteredIncidents.value = incidents.value.filter((incident) => {
      const matchesSearch = !query || incident.title.toLowerCase().includes(query)
      const matchesStatus = !filters.value.status || incident.status === filters.value.status
      const matchesSeverity = !filters.value.severity || incident.severity === filters.value.severity
      const matchesCategory = !filters.value.category || incident.category === filters.value.category
      return matchesSearch && matchesStatus && matchesSeverity && matchesCategory
    })
  }

  /** Quita un filtro concreto y vuelve a aplicar el resto */
  const clearFilter = (key: keyof IncidentFilters) => {
    delete filters.value[key]
    applyFilters()
  }

  /** Limpia todos los filtros */
  const clearFilters = () => {
    filters.value = {}
    applyFilters()
  }

  /** Cambia el orden de prioridad de un incidente (drag & drop) */
  const changePriority = async (incidentId: string, newPriorityOrder: number) => {
    const updated = normalizeIncident(
      await api.incidents.updatePriority(incidentId, newPriorityOrder)
    )
    const index = incidents.value.findIndex((item) => item.id === incidentId)
    if (index >= 0) incidents.value[index] = updated
    const mineIndex = myIncidents.value.findIndex((item) => item.id === incidentId)
    if (mineIndex >= 0) myIncidents.value[mineIndex] = updated
    applyFilters()
    return updated
  }

  /** Asigna un incidente a un usuario */
  const assign = async (incidentId: string, userId: string) => {
    const updated = normalizeIncident(await api.incidents.assign(incidentId, userId))
    const index = incidents.value.findIndex((item) => item.id === incidentId)
    if (index >= 0) incidents.value[index] = updated
    const mineIndex = myIncidents.value.findIndex((item) => item.id === incidentId)
    if (mineIndex >= 0) myIncidents.value[mineIndex] = updated
    applyFilters()
    return updated
  }


  const openCount = computed(() =>
    incidents.value.filter((incident) =>
      incident.status === 'OPEN' || incident.status === 'REOPENED'
    ).length
  )

  const criticalIncidents = computed(() =>
    incidents.value.filter((incident) => incident.severity === 'CRITICAL')
  )

  const overdueIncidents = computed(() =>
    incidents.value.filter((incident) => {
      if (!incident.dueDate) return false
      return new Date(incident.dueDate).getTime() < Date.now()
    })
  )

  const setFilters = (nextFilters: IncidentFilters) => {
    filters.value = { ...filters.value, ...nextFilters }
    applyFilters()
  }

  const fetchAllIncidents = async () => {
    isLoading.value = true
    try {
      const response = await api.incidents.list()
      const items = response?.items ?? response?.data?.items ?? response?.data ?? response ?? []
      incidents.value = Array.isArray(items) ? items.map(normalizeIncident) : []
      filteredIncidents.value = incidents.value
    } catch (error) {
      console.warn('No se pudieron cargar incidentes del backend:', error)
      incidents.value = []
      filteredIncidents.value = []
    } finally {
      isLoading.value = false
    }
  }

  /** Alias usado por IncidentsView (vista de todos los incidentes) */
  const fetchAll = fetchAllIncidents

  /** Métricas del dashboard (/incidents/dashboard/stats) */
  const fetchDashboard = async () => {
    try {
      const response = await api.incidents.dashboard()
      dashboard.value = response?.data ?? response ?? null
      return dashboard.value
    } catch (error) {
      console.warn('No se pudieron cargar las estadísticas de incidentes:', error)
      dashboard.value = null
      return null
    }
  }

  const fetchMyIncidents = async () => {
    isLoading.value = true
    try {
      const response = await api.incidents.my()
      const items = response?.items ?? response?.data?.items ?? response?.data ?? response ?? []
      myIncidents.value = Array.isArray(items) ? items.map(normalizeIncident) : []
    } catch (error) {
      console.warn('No se pudieron cargar los incidentes del usuario:', error)
      myIncidents.value = []
    } finally {
      isLoading.value = false
    }
  }

  const selectIncident = (incident: Incident | null) => {
    selectedIncident.value = incident
  }

  const updateStatus = async (incidentId: string, newStatus: IncidentStatus) => {
    const updated = normalizeIncident(await api.incidents.update(incidentId, { status: newStatus }))
    const mineIndex = myIncidents.value.findIndex((item) => item.id === incidentId)
    if (mineIndex >= 0) myIncidents.value[mineIndex] = updated
    return updated
  }

  const start = async (incidentId: string) => normalizeIncident(await api.incidents.start(incidentId))
  const review = async (incidentId: string) => normalizeIncident(await api.incidents.review(incidentId))
  const reopen = async (incidentId: string) => normalizeIncident(await api.incidents.reopen(incidentId))
  const resolve = async (incidentId: string, notes: string, version?: string) =>
    normalizeIncident(await api.incidents.resolve(incidentId, notes, version))

  const resolveIncident = async (incidentId: string) => {
    await resolve(incidentId, 'Resuelto desde Mis Incidentes')
  }

  const addComment = async (incidentId: string, comment: string) => {
    return api.incidents.addComment(incidentId, comment)
  }

  const reorderIncidents = async (_category: string, _orderedIds: string[]) => {
    return true
  }

  return {
    incidents,
    myIncidents,
    filteredIncidents,
    selectedIncident,
    isLoading,
    filters,
    dashboard,
    openCount,
    criticalIncidents,
    overdueIncidents,
    fetchAllIncidents,
    fetchAll,
    fetchDashboard,
    fetchMyIncidents,
    setFilters,
    clearFilter,
    clearFilters,
    selectIncident,
    updateStatus,
    resolveIncident,
    changePriority,
    assign,
    start,
    review,
    reopen,
    resolve,
    update: updateStatus,
    addComment,
    reorderIncidents
  }
})
