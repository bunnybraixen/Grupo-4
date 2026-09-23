/**
 * Store de Tickets - CoreStream
 * ¡LA TIENDA MÁS IMPORTANTE DE CORESTREAM!
 * 
 * Gestiona el ciclo de vida completo de tickets dentro de épicos
 * Soporta flujos complejos de estado, filtrado, búsqueda y colaboración
 * 
 * Responsabilidades principales:
 * - CRUD de tickets
 * - Filtrado por estado y fecha
 * - Gestión del workbench personal
 * - Transiciones de estado (TODO -> IN_PROGRESS -> BLOCKED/REDIRECTED -> DONE)
 * - Validación de PRs y cambios
 * - Flujo de preguntas/respuestas
 * - Redireccionamiento de tickets
 * - Movimiento entre épicos (drag & drop)
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { TicketStatus, TicketPriority } from '@/types'
import type { Ticket } from '@/types'
import { api } from '@/services/api'

/**
 * Tipos de filtros disponibles
 *
 * Los valores reflejan los 5 estados reales de WEB-08
 * (TODO, IN_PROGRESS, BLOCKED, REDIRECTED, DONE).
 */
type StatusFilter = 'all' | 'todo' | 'in_progress' | 'blocked' | 'redirected' | 'done'
type DateFilter = 'all' | 'overdue' | 'today' | 'week' | 'later'

interface TicketFilters {
  status: StatusFilter
  date: DateFilter
}

