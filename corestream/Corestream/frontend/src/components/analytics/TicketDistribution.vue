<template>
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        Tickets por estado
      </h3>
      <Bar :data="statusChart" :options="options" />
    </div>
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        Tickets por prioridad
      </h3>
      <Bar :data="priorityChart" :options="options" />
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * TicketDistribution: gráficos de barras con la cantidad de tickets
 * por estado y por prioridad (datos de GET /api/analytics/summary/{app_id}).
 */
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend
} from 'chart.js'
import { useAnalyticsStore } from '@/stores/analytics'

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend)

const analyticsStore = useAnalyticsStore()
const summary = computed(() => analyticsStore.summary)

const statusLabels: Record<string, string> = {
  TODO: 'Por hacer',
  IN_PROGRESS: 'En progreso',
  BLOCKED: 'Bloqueado',
  REDIRECTED: 'Redirigido',
  DONE: 'Completado'
}
const priorityLabels: Record<string, string> = {
  LOW: 'Baja',
  MEDIUM: 'Media',
  HIGH: 'Alta',
  URGENT: 'Urgente'
}

const statusChart = computed(() => {
  const data = summary.value?.by_status ?? {}
  const keys = Object.keys(statusLabels)
  return {
    labels: keys.map((k) => statusLabels[k]),
    datasets: [
      {
        label: 'Tickets',
        data: keys.map((k) => data[k] ?? 0),
        backgroundColor: ['#9ca3af', '#3b82f6', '#f97316', '#a855f7', '#22c55e']
      }
    ]
  }
})

const priorityChart = computed(() => {
  const data = summary.value?.by_priority ?? {}
  const keys = Object.keys(priorityLabels)
  return {
    labels: keys.map((k) => priorityLabels[k]),
    datasets: [
      {
        label: 'Tickets',
        data: keys.map((k) => data[k] ?? 0),
        backgroundColor: ['#22c55e', '#eab308', '#f97316', '#ef4444']
      }
    ]
  }
})

const options = {
  responsive: true,
  plugins: { legend: { display: false } },
  scales: { y: { beginAtZero: true, ticks: { precision: 0 } } }
}
</script>