/**
 * Store de Aplicaciones - CoreStream
 * Gestiona la lista de aplicaciones del sistema
 * 
 * Responsabilidades:
 * - Obtener lista de aplicaciones disponibles
 * - Crear, actualizar y eliminar aplicaciones
 * - Seleccionar aplicación activa
 * - Ordenar aplicaciones por diferentes criterios
 */
 
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Application } from '@/types'
import { api } from '@/services/api'
import { useAuthStore } from './auth'

export const useApplicationsStore = defineStore('applications', () => {
  // ========== ESTADO REACTIVO ==========

  /**
   * Lista de todas las aplicaciones disponibles
   */
  const applications = ref<Application[]>([])

  /**
   * Aplicación seleccionada actualmente
   * null cuando no hay selección o al iniciar
   */
  const selectedApp = ref<Application | null>(null)

  /**
   * Flag de carga durante operaciones async
   */
  const isLoading = ref(false)

  /**
   * Mensaje de error de la última operación
   */
  const error = ref<string | null>(null)

  // ========== GETTERS COMPUTADOS ==========

  /**
   * Retorna el ID de la aplicación seleccionada
   * undefined si no hay selección
   */
  const selectedAppId = computed((): string | undefined => selectedApp.value?.id)

  /**
   * Retorna las aplicaciones ordenadas alfabéticamente por nombre
   */
  const sortedByName = computed((): Application[] => {
    return [...applications.value].sort((a, b) => 
      a.name.localeCompare(b.name)
    )
  })

  /**
   * Retorna aplicaciones ordenadas por tickets pendientes (descendente)
   * Útil para visualizar qué apps tienen más trabajo
   */
  const sortedByPending = computed((): Application[] => {
    return [...applications.value].sort((a, b) => {
      const pendingA = a.pendingCount || 0
      const pendingB = b.pendingCount || 0
      return pendingB - pendingA
    })
  })

  /**
   * Retorna aplicaciones ordenadas por tickets atrasados (descendente)
   * Prioriza apps con más tickets vencidos
   */
  const sortedByDelayed = computed((): Application[] => {
    return [...applications.value].sort((a, b) => {
      const delayedA = a.delayedCount || 0
      const delayedB = b.delayedCount || 0
      return delayedB - delayedA
    })
  })

  /**
   * Calcula el progreso general de todas las aplicaciones
   * Porcentaje de tickets completados sobre el total
   */
  const overallProgress = computed((): number => {
    const totalTickets = applications.value.reduce((sum, app) => sum + (app.ticketCount || 0), 0)
    const notCompleted = applications.value.reduce((sum, app) => sum + (app.pendingCount || 0) + (app.delayedCount || 0), 0)
    if (totalTickets === 0) return 0
    return Math.round(((totalTickets - notCompleted) / totalTickets) * 100)
  })

  /**
   * Retorna el número total de tickets atrasados en todas las apps
   */
  const totalDelayedTickets = computed((): number => {
    return applications.value.reduce((sum, app) => sum + (app.delayedCount || 0), 0)
  })

  // ========== ACCIONES ==========

  /**
   * Obtiene la lista de todas las aplicaciones disponibles para el usuario
   * Se ejecuta generalmente al iniciar la aplicación
   * 
   * @returns Promise<Application[]>
   */
  const fetchAll = async (): Promise<Application[]> => {
    isLoading.value = true
    error.value = null

    try {
      const data = await api.applications.list()
      const normalized = Array.isArray(data)
        ? data
        : ((data as any)?.items || (data as any)?.data || [])

      applications.value = normalized
      return normalized
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al obtener aplicaciones'
      error.value = message
      console.error('Error en fetchAll:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Crea una nueva aplicación
   * 
   * @param data - Datos de la aplicación {name, description?, icon?, color?}
   * @returns Promise<Application> - Aplicación creada
   */
  const create = async (data: {
    name: string
    description?: string
    icon?: string
    color?: string
  }): Promise<Application> => {
    isLoading.value = true
    error.value = null

    try {
      const authStore = useAuthStore()
      const created = await api.applications.create({
        ...data,
        color: data.color || '#000000',
        icon: data.icon || '📦',
        description: data.description || '',
        isActive: true,
        ownerId: authStore.user?.id || ''
      })
      applications.value.push(created)
      return created
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al crear aplicación'
      error.value = message
      console.error('Error en create:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Actualiza una aplicación existente
   * 
   * @param id - ID de la aplicación
   * @param data - Datos a actualizar
   * @returns Promise<Application> - Aplicación actualizada
   */
  const update = async (id: string, data: Partial<Application>): Promise<Application> => {
    isLoading.value = true
    error.value = null

    try {
      const updated = await api.applications.update(id, data)
      
      // Actualizar en el array
      const index = applications.value.findIndex(app => app.id === id)
      if (index !== -1) {
        applications.value[index] = updated
      }

      // Actualizar selección si es la misma app
      if (selectedApp.value?.id === id) {
        selectedApp.value = updated
      }

      return updated
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al actualizar aplicación'
      error.value = message
      console.error('Error en update:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Elimina una aplicación
   * 
   * @param id - ID de la aplicación a eliminar
   * @returns Promise<void>
   */
  const remove = async (id: string): Promise<void> => {
    isLoading.value = true
    error.value = null

    try {
      await api.applications.delete(id)
      
      // Remover del array
      applications.value = applications.value.filter(app => app.id !== id)

      // Limpiar selección si es la app eliminada
      if (selectedApp.value?.id === id) {
        selectedApp.value = null
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al eliminar aplicación'
      error.value = message
      console.error('Error en remove:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Selecciona una aplicación como activa
   * Generalmente disparado cuando el usuario hace clic en una app en el sidebar
   * 
   * @param app - Aplicación a seleccionar
   */
  const selectApp = (app: Application | null): void => {
    selectedApp.value = app
  }

  /**
   * Selecciona una aplicación por su ID
   * 
   * @param id - ID de la aplicación
   * @returns boolean - true si se encontró y seleccionó
   */
  const selectAppById = (id: string): boolean => {
    const app = applications.value.find(a => a.id === id)
    if (app) {
      selectedApp.value = app
      return true
    }
    return false
  }

  /**
   * Obtiene una aplicación por su ID del array local
   * 
   * @param id - ID de la aplicación
   * @returns Application | undefined
   */
  const getApplicationById = (id: string): Application | undefined => {
    return applications.value.find(app => app.id === id)
  }

  /**
   * Busca aplicaciones por nombre (búsqueda parcial, case-insensitive)
   * 
   * @param query - Texto a buscar
   * @returns Application[]
   */
  const searchApplications = (query: string): Application[] => {
    const lowerQuery = query.toLowerCase()
    return applications.value.filter(app =>
      app.name.toLowerCase().includes(lowerQuery) ||
      app.description?.toLowerCase().includes(lowerQuery)
    )
  }

  /**
   * Actualiza el estado de una aplicación con datos frescos del servidor
   * Útil para refrescar una app específica sin recargar todas
   * 
   * @param id - ID de la aplicación
   * @returns Promise<Application>
   */
  const refreshApplication = async (id: string): Promise<Application> => {
    try {
      const updated = await api.applications.getById(id)
      
      const index = applications.value.findIndex(app => app.id === id)
      if (index !== -1) {
        applications.value[index] = updated
      }

      if (selectedApp.value?.id === id) {
        selectedApp.value = updated
      }

      return updated
    } catch (err) {
      console.error('Error al refrescar aplicación:', err)
      throw err
    }
  }

  /**
   * Limpia el estado del store (para logout)
   */
  const clear = (): void => {
    applications.value = []
    selectedApp.value = null
    error.value = null
  }

  return {
    // Estado
    applications,
    selectedApp,
    isLoading,
    error,
    // Getters
    selectedAppId,
    sortedByName,
    sortedByPending,
    sortedByDelayed,
    overallProgress,
    totalDelayedTickets,
    // Acciones
    fetchAll,
    create,
    update,
    remove,
    selectApp,
    selectAppById,
    getApplicationById,
    searchApplications,
    refreshApplication,
    clear,
  }
})