export const useTicketsStore = defineStore('tickets', () => {
  // ========== ESTADO REACTIVO ==========

  /**
   * Lista de todos los tickets cargados actualmente
   * Se actualiza cuando se obtienen tickets de un épico
   */
  const tickets = ref<Ticket[]>([])

  /**
   * Ticket seleccionado actualmente
   * Se usa para mostrar detalles en el panel lateral
   */
  const selectedTicket = ref<Ticket | null>(null)

  /**
   * Workbench personal: tickets asignados al usuario actual
   */
  const myWorkbench = ref<Ticket[]>([])

  /**
   * Filtro de estado actual
   */
  const statusFilter = ref<StatusFilter>('all')

  /**
   * Filtro de fecha actual
   */
  const dateFilter = ref<DateFilter>('all')

  /**
   * Flag de carga durante operaciones async
   */
  const isLoading = ref(false)

  /**
   * Mensaje de error de la última operación
   */
  const error = ref<string | null>(null)

  /**
   * Almacena los épicos para contexto (referencia al store de épicos)
   * Usado para obtener información sobre el épico padre de un ticket
   */
  const epicIdContext = ref<string | null>(null)

  // ========== GETTERS COMPUTADOS ==========

  /**
   * Retorna los tickets del workbench personal filtrados por estado y fecha
   * Este es el getter más usado en el UI principal del usuario
   * 
   * Flujo de filtrado:
   * 1. Comienza con myWorkbench
   * 2. Aplica filtro de estado (si no es 'all')
   * 3. Aplica filtro de fecha (si no es 'all')
   */
  const filteredTickets = computed((): Ticket[] => {
    let result = [...myWorkbench.value]

    // Aplicar filtro de estado
    if (statusFilter.value !== 'all') {
      result = result.filter(ticket => {
        const statusMap: Record<StatusFilter, TicketStatus | TicketStatus[]> = {
          'all': ticket.status,
          'todo': TicketStatus.TODO,
          'in_progress': TicketStatus.IN_PROGRESS,
          'blocked': TicketStatus.BLOCKED,
          'redirected': TicketStatus.REDIRECTED,
          'done': TicketStatus.DONE,
        }
        const allowedStatus = statusMap[statusFilter.value]
        return Array.isArray(allowedStatus)
          ? allowedStatus.includes(ticket.status)
          : ticket.status === allowedStatus
      })
    }

    // Aplicar filtro de fecha
    if (dateFilter.value !== 'all') {
      const now = new Date()
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
      const weekEnd = new Date(today)
      weekEnd.setDate(weekEnd.getDate() + 7)

      result = result.filter(ticket => {
        if (!ticket.dueDate) return dateFilter.value === 'later'

        const dueDate = new Date(ticket.dueDate)
        const dueDateStart = new Date(dueDate.getFullYear(), dueDate.getMonth(), dueDate.getDate())

        switch (dateFilter.value) {
          case 'overdue':
            return dueDateStart < today
          case 'today':
            return dueDateStart.getTime() === today.getTime()
          case 'week':
            return dueDateStart >= today && dueDateStart <= weekEnd
          case 'later':
            return dueDateStart > weekEnd
          default:
            return true
        }
      })
    }

    return result
  })

  /**
   * Retorna los tickets que están vencidos (fecha de vencimiento < hoy)
   */
  const overdueTickets = computed((): Ticket[] => {
    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())

    return tickets.value.filter(ticket => {
      if (!ticket.dueDate) return false
      const dueDate = new Date(ticket.dueDate)
      const dueDateStart = new Date(dueDate.getFullYear(), dueDate.getMonth(), dueDate.getDate())
      return dueDateStart < today
    })
  })

  /**
   * Retorna todos los tickets en estado IN_PROGRESS
   */
  const inProgressTickets = computed((): Ticket[] => {
    return tickets.value.filter(t => t.status === TicketStatus.IN_PROGRESS)
  })

  /**
   * Retorna todos los tickets en estado TODO
   */
  const todoTickets = computed((): Ticket[] => {
    return tickets.value.filter(t => t.status === TicketStatus.TODO)
  })

  /**
   * Retorna todos los tickets completados (estado terminal DONE)
   */
  const completedTickets = computed((): Ticket[] => {
    return tickets.value.filter(t => t.status === TicketStatus.DONE)
  })

  /**
   * Retorna todos los tickets bloqueados
   */
  const blockedTickets = computed((): Ticket[] => {
    return tickets.value.filter(t => t.status === TicketStatus.BLOCKED)
  })

  /**
   * Retorna todos los tickets redirigidos a otro usuario
   */
  const redirectedTickets = computed((): Ticket[] => {
    return tickets.value.filter(t => t.status === TicketStatus.REDIRECTED)
  })

  /**
   * Cuenta total de tickets completados
   */
  const completedCount = computed((): number => {
    return completedTickets.value.length
  })

  /**
   * Cuenta total de tickets bloqueados
   */
  const blockedCount = computed((): number => {
    return blockedTickets.value.length
  })

  /**
   * Porcentaje de progreso de los tickets del épico actual
   */
  const epicProgress = computed((): number => {
    if (tickets.value.length === 0) return 0
    return Math.round((completedCount.value / tickets.value.length) * 100)
  })

  /**
   * Retorna los tickets ordenados por fecha de vencimiento
   */
  const sortedByDueDate = computed((): Ticket[] => {
    return [...tickets.value].sort((a, b) => {
      if (!a.dueDate) return 1
      if (!b.dueDate) return -1
      return new Date(a.dueDate).getTime() - new Date(b.dueDate).getTime()
    })
  })

  /**
   * Retorna los tickets ordenados por prioridad
   */
  const sortedByPriority = computed((): Ticket[] => {
    // Orden de urgencia de mayor a menor (WEB-08: LOW, MEDIUM, HIGH, URGENT)
    const priorityOrder: Record<TicketPriority, number> = {
      [TicketPriority.URGENT]: 0,
      [TicketPriority.HIGH]: 1,
      [TicketPriority.MEDIUM]: 2,
      [TicketPriority.LOW]: 3,
    }

    return [...tickets.value].sort((a, b) => {
      const priorityA = priorityOrder[a.priority ?? TicketPriority.MEDIUM] ?? 2
      const priorityB = priorityOrder[b.priority ?? TicketPriority.MEDIUM] ?? 2
      return priorityA - priorityB
    })
  })

  // ========== ACCIONES ==========

  /**
   * Obtiene los tickets de un épico específico
   * Se ejecuta cuando el usuario selecciona un épico
   * 
   * @param epicId - ID del épico
   * @returns Promise<Ticket[]>
   */
  const fetchByEpic = async (epicId: string): Promise<Ticket[]> => {
    isLoading.value = true
    error.value = null
    epicIdContext.value = epicId

    try {
      const data = await api.tickets.listByEpic(epicId)
      tickets.value = data
      return data
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al obtener tickets del épico'
      error.value = message
      console.error('Error en fetchByEpic:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Obtiene el workbench personal del usuario actual
   * Incluye todos los tickets asignados al usuario
   * Se ejecuta frecuentemente para mantener actualizado el workbench
   * 
   * @returns Promise<Ticket[]>
   */
  const fetchMyWorkbench = async (): Promise<Ticket[]> => {
    isLoading.value = true
    error.value = null

    try {
      const data = await api.tickets.listMyWorkbench()
      myWorkbench.value = data
      return data
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al obtener workbench personal'
      error.value = message
      console.error('Error en fetchMyWorkbench:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Crea un nuevo ticket dentro de un épico
   * 
   * @param data - Datos del ticket {epicId, title, description?, priority?, dueDate?}
   * @returns Promise<Ticket>
   */
  const create = async (data: {
    epicId: string
    title: string
    description?: string
    /** Prioridad: LOW, MEDIUM, HIGH o URGENT (WEB-08) */
    priority?: TicketPriority
    /** Estado inicial; el backend usa TODO por defecto (WEB-08) */
    status?: TicketStatus
    dueDate?: string
    /** Enlace opcional al Pull Request asociado (WEB-08) */
    prLink?: string
    assignedTo?: string
  }): Promise<Ticket> => {
    isLoading.value = true
    error.value = null

    try {
      const created = await api.tickets.create(data)
      await fetchByEpic(data.epicId)
      return created
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al crear ticket'
      error.value = message
      console.error('Error en create:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Actualiza un ticket existente
   * 
   * @param id - ID del ticket
   * @param data - Datos a actualizar
   * @returns Promise<Ticket>
   */
  const update = async (id: string, data: Partial<Ticket>): Promise<Ticket> => {
    isLoading.value = true
    error.value = null

    try {
      const updated = await api.tickets.update(id, data)
      
      const index = tickets.value.findIndex(t => t.id === id)
      if (index !== -1) {
        tickets.value[index] = updated
      }

      const wbIndex = myWorkbench.value.findIndex(t => t.id === id)
      if (wbIndex !== -1) {
        myWorkbench.value[wbIndex] = updated
      }

      if (selectedTicket.value?.id === id) {
        selectedTicket.value = updated
      }

      return updated
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al actualizar ticket'
      error.value = message
      console.error('Error en update:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Elimina un ticket
   * 
   * @param id - ID del ticket
   * @returns Promise<void>
   */
  const remove = async (id: string): Promise<void> => {
    isLoading.value = true
    error.value = null

    try {
      await api.tickets.delete(id)
      
      tickets.value = tickets.value.filter(t => t.id !== id)
      myWorkbench.value = myWorkbench.value.filter(t => t.id !== id)

      if (selectedTicket.value?.id === id) {
        selectedTicket.value = null
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al eliminar ticket'
      error.value = message
      console.error('Error en remove:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Mueve un ticket a otro épico (operación de drag & drop)
   * Se valida que el épico destino existe
   * 
   * @param ticketId - ID del ticket a mover
   * @param newEpicId - ID del épico destino
   * @returns Promise<Ticket>
   */
  const moveToEpic = async (ticketId: string, newEpicId: string): Promise<Ticket> => {
    isLoading.value = true
    error.value = null

    try {
      const updated = await api.tickets.moveToEpic({ ticketId, newEpicId })
      
      const index = tickets.value.findIndex(t => t.id === ticketId)
      if (index !== -1) {
        tickets.value[index] = updated
      }

      if (selectedTicket.value?.id === ticketId) {
        selectedTicket.value = updated
      }

      return updated
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al mover ticket'
      error.value = message
      console.error('Error en moveToEpic:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Marca un ticket como completado
   * 
   * VALIDACIONES:
   * - El prLink debe ser una URL válida de GitHub/GitLab
   * - El estado actual debe permitir transición a DONE
   * 
   * Flujo:
   * 1. Valida el prLink
   * 2. Llama api.tickets.complete(ticketId, prLink)
   * 3. Actualiza el ticket localmente
   * 4. Notifica al servidor que se completó
   * 
   * @param ticketId - ID del ticket
   * @param prLink - Link del Pull Request
   * @returns Promise<Ticket>
   * @throws Error si prLink no es válido
   */
  const completeTicket = async (ticketId: string, prLink: string): Promise<Ticket> => {
    isLoading.value = true
    error.value = null

    try {
      // Validar PR link
      const prUrlRegex = /^https?:\/\/(github\.com|gitlab\.com|bitbucket\.org)\//i
      if (!prUrlRegex.test(prLink)) {
        throw new Error('El enlace de PR debe ser válido (GitHub, GitLab o Bitbucket)')
      }

      const updated = await api.tickets.complete(ticketId, prLink)
      
      const index = tickets.value.findIndex(t => t.id === ticketId)
      if (index !== -1) {
        tickets.value[index] = updated
      }

      const wbIndex = myWorkbench.value.findIndex(t => t.id === ticketId)
      if (wbIndex !== -1) {
        myWorkbench.value[wbIndex] = updated
      }

      if (selectedTicket.value?.id === ticketId) {
        selectedTicket.value = updated
      }

      return updated
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al completar ticket'
      error.value = message
      console.error('Error en completeTicket:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Inicia el trabajo en un ticket
   * Transiciona el ticket de TODO a IN_PROGRESS
   * 
   * @param ticketId - ID del ticket
   * @returns Promise<Ticket>
   */
  const startWorking = async (ticketId: string): Promise<Ticket> => {
    try {
      const updated = await api.tickets.updateStatus(ticketId, 'IN_PROGRESS')
      
      const index = tickets.value.findIndex(t => t.id === ticketId)
      if (index !== -1) {
        tickets.value[index] = updated
      }

      const wbIndex = myWorkbench.value.findIndex(t => t.id === ticketId)
      if (wbIndex !== -1) {
        myWorkbench.value[wbIndex] = updated
      }

      if (selectedTicket.value?.id === ticketId) {
        selectedTicket.value = updated
      }

      return updated
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al iniciar trabajo'
      error.value = message
      console.error('Error en startWorking:', err)
      throw err
    }
  }

  /**
   * Levanta una pregunta/bloqueo en un ticket
   * Se usa cuando hay dudas sobre requisitos o dependencias bloqueantes
   * 
   * VALIDACIONES:
   * - questionText debe tener al menos 10 caracteres
   * 
   * @param ticketId - ID del ticket
   * @param questionText - Texto de la pregunta
   * @returns Promise<Ticket>
   * @throws Error si questionText es muy corta
   */
  const raiseQuestion = async (ticketId: string, questionText: string): Promise<Ticket> => {
    isLoading.value = true
    error.value = null

    try {
      if (questionText.trim().length < 10) {
        throw new Error('La pregunta debe tener al menos 10 caracteres')
      }

      const updated = await api.tickets.raiseQuestion(ticketId, questionText)
      
      const index = tickets.value.findIndex(t => t.id === ticketId)
      if (index !== -1) {
        tickets.value[index] = updated
      }

      if (selectedTicket.value?.id === ticketId) {
        selectedTicket.value = updated
      }

      return updated
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al levantar pregunta'
      error.value = message
      console.error('Error en raiseQuestion:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Resuelve una pregunta levantada en un ticket
   * Transiciona el ticket de BLOCKED a su estado anterior
   * 
   * @param ticketId - ID del ticket
   * @returns Promise<Ticket>
   */
  const resolveQuestion = async (ticketId: string): Promise<Ticket> => {
    isLoading.value = true
    error.value = null

    try {
      const updated = await api.tickets.resolveQuestion(ticketId)
      
      const index = tickets.value.findIndex(t => t.id === ticketId)
      if (index !== -1) {
        tickets.value[index] = updated
      }

      if (selectedTicket.value?.id === ticketId) {
        selectedTicket.value = updated
      }

      return updated
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al resolver pregunta'
      error.value = message
      console.error('Error en resolveQuestion:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Redirige un ticket a otro usuario
   * Se usa cuando el desarrollador actual no puede completar la tarea
   * 
   * VALIDACIONES:
   * - reason debe tener al menos 10 caracteres (por qué no puede completarlo)
   * - toUserId debe ser válido
   * 
   * @param ticketId - ID del ticket
   * @param toUserId - ID del usuario destino
   * @param reason - Razón del redireccionamiento
   * @returns Promise<Ticket>
   * @throws Error si la razón es muy corta
   */
  const createSubtask = async (ticketId: string, title: string): Promise<Ticket['subtasks'][number]> => {
    isLoading.value = true
    error.value = null

    try {
      const created = await api.tickets.createSubtask(ticketId, title)
      const ticketIndex = tickets.value.findIndex(t => t.id === ticketId)
      if (ticketIndex !== -1) {
        tickets.value[ticketIndex].subtasks = [...(tickets.value[ticketIndex].subtasks ?? []), created]
      }
      return created
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al crear subtarea'
      error.value = message
      console.error('Error en createSubtask:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const updateSubtask = async (ticketId: string, subtaskId: string, data: Partial<Ticket['subtasks'][number]>): Promise<Ticket['subtasks'][number]> => {
    isLoading.value = true
    error.value = null

    try {
      const updated = await api.tickets.updateSubtask(ticketId, subtaskId, data)
      const ticketIndex = tickets.value.findIndex(t => t.id === ticketId)
      if (ticketIndex !== -1) {
        tickets.value[ticketIndex].subtasks = (tickets.value[ticketIndex].subtasks ?? []).map((subtask) =>
          subtask.id === subtaskId ? { ...subtask, ...updated } : subtask
        )
      }
      if (selectedTicket.value?.id === ticketId) {
        selectedTicket.value = {
          ...selectedTicket.value,
          subtasks: (selectedTicket.value.subtasks ?? []).map((subtask) =>
            subtask.id === subtaskId ? { ...subtask, ...updated } : subtask
          )
        }
      }
      return updated
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al actualizar subtarea'
      error.value = message
      console.error('Error en updateSubtask:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const deleteSubtask = async (ticketId: string, subtaskId: string): Promise<void> => {
    isLoading.value = true
    error.value = null

    try {
      await api.tickets.deleteSubtask(ticketId, subtaskId)
      const ticketIndex = tickets.value.findIndex(t => t.id === ticketId)
      if (ticketIndex !== -1) {
        tickets.value[ticketIndex].subtasks = (tickets.value[ticketIndex].subtasks ?? []).filter(s => s.id !== subtaskId)
      }
      if (selectedTicket.value?.id === ticketId) {
        selectedTicket.value = {
          ...selectedTicket.value,
          subtasks: (selectedTicket.value.subtasks ?? []).filter(s => s.id !== subtaskId)
        }
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al eliminar subtarea'
      error.value = message
      console.error('Error en deleteSubtask:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const redirectTicket = async (
    ticketId: string,
    toUserId: string,
    reason: string
  ): Promise<Ticket> => {
    isLoading.value = true
    error.value = null

    try {
      if (reason.trim().length < 10) {
        throw new Error('La razón debe tener al menos 10 caracteres')
      }

      const updated = await api.tickets.redirect(ticketId, { toUserId, reason })
      
      const index = tickets.value.findIndex(t => t.id === ticketId)
      if (index !== -1) {
        tickets.value.splice(index, 1)
      }

      const wbIndex = myWorkbench.value.findIndex(t => t.id === ticketId)
      if (wbIndex !== -1) {
        myWorkbench.value.splice(wbIndex, 1)
      }

      if (selectedTicket.value?.id === ticketId) {
        selectedTicket.value = null
      }

      return updated
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al redirigir ticket'
      error.value = message
      console.error('Error en redirectTicket:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Selecciona un ticket para mostrar sus detalles
   * 
   * @param ticket - Ticket a seleccionar, o null para deseleccionar
   */
  const selectTicket = (ticket: Ticket | null): void => {
    selectedTicket.value = ticket
  }

  /**
   * Obtiene un ticket por su ID
   * 
   * @param id - ID del ticket
   * @returns Ticket | undefined
   */
  const getTicketById = (id: string): Ticket | undefined => {
    return tickets.value.find(t => t.id === id)
  }

  /**
   * Establece el filtro de estado
   * 
   * @param filter - Filtro a aplicar
   */
  const setStatusFilter = (filter: StatusFilter): void => {
    statusFilter.value = filter
  }

  /**
   * Establece el filtro de fecha
   * 
   * @param filter - Filtro a aplicar
   */
  const setDateFilter = (filter: DateFilter): void => {
    dateFilter.value = filter
  }

  /**
   * Limpia el estado del store (para cuando se cambia de épico/app)
   */
  const clear = (): void => {
    tickets.value = []
    selectedTicket.value = null
    myWorkbench.value = []
    statusFilter.value = 'all'
    dateFilter.value = 'all'
    epicIdContext.value = null
    error.value = null
  }

  return {
    // Estado
    tickets,
    selectedTicket,
    myWorkbench,
    statusFilter,
    dateFilter,
    isLoading,
    error,
    epicIdContext,
    // Getters
    filteredTickets,
    overdueTickets,
    inProgressTickets,
    todoTickets,
    completedTickets,
    blockedTickets,
    redirectedTickets,
    completedCount,
    blockedCount,
    epicProgress,
    sortedByDueDate,
    sortedByPriority,
    // Acciones
    fetchByEpic,
    fetchMyWorkbench,
    create,
    update,
    remove,
    moveToEpic,
    completeTicket,
    startWorking,
    createSubtask,
    updateSubtask,
    deleteSubtask,
    raiseQuestion,
    resolveQuestion,
    redirectTicket,
    selectTicket,
    getTicketById,
    setStatusFilter,
    setDateFilter,
    clear,
  }
})
