/**
 * Store de los tickets operacionales de Soporte.
 *
 * Estado compartido entre las tres vistas (/admin/support, /dev/support):
 * - `openTickets`     → activos, con el timer corriendo
 * - `archivedTickets` → resueltos, con el bloque de cambios para revisar
 *
 * El tick global (`now`) refresca los cronómetros cada segundo desde la vista.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/services/api'
import type { OperationalTicket } from '@/types/operationalSupport'

export const useSupportOperationsStore = defineStore('supportOperations', () => {
  const tickets = ref<OperationalTicket[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const openTickets = computed(() =>
    tickets.value.filter(t => t.status === 'OPEN')
  )
  const archivedTickets = computed(() =>
    tickets.value.filter(t => t.status === 'RESOLVED')
  )

  async function fetchAll() {
    isLoading.value = true
    error.value = null
    try {
      tickets.value = await api.operationalSupport.list()
    } catch (err: any) {
      error.value = err?.response?.data?.detail ?? err?.message ?? 'Error al cargar los tickets de soporte'
    } finally {
      isLoading.value = false
    }
  }

  async function create(data: { title: string; problem: string }) {
    const ticket = await api.operationalSupport.create(data)
    tickets.value.unshift(ticket)
    return ticket
  }

  async function resolve(ticketId: string, resolutionNotes: string) {
    const updated = await api.operationalSupport.resolve(ticketId, resolutionNotes)
    const idx = tickets.value.findIndex(t => t.id === ticketId)
    if (idx !== -1) tickets.value[idx] = updated
    return updated
  }

  /**
   * Segundos a mostrar para un ticket en un instante dado (`nowMs`).
   * Resuelto → duración congelada. Abierto → tiempo en vivo desde el timer.
   */
  function elapsedAt(ticket: OperationalTicket, nowMs: number): number {
    if (ticket.status === 'RESOLVED') return ticket.elapsed_seconds
    const start = Date.parse(ticket.timer_started_at)
    if (Number.isNaN(start)) return ticket.current_elapsed_seconds
    return Math.max(0, Math.floor((nowMs - start) / 1000))
  }

  /** Formatea segundos como HH:MM:SS */
  function formatElapsed(totalSeconds: number): string {
    const h = Math.floor(totalSeconds / 3600)
    const m = Math.floor((totalSeconds % 3600) / 60)
    const s = totalSeconds % 60
    const pad = (n: number) => String(n).padStart(2, '0')
    return `${pad(h)}:${pad(m)}:${pad(s)}`
  }

  return {
    tickets,
    isLoading,
    error,
    openTickets,
    archivedTickets,
    fetchAll,
    create,
    resolve,
    elapsedAt,
    formatElapsed,
  }
})
