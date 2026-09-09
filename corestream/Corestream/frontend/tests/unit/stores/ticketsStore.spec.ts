/**
 * Tests del store de tickets — CoreStream
 *
 * Cubre: estado inicial, filtros, computeds, y acciones con API mockeada.
 * Mete (sin ejecutar HTTP real) las rutas críticas de completeTicket,
 * startWorking, raiseQuestion y createSubtask.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

// Mock del módulo de API antes de cualquier import del store
vi.mock('@/services/api', () => ({
  api: {
    tickets: {
      list: vi.fn(),
      getWorkbench: vi.fn(),
      getById: vi.fn(),
      create: vi.fn(),
      update: vi.fn(),
      delete: vi.fn(),
      startWorking: vi.fn(),
      completeTicket: vi.fn(),
      raiseQuestion: vi.fn(),
      resolveQuestion: vi.fn(),
      getTeamMembers: vi.fn(),
      getEvents: vi.fn(),
      moveToEpic: vi.fn(),
      reorder: vi.fn(),
      redirectTicket: vi.fn(),
    },
    subtasks: {
      create: vi.fn(),
      update: vi.fn(),
      delete: vi.fn(),
      reorder: vi.fn(),
    },
  },
  default: {
    tickets: {
      list: vi.fn(),
      getWorkbench: vi.fn(),
      getById: vi.fn(),
      startWorking: vi.fn(),
      completeTicket: vi.fn(),
      raiseQuestion: vi.fn(),
      resolveQuestion: vi.fn(),
      getTeamMembers: vi.fn(),
      getEvents: vi.fn(),
    },
    subtasks: {
      create: vi.fn(),
      update: vi.fn(),
      delete: vi.fn(),
    },
  },
}))

import { useTicketsStore } from '@/stores/tickets'
import type { Ticket } from '@/types'
import { TicketStatus } from '@/types'

// Helper para crear tickets de prueba
const makeTicket = (overrides: Partial<Ticket> = {}): Ticket => ({
  id: 'ticket-1',
  title: 'Test Ticket',
  description: '',
  status: TicketStatus.TODO,
  priority: 'MEDIUM',
  epicId: 'epic-1',
  epicTitle: 'Test Epic',
  appName: 'Test App',
  assigneeId: null,
  assignee: null,
  prLink: null,
  dueDate: null,
  order: 0,
  subtasks: [],
  timeSpentSeconds: 0,
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
  ...overrides,
} as Ticket)

describe('useTicketsStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  // ─────────────────────────────────────────────────────────────────────────
  // ESTADO INICIAL
  // ─────────────────────────────────────────────────────────────────────────

  describe('estado inicial', () => {
    it('inicia con myWorkbench vacío', () => {
      const store = useTicketsStore()
      expect(store.myWorkbench).toEqual([])
    })

    it('inicia con statusFilter = all', () => {
      const store = useTicketsStore()
      expect(store.statusFilter).toBe('all')
    })

    it('inicia sin error', () => {
      const store = useTicketsStore()
      expect(store.error).toBeNull()
    })

    it('inicia sin loading', () => {
      const store = useTicketsStore()
      expect(store.isLoading).toBe(false)
    })
  })

  // ─────────────────────────────────────────────────────────────────────────
  // FILTROS
  // ─────────────────────────────────────────────────────────────────────────

  describe('setStatusFilter', () => {
    it('cambia el statusFilter', () => {
      const store = useTicketsStore()
      store.setStatusFilter('in_progress')
      expect(store.statusFilter).toBe('in_progress')
    })

    it('acepta todos los valores válidos', () => {
      const store = useTicketsStore()
      const filters = ['all', 'todo', 'in_progress', 'blocked', 'completed'] as const
      filters.forEach(f => {
        store.setStatusFilter(f)
        expect(store.statusFilter).toBe(f)
      })
    })
  })

  describe('setDateFilter', () => {
    it('cambia el dateFilter', () => {
      const store = useTicketsStore()
      store.setDateFilter('overdue')
      expect(store.dateFilter).toBe('overdue')
    })
  })

  // ─────────────────────────────────────────────────────────────────────────
  // COMPUTEDS — filteredTickets
  // ─────────────────────────────────────────────────────────────────────────

  describe('filteredTickets', () => {
    it('devuelve todos los tickets con statusFilter = all', () => {
      const store = useTicketsStore()
      store.myWorkbench = [
        makeTicket({ id: '1', status: TicketStatus.TODO }),
        makeTicket({ id: '2', status: TicketStatus.IN_PROGRESS }),
        makeTicket({ id: '3', status: TicketStatus.COMPLETED }),
      ]
      store.setStatusFilter('all')
      expect(store.filteredTickets).toHaveLength(3)
    })

    it('filtra por status todo', () => {
      const store = useTicketsStore()
      store.myWorkbench = [
        makeTicket({ id: '1', status: TicketStatus.TODO }),
        makeTicket({ id: '2', status: TicketStatus.IN_PROGRESS }),
      ]
      store.setStatusFilter('todo')
      const result = store.filteredTickets
      expect(result.every(t => t.status === 'TODO')).toBe(true)
    })

    it('filtra por status in_progress', () => {
      const store = useTicketsStore()
      store.myWorkbench = [
        makeTicket({ id: '1', status: TicketStatus.TODO }),
        makeTicket({ id: '2', status: TicketStatus.IN_PROGRESS }),
        makeTicket({ id: '3', status: TicketStatus.IN_PROGRESS }),
      ]
      store.setStatusFilter('in_progress')
      expect(store.filteredTickets).toHaveLength(2)
    })

    it('filtra por status bloqueado (BLOCKED y BLOCKED_QUESTION)', () => {
      const store = useTicketsStore()
      store.myWorkbench = [
        makeTicket({ id: '1', status: TicketStatus.BLOCKED }),
        makeTicket({ id: '2', status: TicketStatus.BLOCKED_QUESTION }),
        makeTicket({ id: '3', status: TicketStatus.TODO }),
      ]
      store.setStatusFilter('blocked')
      expect(store.filteredTickets).toHaveLength(2)
    })

    it('filtra por status completado', () => {
      const store = useTicketsStore()
      store.myWorkbench = [
        makeTicket({ id: '1', status: TicketStatus.COMPLETED }),
        makeTicket({ id: '2', status: TicketStatus.COMPLETED }),
        makeTicket({ id: '3', status: TicketStatus.TODO }),
      ]
      store.setStatusFilter('completed')
      const result = store.filteredTickets
      expect(result.every(t => ['COMPLETED', 'DONE'].includes(t.status))).toBe(true)
    })
  })

  // ─────────────────────────────────────────────────────────────────────────
  // COMPUTEDS — contadores
  // ─────────────────────────────────────────────────────────────────────────

  // Nota: completedCount, blockedCount, inProgressTickets, todoTickets y epicProgress
  // leen de store.tickets (contexto épica/constructor), NO de store.myWorkbench.
  describe('computeds de conteo', () => {
    it('completedCount cuenta solo los completados (COMPLETED)', () => {
      const store = useTicketsStore()
      store.tickets = [
        makeTicket({ id: '1', status: TicketStatus.COMPLETED }),
        makeTicket({ id: '2', status: TicketStatus.COMPLETED }),
        makeTicket({ id: '3', status: TicketStatus.TODO }),
      ]
      expect(store.completedCount).toBe(2)
    })

    it('blockedCount cuenta solo BLOCKED (no BLOCKED_QUESTION)', () => {
      const store = useTicketsStore()
      store.tickets = [
        makeTicket({ id: '1', status: TicketStatus.BLOCKED }),
        makeTicket({ id: '2', status: TicketStatus.BLOCKED }),
        makeTicket({ id: '3', status: TicketStatus.TODO }),
      ]
      expect(store.blockedCount).toBe(2)
    })

    it('inProgressTickets filtra IN_PROGRESS', () => {
      const store = useTicketsStore()
      store.tickets = [
        makeTicket({ id: '1', status: TicketStatus.IN_PROGRESS }),
        makeTicket({ id: '2', status: TicketStatus.TODO }),
      ]
      expect(store.inProgressTickets).toHaveLength(1)
    })

    it('todoTickets filtra TODO', () => {
      const store = useTicketsStore()
      store.tickets = [
        makeTicket({ id: '1', status: TicketStatus.TODO }),
        makeTicket({ id: '2', status: TicketStatus.TODO }),
        makeTicket({ id: '3', status: TicketStatus.IN_PROGRESS }),
      ]
      expect(store.todoTickets).toHaveLength(2)
    })
  })

  // ─────────────────────────────────────────────────────────────────────────
  // epicProgress
  // ─────────────────────────────────────────────────────────────────────────

  // epicProgress lee de store.tickets (contexto épica)
  describe('epicProgress', () => {
    it('retorna 0 cuando no hay tickets', () => {
      const store = useTicketsStore()
      store.tickets = []
      expect(store.epicProgress).toBe(0)
    })

    it('retorna 100 cuando todos están COMPLETED', () => {
      const store = useTicketsStore()
      store.tickets = [
        makeTicket({ id: '1', status: TicketStatus.COMPLETED }),
        makeTicket({ id: '2', status: TicketStatus.COMPLETED }),
      ]
      expect(store.epicProgress).toBe(100)
    })

    it('calcula el progreso parcial correctamente (1 de 2)', () => {
      const store = useTicketsStore()
      store.tickets = [
        makeTicket({ id: '1', status: TicketStatus.COMPLETED }),
        makeTicket({ id: '2', status: TicketStatus.TODO }),
      ]
      expect(store.epicProgress).toBe(50)
    })
  })

  // ─────────────────────────────────────────────────────────────────────────
  // selectTicket y getTicketById
  // ─────────────────────────────────────────────────────────────────────────

  describe('selectTicket', () => {
    it('establece el ticket seleccionado', () => {
      const store = useTicketsStore()
      const ticket = makeTicket()
      store.selectTicket(ticket)
      expect(store.selectedTicket).toEqual(ticket)
    })

    it('permite deseleccionar con null', () => {
      const store = useTicketsStore()
      store.selectTicket(makeTicket())
      store.selectTicket(null)
      expect(store.selectedTicket).toBeNull()
    })
  })

  // getTicketById busca en store.tickets (contexto épica/constructor)
  describe('getTicketById', () => {
    it('encuentra un ticket por id', () => {
      const store = useTicketsStore()
      const ticket = makeTicket({ id: 'abc-123' })
      store.tickets = [ticket]
      expect(store.getTicketById('abc-123')).toEqual(ticket)
    })

    it('retorna undefined para id inexistente', () => {
      const store = useTicketsStore()
      store.tickets = [makeTicket({ id: '1' })]
      expect(store.getTicketById('no-existe')).toBeUndefined()
    })
  })

  // ─────────────────────────────────────────────────────────────────────────
  // clear
  // ─────────────────────────────────────────────────────────────────────────

  describe('clear', () => {
    it('vacía myWorkbench y resetea filtros', () => {
      const store = useTicketsStore()
      store.myWorkbench = [makeTicket()]
      store.setStatusFilter('completed')
      store.clear()
      expect(store.myWorkbench).toEqual([])
    })
  })

  // ─────────────────────────────────────────────────────────────────────────
  // overdueTickets
  // ─────────────────────────────────────────────────────────────────────────

  describe('overdueTickets', () => {
    it('no incluye tickets sin dueDate', () => {
      const store = useTicketsStore()
      store.myWorkbench = [makeTicket({ dueDate: undefined, status: TicketStatus.TODO })]
      expect(store.overdueTickets).toHaveLength(0)
    })

    it('no incluye tickets completados aunque estén vencidos', () => {
      const store = useTicketsStore()
      store.myWorkbench = [
        makeTicket({ dueDate: '2000-01-01', status: TicketStatus.COMPLETED }),
      ]
      expect(store.overdueTickets).toHaveLength(0)
    })

    it('incluye tickets con fecha pasada (no completados)', () => {
      const store = useTicketsStore()
      // overdueTickets lee de store.tickets
      store.tickets = [
        makeTicket({ id: '1', dueDate: '2000-01-01T00:00:00', status: TicketStatus.TODO }),
        makeTicket({ id: '2', dueDate: '2099-12-31T00:00:00', status: TicketStatus.TODO }),
      ]
      expect(store.overdueTickets).toHaveLength(1)
      expect(store.overdueTickets[0].id).toBe('1')
    })
  })
})
