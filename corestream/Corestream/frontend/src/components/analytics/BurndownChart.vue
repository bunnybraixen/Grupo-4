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
  <!-- Contenedor Principal -->
  <div class="bg-[var(--bg-card)] rounded-xl shadow-sm border border-[var(--border-subtle)] p-6 mb-8">
    
    <!-- ENCABEZADO CON SELECTOR -->
    <div class="flex flex-col md:flex-row md:justify-between md:items-start gap-4 mb-6">
      <div>
        <h3 class="text-xl font-bold text-[var(--text-primary)] mb-2">{{ t('analytics.burndownTitle') || 'Gráfico Burndown' }}</h3>
        <p class="text-sm text-[var(--text-secondary)]">{{ t('analytics.burndownDesc') || 'Progreso real vs ideal de la épica' }}</p>
      </div>

      <!-- SELECTOR DE ÉPICA -->
      <div class="flex gap-2 w-full md:w-auto">
        <select 
          v-model="selectedEpic"

          class="w-full md:w-64 px-4 py-2 border border-[var(--border-subtle)] rounded-lg bg-[var(--bg-panel)] text-[var(--text-primary)] text-sm font-medium hover:border-[var(--teal)]/50 focus:outline-none focus:ring-2 focus:ring-[var(--teal)]/20 transition-colors"
        >
          <option value="">{{ t('analytics.selectEpic') || 'Seleccione una épica...' }}</option>
          <option v-for="epic in epicsStore.epics" :key="epic.id" :value="epic.id">
            {{ epic.title || t('analytics.untitledEpic') || 'Épica sin título' }}
          </option>
        </select>
      </div>
    </div>

    <!-- CONTENEDOR DEL GRÁFICO -->
    <div class="relative h-96 mb-6">
      <div v-if="!selectedEpic" class="absolute inset-0 flex flex-col items-center justify-center border-2 border-dashed border-[var(--border-subtle)] rounded-xl bg-[var(--bg-panel)]/50 text-center p-6">
        <span class="text-5xl mb-4 opacity-50">📈</span>
        <h4 class="text-lg font-semibold text-[var(--text-primary)]">{{ t('analytics.emptyChartTitle') || 'Selecciona una épica' }}</h4>
        <p class="text-sm text-[var(--text-muted)] mt-1 max-w-md">{{ t('analytics.emptyChartDesc') || 'Elige una épica en el menú de arriba para visualizar su progreso.' }}</p>
      </div>
      <canvas v-show="selectedEpic" ref="chartCanvas"></canvas>
    </div>

    <!-- INFORMACIÓN ADICIONAL (Tarjetas Inferiores) -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <!-- CARD: Velocidad Promedio -->
      <div class="p-4 bg-[var(--bg-panel)] rounded-lg border border-[var(--border-subtle)]">
        <p class="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-1">{{ t('analytics.avgVelocity') || 'Velocidad Promedio' }}</p>
        <p class="text-2xl font-bold text-[var(--teal)]">{{ avgVelocity }}</p>
        <p class="text-xs text-[var(--text-secondary)] mt-1">{{ t('analytics.ticketsPerDay') || 'tickets por día' }}</p>
      </div>

      <!-- CARD: Tiempo Estimado -->
      <div class="p-4 bg-[var(--bg-panel)] rounded-lg border border-[var(--border-subtle)]">
        <p class="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-1">{{ t('analytics.estimatedTime') || 'Tiempo Estimado' }}</p>
        <p class="text-2xl font-bold text-[var(--teal)]">{{ estimatedDays }}</p>
        <p class="text-xs text-[var(--text-secondary)] mt-1">{{ t('analytics.daysRemaining') || 'días restantes' }}</p>
      </div>

      <!-- CARD: Estado Dinámico -->
      <div class="p-4 rounded-lg border" :class="statusClass">
        <p class="text-xs font-semibold uppercase tracking-wider mb-1" :class="statusTextClass">{{ t('analytics.status') || 'Estado' }}</p>
        <p class="text-2xl font-bold" :class="statusTextClass">{{ status }}</p>
        <p class="text-xs mt-1" :class="statusTextClass">{{ statusMessage }}</p>
      </div>
    </div>

    <!-- LEYENDA DEL GRÁFICO (Manual) -->
    <div class="mt-6 pt-6 border-t border-[var(--border-subtle)] flex gap-6">
      <!-- Línea Ideal -->
      <div class="flex items-center gap-2">
        <div class="w-4 h-1 bg-[#9CA3AF] rounded" style="border-top: 2px dashed currentColor;"></div>
        <span class="text-sm text-[var(--text-secondary)]">{{ t('analytics.idealLine') || 'Línea Ideal' }}</span>
      </div>

      <!-- Línea Actual -->
      <div class="flex items-center gap-2">
        <div class="w-4 h-1 bg-[#06B7B2] rounded"></div>
        <span class="text-sm text-[var(--text-secondary)]">{{ t('analytics.actualLine') || 'Línea Real' }}</span>
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

