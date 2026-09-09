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
import { TicketStatus } from '@/types'
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

  /** Última app cargada; se usa para refrescar tras reordenar (PATCH) */
  const lastAppId = ref<string | null>(null)

  /**
   * Contador de peticiones en vuelo para fetchByApp. Si dos llamadas se
   * disparan casi al mismo tiempo (p.ej. un watcher y una llamada directa
   * seleccionando la misma o distinta app) y la más antigua responde
   * después de la más nueva, sin esto pisaría el estado con datos viejos
   * y una épica/aplicación podría "desaparecer" de la lista sin motivo.
   */
  let fetchRequestId = 0

  // ========== GETTERS COMPUTADOS ==========

  /**
   * Retorna los épicos ordenados por su campo de orden
   * Respeta el orden personalizado del usuario
   */
  const sortedByOrder = computed((): any[] => {
    return [...epics.value].sort((a, b) => a.orderIndex - b.orderIndex)
  })

  /**
   * Retorna épicos con información de progreso calculada
   * Cada épico incluye: progress (%), completedTickets, totalTickets
   * 
   * El progreso se calcula usando los tickets almacenados en associatedTickets
   * Si no hay tickets, el progreso es 0%
   */
  const withProgress = computed((): any[] => {
    return sortedByOrder.value.map(epic => {
      // Obtener tickets asociados a este épico
      const epicTickets = associatedTickets.value.get(epic.id) || []
      const totalTickets = epicTickets.length
      const completedTickets = epicTickets.filter(t =>
        t.status === TicketStatus.COMPLETED).length

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
      t.status === TicketStatus.COMPLETED
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
  const fetchByApp = async (appId: string): Promise<Epic[] | undefined> => {
    isLoading.value = true
    error.value = null

    const requestId = ++fetchRequestId

    try {
      // Validar que appId sea un UUID válido
      const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i
      if (!uuidRegex.test(appId)) {
        throw new Error(`ID de aplicación inválido: ${appId}. Se esperaba un UUID válido.`)
      }

      console.log('Fetching epics for app:', appId)
      const data = await api.epics.list(appId)

      // Si mientras esperábamos esta respuesta se disparó una petición más
      // reciente (otra app u otro fetchByApp concurrente), la descartamos:
      // aplicarla ahora pisaría datos más nuevos con datos obsoletos.
      if (requestId !== fetchRequestId) {
        return undefined
      }

      lastAppId.value = appId
      epics.value = [...data].sort((a, b) => a.orderIndex - b.orderIndex)
      collapsedEpics.value.clear()
      // Sync associatedTickets so progress computeds have up-to-date ticket data
      associatedTickets.value.clear()
      for (const epic of epics.value) {
        associatedTickets.value.set(epic.id, (epic as any).tickets || [])
      }
      return epics.value
    } catch (err) {
      if (requestId !== fetchRequestId) {
        // Respuesta obsoleta que además falló: no pisar el estado actual con un error viejo.
        return undefined
      }
      const message = err instanceof Error ? err.message : 'Error al obtener épicos'
      error.value = message
      epics.value = []
      console.error('Error en fetchByApp:', err)
    } finally {
      if (requestId === fetchRequestId) {
        isLoading.value = false
      }
    }
  }

  /**
   * Crea un nuevo épico
   * 
   * @param data - Datos del épico {appId, name, description?, color?, icon?}
   * @returns Promise<Epic>
   */
  const create = async (data: {
    applicationId: string
    title: string
    description?: string
    dueDate?: string | null
  }): Promise<Epic> => {
    isLoading.value = true
    error.value = null

    try {
      const created = await api.epics.create(data.applicationId,{
        title: data.title,
        description: data.description,
        dueDate: data.dueDate || undefined,
      })
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
      const epic = epics.value.find(e => e.id === id)
      if (!epic) {
        throw new Error('Épico no encontrado')
      }

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
   * Reordenamiento solo en memoria (durante dragover).
   */
  const reorderLocal = (fromIndex: number, toIndex: number): void => {
    if (fromIndex === toIndex) return
    const items = [...epics.value]
    const [moved] = items.splice(fromIndex, 1)
    items.splice(toIndex, 0, moved)
    epics.value = items
  }

  /**
   * Persiste el nuevo orden tras soltar (PATCH /epics/{id}/reorder) y refresca desde el servidor.
   */
  const persistEpicReorder = async (epicId: string): Promise<void> => {
    if (!lastAppId.value) {
      throw new Error('No hay aplicación cargada')
    }
    const newIndex = epics.value.findIndex((e) => e.id === epicId)
    if (newIndex < 0) {
      throw new Error('Épica no encontrada en la lista')
    }

    isLoading.value = true
    error.value = null

    try {
      await api.epics.reorder(epicId, newIndex)
      await fetchByApp(lastAppId.value)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al reordenar épica'
      error.value = message
      console.error('Error en persistEpicReorder:', err)
      try {
        await fetchByApp(lastAppId.value)
      } catch {
        /* ignore */
      }
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
    lastAppId.value = null
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
    reorderLocal,
    persistEpicReorder,
    lastAppId,
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
