/**
 * Composable: useWorkbenchTickets
 *
 * Encapsula la obtención de tickets del workbench personal y expone
 * el acceso reactivo al estado de filtros del store, sin duplicar lógica.
 *
 * Uso:
 *   const { tickets, statusFilter, dateFilter, tagFilterIds, isLoading, setStatusFilter, setDateFilter, setTagFilterIds } = useWorkbenchTickets()
 */

import { onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useTicketsStore } from '@/stores/tickets'

export function useWorkbenchTickets() {
  const store = useTicketsStore()

  // Refs reactivos del store (mantienen sincronía bidireccional)
  const {
    filteredTickets,
    statusFilter,
    dateFilter,
    searchQuery,
    priorityFilter,
    assigneeFilterIds,
    sprintFilterId,
    sortBy,
    sortOrder,
    tagFilterIds,
    isLoading,
    myWorkbench,
    error,
  } = storeToRefs(store)

  const refresh = async () => {
    try {
      await store.fetchMyWorkbench()
    } catch {
      // error is set in store; component reads it via `error` ref
    }
  }

  onMounted(() => {
    store.setStatusFilter('all')
    store.setDateFilter('all')
    store.setSearchQuery('')
    store.setPriorityFilter('all')
    store.setAssigneeFilterIds([])
    store.setSprintFilterId('')
    store.setSort('default', 'desc')
    store.setTagFilterIds([])
    refresh()
  })

  return {
    /** Tickets filtrados por estado, fecha, texto, prioridad y etiquetas */
    tickets: filteredTickets,
    /** Todos los tickets del workbench sin filtrar */
    rawTickets: myWorkbench,
    statusFilter,
    dateFilter,
    searchQuery,
    priorityFilter,
    assigneeFilterIds,
    sprintFilterId,
    sortBy,
    sortOrder,
    /** NEW-03: IDs de las etiquetas seleccionadas como filtro */
    tagFilterIds,
    isLoading,
    error,
    setStatusFilter: store.setStatusFilter,
    setDateFilter: store.setDateFilter,
    setSearchQuery: store.setSearchQuery,
    setPriorityFilter: store.setPriorityFilter,
    setAssigneeFilterIds: store.setAssigneeFilterIds,
    setSprintFilterId: store.setSprintFilterId,
    setSort: store.setSort,
    /** NEW-03: cambia el filtro de etiquetas */
    setTagFilterIds: store.setTagFilterIds,
    /** NEW-03: asocia/desasocia etiquetas de un ticket */
    updateTicketTags: store.updateTags,
    refresh,
  }
}
