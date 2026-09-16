/**
 * Store de Equipo - CoreStream
 * Gestiona miembros del equipo, asignaciones y roles
 * 
 * Responsabilidades:
 * - Obtener lista de miembros del equipo
 * - Añadir y remover miembros
 * - Gestionar roles y permisos (promoción a líder)
 * - Asignar y desasignar tickets
 * - Obtener tickets sin asignar
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, Ticket, UserRole } from '@/types'
import { api } from '@/services/api'

export const useTeamStore = defineStore('team', () => {
  // ========== ESTADO REACTIVO ==========

  /**
   * Lista de miembros del equipo
   * Incluye todos los usuarios asociados a la aplicación/grupo actual
   */
  const members = ref<User[]>([])

  /**
   * Tickets sin asignar en la aplicación actual
   * Se usan para mostrar la cola de trabajo disponible
   */
  const unassignedTickets = ref<Ticket[]>([])

  /**
   * Flag de carga durante operaciones async
   */
  const isLoading = ref(false)

  /**
   * Mensaje de error de la última operación
   */
  const error = ref<string | null>(null)

  /**
   * Flag para controlar visibilidad del modal de agregar miembro
   */
  const showAddModal = ref(false)

  /**
   * ID de la aplicación actual para contexto
   */
  const currentAppId = ref<string | null>(null)

  // ========== GETTERS COMPUTADOS ==========

  /**
   * Retorna los miembros que tienen rol de líder de grupo
   * Son los que pueden aprobar cambios y tomar decisiones
   */
  const leaders = computed((): User[] => {
    return members.value.filter(m => m.role === 'GROUP_LEADER' || m.role === 'ADMIN')
  })

  /**
   * Retorna los miembros que tienen rol de desarrollador
   * Son los que trabajan en los tickets
   */
  const developers = computed((): User[] => {
    return members.value.filter(m => m.role === 'DEVELOPER')
  })

  /**
   * Retorna el administrador del grupo/aplicación
   * Generalmente hay solo uno por grupo
   */
  const admin = computed((): User | undefined => {
    return members.value.find(m => m.role === 'ADMIN')
  })

  /**
   * Retorna el número total de miembros del equipo
   */
  const memberCount = computed((): number => {
    return members.value.length
  })

  /**
   * Retorna el número de desarrolladores activos
   */
  const developerCount = computed((): number => {
    return developers.value.length
  })

  /**
   * Retorna los miembros ordenados alfabéticamente por nombre
   */
  const sortedByName = computed((): User[] => {
    return [...members.value].sort((a, b) => 
      a.fullName.localeCompare(b.fullName)
    )
  })

  /**
   * Retorna miembros agrupados por rol
   */
  const groupedByRole = computed((): Record<UserRole, User[]> => {
    const groups: Record<string, User[]> = {
      'ADMIN': [],
      'GROUP_LEADER': [],
      'DEVELOPER': [],
    }

    members.value.forEach(member => {
      if (groups[member.role]) {
        groups[member.role].push(member)
      }
    })

    return groups as Record<UserRole, User[]>
  })

  /**
   * Retorna el número de tickets sin asignar
   */
  const unassignedTicketCount = computed((): number => {
    return unassignedTickets.value.length
  })

  /**
   * Retorna tickets sin asignar ordenados por prioridad
   */
  const unassignedSortedByPriority = computed((): Ticket[] => {
    const priorityOrder: Record<string, number> = {
      'CRITICAL': 0,
      'HIGH': 1,
      'MEDIUM': 2,
      'LOW': 3,
    }

    return [...unassignedTickets.value].sort((a, b) => {
      const priorityA = priorityOrder[a.priority || 'MEDIUM'] ?? 2
      const priorityB = priorityOrder[b.priority || 'MEDIUM'] ?? 2
      return priorityA - priorityB
    })
  })

  // ========== ACCIONES ==========

  /**
   * Obtiene la lista de miembros del equipo
   * Puede filtrar por aplicación específica
   * 
   * @param appId - ID de la aplicación (opcional)
   * @returns Promise<User[]>
   */
  const fetchMembers = async (appId?: string): Promise<User[]> => {
    isLoading.value = true
    error.value = null

    if (appId) {
      currentAppId.value = appId
    }

    try {
      const data = appId
        ? await api.team.listByApplication(appId)
        : await api.team.list()
      
      members.value = data
      return data
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al obtener miembros del equipo'
      error.value = message
      console.error('Error en fetchMembers:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Añade un nuevo miembro al equipo
   * 
   * @param data - Datos del nuevo miembro {email, fullName, role, department?}
   * @returns Promise<User>
   */
  const addMember = async (data: {
    email: string
    fullName: string
    role: UserRole
    department?: string
  }): Promise<User> => {
    isLoading.value = true
    error.value = null

    try {
      const created = await api.team.addMember({
        ...data,
        appId: currentAppId.value,
      })

      members.value.push(created)
      return created
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al añadir miembro'
      error.value = message
      console.error('Error en addMember:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Actualiza los datos de un miembro del equipo
   * 
   * @param id - ID del usuario
   * @param data - Datos a actualizar
   * @returns Promise<User>
   */
  const updateMember = async (id: string, data: Partial<User>): Promise<User> => {
    isLoading.value = true
    error.value = null

    try {
      const updated = await api.team.updateMember(id, data)
      
      const index = members.value.findIndex(m => m.id === id)
      if (index !== -1) {
        members.value[index] = updated
      }

      return updated
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al actualizar miembro'
      error.value = message
      console.error('Error en updateMember:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Elimina un miembro del equipo
   * El usuario será removido de la aplicación/grupo
   * 
   * @param id - ID del usuario
   * @returns Promise<void>
   */
  const deleteMember = async (id: string): Promise<void> => {
    isLoading.value = true
    error.value = null

    try {
      await api.team.deleteMember(id, currentAppId.value)
      
      members.value = members.value.filter(m => m.id !== id)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al eliminar miembro'
      error.value = message
      console.error('Error en deleteMember:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Promociona un usuario a líder de grupo
   * Solo administradores pueden hacer esto
   * 
   * @param userId - ID del usuario a promocionar
   * @returns Promise<User>
   */
  const promoteToLeader = async (userId: string): Promise<User> => {
    isLoading.value = true
    error.value = null

    try {
      const updated = await api.team.promoteToLeader(userId)
      
      const index = members.value.findIndex(m => m.id === userId)
      if (index !== -1) {
        members.value[index] = updated
      }

      return updated
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al promover a líder'
      error.value = message
      console.error('Error en promoteToLeader:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Degrada un líder de grupo a desarrollador
   * Solo administradores pueden hacer esto
   * 
   * @param userId - ID del usuario a degradar
   * @returns Promise<User>
   */
  const demoteLeader = async (userId: string): Promise<User> => {
    isLoading.value = true
    error.value = null

    try {
      const updated = await api.team.demoteLeader(userId)
      
      const index = members.value.findIndex(m => m.id === userId)
      if (index !== -1) {
        members.value[index] = updated
      }

      return updated
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al degradar líder'
      error.value = message
      console.error('Error en demoteLeader:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Obtiene los tickets sin asignar en la aplicación actual
   * Se usa para mostrar el backlog de trabajo disponible
   * 
   * @param appId - ID de la aplicación (opcional, usa currentAppId si no se especifica)
   * @returns Promise<Ticket[]>
   */
  const fetchUnassigned = async (appId?: string): Promise<Ticket[]> => {
    isLoading.value = true
    error.value = null

    const targetAppId = appId || currentAppId.value
    if (!targetAppId) {
      throw new Error('No hay aplicación seleccionada')
    }

    try {
      const data = await api.team.getUnassignedTickets(targetAppId)
      unassignedTickets.value = data
      return data
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al obtener tickets sin asignar'
      error.value = message
      console.error('Error en fetchUnassigned:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Asigna un ticket a un usuario del equipo
   * 
   * @param ticketId - ID del ticket
   * @param userId - ID del usuario a asignar
   * @returns Promise<Ticket>
   */
  const assignTicket = async (ticketId: string, userId: string): Promise<Ticket> => {
    isLoading.value = true
    error.value = null

    try {
      const updated = await api.team.assignTicket(ticketId, userId)
      
      const index = unassignedTickets.value.findIndex(t => t.id === ticketId)
      if (index !== -1) {
        unassignedTickets.value.splice(index, 1)
      }

      return updated
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al asignar ticket'
      error.value = message
      console.error('Error en assignTicket:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Desasigna un ticket de un usuario
   * El ticket vuelve a la lista de sin asignar
   * 
   * @param ticketId - ID del ticket
   * @returns Promise<Ticket>
   */
  const unassignTicket = async (ticketId: string): Promise<Ticket> => {
    isLoading.value = true
    error.value = null

    try {
      const updated = await api.team.unassignTicket(ticketId)
      
      unassignedTickets.value.push(updated)

      return updated
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al desasignar ticket'
      error.value = message
      console.error('Error en unassignTicket:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Obtiene un miembro por su ID
   * 
   * @param id - ID del usuario
   * @returns User | undefined
   */
  const getMemberById = (id: string): User | undefined => {
    return members.value.find(m => m.id === id)
  }

  /**
   * Obtiene un miembro por su email
   * 
   * @param email - Email del usuario
   * @returns User | undefined
   */
  const getMemberByEmail = (email: string): User | undefined => {
    return members.value.find(m => m.email.toLowerCase() === email.toLowerCase())
  }

  /**
   * Busca miembros por nombre (búsqueda parcial)
   * 
   * @param query - Texto a buscar
   * @returns User[]
   */
  const searchMembers = (query: string): User[] => {
    const lowerQuery = query.toLowerCase()
    return members.value.filter(m =>
      m.fullName.toLowerCase().includes(lowerQuery) ||
      m.email.toLowerCase().includes(lowerQuery)
    )
  }

  /**
   * Abre el modal para añadir nuevo miembro
   */
  const openAddModal = (): void => {
    showAddModal.value = true
  }

  /**
   * Cierra el modal para añadir nuevo miembro
   */
  const closeAddModal = (): void => {
    showAddModal.value = false
  }

  /**
   * Limpia el estado del store (para cuando se cambia de aplicación)
   */
  const clear = (): void => {
    members.value = []
    unassignedTickets.value = []
    currentAppId.value = null
    showAddModal.value = false
    error.value = null
  }

  return {
    // Estado
    members,
    unassignedTickets,
    isLoading,
    error,
    showAddModal,
    currentAppId,
    // Getters
    leaders,
    developers,
    admin,
    memberCount,
    developerCount,
    sortedByName,
    groupedByRole,
    unassignedTicketCount,
    unassignedSortedByPriority,
    // Acciones
    fetchMembers,
    addMember,
    updateMember,
    deleteMember,
    promoteToLeader,
    demoteLeader,
    fetchUnassigned,
    assignTicket,
    unassignTicket,
    getMemberById,
    getMemberByEmail,
    searchMembers,
    openAddModal,
    closeAddModal,
    clear,
  }
})