import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useAnalyticsStore } from '@/stores/analytics'
import { useEpicsStore } from '@/stores/epics'
import { useI18n } from 'vue-i18n'
import type ChartType from 'chart.js/auto'

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
const { t, locale } = useI18n()

// Recibimos el ID de la app desde la vista principal
const props = defineProps<{ appId: string }>()

// REFERENCIAS REACTIVAS
const chartCanvas = ref<HTMLCanvasElement | null>(null)
const selectedEpic = ref('')
let chart: ChartType | null = null

// DATOS REALES (Inicializados vacíos para que el gráfico siempre sea visible)
const burndownData = ref<BurndownData>({
  dates: [],
  ideal: [],
  actual: [],
})

// === CÁLCULOS MATEMÁTICOS ===

// Función escudo para evitar cualquier NaN
const safeNum = (val: any, fallback = 0) => {
  if (val === null || val === undefined) return fallback;
  const n = Number(val);
  return isNaN(n) ? fallback : n;
};

/**
 * PROPIEDAD COMPUTADA: currentStats
 * DESCRIPCIÓN: Busca el último día real y alinea todos los datos
 */
const currentStats = computed(() => {
  const actual = Array.isArray(burndownData.value.actual) ? burndownData.value.actual : [];
  const ideal = Array.isArray(burndownData.value.ideal) ? burndownData.value.ideal : [];
  
  let lastValidIndex = -1;
  let ticketsRestantesHoy = 0; // Tickets que aún faltan por completar
  
  // Encontramos el índice exacto de "hoy" (el último dato que no es null)
  for (let i = 0; i < actual.length; i++) {
    if (actual[i] !== null && actual[i] !== undefined) {
      lastValidIndex = i;
      ticketsRestantesHoy = safeNum(actual[i]);
    }
  }
  
  // 1. Total de tickets al inicio (El punto más alto de la línea gris)
  const totalTickets = ideal.length > 0 ? safeNum(ideal[0]) : 0;
  
  // 2. Tickets que ya terminamos = (Total que había) - (Los que quedan pendientes hoy)
  const ticketsCompletados = Math.max(0, totalTickets - ticketsRestantesHoy);
  
  // 3. Días de trabajo (índice 0 significa que ha pasado 1 día)
  const diasTranscurridos = lastValidIndex >= 0 ? (lastValidIndex + 1) : 1;
  
  // 4. Cuántos tickets DEBERÍAN quedar hoy según el plan ideal (línea gris)
  const ticketsIdealesHoy = lastValidIndex >= 0 && ideal.length > lastValidIndex 
    ? safeNum(ideal[lastValidIndex]) 
    : 0;
  
  return { 
    lastValidIndex, 
    totalTickets, 
    ticketsRestantesHoy, 
    ticketsCompletados, 
    diasTranscurridos, 
    ticketsIdealesHoy 
  };
});

/**
 * PROPIEDAD COMPUTADA: avgVelocity
 * DESCRIPCIÓN: Calcula la velocidad promedio (tickets completados por día)
 * FÓRMULA: (Inicial - Actual) / número de días
 */
const avgVelocity = computed<number | string>(() => {
  const stats = currentStats.value;
  if (stats.lastValidIndex === -1 || stats.diasTranscurridos === 0) return 0;
  
  // Velocidad = Tickets Terminados / Días Trabajados
  const vel = stats.ticketsCompletados / stats.diasTranscurridos;
  return isNaN(vel) || !isFinite(vel) ? '0.0' : vel.toFixed(1);
});

/**
 * PROPIEDAD COMPUTADA: estimatedDays
 * DESCRIPCIÓN: Estima días faltantes basado en velocidad actual
 * CÁLCULO: tickets restantes / velocidad promedio
 */
const estimatedDays = computed<number | string>(() => {
  const stats = currentStats.value;
  if (stats.lastValidIndex === -1) return '-';
  
  const vel = Number(avgVelocity.value);
  // Si no avanzamos nada (velocidad 0), es imposible estimar cuándo terminaremos
  if (vel <= 0) return '-'; 
  
  // Días estimados = Tickets que faltan / Velocidad diaria
  return Math.ceil(stats.ticketsRestantesHoy / vel);
});

/**
 * PROPIEDAD COMPUTADA: status
 * DESCRIPCIÓN: Determina si está adelante o atrasado
 */
const status = computed<string>(() => {
  const stats = currentStats.value;
  if (stats.lastValidIndex === -1) return t('analytics.noData') || 'Sin datos';
  return stats.ticketsRestantesHoy <= stats.ticketsIdealesHoy 
    ? t('analytics.onTime') || 'A Tiempo' 
    : t('analytics.delayed') || 'Atrasado';
});

/**
 * PROPIEDAD COMPUTADA: statusMessage
 * DESCRIPCIÓN: Mensaje detallado del estado
 */
