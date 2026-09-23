import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { api } from '@/services/api'
import type { Incident, IncidentFilters, IncidentStatus } from '@/types/incidents'

export const useIncidentsStore = defineStore('incidents', () => {
  const incidents = ref<Incident[]>([])
  const myIncidents = ref<Incident[]>([])
  const filteredIncidents = ref<Incident[]>([])
  const selectedIncident = ref<Incident | null>(null)
  const isLoading = ref(false)
  const filters = ref<IncidentFilters>({})

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
    const query = (filters.value.search ?? '').trim().toLowerCase()
    filteredIncidents.value = incidents.value.filter((incident) => {
      const matchesSearch = !query || incident.title.toLowerCase().includes(query)
      const matchesStatus = !filters.value.status || incident.status === filters.value.status
      const matchesSeverity = !filters.value.severity || incident.severity === filters.value.severity
      const matchesCategory = !filters.value.category || incident.category === filters.value.category
      return matchesSearch && matchesStatus && matchesSeverity && matchesCategory
    })
  }

  const fetchAllIncidents = async () => {
    isLoading.value = true
    try {
      const response = await (api as any)?.incidents?.list?.()
      const items = response?.data ?? response ?? []
      incidents.value = Array.isArray(items) ? items : []
      filteredIncidents.value = incidents.value
    } catch (error) {
      console.warn('No se pudieron cargar incidentes del backend:', error)
      incidents.value = []
      filteredIncidents.value = []
    } finally {
      isLoading.value = false
    }
  }

  const fetchMyIncidents = async () => {
    isLoading.value = true
    try {
      const response = await (api as any)?.incidents?.my?.()
      const items = response?.data ?? response ?? []
      myIncidents.value = Array.isArray(items) ? items : []
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
    const incident = incidents.value.find((item) => item.id === incidentId)
    if (incident) incident.status = newStatus
    const mine = myIncidents.value.find((item) => item.id === incidentId)
    if (mine) mine.status = newStatus
  }

  const resolveIncident = async (incidentId: string) => {
    await updateStatus(incidentId, 'RESOLVED')
  }

  const addComment = async (_incidentId: string, _comment: string) => {
    return true
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
    openCount,
    criticalIncidents,
    overdueIncidents,
    fetchAllIncidents,
    fetchMyIncidents,
    setFilters,
    selectIncident,
    updateStatus,
    resolveIncident,
    addComment,
    reorderIncidents
  }
})
