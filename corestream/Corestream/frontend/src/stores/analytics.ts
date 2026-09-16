/**
 * Store de Analíticas - CoreStream
 * Gestiona datos analíticos y reportes de rendimiento
 * 
 * Responsabilidades:
 * - Obtener resumen analítico de aplicaciones
 * - Recopilar datos de rendimiento de usuarios
 * - Generar mapas de calor de actividad
 * - Calcular datos de burndown para épicos
 * - Ordenar y filtrar datos analíticos
 */
 
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  AnalyticsSummary,
  UserPerformance,
  HeatmapData,
  BurndownData,
  SupportSummary,
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
  const heatmapData = ref<HeatmapData[]>([])

  /**
   * Datos de burndown para un épico específico
   * Usado para gráficos de progreso en el tiempo
   */
  const burndownData = ref<BurndownData | null>(null)

  /**
   * Resumen agregado de tickets de soporte (global, independiente de aplicación).
   */
  const supportSummary = ref<SupportSummary | null>(null)

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
    const perf = Array.isArray(performance.value) ? performance.value : []
    const sorted = [...perf].sort((a, b) => {
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
          compareA = a.blockedPercentage || 0
          compareB = b.blockedPercentage || 0
          break
        case 'avgCompletionTime':
          compareA = a.averageHoursPerTicket || 0
          compareB = b.averageHoursPerTicket || 0
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
    const total = performance.value.reduce((sum, p) => sum + (p.blockedPercentage || 0), 0)
    return Math.round(total / performance.value.length)
  })

  /**
   * Retorna el tiempo promedio de finalización en horas
   */
  const teamAverageCompletionTime = computed((): number => {
    if (performance.value.length === 0) return 0
    const totalTime = performance.value.reduce((sum, p) => sum + (p.averageHoursPerTicket || 0), 0)
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
  const fetchSummary = async (appId: string): Promise<AnalyticsSummary | undefined> => {
    isLoading.value = true
    error.value = null

    try {
      const res = await api.analytics.getSummary({
        applicationId: appId,
        startDate: dateRange.value.from.toISOString(),
        endDate: dateRange.value.to.toISOString()
      })
      const data: AnalyticsSummary = (res as any)?.data ?? res as unknown as AnalyticsSummary
      summary.value = data
      return data
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al obtener resumen analítico'
      error.value = message
      summary.value = null
      console.error('Error en fetchSummary:', err)
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
  ): Promise<UserPerformance[] | undefined> => {
    isLoading.value = true
    error.value = null

    try {
      const fromStr = typeof from === 'string' ? from : from.toISOString()
      const toStr = typeof to === 'string' ? to : to.toISOString()

      const res = await api.analytics.getPerformance({ applicationId: appId, startDate: fromStr, endDate: toStr })
      const data: UserPerformance[] = Array.isArray(res) ? res : (res as any).data
      performance.value = data
      return data
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al obtener rendimiento'
      error.value = message
      performance.value = []
      console.error('Error en fetchPerformance:', err)
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
   * @returns Promise<HeatmapData[]>
   */
  const fetchHeatmap = async (
    appId: string,
    from: Date | string = dateRange.value.from,
    to: Date | string = dateRange.value.to
  ): Promise<HeatmapData[] | undefined> => {
    isLoading.value = true
    error.value = null

    try {
      const fromStr = typeof from === 'string' ? from : from.toISOString()
      const toStr = typeof to === 'string' ? to : to.toISOString()

      // Llamamos a la API con el appId
      const res = await api.analytics.getHeatmap(appId, { startDate: fromStr, endDate: toStr })

      // El backend de tu compañero devuelve { application_id, heatmap: [...] }
      const rawData = res?.heatmap || res?.data?.heatmap || []
      
      const mappedData: HeatmapData[] = rawData.map((item: any) => ({
        name: item.name || 'Desconocido',
        values: item.data || item.values || [0, 0, 0, 0, 0, 0, 0],
        dates: [] 
      }))

      heatmapData.value = mappedData
      return mappedData
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al obtener mapa de calor'
      error.value = message
      heatmapData.value = []
      console.error('Error en fetchHeatmap:', err)
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
  const fetchBurndown = async (epicId: string): Promise<BurndownData | null> => {
    isLoading.value = true
    error.value = null

    try {
      const res = await api.analytics.getBurndown(epicId)
      const data: BurndownData = (res as any)?.data ?? res as unknown as BurndownData
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
   * Carga TODOS los datos analíticos de una app en paralelo
   * @param appId - ID de la aplicación
   */
  const fetchAllData = async (appId: string): Promise<void> => {
    isLoading.value = true
    try {
      await Promise.all([
        fetchSummary(appId),
        fetchPerformance(appId),
        fetchHeatmap(appId)
      ])
    } catch (err) {
      console.error('Error cargando analíticas globales:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Obtiene el resumen de tickets de soporte (conteos por estado/severidad y
   * tiempo promedio de resolución). No depende de la aplicación seleccionada.
   *
   * @returns Promise<SupportSummary | undefined>
   */
  const fetchSupportSummary = async (): Promise<SupportSummary | undefined> => {
    try {
      const data = await api.analytics.getSupportSummary()
      supportSummary.value = data
      return data
    } catch (err) {
      console.error('Error en fetchSupportSummary:', err)
      supportSummary.value = null
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
   * Limpia el estado del store (para cuando se cambia de aplicación)
   */
  const clear = (): void => {
    summary.value = null
    performance.value = []
    heatmapData.value = []
    burndownData.value = null
    error.value = null
  }

  return {
    // Estado
    summary,
    performance,
    heatmapData,
    burndownData,
    supportSummary,
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
    fetchAllData,
    fetchSupportSummary,
    setDateRange,
    setDateRangeLastDays,
    setSortColumn,
    setSortDirection,
    clear,
  }
})