const statusMessage = computed<string>(() => {
  const stats = currentStats.value;
  if (stats.lastValidIndex === -1) return t('analytics.selectEpicProgress') || 'Seleccione una épica para ver el progreso';
  
  const diff = Math.ceil(Math.abs(stats.ticketsRestantesHoy - stats.ticketsIdealesHoy));
  return stats.ticketsRestantesHoy <= stats.ticketsIdealesHoy 
    ? `${diff} ${t('analytics.ticketsAhead') || 'tickets adelantado'}` 
    : `${diff} ${t('analytics.ticketsBehind') || 'tickets de retraso'}`;
});

/**
 * PROPIEDAD COMPUTADA: statusClass
 * DESCRIPCIÓN: Clases Tailwind para el color de fondo del estado
 */
const statusClass = computed<string>(() => {
  const stats = currentStats.value;
  if (stats.lastValidIndex === -1) return 'bg-[var(--bg-panel)] border-[var(--border-subtle)]';
  return stats.ticketsRestantesHoy <= stats.ticketsIdealesHoy 
    ? 'bg-emerald-500/10 border-emerald-500/30' 
    : 'bg-amber-500/10 border-amber-500/30';
});

/**
 * PROPIEDAD COMPUTADA: statusTextClass
 * DESCRIPCIÓN: Clases para el color de texto del estado
 */
const statusTextClass = computed<string>(() => {
  const stats = currentStats.value;
  if (stats.lastValidIndex === -1) return 'text-[var(--text-muted)]';
  return stats.ticketsRestantesHoy <= stats.ticketsIdealesHoy 
    ? 'text-emerald-600 dark:text-emerald-400' 
    : 'text-amber-600 dark:text-amber-400';
});

/**
 * FUNCIÓN: initChart
 * DESCRIPCIÓN: Inicializa o actualiza el gráfico de burndown
 * RESPONSABILIDADES:
 * - Crear instancia de Chart.js
 * - Configurar datasets para línea ideal y actual
 * - Aplicar estilos y colores
 * - Incluir opciones de interpolación y animación
 */
async function initChart() {
  if (!chartCanvas.value) return

  const { default: Chart } = await import('chart.js/auto')

  // Destruir gráfico anterior si existe
  if (chart) {
    chart.destroy()
    chart = null
  }

  const ctx = chartCanvas.value.getContext('2d')
  if (!ctx) return

  const idealColor = '#9CA3AF'
  const actualColor = '#06B7B2'
  const gridColor = 'rgba(100, 116, 139, 0.15)'
  const textColor = '#64748B'

  chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: burndownData.value.dates,
      datasets: [
        {
          // Línea Ideal
          label: t('analytics.idealLine') || 'Línea Ideal',
          data: burndownData.value.ideal,
          borderColor: idealColor,
          backgroundColor: 'transparent',
          borderWidth: 2,
          borderDash: [5, 5],
          pointRadius: 4,
          pointBackgroundColor: idealColor,
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
          pointHoverRadius: 6,
          tension: 0.4,
        },
        {
          // Línea Real
          label: t('analytics.actualLine') || 'Línea Real (Restantes)',
          data: burndownData.value.actual,
          borderColor: actualColor,
          backgroundColor: 'rgba(6, 183, 178, 0.1)',
          borderWidth: 3,
          pointRadius: 5,
          pointBackgroundColor: actualColor,
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
        legend: { display: false },
        tooltip: {
          backgroundColor: '#1E293B',
          padding: 12,
          titleFont: { size: 12, weight: 'bold' },
          bodyFont: { size: 11 },
          borderColor: actualColor,
          borderWidth: 1,
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: t('analytics.pendingTickets') || 'Tickets Pendientes',
            color: textColor,
          },
          ticks: { color: textColor, font: { size: 11 }, stepSize: 1 },
          grid: { color: gridColor },
        },
        x: {
          title: {
            display: true,
            text: t('analytics.date') || 'Fecha',
            color: textColor,
          },
          ticks: { color: textColor, font: { size: 11 } },
          grid: { display: false },
        },
      },
    },
  })
}

// ========== LIFECYCLE ==========
watch(() => props.appId, async (newAppId) => {
  if (newAppId) {
    selectedEpic.value = ''
    if (chart) {
      chart.destroy()
      chart = null
    }
    // Traemos las épicas reales de la base de datos
    await epicsStore.fetchByApp(newAppId)
  }
}, { immediate: true })

watch(selectedEpic, async (epicId) => {
  try {
    if (epicId) {
      await analyticsStore.fetchBurndown(epicId)
    } else {
      burndownData.value = { dates: [], ideal: [], actual: [] }
      initChart()
    }
  } catch (error) {
    console.error('Error cambiando épica:', error)
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
  async (newData: any) => {
    const data = newData?.burndown || newData; 
    
    if (data && data.dates) {
      burndownData.value = {
        dates: data.dates,
        ideal: data.ideal,
        actual: data.actual,
      }
      await nextTick()
      initChart()
    }
  },
  { deep: true, immediate: true }
)
onMounted(() => {
  if (burndownData.value.dates.length > 0) {
    nextTick(() => {
      initChart()
    })
  }
})

watch(locale, () => {
  if (selectedEpic.value && burndownData.value.dates.length > 0) {
    initChart()
  }
})
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
