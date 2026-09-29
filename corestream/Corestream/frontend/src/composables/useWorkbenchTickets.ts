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
  const { filteredTickets, statusFilter, dateFilter, tagFilterIds, isLoading, myWorkbench, error } = storeToRefs(store)

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
    store.setTagFilterIds([])
    refresh()
  })

  return {
    /** Tickets filtrados por estado, fecha y etiquetas (computed del store) */
    tickets: filteredTickets,
    /** Todos los tickets del workbench sin filtrar */
    rawTickets: myWorkbench,
    statusFilter,
    dateFilter,
    /** NEW-03: IDs de las etiquetas seleccionadas como filtro */
    tagFilterIds,
    isLoading,
    error,
    setStatusFilter: store.setStatusFilter,
    setDateFilter: store.setDateFilter,
    /** NEW-03: cambia el filtro de etiquetas */
    setTagFilterIds: store.setTagFilterIds,
    /** NEW-03: asocia/desasocia etiquetas de un ticket */
    updateTicketTags: store.updateTags,
    refresh,
  }
}
