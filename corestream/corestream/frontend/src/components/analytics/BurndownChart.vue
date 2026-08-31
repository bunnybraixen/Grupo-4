<template>
  <!-- 
    COMPONENTE: BurndownChart
    DESCRIPCIÓN: Gráfico de línea que visualiza la tendencia de tickets completados vs. línea ideal
    - Dos líneas: Ideal (punteada gris) y Actual (línea azul sólida)
    - Eje X: Fechas del período
    - Eje Y: Tickets pendientes
    - Selector de épica para filtrar datos
    - Leyenda interactiva
    - Información de velocidad y proyección de finalización
    
    CARACTERÍSTICAS:
    - Gráfico interactivo usando Chart.js/vue-chartjs
    - Selector dropdown para cambiar épica
    - Animación suave de datos
    - Tooltips informativos al pasar el mouse
    - Indicador de si se está adelante/atrás de lo planeado
    - Información de velocidad promedio
  -->
  <div class="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6">
    <!-- ENCABEZADO CON SELECTOR -->
    <div class="flex justify-between items-center mb-6">
      <div>
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">{{ $t('analytics.burndownChart') }}</h3>
        <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">{{ $t('analytics.burndownDescription') }}</p>
      </div>

      <!-- SELECTOR DE ÉPICA -->
      <div class="flex gap-2">
        <select 
          v-model="selectedEpic"
          @change="onEpicChange"
          class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm font-medium hover:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">{{ $t('filters.allEpics') }}</option>
          <option v-for="epic in epics" :key="epic.id" :value="epic.id">
            {{ epic.name }}
          </option>
        </select>
      </div>
    </div>

    <!-- CONTENEDOR DEL GRÁFICO -->
    <div class="relative h-96 mb-6">
      <canvas ref="chartCanvas"></canvas>
    </div>

    <!-- INFORMACIÓN ADICIONAL -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <!-- CARD: Velocidad Promedio -->
      <div class="p-4 bg-blue-50 dark:bg-blue-900 rounded-lg border border-blue-200 dark:border-blue-700">
        <p class="text-xs font-semibold text-blue-700 dark:text-blue-300 uppercase mb-1">{{ $t('analytics.averageVelocity') }}</p>
        <p class="text-2xl font-bold text-blue-900 dark:text-blue-100">{{ avgVelocity }}</p>
        <p class="text-xs text-blue-600 dark:text-blue-400 mt-1">{{ $t('analytics.ticketsPerDay') }}</p>
      </div>

      <!-- CARD: Tiempo Estimado -->
      <div class="p-4 bg-green-50 dark:bg-green-900 rounded-lg border border-green-200 dark:border-green-700">
        <p class="text-xs font-semibold text-green-700 dark:text-green-300 uppercase mb-1">{{ $t('analytics.estimatedCompletion') }}</p>
        <p class="text-2xl font-bold text-green-900 dark:text-green-100">{{ estimatedDays }}</p>
        <p class="text-xs text-green-600 dark:text-green-400 mt-1">{{ $t('analytics.daysRemaining') }}</p>
      </div>

      <!-- CARD: Estado -->
      <div class="p-4" :class="statusClass">
        <p class="text-xs font-semibold uppercase mb-1" :class="statusTextClass">{{ $t('analytics.status') }}</p>
        <p class="text-2xl font-bold" :class="statusTextClass">{{ status }}</p>
        <p class="text-xs mt-1" :class="statusTextClass">{{ statusMessage }}</p>
      </div>
    </div>

    <!-- LEYENDA DEL GRÁFICO -->
    <div class="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700 flex gap-6">
      <!-- Línea Ideal -->
      <div class="flex items-center gap-2">
        <div class="w-4 h-1 bg-gray-400 rounded" style="border-top: 2px dashed currentColor;"></div>
        <span class="text-sm text-gray-600 dark:text-gray-400">{{ $t('analytics.idealLine') }}</span>
      </div>

      <!-- Línea Actual -->
      <div class="flex items-center gap-2">
        <div class="w-4 h-1 bg-blue-500 rounded"></div>
        <span class="text-sm text-gray-600 dark:text-gray-400">{{ $t('analytics.actualLine') }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * ESTRUCTURA DEL SCRIPT:
 * 1. Imports de librerías (Chart.js, vue-chartjs)
 * 2. Tipos e interfaces para datos
 * 3. Inicialización de stores y composables
 * 4. Referencias reactivas
 * 5. Propiedades computadas para cálculos
 * 6. Funciones de gráfico y utilidad
 * 7. Ciclo de vida
 */

import { ref, computed, onMounted, watch } from 'vue'
import { useAnalyticsStore } from '@/stores/analytics'
import { useEpicsStore } from '@/stores/epics'
import { useI18n } from 'vue-i18n'
import Chart from 'chart.js/auto'

// TIPOS
interface Epic {
  id: string
  name: string
}

interface BurndownData {
  dates: string[]
  ideal: number[]
  actual: number[]
}

// INICIALIZACIÓN
const analyticsStore = useAnalyticsStore()
const epicsStore = useEpicsStore()
const { t } = useI18n()

// REFERENCIAS REACTIVAS
const chartCanvas = ref<HTMLCanvasElement | null>(null)
const selectedEpic = ref('')
const epics = ref<Epic[]>([
  { id: '1', name: 'Epic Sprint 1' },
  { id: '2', name: 'Epic Sprint 2' },
  { id: '3', name: 'Mejoras UI' },
])
let chart: Chart | null = null

// DATOS SIMULADOS (En producción, vendrían del store)
const burndownData = ref<BurndownData>({
  dates: ['Día 1', 'Día 2', 'Día 3', 'Día 4', 'Día 5', 'Día 6', 'Día 7'],
  ideal: [100, 85, 70, 55, 40, 25, 10],
  actual: [95, 90, 75, 60, 50, 35, 22],
})

/**
 * PROPIEDAD COMPUTADA: avgVelocity
 * DESCRIPCIÓN: Calcula la velocidad promedio (tickets completados por día)
 * FÓRMULA: (Inicial - Actual) / número de días
 */
const avgVelocity = computed<number>(() => {
  if (!burndownData.value.actual.length) return 0
  const initial = burndownData.value.ideal[0]
  const current = burndownData.value.actual[burndownData.value.actual.length - 1]
  const ticketsCompleted = initial - current
  const days = burndownData.value.dates.length
  return Math.round((ticketsCompleted / days) * 10) / 10
})

/**
 * PROPIEDAD COMPUTADA: estimatedDays
 * DESCRIPCIÓN: Estima días faltantes basado en velocidad actual
 * CÁLCULO: tickets restantes / velocidad promedio
 */
const estimatedDays = computed<number>(() => {
  const remaining = burndownData.value.actual[burndownData.value.actual.length - 1]
  return avgVelocity.value > 0 ? Math.ceil(remaining / avgVelocity.value) : 0
})

/**
 * PROPIEDAD COMPUTADA: status
 * DESCRIPCIÓN: Determina si está adelante o atrasado
 */
const status = computed<string>(() => {
  const actualLast = burndownData.value.actual[burndownData.value.actual.length - 1]
  const idealLast = burndownData.value.ideal[burndownData.value.ideal.length - 1]
  
  if (actualLast <= idealLast) {
    return t('analytics.onTrack')
  } else {
    return t('analytics.behindSchedule')
  }
})

/**
 * PROPIEDAD COMPUTADA: statusMessage
 * DESCRIPCIÓN: Mensaje detallado del estado
 */
const statusMessage = computed<string>(() => {
  const actualLast = burndownData.value.actual[burndownData.value.actual.length - 1]
  const idealLast = burndownData.value.ideal[burndownData.value.ideal.length - 1]
  const diff = Math.abs(actualLast - idealLast)
  
  if (actualLast <= idealLast) {
    return t('analytics.statusAhead', { tickets: diff })
  } else {
    return t('analytics.statusBehind', { tickets: diff })
  }
})

/**
 * PROPIEDAD COMPUTADA: statusClass
 * DESCRIPCIÓN: Clases Tailwind para el color de fondo del estado
 */
const statusClass = computed<string>(() => {
  const actualLast = burndownData.value.actual[burndownData.value.actual.length - 1]
  const idealLast = burndownData.value.ideal[burndownData.value.ideal.length - 1]
  
  if (actualLast <= idealLast) {
    return 'bg-green-50 dark:bg-green-900 border border-green-200 dark:border-green-700'
  } else {
    return 'bg-orange-50 dark:bg-orange-900 border border-orange-200 dark:border-orange-700'
  }
})

/**
 * PROPIEDAD COMPUTADA: statusTextClass
 * DESCRIPCIÓN: Clases para el color de texto del estado
 */
const statusTextClass = computed<string>(() => {
  const actualLast = burndownData.value.actual[burndownData.value.actual.length - 1]
  const idealLast = burndownData.value.ideal[burndownData.value.ideal.length - 1]
  
  if (actualLast <= idealLast) {
    return 'text-green-700 dark:text-green-300'
  } else {
    return 'text-orange-700 dark:text-orange-300'
  }
})

/**
 * FUNCIÓN: initChart
 * DESCRIPCIÓN: Inicializa o actualiza el gráfico de burndown
 * RESPONSABILIDADES:
 * - Crear instancia de Chart.js
 * - Configurar datasets para línea ideal y actual
 * - Aplicar estilos y colores
 * - Incluir opciones de interpolación y animación
 */
function initChart() {
  if (!chartCanvas.value) return

  // Destruir gráfico anterior si existe
  if (chart) {
    chart.destroy()
  }

  const ctx = chartCanvas.value.getContext('2d')
  if (!ctx) return

  chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: burndownData.value.dates,
      datasets: [
        {
          // LÍNEA IDEAL (Punteada gris)
          label: t('analytics.ideal'),
          data: burndownData.value.ideal,
          borderColor: '#9CA3AF',
          backgroundColor: 'rgba(156, 163, 175, 0.05)',
          borderWidth: 2,
          borderDash: [5, 5],
          pointRadius: 4,
          pointBackgroundColor: '#9CA3AF',
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
          pointHoverRadius: 6,
          tension: 0.4,
        },
        {
          // LÍNEA ACTUAL (Línea azul sólida)
          label: t('analytics.actual'),
          data: burndownData.value.actual,
          borderColor: '#3B82F6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          borderWidth: 3,
          pointRadius: 5,
          pointBackgroundColor: '#3B82F6',
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
          pointHoverRadius: 7,
          tension: 0.4,
          fill: true,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top' as const,
          labels: {
            usePointStyle: true,
            padding: 15,
            font: {
              size: 12,
              weight: '500',
            },
            color: '#6B7280',
          },
        },
        tooltip: {
          backgroundColor: '#1F2937',
          padding: 12,
          titleFont: { size: 12, weight: 'bold' },
          bodyFont: { size: 11 },
          borderColor: '#3B82F6',
          borderWidth: 1,
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: t('analytics.ticketsRemaining'),
            color: '#6B7280',
          },
          ticks: {
            color: '#6B7280',
            font: { size: 11 },
          },
          grid: {
            color: '#E5E7EB',
            drawBorder: false,
          },
        },
        x: {
          title: {
            display: true,
            text: t('analytics.date'),
            color: '#6B7280',
          },
          ticks: {
            color: '#6B7280',
            font: { size: 11 },
          },
          grid: {
            display: false,
            drawBorder: false,
          },
        },
      },
    },
  })
}

