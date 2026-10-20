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
import type { Application, ApplicationCreatePayload } from '@/types'
import { api } from '@/services/api'

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
      applications.value = data
      return data
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
  const create = async (data: ApplicationCreatePayload): Promise<Application> => {
    isLoading.value = true
    error.value = null

    try {
      const created = await api.applications.create(data)
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
