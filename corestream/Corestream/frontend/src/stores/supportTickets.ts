import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Ticket } from '@/types'
import { TicketStatus, SupportSeverity } from '@/types'
import { api } from '@/services/api'

type SupportStatusFilter = 'all' | 'reported' | 'investigating' | 'resolved'
type SeverityFilter = 'all' | 'critical' | 'high' | 'medium' | 'low'

export const useSupportTicketsStore = defineStore('supportTickets', () => {
  const tickets = ref<Ticket[]>([])
  const selectedTicket = ref<Ticket | null>(null)
  const statusFilter = ref<SupportStatusFilter>('all')
  const severityFilter = ref<SeverityFilter>('all')
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // ── Getters ──────────────────────────────────────────────────────────────

  const filteredTickets = computed(() => {
    return tickets.value.filter(t => {
      const matchesStatus =
        statusFilter.value === 'all' ||
        t.status.toLowerCase() === statusFilter.value

      const matchesSeverity =
        severityFilter.value === 'all' ||
        (t.severity ?? '').toLowerCase() === severityFilter.value

      return matchesStatus && matchesSeverity
    })
  })

  const reportedTickets = computed(() =>
    tickets.value.filter(t => t.status === TicketStatus.REPORTED)
  )

  const investigatingTickets = computed(() =>
    tickets.value.filter(t => t.status === TicketStatus.INVESTIGATING)
  )

  const resolvedTickets = computed(() =>
    tickets.value.filter(t => t.status === TicketStatus.RESOLVED)
  )

  const criticalTickets = computed(() =>
    tickets.value.filter(t => t.severity === SupportSeverity.CRITICAL)
  )

  // ── Actions ───────────────────────────────────────────────────────────────

  async function fetchAll(filters?: { assigneeId?: string }) {
    isLoading.value = true
    error.value = null
    try {
      tickets.value = await api.supportTickets.list({
        assigneeId: filters?.assigneeId,
        limit: 200,
      })
    } catch (err: any) {
      error.value = err?.message ?? 'Error al cargar tickets de soporte'
    } finally {
      isLoading.value = false
    }
  }

  async function create(data: {
    title: string
    description?: string
    severity?: string
    stackTrace?: string
    reproductionSteps?: string
    browser?: string
    operatingSystem?: string
    linkedTicketId?: string
  }): Promise<Ticket> {
    const ticket = await api.supportTickets.create(data)
    tickets.value.unshift(ticket)
    return ticket
  }

  async function update(ticketId: string, data: Parameters<typeof api.supportTickets.update>[1]): Promise<Ticket> {
    const updated = await api.supportTickets.update(ticketId, data)
    _replaceInList(updated)
    if (selectedTicket.value?.id === ticketId) {
      selectedTicket.value = updated
    }
    return updated
  }

  async function assign(ticketId: string, assigneeId: string): Promise<Ticket> {
    const updated = await api.supportTickets.assign(ticketId, assigneeId)
    _replaceInList(updated)
    if (selectedTicket.value?.id === ticketId) {
      selectedTicket.value = updated
    }
    return updated
  }

  async function investigate(ticketId: string): Promise<Ticket> {
    const updated = await api.supportTickets.investigate(ticketId)
    _replaceInList(updated)
    if (selectedTicket.value?.id === ticketId) {
      selectedTicket.value = updated
    }
    return updated
  }

  async function resolve(ticketId: string, prLink: string): Promise<Ticket> {
    const updated = await api.supportTickets.resolve(ticketId, prLink)
    _replaceInList(updated)
    if (selectedTicket.value?.id === ticketId) {
      selectedTicket.value = updated
    }
    return updated
  }

  function selectTicket(ticket: Ticket | null) {
    selectedTicket.value = ticket
  }

  function setStatusFilter(filter: SupportStatusFilter) {
    statusFilter.value = filter
  }

  function setSeverityFilter(filter: SeverityFilter) {
    severityFilter.value = filter
  }

  function _replaceInList(updated: Ticket) {
    const idx = tickets.value.findIndex(t => t.id === updated.id)
    if (idx !== -1) tickets.value[idx] = updated
  }

  return {
    tickets,
    selectedTicket,
    statusFilter,
    severityFilter,
    isLoading,
    error,
    filteredTickets,
    reportedTickets,
    investigatingTickets,
    resolvedTickets,
    criticalTickets,
    fetchAll,
    create,
    update,
    assign,
    investigate,
    resolve,
    selectTicket,
    setStatusFilter,
    setSeverityFilter,
  }
})
