<template>
  <!-- 
    COMPONENTE: Heatmap
    DESCRIPCIÓN: Visualización en forma de matriz de calor para analizar actividad de desarrolladores:
    - Eje X: Días de la semana (Lunes a Domingo)
    - Eje Y: Nombres de desarrolladores
    - Intensidad de color: Cantidad de tickets cerrados
    - Escala de color: Blanco (menos) a Verde profundo (más)
    - Tooltips en hover mostrando cantidad exacta de tickets
    - Totales de filas y columnas
    - Análisis de patrón al pie
    
    CARACTERÍSTICAS:
    - Grid interactivo con colores dinámicos
    - Tooltips informativos al pasar el mouse
    - Detección automática de patrones (ej: "Actividad baja los viernes")
    - Totales por desarrollador y por día
    - Escala de colores suave y gradual
  -->
  <div class="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6">
    <!-- ENCABEZADO -->
    <div class="mb-6">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">{{ $t('analytics.heatmap') }}</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400">{{ $t('analytics.heatmapDescription') }}</p>
    </div>

    <!-- CONTENEDOR DE LA MATRIZ CON SCROLL -->
    <div class="overflow-x-auto mb-6">
      <!-- TABLA DE MATRIZ DE CALOR -->
      <table class="w-full border-collapse">
        <thead>
          <tr>
            <!-- Esquina superior izquierda (vacío) -->
            <th class="w-32 h-10 border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700"></th>
            
            <!-- Encabezados de días de la semana -->
            <th 
              v-for="(day, index) in daysOfWeek"
              :key="index"
              class="w-20 h-10 border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700 text-xs font-semibold text-gray-700 dark:text-gray-300"
            >
              {{ $t(`days.${day.toLowerCase()}`) }}
            </th>
            
            <!-- Columna de totales por fila -->
            <th class="w-16 h-10 border border-gray-200 dark:border-gray-700 bg-blue-50 dark:bg-blue-900 text-xs font-semibold text-blue-700 dark:text-blue-300">
              {{ $t('analytics.total') }}
            </th>
          </tr>
        </thead>

        <tbody>
          <!-- FILAS: Desarrolladores -->
          <tr v-for="(developer, devIndex) in developers" :key="devIndex">
            <!-- NOMBRE DEL DESARROLLADOR -->
            <td class="px-3 py-2 border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700 font-medium text-sm text-gray-900 dark:text-white whitespace-nowrap">
              <div class="flex items-center gap-2">
                <img 
                  :src="developer.avatar"
                  :alt="developer.name"
                  class="w-6 h-6 rounded-full"
                />
                <span class="truncate">{{ developer.name }}</span>
              </div>
            </td>

            <!-- CELDAS DE MATRIZ (Intensidad según tickets cerrados) -->
            <td 
              v-for="(dayIndex) in Array.from({ length: 7 })"
              :key="dayIndex"
              class="w-20 h-16 border border-gray-200 dark:border-gray-700 p-2 relative group cursor-pointer transition-all duration-200 hover:shadow-md"
              :style="{ 
                backgroundColor: getHeatmapColor(heatmapData[devIndex][dayIndex as number])
              }"
            >
              <!-- VALOR EN LA CELDA -->
              <div class="text-center h-full flex items-center justify-center">
                <span class="text-sm font-semibold" :class="getTextColorClass(heatmapData[devIndex][dayIndex as number])">
                  {{ heatmapData[devIndex][dayIndex as number] }}
                </span>
              </div>

              <!-- TOOLTIP AL PASAR EL MOUSE -->
              <div class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 dark:bg-gray-950 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap z-10 pointer-events-none">
                {{ heatmapData[devIndex][dayIndex as number] }} {{ $t('analytics.ticketsClosedShort') }}
                <div class="absolute top-full left-1/2 transform -translate-x-1/2 w-2 h-2 bg-gray-900 dark:bg-gray-950"></div>
              </div>
            </td>

            <!-- TOTAL POR FILA (Desarrollador) -->
            <td class="px-3 py-2 border border-gray-200 dark:border-gray-700 bg-blue-50 dark:bg-blue-900 font-semibold text-sm text-blue-900 dark:text-blue-100">
              {{ getRowTotal(devIndex) }}
            </td>
          </tr>

          <!-- FILA DE TOTALES POR COLUMNA (Día) -->
          <tr>
            <!-- Etiqueta "Totales" -->
            <td class="px-3 py-2 border border-gray-200 dark:border-gray-700 bg-green-50 dark:bg-green-900 font-semibold text-sm text-green-900 dark:text-green-100">
              {{ $t('analytics.daily') }}
            </td>

            <!-- Totales por día -->
            <td 
              v-for="(dayIndex) in Array.from({ length: 7 })"
              :key="'total-' + dayIndex"
              class="px-3 py-2 border border-gray-200 dark:border-gray-700 bg-green-50 dark:bg-green-900 font-semibold text-sm text-green-900 dark:text-green-100 text-center"
            >
              {{ getColumnTotal(dayIndex as number) }}
            </td>

            <!-- Total general -->
            <td class="px-3 py-2 border border-gray-200 dark:border-gray-700 bg-purple-50 dark:bg-purple-900 font-bold text-sm text-purple-900 dark:text-purple-100">
              {{ getTotalAll() }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- LEYENDA DE COLORES -->
    <div class="mb-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
      <p class="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-3">{{ $t('analytics.colorScale') }}:</p>
      <div class="flex items-center gap-4 flex-wrap">
        <div class="flex items-center gap-2">
          <div class="w-6 h-6 rounded border border-gray-300" style="background-color: rgb(255, 255, 255)"></div>
          <span class="text-xs text-gray-600 dark:text-gray-400">{{ $t('analytics.low') }}</span>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-6 h-6 rounded border border-gray-300" style="background-color: rgb(200, 230, 201)"></div>
          <span class="text-xs text-gray-600 dark:text-gray-400">{{ $t('analytics.medium') }}</span>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-6 h-6 rounded border border-gray-300" style="background-color: rgb(76, 175, 80)"></div>
          <span class="text-xs text-gray-600 dark:text-gray-400">{{ $t('analytics.high') }}</span>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-6 h-6 rounded border border-gray-300" style="background-color: rgb(27, 94, 32)"></div>
          <span class="text-xs text-gray-600 dark:text-gray-400">{{ $t('analytics.veryHigh') }}</span>
        </div>
      </div>
    </div>

    <!-- ANÁLISIS DE PATRÓN -->
    <div class="p-4 bg-blue-50 dark:bg-blue-900 rounded-lg border-l-4 border-blue-500">
      <div class="flex gap-3">
        <!-- Icono de bombilla -->
        <svg class="w-5 h-5 text-blue-600 dark:text-blue-300 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
          <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1011.586 11.586z" />
        </svg>
        <div>
          <p class="text-sm font-semibold text-blue-900 dark:text-blue-100 mb-1">{{ $t('analytics.insight') }}</p>
          <p class="text-sm text-blue-800 dark:text-blue-200">{{ patternInsight }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * ESTRUCTURA DEL SCRIPT PARA COMPONENTE HEATMAP:
 * 1. Imports necesarios
 * 2. Tipos e interfaces
 * 3. Inicialización de composables y stores
 * 4. Datos reactivos
 * 5. Propiedades computadas
 * 6. Funciones auxiliares de cálculo
 * 7. Funciones de colorización
 * 8. Ciclo de vida
 */

import { ref, computed, onMounted } from 'vue'
import { useAnalyticsStore } from '@/stores/analytics'
import { useI18n } from 'vue-i18n'

// TIPOS: Interfaz para datos de desarrollador
interface Developer {
  id: string
  name: string
  avatar: string
}

// INICIALIZACIÓN
const analyticsStore = useAnalyticsStore()
const { t } = useI18n()

// REFERENCIAS REACTIVAS
const daysOfWeek = ref(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
const developers = ref<Developer[]>([])
const heatmapData = ref<number[][]>([])

/**
 * FUNCIÓN: getHeatmapColor
 * DESCRIPCIÓN: Calcula el color de una celda basado en la cantidad de tickets
 * PARÁMETRO: value - número de tickets cerrados
 * RETORNA: Código hexadecimal del color o rgb()
 * LÓGICA:
 * - 0 tickets: Blanco
 * - 1-5 tickets: Verde claro
 * - 6-15 tickets: Verde medio
 * - 16+ tickets: Verde oscuro
 */
function getHeatmapColor(value: number): string {
  if (value === 0) {
    return '#ffffff'
  } else if (value < 5) {
    return '#c8e6c9'
  } else if (value < 15) {
    return '#4caf50'
  } else {
    return '#1b5e20'
  }
}

/**
 * FUNCIÓN: getTextColorClass
 * DESCRIPCIÓN: Retorna clases para el color de texto según el fondo
 * LÓGICA: Texto oscuro para fondos claros, texto claro para fondos oscuros
 */
function getTextColorClass(value: number): string {
  if (value === 0 || value < 5) {
    return 'text-gray-700'
  } else {
    return 'text-white'
  }
}

/**
 * FUNCIÓN: getRowTotal
 * DESCRIPCIÓN: Calcula el total de tickets para un desarrollador (suma de todos los días)
 * PARÁMETRO: rowIndex - índice de la fila (desarrollador)
 * RETORNA: Suma total de tickets del desarrollador
 */
function getRowTotal(rowIndex: number): number {
  return heatmapData.value[rowIndex].reduce((sum, val) => sum + val, 0)
}

/**
 * FUNCIÓN: getColumnTotal
 * DESCRIPCIÓN: Calcula el total de tickets para un día (suma de todos los desarrolladores)
 * PARÁMETRO: colIndex - índice de la columna (día)
 * RETORNA: Suma total de tickets del día
 */
function getColumnTotal(colIndex: number): number {
  return heatmapData.value.reduce((sum, row) => sum + row[colIndex], 0)
}

/**
 * FUNCIÓN: getTotalAll
 * DESCRIPCIÓN: Calcula el total general de tickets en toda la matriz
 * RETORNA: Suma total de todos los tickets
 */
function getTotalAll(): number {
  return heatmapData.value.reduce((total, row) => total + row.reduce((sum, val) => sum + val, 0), 0)
}

/**
 * PROPIEDAD COMPUTADA: patternInsight
 * DESCRIPCIÓN: Analiza patrones en los datos y retorna un insight significativo
 * LÓGICA:
 * - Detecta días con baja actividad
 * - Detecta desarrolladores con patrón consistente
 * - Genera mensaje en i18n basado en patrones detectados
 */
const patternInsight = computed<string>(() => {
  // Encontrar día con menos tickets
  const dailyTotals = Array.from({ length: 7 }, (_, i) => getColumnTotal(i))
  const minDay = dailyTotals.indexOf(Math.min(...dailyTotals))
  const dayName = daysOfWeek.value[minDay].toLowerCase()
  
  // Mensaje base
  return t('analytics.lowActivityPattern', { day: t(`days.${dayName}`) })
})

/**
 * CICLO DE VIDA: onMounted
 * RESPONSABILIDADES:
 * - Cargar datos de heatmap desde el store
 * - Inicializar la matriz de datos
 * - Cargar información de desarrolladores
 */
onMounted(async () => {
  try {
    // Cargar datos del store
    await analyticsStore.fetchHeatmap()
    
    // Inicializar datos de desarrolladores (simulado, en producción venir del store)
    developers.value = [
      { id: '1', name: 'Juan García', avatar: 'https://i.pravatar.cc/40?u=juan' },
      { id: '2', name: 'María López', avatar: 'https://i.pravatar.cc/40?u=maria' },
      { id: '3', name: 'Carlos Martínez', avatar: 'https://i.pravatar.cc/40?u=carlos' },
      { id: '4', name: 'Ana Rodríguez', avatar: 'https://i.pravatar.cc/40?u=ana' },
    ]
    
    // Inicializar matriz con datos aleatorios (en producción venir del store)
    heatmapData.value = [
      [8, 12, 15, 10, 3, 5, 4],  // Juan García
      [10, 14, 12, 11, 2, 3, 6], // María López
      [6, 9, 8, 7, 4, 2, 3],     // Carlos Martínez
      [12, 15, 13, 9, 5, 7, 5],  // Ana Rodríguez
    ]
  } catch (error) {
    console.error('Error cargando datos de heatmap:', error)
  }
})
</script>

<style scoped>
/* Estilos personalizados para matriz de calor */

/* Animación de hover para las celdas */
@keyframes heatmapPulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.3);
  }
  50% {
    box-shadow: 0 0 0 4px rgba(59, 130, 246, 0);
  }
}

/* Transición suave de colores */
:deep(table td) {
  transition: background-color 0.3s ease;
}
</style>
