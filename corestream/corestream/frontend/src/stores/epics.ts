/**
 * Store de Épicos - CoreStream
 * Gestiona la lista de épicos dentro de aplicaciones
 * 
 * Responsabilidades:
 * - Obtener épicos por aplicación
 * - Crear, actualizar y eliminar épicos
 * - Reordenar épicos (drag & drop)
 * - Expandir/contraer épicos
 * - Calcular progreso de épicos basado en tickets
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Epic, Ticket } from '@/types'
import { api } from '@/services/api'

interface EpicWithProgress extends Epic {
  /**
   * Porcentaje de progreso calculado dinamicamente
   */
  progress: number
  /**
   * Número de tickets completados en este épico
   */
  completedTickets: number
  /**
   * Número total de tickets en este épico
   */
  totalTickets: number
}

export const useEpicsStore = defineStore('epics', () => {
  // ========== ESTADO REACTIVO ==========

  /**
   * Lista de épicos de la aplicación seleccionada
   */
  const epics = ref<Epic[]>([])

  /**
   * Flag de carga durante operaciones async
   */
  const isLoading = ref(false)

  /**
   * Mensaje de error de la última operación
   */
  const error = ref<string | null>(null)

  /**
   * Set de IDs de épicos colapsados
   * Usado para persistir estado de expandido/colapsado en el UI
   */
  const collapsedEpics = ref<Set<string>>(new Set())

  /**
   * Almacena los tickets asociados para calcular progreso
   * En una aplicación real, esto vendría desde ticketsStore
   */
  const associatedTickets = ref<Map<string, Ticket[]>>(new Map())

  // ========== GETTERS COMPUTADOS ==========

  /**
   * Retorna los épicos ordenados por su campo de orden
   * Respeta el orden personalizado del usuario
   */
  const sortedByOrder = computed((): Epic[] => {
    return [...epics.value].sort((a, b) => {
      const orderA = a.order ?? Number.MAX_SAFE_INTEGER
      const orderB = b.order ?? Number.MAX_SAFE_INTEGER
      return orderA - orderB
    })
  })

  /**
   * Retorna épicos con información de progreso calculada
   * Cada épico incluye: progress (%), completedTickets, totalTickets
   * 
   * El progreso se calcula usando los tickets almacenados en associatedTickets
   * Si no hay tickets, el progreso es 0%
   */
  const withProgress = computed((): EpicWithProgress[] => {
    return sortedByOrder.value.map(epic => {
      // Obtener tickets asociados a este épico
      const epicTickets = associatedTickets.value.get(epic.id) || []
      const totalTickets = epicTickets.length
      const completedTickets = epicTickets.filter(t => 
        t.status === 'COMPLETED' || t.status === 'CLOSED'
      ).length

      const progress = totalTickets === 0 ? 0 : Math.round((completedTickets / totalTickets) * 100)

      return {
        ...epic,
        progress,
        completedTickets,
        totalTickets,
      }
    })
  })

  /**
   * Retorna los IDs de los épicos actualmente colapsados
   */
  const collapsedEpicIds = computed((): string[] => {
    return Array.from(collapsedEpics.value)
  })

  /**
   * Retorna los épicos que están expandidos
   */
  const expandedEpics = computed((): Epic[] => {
    return epics.value.filter(epic => !collapsedEpics.value.has(epic.id))
  })

  /**
   * Calcula el progreso general de todos los épicos
   */
  const overallEpicsProgress = computed((): number => {
    const allTickets = Array.from(associatedTickets.value.values()).flat()
    const totalTickets = allTickets.length
    const completedTickets = allTickets.filter(t => 
      t.status === 'COMPLETED' || t.status === 'CLOSED'
    ).length

    if (totalTickets === 0) return 0
    return Math.round((completedTickets / totalTickets) * 100)
  })

  // ========== ACCIONES ==========

  /**
   * Obtiene los épicos de una aplicación específica
   * 
   * @param appId - ID de la aplicación
   * @returns Promise<Epic[]>
   */
  const fetchByApp = async (appId: string): Promise<Epic[]> => {
    isLoading.value = true
    error.value = null

    try {
      const data = await api.epics.listByApplication(appId)
      epics.value = data
      collapsedEpics.value.clear()
      return data
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al obtener épicos'
      error.value = message
      console.error('Error en fetchByApp:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Crea un nuevo épico
   * 
   * @param data - Datos del épico {appId, name, description?, color?, icon?}
   * @returns Promise<Epic>
   */
  const create = async (data: {
    appId: string
    name: string
    description?: string
    color?: string
    icon?: string
  }): Promise<Epic> => {
    isLoading.value = true
    error.value = null

    try {
      const created = await api.epics.create(data)
      epics.value.push(created)
      associatedTickets.value.set(created.id, [])
      return created
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al crear épico'
      error.value = message
      console.error('Error en create:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Actualiza un épico existente
   * 
   * @param id - ID del épico
   * @param data - Datos a actualizar
   * @returns Promise<Epic>
   */
  const update = async (id: string, data: Partial<Epic>): Promise<Epic> => {
    isLoading.value = true
    error.value = null

    try {
      const updated = await api.epics.update(id, data)
      
      const index = epics.value.findIndex(e => e.id === id)
      if (index !== -1) {
        epics.value[index] = updated
      }

      return updated
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al actualizar épico'
      error.value = message
      console.error('Error en update:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Elimina un épico
   * 
   * @param id - ID del épico a eliminar
   * @returns Promise<void>
   */
  const remove = async (id: string): Promise<void> => {
    isLoading.value = true
    error.value = null

    try {
      await api.epics.delete(id)
      
      epics.value = epics.value.filter(e => e.id !== id)
      collapsedEpics.value.delete(id)
      associatedTickets.value.delete(id)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al eliminar épico'
      error.value = message
      console.error('Error en remove:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Reordena un épico a una nueva posición
   * Llama a la API PATCH para actualizar el orden en el servidor
   * 
   * Flujo de reordenamiento:
   * 1. El usuario arrastra un épico a una nueva posición (drag & drop)
   * 2. Se calcula el nuevo índice
   * 3. Se envía a la API el epicId y newIndex
   * 4. Se actualiza el array local para reflejar el cambio
   * 
   * @param epicId - ID del épico a reordenar
   * @param newIndex - Nueva posición (0-based)
   * @returns Promise<Epic[]> - Lista de épicos reordenados
   */
  const reorder = async (epicId: string, newIndex: number): Promise<Epic[]> => {
    isLoading.value = true
    error.value = null

    try {
      // Validar índice
      if (newIndex < 0 || newIndex >= epics.value.length) {
        throw new Error('Índice fuera de rango')
      }

      // Hacer cambio optimista en UI
      const currentIndex = epics.value.findIndex(e => e.id === epicId)
      if (currentIndex === -1) throw new Error('Épico no encontrado')

      const [movedEpic] = epics.value.splice(currentIndex, 1)
      epics.value.splice(newIndex, 0, movedEpic)

      // Llamar API para persistir
      const updated = await api.epics.reorder({
        epicId,
        newIndex,
      })

      epics.value = updated

      return updated
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al reordenar épico'
      error.value = message
      console.error('Error en reorder:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Alterna el estado de collapse de un épico
   * Un épico colapsado ocultará sus tickets en el UI
   * 
   * @param epicId - ID del épico
   */
  const toggleCollapse = (epicId: string): void => {
    if (collapsedEpics.value.has(epicId)) {
      collapsedEpics.value.delete(epicId)
    } else {
      collapsedEpics.value.add(epicId)
    }
  }

  /**
   * Expande un épico específico (lo saca del set colapsados)
   * 
   * @param epicId - ID del épico
   */
  const expand = (epicId: string): void => {
    collapsedEpics.value.delete(epicId)
  }

  /**
   * Colapsa un épico específico
   * 
   * @param epicId - ID del épico
   */
  const collapse = (epicId: string): void => {
    collapsedEpics.value.add(epicId)
  }

  /**
   * Expande todos los épicos
   */
  const expandAll = (): void => {
    collapsedEpics.value.clear()
  }

  /**
   * Colapsa todos los épicos
   */
  const collapseAll = (): void => {
    epics.value.forEach(epic => {
      collapsedEpics.value.add(epic.id)
    })
  }

  /**
   * Obtiene un épico por su ID
   * 
   * @param id - ID del épico
   * @returns Epic | undefined
   */
  const getEpicById = (id: string): Epic | undefined => {
    return epics.value.find(e => e.id === id)
  }

  /**
   * Actualiza los tickets asociados a un épico
   * Se llama desde ticketsStore cuando cambian los tickets
   * 
   * @param epicId - ID del épico
   * @param tickets - Array de tickets del épico
   */
  const setEpicTickets = (epicId: string, tickets: Ticket[]): void => {
    associatedTickets.value.set(epicId, tickets)
  }

  /**
   * Limpia el estado del store (para cuando se cambia de aplicación)
   */
  const clear = (): void => {
    epics.value = []
    collapsedEpics.value.clear()
    associatedTickets.value.clear()
    error.value = null
  }

  return {
    // Estado
    epics,
    isLoading,
    error,
    collapsedEpics,
    associatedTickets,
    // Getters
    sortedByOrder,
    withProgress,
    collapsedEpicIds,
    expandedEpics,
    overallEpicsProgress,
    // Acciones
    fetchByApp,
    create,
    update,
    remove,
    reorder,
    toggleCollapse,
    expand,
    collapse,
    expandAll,
    collapseAll,
    getEpicById,
    setEpicTickets,
    clear,
  }
})