/**
 * FUNCIÓN: onEpicChange
 * DESCRIPCIÓN: Manejador de cambio de épica
 * RESPONSABILIDADES:
 * - Cargar nuevos datos de burndown para épica seleccionada
 * - Actualizar el gráfico
 */
async function onEpicChange() {
  try {
    if (selectedEpic.value) {
      await analyticsStore.fetchBurndown(selectedEpic.value)
    } else {
      // Cargar todos los épicos
      await analyticsStore.fetchBurndown()
    }
    // Actualizar gráfico con nuevos datos
    initChart()
  } catch (error) {
    console.error('Error cambiando épica:', error)
  }
}

/**
 * CICLO DE VIDA: onMounted
 * RESPONSABILIDADES:
 * - Cargar datos iniciales
 * - Inicializar el gráfico
 * - Cargar lista de épicas
 */
onMounted(async () => {
  try {
    // Cargar datos de burndown
    await analyticsStore.fetchBurndown()
    
    // Cargar lista de épicas
    await epicsStore.fetchByApp('')
    
    // Inicializar gráfico
    setTimeout(() => initChart(), 0)
  } catch (error) {
    console.error('Error cargando gráfico de burndown:', error)
  }
})

/**
 * WATCHER: Monitorea cambios en datos de burndown del store
 * RESPONSABILIDADES:
 * - Actualizar datos locales cuando cambia el store
 * - Re-inicializar gráfico con nuevos datos
 */
watch(
  () => analyticsStore.burndownData,
  (newData) => {
    if (newData) {
      burndownData.value = newData
      initChart()
    }
  }
)
</script>

<style scoped>
/* Estilos específicos del componente de gráfico */

/* Animación de carga del gráfico */
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

:deep(canvas) {
  animation: slideUp 0.5s ease-out;
}
</style>
