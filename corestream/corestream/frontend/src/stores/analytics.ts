/**
 * Store de Analíticas - CoreStream
 * Gestiona datos analíticos y reportes de rendimiento
 * 
 * Responsabilidades:
 * - Obtener resumen analítico de aplicaciones
 * - Recopilar datos de rendimiento de usuarios
 * - Generar mapas de calor de actividad
 * - Calcular datos de burndown para épicos
 * - Exportar reportes en CSV
 * - Ordenar y filtrar datos analíticos
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  AnalyticsSummary,
  UserPerformance,
  HeatmapEntry,
  BurndownData,
} from '@/types'
import { api } from '@/services/api'

type SortColumn = 'name' | 'completed' | 'velocity' | 'blockedRate' | 'avgCompletionTime'
type SortDirection = 'asc' | 'desc'

export const useAnalyticsStore = defineStore('analytics', () => {
  // ========== ESTADO REACTIVO ==========

  /**
   * Resumen analítico de la aplicación seleccionada
   * Incluye métricas generales, tendencias, etc.
   */
  const summary = ref<AnalyticsSummary | null>(null)

  /**
   * Lista de rendimiento por usuario
   * Contiene métricas individuales: tickets completados, velocidad, etc.
   */
  const performance = ref<UserPerformance[]>([])

  /**
   * Datos de mapa de calor de actividad
   * Mostrado típicamente en una vista de calendario/heatmap
   */
  const heatmapData = ref<HeatmapEntry[]>([])

  /**
   * Datos de burndown para un épico específico
   * Usado para gráficos de progreso en el tiempo
   */
  const burndownData = ref<BurndownData[]>([])

  /**
   * Flag de carga durante operaciones async
   */
  const isLoading = ref(false)

  /**
   * Mensaje de error de la última operación
   */
  const error = ref<string | null>(null)

  /**
   * Rango de fechas para filtrar datos analíticos
   */
  const dateRange = ref<{ from: Date; to: Date }>({
    from: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), // Últimos 30 días
    to: new Date(),
  })

  /**
   * Columna por la que se ordena actualmente
   */
  const sortColumn = ref<SortColumn>('completed')

  /**
   * Dirección de ordenamiento (ascendente o descendente)
   */
  const sortDirection = ref<SortDirection>('desc')

  // ========== GETTERS COMPUTADOS ==========

  /**
   * Retorna el rendimiento de usuarios ordenado por sortColumn y sortDirection
   * 
   * Soporta ordenamiento por:
   * - name: nombre del usuario (alfabético)
   * - completed: número de tickets completados
   * - velocity: velocidad de desarrollo (tickets/día)
   * - blockedRate: tasa de tickets bloqueados
   * - avgCompletionTime: tiempo promedio de finalización
   */
  const sortedPerformance = computed((): UserPerformance[] => {
    const sorted = [...performance.value].sort((a, b) => {
      let compareA: string | number = 0
      let compareB: string | number = 0

      switch (sortColumn.value) {
        case 'name':
          compareA = a.userName.toLowerCase()
          compareB = b.userName.toLowerCase()
          break
        case 'completed':
          compareA = a.completedTickets
          compareB = b.completedTickets
          break
        case 'velocity':
          compareA = a.velocity || 0
          compareB = b.velocity || 0
          break
        case 'blockedRate':
          compareA = a.blockedTickets / Math.max(a.totalTickets, 1)
          compareB = b.blockedTickets / Math.max(b.totalTickets, 1)
          break
        case 'avgCompletionTime':
          compareA = a.averageCompletionTime || 0
          compareB = b.averageCompletionTime || 0
          break
        default:
          compareA = 0
          compareB = 0
      }

      if (typeof compareA === 'string' && typeof compareB === 'string') {
        return sortDirection.value === 'asc'
          ? compareA.localeCompare(compareB)
          : compareB.localeCompare(compareA)
      }

      const numA = typeof compareA === 'number' ? compareA : 0
      const numB = typeof compareB === 'number' ? compareB : 0

      return sortDirection.value === 'asc' ? numA - numB : numB - numA
    })

    return sorted
  })

  /**
   * Retorna el usuario con mejor rendimiento
   * Basado en el ordenamiento actual
   */
  const topPerformer = computed((): UserPerformance | undefined => {
    if (sortDirection.value === 'desc') {
      return sortedPerformance.value[0]
    }
    return sortedPerformance.value[sortedPerformance.value.length - 1]
  })

  /**
   * Retorna el promedio general de velocidad de todo el equipo
   */
  const teamAverageVelocity = computed((): number => {
    if (performance.value.length === 0) return 0
    const totalVelocity = performance.value.reduce((sum, p) => sum + (p.velocity || 0), 0)
    return totalVelocity / performance.value.length
  })

  /**
   * Retorna el porcentaje promedio de bloqueos en el equipo
   */
  const teamBlockedRate = computed((): number => {
    if (performance.value.length === 0) return 0
    const totalBlocked = performance.value.reduce((sum, p) => sum + p.blockedTickets, 0)
    const totalTickets = performance.value.reduce((sum, p) => sum + p.totalTickets, 0)
    
    if (totalTickets === 0) return 0
    return Math.round((totalBlocked / totalTickets) * 100)
  })

  /**
   * Retorna el tiempo promedio de finalización en horas
   */
  const teamAverageCompletionTime = computed((): number => {
    if (performance.value.length === 0) return 0
    const totalTime = performance.value.reduce((sum, p) => sum + (p.averageCompletionTime || 0), 0)
    return totalTime / performance.value.length
  })

  // ========== ACCIONES ==========

  /**
   * Obtiene el resumen analítico de una aplicación específica
   * Incluye métricas como: tickets totales, completados, en progreso, bloqueados, etc.
   * 
   * @param appId - ID de la aplicación
   * @returns Promise<AnalyticsSummary>
   */
  const fetchSummary = async (appId: string): Promise<AnalyticsSummary> => {
    isLoading.value = true
    error.value = null

    try {
      const data = await api.analytics.getSummary(appId)
      summary.value = data
      return data
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al obtener resumen analítico'
      error.value = message
      console.error('Error en fetchSummary:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Obtiene datos de rendimiento por usuario para una aplicación
   * Incluye métricas individuales y comparativas
   * 
   * PARÁMETROS DE FECHA:
   * - from: fecha de inicio (ISO string o Date)
   * - to: fecha de fin (ISO string o Date)
   * 
   * @param appId - ID de la aplicación
   * @param from - Fecha de inicio del rango
   * @param to - Fecha de fin del rango
   * @returns Promise<UserPerformance[]>
   */
  const fetchPerformance = async (
    appId: string,
    from: Date | string = dateRange.value.from,
    to: Date | string = dateRange.value.to
  ): Promise<UserPerformance[]> => {
    isLoading.value = true
    error.value = null

    try {
      const fromStr = typeof from === 'string' ? from : from.toISOString()
      const toStr = typeof to === 'string' ? to : to.toISOString()

      const data = await api.analytics.getPerformance(appId, fromStr, toStr)
      performance.value = data
      return data
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al obtener rendimiento'
      error.value = message
      console.error('Error en fetchPerformance:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Obtiene datos de mapa de calor de actividad
   * Mostrado típicamente en una vista de calendario
   * 
   * El mapa de calor muestra:
   * - Fecha
   * - Número de eventos (commits, PRs, comentarios, etc.)
   * - Intensidad (escala de color)
   * 
   * @param appId - ID de la aplicación
   * @param from - Fecha de inicio
   * @param to - Fecha de fin
   * @returns Promise<HeatmapEntry[]>
   */
  const fetchHeatmap = async (
    appId: string,
    from: Date | string = dateRange.value.from,
    to: Date | string = dateRange.value.to
  ): Promise<HeatmapEntry[]> => {
    isLoading.value = true
    error.value = null

    try {
      const fromStr = typeof from === 'string' ? from : from.toISOString()
      const toStr = typeof to === 'string' ? to : to.toISOString()

      const data = await api.analytics.getHeatmap(appId, fromStr, toStr)
      heatmapData.value = data
      return data
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al obtener mapa de calor'
      error.value = message
      console.error('Error en fetchHeatmap:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Obtiene datos de burndown para un épico específico
   * 
   * El burndown chart muestra:
   * - Fecha
   * - Trabajo restante (tickets pendientes)
   * - Línea de tendencia ideal
   * 
   * Se usa para visualizar si un épico está en camino o retrasado
   * 
   * @param epicId - ID del épico
   * @returns Promise<BurndownData[]>
   */
  const fetchBurndown = async (epicId: string): Promise<BurndownData[]> => {
    isLoading.value = true
    error.value = null

    try {
      const data = await api.analytics.getBurndown(epicId)
      burndownData.value = data
      return data
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al obtener burndown'
      error.value = message
      console.error('Error en fetchBurndown:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Establece el rango de fechas para los filtros analíticos
   * Se usa cuando el usuario cambia el rango en el UI
   * 
   * Ejemplo:
   * - Últimos 7 días
   * - Últimos 30 días
   * - Este mes
   * - Personalizado
   * 
   * @param from - Fecha de inicio
   * @param to - Fecha de fin
   */
  const setDateRange = (from: Date, to: Date): void => {
    dateRange.value = { from, to }
  }

  /**
   * Establece el rango a los últimos N días
   * 
   * @param days - Número de días atrás
   */
  const setDateRangeLastDays = (days: number): void => {
    const to = new Date()
    const from = new Date(to)
    from.setDate(from.getDate() - days)
    setDateRange(from, to)
  }

  /**
   * Cambia la columna por la que ordenar
   * Si es la misma columna, invierte la dirección
   * 
   * @param column - Columna a ordenar
   */
  const setSortColumn = (column: SortColumn): void => {
    if (sortColumn.value === column) {
      sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
    } else {
      sortColumn.value = column
      sortDirection.value = 'desc' // Default descendente para columnas numéricas
    }
  }

  /**
   * Establece la dirección de ordenamiento manualmente
   * 
   * @param direction - 'asc' o 'desc'
   */
  const setSortDirection = (direction: SortDirection): void => {
    sortDirection.value = direction
  }

  /**
   * Exporta un reporte en formato CSV
   * Se descarga automáticamente en el navegador del usuario
   * 
   * CONTENIDO DEL CSV:
   * - Resumen de aplicación
   * - Datos de rendimiento por usuario
   * - Métricas generales
   * 
   * @param appId - ID de la aplicación
   * @returns Promise<void>
   */
  const exportCsv = async (appId: string): Promise<void> => {
    isLoading.value = true
    error.value = null

    try {
      // La API retorna un blob con el contenido CSV
      const csvContent = await api.analytics.exportCsv(appId)
      
      // Crear blob y descargar
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      
      link.setAttribute('href', url)
      link.setAttribute('download', `analytics-${appId}-${Date.now()}.csv`)
      link.style.visibility = 'hidden'
      
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al exportar CSV'
      error.value = message
      console.error('Error en exportCsv:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Exporta un reporte en formato PDF
   * Se descarga automáticamente en el navegador del usuario
   * 
   * @param appId - ID de la aplicación
   * @returns Promise<void>
   */
  const exportPdf = async (appId: string): Promise<void> => {
    isLoading.value = true
    error.value = null

    try {
      const pdfContent = await api.analytics.exportPdf(appId)
      
      const blob = new Blob([pdfContent], { type: 'application/pdf' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      
      link.setAttribute('href', url)
      link.setAttribute('download', `analytics-${appId}-${Date.now()}.pdf`)
      link.style.visibility = 'hidden'
      
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al exportar PDF'
      error.value = message
      console.error('Error en exportPdf:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Limpia el estado del store (para cuando se cambia de aplicación)
   */
  const clear = (): void => {
    summary.value = null
    performance.value = []
    heatmapData.value = []
    burndownData.value = []
    error.value = null
  }

  return {
    // Estado
    summary,
    performance,
    heatmapData,
    burndownData,
    isLoading,
    error,
    dateRange,
    sortColumn,
    sortDirection,
    // Getters
    sortedPerformance,
    topPerformer,
    teamAverageVelocity,
    teamBlockedRate,
    teamAverageCompletionTime,
    // Acciones
    fetchSummary,
    fetchPerformance,
    fetchHeatmap,
    fetchBurndown,
    setDateRange,
    setDateRangeLastDays,
    setSortColumn,
    setSortDirection,
    exportCsv,
    exportPdf,
    clear,
  }
})
