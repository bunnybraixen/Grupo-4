/**
 * Composable: useWorkbenchTickets
 *
 * Encapsula la obtención de tickets del workbench personal y expone
 * el acceso reactivo al estado de filtros del store, sin duplicar lógica.
 *
 * Uso:
 *   const { tickets, statusFilter, dateFilter, isLoading, setStatusFilter, setDateFilter } = useWorkbenchTickets()
 */

import { onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useTicketsStore } from '@/stores/tickets'

export function useWorkbenchTickets() {
  const store = useTicketsStore()

  // Refs reactivos del store (mantienen sincronía bidireccional)
  const { filteredTickets, statusFilter, dateFilter, isLoading, myWorkbench, error } = storeToRefs(store)

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
    refresh()
  })

  return {
    /** Tickets filtrados por estado y fecha (computed del store) */
    tickets: filteredTickets,
    /** Todos los tickets del workbench sin filtrar */
    rawTickets: myWorkbench,
    statusFilter,
    dateFilter,
    isLoading,
    error,
    setStatusFilter: store.setStatusFilter,
    setDateFilter: store.setDateFilter,
    refresh,
  }
}
